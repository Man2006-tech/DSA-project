"""
Veridia Search Engine - Text Processing Module
Optimized text cleaning and tokenization with LRU Caching
"""
import re
from functools import lru_cache # Added for performance optimization
from config import STOP_WORDS, MIN_WORD_LENGTH

# Compile regex pattern once for performance
WORD_PATTERN = re.compile(r'[a-z]+')

# --- VALUABLE CHANGE: Added LRU Cache ---
# Caching the results of tokenization prevents re-processing common strings
@lru_cache(maxsize=1024)
def clean_and_tokenize(text):
    """
    Fast tokenization and cleaning of text with result caching.
    
    Args:
        text: Raw input text
        
    Returns:
        List of cleaned tokens
    """
    if not text:
        return []

    # Convert to lowercase and extract words in one pass
    words = WORD_PATTERN.findall(text.lower())
    
    # Filter in one pass using list comprehension
    return [w for w in words if len(w) >= MIN_WORD_LENGTH and w not in STOP_WORDS]


def is_english_text(text, min_english_words=5):
    """
    Quick English language detection using basic stop-word indicators.
    """
    # Check first 500 characters for speed
    sample = text[:500].lower()
    words = WORD_PATTERN.findall(sample)
    
    # Count English indicators
    english_indicators = {"the", "and", "is", "of", "in", "to", "a", "that"}
    count = sum(1 for w in words if w in english_indicators)
    
    return count >= min_english_words


def extract_title_preview(text, max_length=200):
    """
    Extract a clean title preview from text, cutting at word boundaries.
    """
    # Remove newlines and extra spaces
    cleaned = ' '.join(text.split())
    
    if len(cleaned) <= max_length:
        return cleaned
    
    # Cut at word boundary to avoid partial words
    preview = cleaned[:max_length]
    last_space = preview.rfind(' ')
    
    if last_space > 0:
        preview = preview[:last_space]
    
    return preview + "..."