import os
import numpy as np

class VectorModel:
    def __init__(self, model_path):
        self.model_path = model_path
        self.vectors = {}
        self.vector_size = 0
        self.loaded = False

    def load_model(self):
        """
        Loads word vectors from a text file (GloVe format).
        Format: word val1 val2 ...
        """
        if not os.path.exists(self.model_path):
            print(f"Warning: Embeddings file not found at {self.model_path}. Semantic search will be disabled.")
            return

        print(f"Loading embeddings from {self.model_path}...")
        try:
            with open(self.model_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    word = parts[0]
                    # vectors might be floats
                    vec = np.array([float(x) for x in parts[1:]], dtype=np.float32)
                    self.vectors[word] = vec
                    
            if self.vectors:
                self.vector_size = len(next(iter(self.vectors.values())))
                self.loaded = True
                print(f"Loaded {len(self.vectors)} vectors of size {self.vector_size}.")
        except Exception as e:
            print(f"Error loading embeddings: {e}")

    def get_vector(self, word):
        return self.vectors.get(word.lower())

    def cosine_similarity(self, v1, v2):
        if v1 is None or v2 is None:
            return 0.0
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return np.dot(v1, v2) / (norm1 * norm2)

    def find_similar_words(self, query_word, top_n=5):
        """
        Finds synonyms using brute-force cosine similarity.
        For production, use a KDTree or Annoy, but this is sufficient for small/medium vocab.
        """
        if not self.loaded:
            return []
            
        target_vec = self.get_vector(query_word)
        if target_vec is None:
            return []
            
        scores = []
        # Optimization: We could use matrix multiplication if we stacked all vectors,
        # but iterating dict is safer for memory if massive, though slower.
        # Given constraints, let's try a simple iteration.
        
        for word, vec in self.vectors.items():
            if word == query_word:
                continue
            score = self.cosine_similarity(target_vec, vec)
            if score > 0.5: # Threshold for relevance
                scores.append((word, score))
        
        # Sort desc
        scores.sort(key=lambda x: x[1], reverse=True)
        return [w for w, s in scores[:top_n]]
