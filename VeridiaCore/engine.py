import os
import json
import re
import struct
import mmap
import time
import sqlite3
from .vector_model import VectorModel

class SearchEngine:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.metadata = {}
        self.word_offsets = {}
        self.barrels = {}
        self.barrel_files = {}
        
        self.dataset_file = None
        self.dataset_mmap = None
        self.doc_offsets_file = None
        self.doc_offsets_mmap = None
        
        self.vector_model = VectorModel(os.path.join(self.data_dir, "glove.txt"))
        
        self.offsets_dense_path = os.path.join(self.data_dir, "word_offsets_dense.bin")
        self.offsets_mmap = None
        self.offsets_file_handle = None

        # Connect to SQLite Lexicon (Memory Efficient)
        self.db_path = os.path.join(self.data_dir, "lexicon.db")
        self.conn = None
        if os.path.exists(self.db_path):
            try:
                self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                self.conn.row_factory = sqlite3.Row
                print(f"  [OK] Connected to SQLite lexicon at {self.db_path}")
            except Exception as e:
                print(f"  [ERR] Failed to connect to DB: {e}")
        else:
            print(f"  [ERR] Lexicon DB not found at {self.db_path}. Please run build_sqlite.py")

        self.load_indices()
        self.vector_model.load_model()
        
        # --- DYNAMIC MEMORY INDEX (For Instant Demo Uploads) ---
        self.dynamic_index = {} # word -> set(doc_id)
        self.dynamic_metadata = {} # doc_id -> {title, filename, text, authors}
        self.dynamic_doc_id_counter = 10000000 # Start high to avoid collision

    def add_document_dynamic(self, title, text, filename):
        """Add a document instantly to memory-only index"""
        doc_id = self.dynamic_doc_id_counter
        self.dynamic_doc_id_counter += 1
        
        # storage
        self.dynamic_metadata[doc_id] = {
            "title": title,
            "filename": filename,
            "text": text,
            "authors": "Uploaded User",
            "abstract": text[:300] + "..."
        }
        self.metadata[doc_id] = {"title": title, "filename": filename} # consistency
        
        # index
        words = re.findall(r'[a-z0-9]+', text.lower())
        for word in words:
            if len(word) < 2: continue
            if word not in self.dynamic_index:
                self.dynamic_index[word] = set()
            self.dynamic_index[word].add(doc_id)
            
        print(f"  [DYNAMIC] Added '{filename}' (ID: {doc_id}) to memory index.")
        return doc_id

    def __del__(self):
        try:
            if self.conn: self.conn.close()
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

    def get_word_id(self, word):
        """Get ID for a word from SQLite"""
        if not self.conn: return None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM lexicon WHERE word = ?", (word,))
            row = cursor.fetchone()
            return row['id'] if row else None
        except: return None

    def load_indices(self):
        print("Loading indices...")
        
        # Load Offsets (Dense Mmap)
        if os.path.exists(self.offsets_dense_path):
            try:
                self.offsets_file_handle = open(self.offsets_dense_path, 'rb')
                self.offsets_mmap = mmap.mmap(self.offsets_file_handle.fileno(), 0, access=mmap.ACCESS_READ)
                print(f"  [OK] Mapped offsets ({len(self.offsets_mmap)//16:,} records)")
            except Exception as e:
                print(f"  [ERR] Failed to map offsets: {e}")

        # Load Barrels
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

        # Load Metadata
        meta_path = os.path.join(self.data_dir, "document_metadata.txt")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split('||')
                        if len(parts) >= 2:
                            doc_id = int(parts[0])
                            title = parts[1][:200] if len(parts[1]) > 200 else parts[1]
                            filename = parts[2] if len(parts) > 2 else "unknown.txt"
                            self.metadata[doc_id] = {"title": title, "filename": filename}
                print(f"  [OK] Loaded {len(self.metadata):,} documents metadata")
            except Exception as e:
                print(f"  [ERR] Metadata load failed: {e}")
        
        # Load Dataset for content retrieval
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
                print("  [OK] Dataset mapped for content retrieval")
            except Exception as e:
                print(f"  [WARN] Dataset mapping failed: {e}")
        
        print("[OK] READY")

    def get_word_info(self, word_id):
        """Get barrel info for a word ID"""
        if not self.offsets_mmap: return None
        start = word_id * 16
        if start + 16 > len(self.offsets_mmap): return None
        return struct.unpack_from('<IQI', self.offsets_mmap, start)

    def get_suggestions(self, prefix):
        """Get autocomplete suggestions from SQLite"""
        if not prefix or not self.conn: return []
        try:
            cursor = self.conn.cursor()
            query = prefix.lower()
            # Optimization: Use >= and < for range scan if index exists, but LIKE is easier
            # Lexicon is indexed on 'word'. LIKE 'prefix%' uses index in SQLite!
            cursor.execute("SELECT word FROM lexicon WHERE word LIKE ? ORDER BY word LIMIT 10", (query + '%',))
            return [row['word'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Autocomplete error: {e}")
            return []

    def search(self, query, use_semantic=True):
        STOP_WORDS = {
            "a", "an", "the", "and", "or", "but", "if", "of", "at", "by", "for", "with",
            "about", "in", "on", "is", "it", "to"
        }
        
        # Allow both letters and numbers
        all_words = re.findall(r'[a-z0-9]+', query.lower())
        if not all_words: return []
        
        # Relaxed filtering
        keywords = [w for w in all_words if w not in STOP_WORDS]
        keywords = [w for w in keywords if len(w) >= 2 or w.isdigit()]
        
        if not keywords: keywords = all_words
        
        print(f"  Searching for keywords: {keywords}")
        doc_scores = {}
        
        for word in keywords:
            terms = {word}
            if use_semantic:
                synonyms = self.vector_model.find_similar_words(word, top_n=2)
                terms.update(synonyms)
            
            for term in terms:
                # 1. Search Main Disk Index
                word_id = self.get_word_id(term)
                if word_id is not None:
                    info = self.get_word_info(word_id)
                    if info:
                        barrel_id, offset, count = info
                        if barrel_id in self.barrels and self.barrels[barrel_id]:
                            mm = self.barrels[barrel_id]
                            if offset + count * 4 <= len(mm):
                                doc_ids = struct.unpack_from(f'<{count}I', mm, offset)
                                weight = 1.0 if term == word else 0.5
                                for doc_id in doc_ids:
                                    if doc_id not in doc_scores:
                                        doc_scores[doc_id] = 0
                                    doc_scores[doc_id] += weight
                
                # 2. Search Dynamic Memory Index
                if term in self.dynamic_index:
                    for doc_id in self.dynamic_index[term]:
                        weight = 1.0 if term == word else 0.5
                        if doc_id not in doc_scores: doc_scores[doc_id] = 0
                        doc_scores[doc_id] += weight * 2.0 # Boost fresh content

        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for doc_id, score in sorted_docs[:50]:
            if doc_id in self.metadata:
                results.append({
                    "doc_id": doc_id,
                    "title": self.metadata[doc_id]["title"],
                    "filename": self.metadata[doc_id]["filename"],
                    "score": round(score, 2)
                })
        
        print(f"  Found {len(results)} results")
        return results

    def get_document_content(self, doc_id):
        # 1. Check Dynamic Index First
        if hasattr(self, 'dynamic_metadata') and doc_id in self.dynamic_metadata:
             return self.dynamic_metadata[doc_id]

        # 2. Check Disk Index
        if doc_id not in self.metadata: 
            return None
        if not self.dataset_mmap or not self.doc_offsets_mmap: 
            return None
        
        try:
            off_pos = (doc_id - 1) * 8
            if off_pos + 8 > len(self.doc_offsets_mmap): 
                return None
            
            byte_offset = struct.unpack_from('Q', self.doc_offsets_mmap, off_pos)[0]
            end_pos = self.dataset_mmap.find(b'\n', byte_offset)
            if end_pos == -1: 
                end_pos = len(self.dataset_mmap)
            
            line_bytes = self.dataset_mmap[byte_offset:end_pos]
            line = line_bytes.decode('utf-8', errors='ignore')
            
            data = json.loads(line)
            return {
                "title": data.get('title', 'No Title'),
                "abstract": data.get('abstract', '')[:500],
                "text": data.get('text', data.get('abstract', 'No content available')), 
                "authors": data.get('authors', 'Unknown'),
                "filename": self.metadata[doc_id]["filename"]
            }
        except Exception as e:
            print(f"  [ERROR] Content retrieval failed for doc {doc_id}: {e}")
            return None
