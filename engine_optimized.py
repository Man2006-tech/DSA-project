"""
Veridia Search Engine - Optimized Search Engine
Fast query processing with caching
"""
import os
import time
from collections import defaultdict
from functools import lru_cache
from text_processor import clean_and_tokenize
from config import (
    LEXICON_PATH, INVERTED_INDEX_PATH, METADATA_PATH,
    MAX_RESULTS, QUERY_CACHE_SIZE
)


class SearchEngine:
    def __init__(self):
        """Initialize search engine and load indices into memory."""
        print("Initializing Veridia Search Engine...")
        start = time.time()
        
        self.lexicon = {}           # word -> word_id
        self.inverted_index = {}    # word_id -> [doc_ids]
        self.metadata = {}          # doc_id -> {title, authors}
        
        self._load_indices()
        
        elapsed = time.time() - start
        print(f"✓ Engine ready in {elapsed:.2f}s")
        print(f"  - Lexicon: {len(self.lexicon):,} words")
        print(f"  - Documents: {len(self.metadata):,}")
    
    def _load_indices(self):
        """Load all indices into memory for fast searching."""
        
        # Load lexicon
        if os.path.exists(LEXICON_PATH):
            with open(LEXICON_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        word, word_id = parts
                        self.lexicon[word] = word_id
        else:
            print(f"WARNING: Lexicon not found at {LEXICON_PATH}")
        
        # Load inverted index
        if os.path.exists(INVERTED_INDEX_PATH):
            with open(INVERTED_INDEX_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        word_id = parts[0]
                        doc_ids = parts[1].split()
                        self.inverted_index[word_id] = doc_ids
        else:
            print(f"WARNING: Inverted index not found at {INVERTED_INDEX_PATH}")
        
        # Load metadata
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        doc_id = parts[0]
                        title = parts[1] if len(parts) > 1 else "Untitled"
                        authors = parts[2] if len(parts) > 2 else "Unknown"
                        self.metadata[doc_id] = {
                            "title": title,
                            "authors": authors
                        }
        else:
            print(f"WARNING: Metadata not found at {METADATA_PATH}")
    
    @lru_cache(maxsize=QUERY_CACHE_SIZE)
    def search(self, query):
        """
        Search for documents matching the query.
        Uses LRU cache for frequently searched queries.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching documents with scores
        """
        if not query or not query.strip():
            return []
        
        start_time = time.time()
        
        # Tokenize query
        query_words = clean_and_tokenize(query)
        
        if not query_words:
            return []
        
        # Get word IDs for query terms
        query_word_ids = []
        for word in query_words:
            if word in self.lexicon:
                query_word_ids.append(self.lexicon[word])
        
        if not query_word_ids:
            return []
        
        # Score documents using term frequency
        doc_scores = defaultdict(int)
        
        for word_id in query_word_ids:
            if word_id in self.inverted_index:
                for doc_id in self.inverted_index[word_id]:
                    doc_scores[doc_id] += 1
        
        # Sort by score (descending)
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Build results
        results = []
        for doc_id, score in sorted_docs[:MAX_RESULTS]:
            if doc_id in self.metadata:
                meta = self.metadata[doc_id]
                results.append({
                    "doc_id": doc_id,
                    "title": meta["title"],
                    "authors": meta["authors"],
                    "filename": f"arxiv_{doc_id}.txt",
                    "score": score
                })
        
        elapsed = time.time() - start_time
        
        # Log query performance
        print(f"Query: '{query}' | Results: {len(results)} | Time: {elapsed*1000:.1f}ms")
        
        return results
    
    def get_stats(self):
        """Get search engine statistics."""
        return {
            "total_documents": len(self.metadata),
            "unique_words": len(self.lexicon),
            "index_entries": len(self.inverted_index),
            "cache_info": self.search.cache_info()._asdict()
        }


# Singleton instance for Flask app
_search_engine_instance = None

def get_search_engine():
    """Get or create search engine instance (singleton pattern)."""
    global _search_engine_instance
    
    if _search_engine_instance is None:
        _search_engine_instance = SearchEngine()
    
    return _search_engine_instance