"""
AI-Powered Autocorrection and Suggestion Engine
Using machine learning and semantic analysis for intelligent suggestions
Similar to Google's advanced search assistance
"""

import os
import json
import numpy as np
from typing import List, Tuple, Dict, Set
from collections import Counter
import difflib

# Try to import ML libraries
try:
    from thefuzz import fuzz, process
    HAS_THEFUZZ = True
except ImportError:
    HAS_THEFUZZ = False
    print("Warning: python-Levenshtein not installed. Install with: pip install thefuzz python-Levenshtein")

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    print("Warning: TextBlob not installed. Install with: pip install textblob")

try:
    import nltk
    from nltk.corpus import wordnet
    from nltk.tokenize import word_tokenize
    # Download required resources
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    print("Warning: NLTK not installed. Install with: pip install nltk")


class AIAutoCorrector:
    """
    Advanced spell correction using multiple AI techniques:
    - Edit distance (Levenshtein)
    - Fuzzy matching
    - Semantic similarity
    - Frequency analysis
    """
    
    def __init__(self, vocabulary: Set[str], word_frequencies: Dict[str, int] = None):
        """
        Initialize the autocorrector
        
        Args:
            vocabulary: Set of valid words from lexicon
            word_frequencies: Dict of word -> frequency for ranking
        """
        self.vocabulary = vocabulary
        self.word_frequencies = word_frequencies or {}
        self.max_distance = 2  # Max edit distance
        
        print(f"[AI AutoCorrector] Initialized with {len(vocabulary):,} words in vocabulary")
    
    def get_edit_distance_suggestions(self, word: str, max_suggestions: int = 5) -> List[Tuple[str, float]]:
        """
        Find suggestions using edit distance (Levenshtein)
        Fast for single character errors and typos
        """
        if len(word) < 2:
            return []
        
        suggestions = []
        word_lower = word.lower()
        
        # Find words within edit distance
        for vocab_word in self.vocabulary:
            if abs(len(vocab_word) - len(word_lower)) > self.max_distance:
                continue
            
            # Calculate similarity
            similarity = difflib.SequenceMatcher(None, word_lower, vocab_word).ratio()
            
            if similarity > 0.7:  # 70% similarity threshold
                # Score by frequency
                freq_score = self.word_frequencies.get(vocab_word, 1)
                combined_score = similarity * (1 + np.log1p(freq_score))
                suggestions.append((vocab_word, combined_score))
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:max_suggestions]
    
    def get_fuzzy_suggestions(self, word: str, max_suggestions: int = 5) -> List[Tuple[str, float]]:
        """
        Find suggestions using fuzzy matching (thefuzz library)
        More sophisticated than simple edit distance
        """
        if not HAS_THEFUZZ or len(word) < 2:
            return []
        
        word_lower = word.lower()
        candidates = list(self.vocabulary)
        
        # Use token_set_ratio for better matching
        matches = process.extract(
            word_lower,
            candidates,
            scorer=fuzz.token_set_ratio,
            limit=max_suggestions * 2
        )
        
        # Filter by score and rerank by frequency
        suggestions = []
        for match_word, score in matches:
            if score > 75:  # 75% match threshold
                freq_score = self.word_frequencies.get(match_word, 1)
                combined_score = (score / 100) * (1 + np.log1p(freq_score))
                suggestions.append((match_word, combined_score))
        
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:max_suggestions]
    
    def get_semantic_suggestions(self, word: str, max_suggestions: int = 5) -> List[Tuple[str, float]]:
        """
        Find semantically similar words using WordNet
        Finds synonyms and related concepts
        """
        if not HAS_NLTK:
            return []
        
        suggestions = []
        word_lower = word.lower()
        
        try:
            # Get synsets (synonym sets) for the word
            synsets = wordnet.synsets(word_lower)
            
            if not synsets:
                return []
            
            # Collect all related words
            related_words = set()
            for synset in synsets[:3]:  # Use top 3 synsets
                # Get lemmas (word forms)
                for lemma in synset.lemmas():
                    related_word = lemma.name().replace('_', ' ')
                    if related_word.lower() != word_lower and related_word in self.vocabulary:
                        related_words.add(related_word)
                
                # Get hypernyms (more general terms)
                for hypernym in synset.hypernyms()[:2]:
                    for lemma in hypernym.lemmas():
                        related_word = lemma.name().replace('_', ' ')
                        if related_word.lower() != word_lower and related_word in self.vocabulary:
                            related_words.add(related_word)
            
            # Rank by frequency
            for related_word in related_words:
                freq_score = self.word_frequencies.get(related_word, 1)
                suggestions.append((related_word, freq_score))
            
            suggestions.sort(key=lambda x: x[1], reverse=True)
            return suggestions[:max_suggestions]
        
        except Exception as e:
            print(f"Warning in semantic suggestions: {e}")
            return []
    
    def correct_word(self, word: str, max_suggestions: int = 5) -> Dict:
        """
        Comprehensive spell correction using multiple techniques
        
        Returns:
            {
                'original': input word,
                'is_correct': bool,
                'suggestions': [(word, score), ...],
                'correction_type': 'fuzzy'|'edit_distance'|'semantic'|'none'
            }
        """
        word_lower = word.lower()
        
        # Check if word is correct
        if word_lower in self.vocabulary:
            return {
                'original': word,
                'is_correct': True,
                'suggestions': [],
                'correction_type': 'none'
            }
        
        # Try different correction strategies
        suggestions = []
        correction_type = 'none'
        
        # 1. Fuzzy matching (most accurate)
        fuzzy_suggestions = self.get_fuzzy_suggestions(word, max_suggestions)
        if fuzzy_suggestions:
            suggestions = fuzzy_suggestions
            correction_type = 'fuzzy'
        
        # 2. Edit distance (fast, good for typos)
        if not suggestions or len(suggestions) < 3:
            edit_suggestions = self.get_edit_distance_suggestions(word, max_suggestions)
            if edit_suggestions:
                # Combine with fuzzy suggestions
                existing_words = {s[0] for s in suggestions}
                for word_sugg, score in edit_suggestions:
                    if word_sugg not in existing_words:
                        suggestions.append((word_sugg, score))
                        if not correction_type or correction_type == 'fuzzy':
                            correction_type = 'edit_distance'
        
        # 3. Semantic suggestions (for word sense errors)
        if len(suggestions) < 3:
            semantic_suggestions = self.get_semantic_suggestions(word, max_suggestions)
            if semantic_suggestions:
                existing_words = {s[0] for s in suggestions}
                for word_sugg, score in semantic_suggestions:
                    if word_sugg not in existing_words:
                        suggestions.append((word_sugg, score))
                        correction_type = 'semantic'
        
        # Sort and limit
        suggestions.sort(key=lambda x: x[1], reverse=True)
        suggestions = suggestions[:max_suggestions]
        
        return {
            'original': word,
            'is_correct': False,
            'suggestions': [(w, float(s)) for w, s in suggestions],
            'correction_type': correction_type
        }


