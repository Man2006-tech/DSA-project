import os
import numpy as np
import time

class VectorModel:
    def __init__(self, model_path):
        self.model_path = model_path
        self.vocab = {} # word -> index
        self.words = [] # index -> word
        self.matrix = None # numpy array
        self.vector_size = 0
        self.loaded = False

    def load_model(self):
        """
        Loads word vectors. Checks for binary cache first (.npy + .vocab).
        If not found, parses text file and creates cache.
        """
        base_path = os.path.splitext(self.model_path)[0]
        npy_path = base_path + ".npy"
        vocab_path = base_path + ".vocab"
        
        # Try loading binary cache
        if os.path.exists(npy_path) and os.path.exists(vocab_path):
            try:
                print(f"Loading cached vectors from {npy_path}...")
                data = np.load(npy_path, mmap_mode='r') # mmap for instant load!
                
                # Load vocab
                with open(vocab_path, 'r', encoding='utf-8') as f:
                    self.words = f.read().splitlines()
                
                self.vocab = {w: i for i, w in enumerate(self.words)}
                self.matrix = data
                self.vector_size = self.matrix.shape[1]
                self.loaded = True
                print(f"  [OK] Instant load: {len(self.words)} vectors.")
                return
            except Exception as e:
                print(f"  [WARN] Failed to load cache: {e}. Re-parsing...")

        if not os.path.exists(self.model_path):
            print(f"Warning: Embeddings file not found at {self.model_path}. Semantic search disabled.")
            return

        print(f"Parsing embeddings text from {self.model_path} (First Run)...")
        t_start = time.time()
        try:
            vectors = []
            self.words = []
            self.vocab = {}
            
            with open(self.model_path, 'r', encoding='utf-8') as f:
                idx = 0
                for line in f:
                    parts = line.strip().split()
                    if len(parts) < 2: continue
                    
                    word = parts[0]
                    vals = [float(x) for x in parts[1:]]
                    
                    # Normalize
                    vec = np.array(vals, dtype=np.float32)
                    norm = np.linalg.norm(vec)
                    if norm > 0: vec /= norm
                    
                    vectors.append(vec)
                    self.words.append(word)
                    self.vocab[word] = idx
                    idx += 1
            
            if vectors:
                self.matrix = np.vstack(vectors)
                self.vector_size = self.matrix.shape[1]
                self.loaded = True
                print(f"  Parsed {len(self.words)} vectors in {time.time()-t_start:.2f}s.")
                
                # Save cache for next time
                print("  Saving binary cache for next time...")
                np.save(npy_path, self.matrix)
                with open(vocab_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.words))
        except Exception as e:
            print(f"Error loading embeddings: {e}")

    def get_vector(self, word):
        if not self.loaded: return None
        idx = self.vocab.get(word.lower())
        if idx is not None:
            return self.matrix[idx]
        return None

    def find_similar_words(self, query_word, top_n=5):
        if not self.loaded: return []
        word_lower = query_word.lower()
        if word_lower not in self.vocab: return []
            
        target_idx = self.vocab[word_lower]
        target_vec = self.matrix[target_idx]
        
        scores = np.dot(self.matrix, target_vec)
        
        # Sort top N (excluding self)
        top_indices = np.argsort(scores)[::-1][1:top_n+1]
        
        results = []
        for idx in top_indices:
            if self.words[idx] == word_lower: continue
            if scores[idx] < 0.5: break
            results.append(self.words[idx])
            if len(results) >= top_n: break
            
        return results
