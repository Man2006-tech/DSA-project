import os
import sys
import pickle
import gc

DATA_DIR = os.path.abspath('VeridiaCore')
LEX_PATH = os.path.join(DATA_DIR, "lexicon.txt")
CACHE_PATH = os.path.join(DATA_DIR, "lexicon_cache.pkl")

def build_cache():
    print(f"Building cache from {LEX_PATH}...")
    lexicon = {}
    sorted_lexicon = []
    
    try:
        # Read file
        with open(LEX_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    lexicon[parts[0]] = int(parts[1])
        
        print(f"Loaded {len(lexicon)} words. Sorting...")
        sorted_lexicon = sorted(lexicon.keys())
        
        print("Saving pickle...")
        with open(CACHE_PATH, 'wb') as f:
            pickle.dump({
                'lexicon': lexicon,
                'sorted_lexicon': sorted_lexicon
            }, f)
        print("[OK] Cache built successfully.")
        
    except MemoryError:
        print("[ERR] MemoryError during build.")
    except Exception as e:
        print(f"[ERR] {e}")

if __name__ == "__main__":
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)
    build_cache()