class AISuggestionEngine:
    """
    Advanced suggestion engine for search queries
    Generates suggestions based on:
    - Query frequency analysis
    - Semantic similarity
    - Context understanding
    - User intent prediction
    """
    
    def __init__(self, lexicon: Dict[str, int], document_frequencies: Dict[str, int] = None):
        """
        Initialize suggestion engine
        
        Args:
            lexicon: word -> word_id mapping
            document_frequencies: word -> doc_frequency mapping
        """
        self.lexicon = lexicon
        self.document_frequencies = document_frequencies or {}
        self.vocabulary = set(lexicon.keys())
        
        # Calculate TF-IDF weights
        self._calculate_importance_scores()
        
        print(f"[AI Suggestion Engine] Initialized with {len(lexicon):,} words")
    
    def _calculate_importance_scores(self):
        """Calculate importance score for each word"""
        self.importance_scores = {}
        
        total_words = len(self.vocabulary)
        
        for word in self.vocabulary:
            doc_freq = self.document_frequencies.get(word, 1)
            # Inverse document frequency
            idf = np.log(total_words / max(1, doc_freq))
            self.importance_scores[word] = idf
    
    def get_prefix_suggestions(self, prefix: str, max_suggestions: int = 10) -> List[Dict]:
        """
        Get suggestions based on prefix (auto-complete style)
        
        Returns:
            [{
                'word': suggestion,
                'score': relevance_score,
                'frequency': doc_frequency,
                'type': 'prefix'
            }, ...]
        """
        if not prefix or len(prefix) < 1:
            return []
        
        prefix_lower = prefix.lower()
        suggestions = []
        
        # Find all words starting with prefix
        for word in self.vocabulary:
            if word.startswith(prefix_lower):
                score = self.importance_scores.get(word, 1)
                suggestions.append({
                    'word': word,
                    'score': float(score),
                    'frequency': self.document_frequencies.get(word, 0),
                    'type': 'prefix'
                })
        
        # Sort by importance and frequency
        suggestions.sort(key=lambda x: (x['score'], x['frequency']), reverse=True)
        return suggestions[:max_suggestions]
    
    def get_related_suggestions(self, query_words: List[str], max_suggestions: int = 10) -> List[Dict]:
        """
        Get suggestions related to query words
        Finds frequently co-occurring terms
        
        Args:
            query_words: List of words in the query
            max_suggestions: Number of suggestions to return
        
        Returns:
            List of related word suggestions
        """
        if not query_words:
            return []
        
        related_words = Counter()
        
        # For each query word, find related vocabulary
        for query_word in query_words:
            query_lower = query_word.lower()
            
            # Find words with high semantic similarity
            for vocab_word in self.vocabulary:
                if vocab_word == query_lower:
                    continue
                
                # Simple similarity: common prefixes, shared characters
                similarity = difflib.SequenceMatcher(None, query_lower, vocab_word).ratio()
                
                if similarity > 0.5:  # At least 50% similar
                    score = self.importance_scores.get(vocab_word, 1) * similarity
                    related_words[vocab_word] += score
        
        # Convert to suggestions
        suggestions = [
            {
                'word': word,
                'score': float(score),
                'frequency': self.document_frequencies.get(word, 0),
                'type': 'related'
            }
            for word, score in related_words.most_common(max_suggestions)
        ]
        
        return suggestions
    
    def get_trending_suggestions(self, max_suggestions: int = 5) -> List[Dict]:
        """
        Get trending/popular search terms
        Based on document frequency
        """
        trending = []
        
        for word in self.vocabulary:
            freq = self.document_frequencies.get(word, 0)
            if freq > 100:  # Minimum frequency threshold
                trending.append({
                    'word': word,
                    'score': float(self.importance_scores.get(word, 1)),
                    'frequency': freq,
                    'type': 'trending'
                })
        
        # Sort by frequency
        trending.sort(key=lambda x: x['frequency'], reverse=True)
        return trending[:max_suggestions]
    
    def get_query_completions(self, partial_query: str, max_suggestions: int = 10) -> List[Dict]:
        """
        Generate complete query suggestions from partial input
        Combines prefix matching with semantic relevance
        """
        words = partial_query.strip().split()
        
        if not words:
            return []
        
        last_word = words[-1].lower()
        
        # Get prefix suggestions for the last word
        prefix_suggestions = self.get_prefix_suggestions(last_word, max_suggestions * 2)
        
        # Get related suggestions based on previous words
        if len(words) > 1:
            related = self.get_related_suggestions(words[:-1], max_suggestions)
        else:
            related = []
        
        # Combine and deduplicate
        suggestions = []
        seen = set()
        
        for sugg in prefix_suggestions + related:
            if sugg['word'] not in seen:
                suggestions.append(sugg)
                seen.add(sugg['word'])
        
        return suggestions[:max_suggestions]


