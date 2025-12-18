import os
import numpy as np

class VectorModel:
    def __init__(self, model_path):
        self.model_path = model_path
        self.vocab = {} # word -> index
        self.words = [] # index -> word
        self.matrix = None # numpy array (normalized)
        self.vector_size = 0
        self.loaded = False

    def load_model(self):
        """
        Loads word vectors from a text file (GloVe format).
        Optimized to use numpy matrix for fast similarity search.
        """
        if not os.path.exists(self.model_path):
            print(f"Warning: Embeddings file not found at {self.model_path}. Semantic search will be disabled.")
            return

        print(f"Loading embeddings from {self.model_path}...")
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
                    
                    # Normalize vector immediately for cosine similarity
                    vec = np.array(vals, dtype=np.float32)
                    norm = np.linalg.norm(vec)
                    if norm > 0:
                        vec /= norm
                    
                    vectors.append(vec)
                    self.words.append(word)
                    self.vocab[word] = idx
                    idx += 1
            
            if vectors:
                self.matrix = np.vstack(vectors)
                self.vector_size = self.matrix.shape[1]
                self.loaded = True
                print(f"Loaded {len(self.words)} vectors of size {self.vector_size}. Matrix shape: {self.matrix.shape}")
        except Exception as e:
            print(f"Error loading embeddings: {e}")

    def get_vector(self, word):
        if not self.loaded: return None
        idx = self.vocab.get(word.lower())
        if idx is not None:
            return self.matrix[idx]
        return None

    def find_similar_words(self, query_word, top_n=5):
        """
        Finds synonyms using vectorized cosine similarity.
        Complexity: O(V) but heavily optimized by BLAS.
        """
        if not self.loaded:
            return []
            
        word_lower = query_word.lower()
        if word_lower not in self.vocab:
            return []
            
        target_idx = self.vocab[word_lower]
        target_vec = self.matrix[target_idx]
        
        # Matrix-vector multiplication for cosine similarity (since vectors are normalized)
        # scores[i] = dot(matrix[i], target_vec)
        scores = np.dot(self.matrix, target_vec)
        
        # Get top N indices
        # partition is faster than sort
        # But we need sorted results for top_n
        top_indices = np.argsort(scores)[::-1][1:top_n+1] # Exclude self (index 0 usually, but argsort puts self first as score=1.0)
        
        results = []
        for idx in top_indices:
            # Check if it's the same word (redundant if logic is correct but safe)
            if self.words[idx] == word_lower: continue
            
            # Additional check: score threshold
            if scores[idx] < 0.5: break
            
            results.append(self.words[idx])
            if len(results) >= top_n: break
            
        return results
