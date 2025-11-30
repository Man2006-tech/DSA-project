import os
import re

class SearchEngine:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.lexicon = {}
        self.inverted_index = {}
        self.metadata = {}
        self.load_indices()

    def load_indices(self):
        print("Loading indices...")
        
        # Load Lexicon
        lex_path = os.path.join(self.data_dir, "lexicon.txt")
        if os.path.exists(lex_path):
            with open(lex_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        self.lexicon[parts[0]] = parts[1]
        
        # Load Inverted Index
        inv_path = os.path.join(self.data_dir, "inverted_index.txt")
        if os.path.exists(inv_path):
            with open(inv_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        word_id = parts[0]
                        doc_ids = parts[1].split()
                        self.inverted_index[word_id] = doc_ids

        # Load Metadata
        meta_path = os.path.join(self.data_dir, "document_metadata.txt")
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 3:
                        doc_id = parts[0]
                        filename = parts[1]
                        title = parts[2]
                        self.metadata[doc_id] = {"filename": filename, "title": title}
        
        print(f"Loaded {len(self.lexicon)} words, {len(self.inverted_index)} postings, {len(self.metadata)} docs.")

    def search(self, query):
        """
        Performs a search for the given query.
        Returns a list of results: [{'doc_id': ..., 'title': ..., 'filename': ..., 'score': ...}]
        """
        words = re.findall(r'[a-z]+', query.lower())
        if not words:
            return []

        # Map query words to WordIDs
        query_word_ids = []
        for word in words:
            if word in self.lexicon:
                query_word_ids.append(self.lexicon[word])
        
        if not query_word_ids:
            return []

        # Ranking: Simple Term Frequency in Query (how many query terms match)
        doc_scores = {}
        
        for word_id in query_word_ids:
            if word_id in self.inverted_index:
                for doc_id in self.inverted_index[word_id]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1
        
        # Sort by score (descending)
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in sorted_docs[:50]: # Limit to top 50
            if doc_id in self.metadata:
                meta = self.metadata[doc_id]
                results.append({
                    "doc_id": doc_id,
                    "title": meta["title"],
                    "filename": meta["filename"],
                    "score": score
                })
        
        return results
