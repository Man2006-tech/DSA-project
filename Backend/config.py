"""
Veridia Search Engine - Configuration (FIXED)
Centralized configuration for all modules
"""
import os

# ============= PATH CONFIGURATION =============
# Base directory of the project (assuming this file is in Backend/)
# Root is one level up
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Data directory containing raw text/JSON files
DATA_DIR = os.path.join(BASE_DIR, "DATA")
# Output directory for indices (VeridiaCore)
OUTPUT_DIR = os.path.join(BASE_DIR, "VeridiaCore")

# JSON dataset path
JSON_DATASET_PATH = os.path.join(OUTPUT_DIR, "dataset.jsonl")

# Index file paths
LEXICON_PATH = os.path.join(OUTPUT_DIR, "lexicon.txt")
FORWARD_INDEX_PATH = os.path.join(OUTPUT_DIR, "forward_index.txt")
INVERTED_INDEX_PATH = os.path.join(OUTPUT_DIR, "inverted_index.txt")
METADATA_PATH = os.path.join(OUTPUT_DIR, "document_metadata.txt")

# ============= INDEXING CONFIGURATION =============
MAX_DOCUMENTS = 300000
BATCH_SIZE = 50000
PROGRESS_INTERVAL = 10000

# ============= LANGUAGE FILTERING =============
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "of", "at", "by", "for", "with",
    "about", "against", "between", "into", "through", "during", "before", "after",
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
    "very", "s", "t", "can", "will", "just", "don", "should", "now", "are", "is",
    "was", "were", "have", "has", "had", "do", "does", "did", "be", "been", "being",
    "this", "that", "these", "those", "have", "has", "had", "which", "it", "its"
}

MIN_WORD_LENGTH = 3

# ============= SEARCH CONFIGURATION =============
MAX_RESULTS = 50
USE_MEMORY_MAPPING = True
QUERY_CACHE_SIZE = 1000