import sys
import os
import time # Added for timing the search
# --- CHANGE 1: Use absolute path for robustness ---
# This ensures Python can find the 'engine.py' module reliably
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'VeridiaCore')))
# -------------------------------------------------

from engine import SearchEngine

def test():
    # --- CHANGE 2: Simplified Data Path ---
    # Assuming SearchEngine is designed to look in its own directory
    # or the current working directory for index files.
    # If the index files are *in* the same directory as 'engine.py', 
    # we can pass the engine module's location as the data directory.
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'VeridiaCore'))
    
    # If your index files are built *outside* of VeridiaCore, use:
    # data_dir = os.path.dirname(__file__) # This assumes index files are in the test script directory
    
    print(f"Initializing engine with data from: {data_dir}")
    engine = SearchEngine(data_dir)
    
    query = "protein"
    print(f"Searching for '{query}'...")
    
    # --- CHANGE 3: Add Timing for Performance Measurement ---
    search_start_time = time.time()
    results = engine.search(query)
    search_end_time = time.time()
    # -----------------------------------------------------

    print(f"Found {len(results)} results in {round(search_end_time - search_start_time, 4)} seconds.")
    
    # Display results and check for edge case
    if results:
        print("\n--- Top 5 Results ---")
        for i, res in enumerate(results[:5]):
            print(f"  {i+1}. {res['title']} (Score: {res['score']:.4f})")
    else:
        print("No results found for this query.")

if __name__ == "__main__":
    test()