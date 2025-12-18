"""
Veridia Search Engine - Configuration
Centralized configuration for all modules
"""
import os

# ============= PATH CONFIGURATION =============
# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directory containing raw text/JSON files
# Point to the DATA directory (Directly in Search-Engine root)
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "DATA"))

# JSON dataset path
JSON_DATASET_PATH = os.path.join(os.path.dirname(DATA_DIR), "VeridiaCore", "dataset.jsonl")

# Output directory for indices (Where barrels and lexicon are)
# Point to VeridiaCore (Directly in Search-Engine root)
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "VeridiaCore"))

# Index file paths
LEXICON_PATH = os.path.join(OUTPUT_DIR, "lexicon.txt")
FORWARD_INDEX_PATH = os.path.join(OUTPUT_DIR, "forward_index.txt")
INVERTED_INDEX_PATH = os.path.join(OUTPUT_DIR, "inverted_index.txt")
METADATA_PATH = os.path.join(OUTPUT_DIR, "document_metadata.txt")

# ============= INDEXING CONFIGURATION =============
# Maximum number of documents to index
MAX_DOCUMENTS = 300000

# Batch size for processing (larger = faster but more memory)
BATCH_SIZE = 50000

# Progress reporting interval
PROGRESS_INTERVAL = 10000

# ============= LANGUAGE FILTERING =============
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "of", "at", "by", "for", "with",
    "about", "against", "between", "into", "through", "during", "before", "after",
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
    "very", "can", "will", "just", "don", "should", "now", "are", "is", "was", "were",
    "this", "that", "these", "those", "have", "has", "had", "which", "it", "its"
}

# Minimum word length to index
MIN_WORD_LENGTH = 3

# ============= SEARCH CONFIGURATION =============
# Maximum number of results to return
MAX_RESULTS = 50

# Memory-mapped file usage (faster for large indices)
USE_MEMORY_MAPPING = True

# Cache size for frequent queries
QUERY_CACHE_SIZE = 1000