class SemanticQueryAnalyzer:
    """
    Analyzes query intent and structure using NLP
    Provides contextual suggestions
    """
    
    def __init__(self, vector_model=None):
        """
        Initialize analyzer
        
        Args:
            vector_model: VectorModel instance for semantic analysis
        """
        self.vector_model = vector_model
    
    def analyze_query(self, query: str) -> Dict:
        """
        Analyze query for intent and structure
        
        Returns:
            {
                'original_query': str,
                'tokens': List[str],
                'intent': str,  # 'search'|'filter'|'compare'
                'entities': List[str],
                'complexity': str  # 'simple'|'complex'|'advanced'
            }
        """
        query_lower = query.lower().strip()
        tokens = query_lower.split()
        
        # Determine complexity
        if len(tokens) > 5:
            complexity = 'complex'
        elif len(tokens) > 2:
            complexity = 'advanced'
        else:
            complexity = 'simple'
        
        # Simple intent detection
        if any(word in query_lower for word in ['vs', 'versus', 'compare', 'difference']):
            intent = 'compare'
        elif any(word in query_lower for word in ['filter', 'where', 'find', 'get']):
            intent = 'filter'
        else:
            intent = 'search'
        
        return {
            'original_query': query,
            'tokens': tokens,
            'intent': intent,
            'entities': tokens,  # Simplified for now
            'complexity': complexity
        }


