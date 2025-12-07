"""
Veridia Search Engine - Text Processing Module
Optimized text cleaning and tokenization
"""
import re
from config import STOP_WORDS, MIN_WORD_LENGTH

# Compile regex pattern once for performance
WORD_PATTERN = re.compile(r'[a-z]+')

def clean_and_tokenize(text):
    """
    Fast tokenization and cleaning of text.
    
    Args:
        text: Raw input text
        
    Returns:
        List of cleaned tokens
    """
    # Convert to lowercase and extract words in one pass
    words = WORD_PATTERN.findall(text.lower())
    
    # Filter in one pass using list comprehension
    return [w for w in words if len(w) >= MIN_WORD_LENGTH and w not in STOP_WORDS]


def is_english_text(text, min_english_words=5):
    """
    Quick English language detection.
    
    Args:
        text: Text to check
        min_english_words: Minimum number of English stop words required
        
    Returns:
        True if text appears to be English
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
    Extract a clean title preview from text.
    
    Args:
        text: Source text
        max_length: Maximum length of preview
        
    Returns:
        Cleaned preview string
    """
    # Remove newlines and extra spaces
    cleaned = ' '.join(text.split())
    
    if len(cleaned) <= max_length:
        return cleaned
    
    # Cut at word boundary
    preview = cleaned[:max_length]
    last_space = preview.rfind(' ')
    
    if last_space > 0:
        preview = preview[:last_space]
    
    return preview + "..."