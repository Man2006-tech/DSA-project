import os
import json
import re
import struct
import mmap
import time
from .trie import Trie
from .vector_model import VectorModel

class SearchEngine:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.lexicon = {}
        self.metadata = {}
        
        # WordID -> (BarrelID, Offset, Count)
        self.word_offsets = {} 
        
        # BarrelID -> mmap object
        self.barrels = {}
        self.barrel_files = {} # Keep file handles to close later if needed
        
        # New Components
        self.trie = Trie()
        self.vector_model = VectorModel(os.path.join(self.data_dir, "glove.txt"))
        
        self.offsets_file = os.path.join(self.data_dir, "word_offsets_barrels.bin")
        
        self.load_indices()
        self.vector_model.load_model()

    def load_indices(self):
        print("Loading indices (Barrels Mode)...")
        
        # Clear existing data to avoid duplication on reload
        self.lexicon.clear()
        self.metadata.clear()
        self.word_offsets.clear()
        self.trie = Trie()
        
        # Close existing barrel file handles
        for f in self.barrel_files.values():
            try:
                f.close()
            except:
                pass
        self.barrel_files.clear()
        self.barrels.clear()
        
        # Load Lexicon and Trie
        lex_path = os.path.join(self.data_dir, "lexicon.txt")
        if os.path.exists(lex_path):
            with open(lex_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        word = parts[0]
                        word_id = int(parts[1])
                        self.lexicon[word] = word_id
                        self.trie.insert(word)
            print(f"  ✓ Loaded lexicon: {len(self.lexicon):,} words")
        
        # Load Word Offsets (Barrels Version)
        # Format: WordID (4B) | BarrelID (4B) | Offset (8B) | Count (4B) = 20 bytes
        if os.path.exists(self.offsets_file):
            print(f"  ✓ Loading barrel offsets from {self.offsets_file}...")
            with open(self.offsets_file, 'rb') as f:
                while True:
                    data = f.read(20)
                    if not data:
                        break
                    word_id, barrel_id, offset, count = struct.unpack('<IIQI', data)
                    self.word_offsets[word_id] = (barrel_id, offset, count)
        else:
            print(f"  WARNING: {self.offsets_file} not found. Search will fail.")

        # Open Barrels (Lazy or Eager? Let's do Eager mmap for now for speed)
        # Assuming barrels are named barrel_0.bin, barrel_1.bin, etc.
        # We can find them by listing dir or by max barrel_id found
        max_barrel = 0
        if self.word_offsets:
            # Quick way to find max barrel if we assumed contiguous
            # But let's just look for files
            for filename in os.listdir(self.data_dir):
                if filename.startswith("barrel_") and filename.endswith(".bin"):
                    try:
                        bid = int(filename.split('_')[1].split('.')[0])
                        max_barrel = max(max_barrel, bid)
                    except:
                        pass
            
            print(f"  ✓ Detected {max_barrel + 1} barrel file(s).")
            
            for i in range(max_barrel + 1):
                path = os.path.join(self.data_dir, f"barrel_{i}.bin")
                if os.path.exists(path):
                    f = open(path, 'rb')
                    self.barrel_files[i] = f
                    try:
                        # Windows mmap requires non-empty file
                        if os.path.getsize(path) > 0:
                            self.barrels[i] = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                        else:
                            self.barrels[i] = None
                    except Exception as e:
                        print(f"  Warning: Error mapping barrel {i}: {e}")
                        self.barrels[i] = None

        # Load Metadata
        meta_path = os.path.join(self.data_dir, "document_metadata.txt")
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 3:
                        doc_id = int(parts[0])
                        filename = parts[1]
                        title = parts[2]
                        self.metadata[doc_id] = {"filename": filename, "title": title}
        
        print(f"Loaded {len(self.lexicon)} words, {len(self.word_offsets)} offsets, {len(self.metadata)} docs.")

    def get_suggestions(self, prefix):
        return self.trie.search_prefix(prefix.lower())

    def search(self, query, use_semantic=True):
        words = re.findall(r'[a-z]+', query.lower())
        if not words:
            return []

        # List of sets: each set contains doc_ids that match one query concept
        concept_doc_sets = []
        relevant_doc_scores = {}

        for word in words:
            # 1. Expand Terms
            terms = {word}
            if use_semantic:
                synonyms = self.vector_model.find_similar_words(word, top_n=3)
                terms.update(synonyms)
            
            # 2. Collect Docs for this Concept
            current_concept_docs = set()
            
            for term in terms:
                if term in self.lexicon:
                    word_id = self.lexicon[term]
                    if word_id in self.word_offsets:
                        barrel_id, offset, count = self.word_offsets[word_id]
                        
                        if barrel_id in self.barrels and self.barrels[barrel_id]:
                            mm = self.barrels[barrel_id]
                            
                            if offset + count * 4 <= mm.size():
                                doc_ids = struct.unpack_from(f'<{count}I', mm, offset)
                                
                                current_concept_docs.update(doc_ids)
                                
                                weight = 1.5 if term == word else 0.8
                                for doc_id in doc_ids:
                                    relevant_doc_scores[doc_id] = relevant_doc_scores.get(doc_id, 0) + weight

            if not current_concept_docs:
                    return [] 
                    
            concept_doc_sets.append(current_concept_docs)

        # 3. Intersect
        if not concept_doc_sets:
            return []
            
        final_doc_ids = set.intersection(*concept_doc_sets)
        
        if not final_doc_ids:
            return []

        # 4. Filter and Sort
        final_results = []
        for doc_id in final_doc_ids:
            score = relevant_doc_scores.get(doc_id, 0)
            final_results.append((doc_id, score))
            
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in final_results[:50]:
            if doc_id in self.metadata:
                meta = self.metadata[doc_id]
                results.append({
                    "doc_id": doc_id,
                    "title": meta["title"],
                    "filename": meta["filename"],
                    "score": round(score, 2)
                })
        
        return results
    
    def get_document_content(self, doc_id):
        if doc_id not in self.metadata:
            return None
            
        offset_pos = (doc_id - 1) * 8
        doc_offset_file = os.path.join(self.data_dir, "doc_offsets.bin")
        jsonl_file = os.path.join(self.data_dir, "dataset.jsonl")
        
        if not os.path.exists(doc_offset_file) or not os.path.exists(jsonl_file):
            return None
            
        try:
            with open(doc_offset_file, 'rb') as f:
                f.seek(offset_pos)
                data = f.read(8)
                if not data:
                    return None
                byte_offset = struct.unpack('Q', data)[0]
                
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                f.seek(byte_offset)
                line = f.readline()
                if line:
                    data = json.loads(line)
                    title = data.get('title', 'No Title').replace('\n', ' ')
                    abstract = data.get('abstract', '').replace('\n', ' ')
                    return {"title": title, "abstract": abstract, "full": line}
        except Exception as e:
            print(f"Error retrieving doc {doc_id}: {e}")
            return None
        return None
