import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'VeridiaCore'))
from engine import SearchEngine

def test():
    data_dir = os.path.join(os.path.dirname(__file__), 'VeridiaCore')
    print(f"Initializing engine with {data_dir}...")
    engine = SearchEngine(data_dir)
    
    query = "protein"
    print(f"Searching for '{query}'...")
    results = engine.search(query)
    print(f"Found {len(results)} results.")
    for res in results[:5]:
        print(f"- {res['title']} (Score: {res['score']})")

if __name__ == "__main__":
    test()
