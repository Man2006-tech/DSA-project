import sys
import os
import traceback

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERIDIA_CORE = os.path.join(BASE_DIR, 'VeridiaCore')
sys.path.append(BASE_DIR)

from VeridiaCore.engine import SearchEngine

def debug_search():
    print("Initializing Engine...")
    try:
        engine = SearchEngine(VERIDIA_CORE)
        print("Engine Ready.")
        
        query = "dengue is a dangerous disease"
        print(f"Testing Search: '{query}'")
        
        # Test 1: Standard Search
        print("--- Attempt 1: Standard Search ---")
        results = engine.search(query, use_semantic=False)
        print(f"Results: {len(results)}")
        
        # Test 2: Semantic Search (might fail if no model)
        print("--- Attempt 2: Semantic Search ---")
        results = engine.search(query, use_semantic=True)
        print(f"Results: {len(results)}")
        
    except Exception:
        print("\nCRASH DETECTED:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_search()
