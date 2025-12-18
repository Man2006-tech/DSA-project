import sys
import os

# Ensure we can import from VeridiaCore
sys.path.append(os.getcwd())

try:
    from VeridiaCore.engine import SearchEngine
    
    print("Loading Search Engine...")
    engine = SearchEngine("VeridiaCore")
    
    queries = ["dengue", "computer", "algorithm"]
    
    for q in queries:
        print(f"\nTesting query: '{q}'")
        results = engine.search(q)
        if results:
            print(f"  Found {len(results)} results.")
            print(f"  Top result: {results[0]['title']}")
        else:
            print("  No results found.")
            
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