# Example initialization
def create_ai_corrector_from_engine(search_engine):
    """
    Create AI corrector from existing search engine
    """
    vocabulary = set(search_engine.lexicon.keys())
    
    # Calculate word frequencies from inverted index
    word_frequencies = {}
    for word_id, word in [(v, k) for k, v in search_engine.lexicon.items()]:
        # Count documents containing this word
        word_frequencies[word] = len(search_engine.word_offsets.get(word_id, (None, None, 0))[2:])
    
    return AIAutoCorrector(vocabulary, word_frequencies)


def create_ai_suggestion_engine(search_engine):
    """
    Create AI suggestion engine from existing search engine
    """
    lexicon = search_engine.lexicon
    
    # Calculate document frequencies
    doc_frequencies = {}
    for word_id, word in [(v, k) for k, v in lexicon.items()]:
        if word_id in search_engine.word_offsets:
            doc_frequencies[word] = len(search_engine.word_offsets.get(word_id, (None, None, 0))[2:])
    
    return AISuggestionEngine(lexicon, doc_frequencies)


if __name__ == "__main__":
    # Test the modules
    print("AI Autocorrection and Suggestion Engine")
    print("=" * 60)
    
    # Test vocabulary
    test_vocab = {
        'machine', 'learning', 'artificial', 'intelligence',
        'neural', 'network', 'deep', 'algorithm', 'data',
        'science', 'python', 'tensorflow', 'pytorch'
    }
    
    # Test frequencies
    test_freqs = {
        'machine': 150, 'learning': 140, 'neural': 120,
        'network': 110, 'algorithm': 95, 'data': 200,
        'artificial': 85, 'intelligence': 80, 'python': 75
    }
    
    # Test corrector
    print("\n[Test] AI AutoCorrector")
    corrector = AIAutoCorrector(test_vocab, test_freqs)
    
    test_words = ['machne', 'lerning', 'neurel', 'dataa']
    for word in test_words:
        result = corrector.correct_word(word, max_suggestions=3)
        print(f"\nWord: '{word}'")
        print(f"  Correct: {result['is_correct']}")
        print(f"  Type: {result['correction_type']}")
        if result['suggestions']:
            print(f"  Suggestions: {result['suggestions']}")
    
    # Test suggestion engine
    print("\n\n[Test] AI Suggestion Engine")
    suggestion_engine = AISuggestionEngine(
        {w: i for i, w in enumerate(test_vocab)},
        test_freqs
    )
    
    # Test prefix suggestions
    prefix_sugg = suggestion_engine.get_prefix_suggestions('neur', max_suggestions=3)
    print(f"\nPrefix 'neur': {[s['word'] for s in prefix_sugg]}")
    
    # Test related suggestions
    related_sugg = suggestion_engine.get_related_suggestions(['machine', 'learning'], max_suggestions=3)
    print(f"Related to 'machine learning': {[s['word'] for s in related_sugg]}")
