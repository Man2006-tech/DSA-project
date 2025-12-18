import os
import json
import re
import struct
import mmap
import time
import bisect
from .vector_model import VectorModel
# Trie removed

class SearchEngine:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.lexicon = {}
        self.sorted_lexicon = [] # For bisect suggestions
        self.metadata = {}
        self.word_offsets = {} 
        self.barrels = {}
        self.barrel_files = {} 
        
        # Persistent Handles for Enrichment
        self.dataset_file = None
        self.dataset_mmap = None
        self.doc_offsets_file = None
        self.doc_offsets_mmap = None
        
        # Components
        self.vector_model = VectorModel(os.path.join(self.data_dir, "glove.txt"))
        
        self.offsets_file = os.path.join(self.data_dir, "word_offsets_barrels.bin")
        self.offsets_dense_path = os.path.join(self.data_dir, "word_offsets_dense.bin")
        self.offsets_mmap = None
        self.offsets_file_handle = None

        self.load_indices()
        self.vector_model.load_model()

    def __del__(self):
        # Cleanup handles
        try:
            if self.dataset_mmap: self.dataset_mmap.close()
            if self.dataset_file: self.dataset_file.close()
            if self.doc_offsets_mmap: self.doc_offsets_mmap.close()
            if self.doc_offsets_file: self.doc_offsets_file.close()
            if self.offsets_mmap: self.offsets_mmap.close()
            if self.offsets_file_handle: self.offsets_file_handle.close()
            for f in self.barrel_files.values():
                try: f.close()
                except: pass
        except: pass

    def load_indices(self):
        print("Loading indices (Optimized Bisect)...")
        
        self.lexicon.clear()
        self.sorted_lexicon = []
        self.id_to_word = {}
        
        # 1. Load Lexicon
        lex_cache_path = os.path.join(self.data_dir, "lexicon_cache.pkl")
        loaded_from_cache = False
        
        try:
            if os.path.exists(lex_cache_path):
                print("  Loading lexicon from cache (fast)...")
                import pickle
                with open(lex_cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.lexicon = cache_data['lexicon']
                    self.sorted_lexicon = cache_data['sorted_lexicon']
                    # self.id_to_word could be rebuilt or cached. Rebuilding is fast enough or cache it too.
                    self.id_to_word = {v: k for k, v in self.lexicon.items()} 
                print(f"  [OK] Lexicon cache loaded ({len(self.lexicon):,} words).")
                loaded_from_cache = True
        except Exception as e:
            print(f"  [WARN] Failed to load lexicon cache: {e}")

        if not loaded_from_cache:
            lex_path = os.path.join(self.data_dir, "lexicon.txt")
            if os.path.exists(lex_path):
                print("  Loading lexicon from text...")
                with open(lex_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split('\t')
                        if len(parts) == 2:
                            word = parts[0]
                            word_id = int(parts[1])
                            self.lexicon[word] = word_id
                            self.id_to_word[word_id] = word
                
                # Prepare for Autocomplete
                print(f"  [OK] Lexicon loaded ({len(self.lexicon):,} words). Sorting for autocomplete...")
                t_start = time.time()
                self.sorted_lexicon = sorted(self.lexicon.keys())
                print(f"  [OK] Sorted in {time.time()-t_start:.2f}s")
                
                # Save cache
                try:
                    print("  Saving lexicon cache...")
                    import pickle
                    with open(lex_cache_path, 'wb') as f:
                        pickle.dump({
                            'lexicon': self.lexicon,
                            'sorted_lexicon': self.sorted_lexicon
                        }, f)
                    print("  [OK] Lexicon cache saved.")
                except Exception as e:
                    print(f"  [WARN] Failed to save cache: {e}")
                
            else:
                 print(f"  [ERR] Lexicon not found at {lex_path}")
        
        # 2. Load Offsets (Dense Mmap)
        if os.path.exists(self.offsets_dense_path):
            try:
                self.offsets_file_handle = open(self.offsets_dense_path, 'rb')
                self.offsets_mmap = mmap.mmap(self.offsets_file_handle.fileno(), 0, access=mmap.ACCESS_READ)
                print(f"  [OK] Mapped offsets ({len(self.offsets_mmap)//16:,} records)")
            except Exception as e:
                print(f"  [ERR] Failed to map offsets: {e}")
        else:
            print(f"  [WARN] {self.offsets_dense_path} missing!")

        # 3. Barrels (Mmap)
        max_barrel = 0
        for filename in os.listdir(self.data_dir):
            if filename.startswith("barrel_") and filename.endswith(".bin"):
                try:
                    bid = int(filename.split('_')[1].split('.')[0])
                    max_barrel = max(max_barrel, bid)
                except: pass
        
        print(f"  [OK] Barrels: 0 to {max_barrel}")
        for i in range(max_barrel + 1):
            path = os.path.join(self.data_dir, f"barrel_{i}.bin")
            if os.path.exists(path) and os.path.getsize(path) > 0:
                f = open(path, 'rb')
                self.barrel_files[i] = f
                self.barrels[i] = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            else:
                self.barrels[i] = None

        # 4. Metadata
        meta_path = os.path.join(self.data_dir, "document_metadata.txt")
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 3:
                        doc_id = int(parts[0])
                        raw_title = parts[1]
                        # Fix display issue: Truncate very long titles (likely parse errors)
                        title = raw_title[:150] + "..." if len(raw_title) > 150 else raw_title
                        self.metadata[doc_id] = {"title": title, "filename": parts[2]}
                        
        # 5. Persistent Dataset Access
        jsonl_path = os.path.join(self.data_dir, "dataset.jsonl")
        offsets_path = os.path.join(self.data_dir, "doc_offsets.bin")
        
        if os.path.exists(jsonl_path) and os.path.exists(offsets_path):
            try:
                self.dataset_file = open(jsonl_path, 'rb') 
                if os.path.getsize(jsonl_path) > 0:
                    self.dataset_mmap = mmap.mmap(self.dataset_file.fileno(), 0, access=mmap.ACCESS_READ)
                
                self.doc_offsets_file = open(offsets_path, 'rb')
                if os.path.getsize(offsets_path) > 0:
                    self.doc_offsets_mmap = mmap.mmap(self.doc_offsets_file.fileno(), 0, access=mmap.ACCESS_READ)
                print("  [OK] Dataset & Doc Offsets mapped.")
            except Exception as e:
                print(f"  [ERR] Failed to map dataset: {e}")
        else:
            print("  [WARN] Dataset components missing.")
            
        print("READY.")

    def get_word_info(self, word_id):
        if not self.offsets_mmap: return None
        start = word_id * 16
        if start + 16 > len(self.offsets_mmap): return None
        return struct.unpack_from('<IQI', self.offsets_mmap, start)

    def get_suggestions(self, prefix):
        if not prefix: return []
        prefix = prefix.lower()
        
        # Binary search for start
        idx = bisect.bisect_left(self.sorted_lexicon, prefix)
        
        suggestions = []
        # Collect matches
        for j in range(idx, len(self.sorted_lexicon)):
            word = self.sorted_lexicon[j]
            if not word.startswith(prefix):
                break
            suggestions.append(word)
            if len(suggestions) >= 8: # Limit
                break
                
        # Optional: Sort shorter words first? 
        # They are already sorted alphabetically. 'apple' comes before 'apples'. Good.
        return suggestions

    def search(self, query, use_semantic=True):
        STOP_WORDS = {
            "a", "an", "the", "and", "or", "but", "if", "of", "at", "by", "for", "with",
            "about", "against", "between", "into", "through", "during", "before", "after",
            "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over",
            "under", "again", "further", "then", "once", "here", "there", "when", "where",
            "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
            "very", "can", "will", "just", "don", "should", "now", "are", "is", "was", "were",
            "this", "that", "these", "those", "have", "has", "had", "which", "it", "its"
        }
        
        all_words = re.findall(r'[a-z]+', query.lower())
        if not all_words: return []
        
        keywords = [w for w in all_words if w not in STOP_WORDS]
        if not keywords: keywords = all_words
        
        concept_doc_sets = []
        doc_scores = {}
        
        for word in keywords:
            terms = {word}
            if use_semantic:
                synonyms = self.vector_model.find_similar_words(word, top_n=2)
                terms.update(synonyms)
            
            current_concept_docs = set()
            
            for term in terms:
                if term in self.lexicon:
                    word_id = self.lexicon[term]
                    info = self.get_word_info(word_id)
                    if info:
                        barrel_id, offset, count = info
                        if barrel_id in self.barrels and self.barrels[barrel_id]:
                             mm = self.barrels[barrel_id]
                             if offset + count * 4 <= len(mm):
                                 doc_ids = struct.unpack_from(f'<{count}I', mm, offset)
                                 current_concept_docs.update(doc_ids)
                                 
                                 weight = 1.0 if term == word else 0.7
                                 for doc_id in doc_ids:
                                     doc_scores[doc_id] = doc_scores.get(doc_id, 0) + weight

            if current_concept_docs:
                concept_doc_sets.append(current_concept_docs)
        
        final_doc_ids = set()
        results_mode = "STRICT"
        
        if len(concept_doc_sets) == len(keywords):
            try:
                final_doc_ids = set.intersection(*concept_doc_sets)
            except: pass
            
        if len(final_doc_ids) < 5:
            results_mode = "FALLBACK"
            sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
            final_doc_ids = [did for did, score in sorted_docs[:100]]
            
        final_results = []
        for doc_id in final_doc_ids:
             score = doc_scores.get(doc_id, 0)
             if results_mode == "STRICT": score *= 2.0
             final_results.append((doc_id, score))
             
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        output = []
        for doc_id, score in final_results[:50]:
            if doc_id in self.metadata:
                output.append({
                    "doc_id": doc_id,
                    "title": self.metadata[doc_id]["title"],
                    "filename": self.metadata[doc_id]["filename"],
                    "score": round(score, 2)
                })
        return output

    def get_document_content(self, doc_id):
        if doc_id not in self.metadata: return None
        if not self.dataset_mmap or not self.doc_offsets_mmap: return None
        
        try:
            off_pos = (doc_id - 1) * 8
            if off_pos + 8 > len(self.doc_offsets_mmap): return None
            
            byte_offset = struct.unpack_from('Q', self.doc_offsets_mmap, off_pos)[0]
            
            end_pos = self.dataset_mmap.find(b'\n', byte_offset)
            if end_pos == -1: end_pos = len(self.dataset_mmap)
            
            line_bytes = self.dataset_mmap[byte_offset:end_pos]
            line = line_bytes.decode('utf-8')
            
            data = json.loads(line)
            title = data.get('title', 'No Title').replace('\n', ' ')
            abstract = data.get('abstract', '').replace('\n', ' ')
            return {"title": title, "abstract": abstract, "full": line}
            
        except Exception as e:
            return None
