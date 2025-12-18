import sys
import os

# Add the inner directory to path to import engine
sys.path.append(os.path.join(os.path.dirname(__file__), 'VeridiaCore'))

from engine import SearchEngine

def test_search():
    data_dir = os.path.join(os.path.dirname(__file__), 'VeridiaCore')
    print(f"Data Directory: {data_dir}")
    
    if not os.path.exists(data_dir):
        print("ERROR: Data directory not found!")
        return

    try:
        engine = SearchEngine(data_dir)
        
        # Test with a common word
        query = "computer" 
        print(f"Searching for: '{query}'")
        results = engine.search(query)
        
        print(f"Found {len(results)} results.")
        for res in results[:5]:
            print(res)
            
        # Test with another word if first one fails
        if not results:
            query = "science"
            print(f"Searching for: '{query}'")
            results = engine.search(query)
            print(f"Found {len(results)} results.")
            for res in results[:5]:
                print(res)

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
