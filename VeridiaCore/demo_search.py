from engine import SearchEngine
import os

def main():
    print("Initializing Search Engine...")
    data_dir = os.path.dirname(os.path.abspath(__file__))
    engine = SearchEngine(data_dir)
    
    print("\n--- VeridiaCore Interactive Search ---")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            query = input("Enter search query: ").strip()
        except EOFError:
            break
            
        if query.lower() in ('exit', 'quit'):
            break
        
        if not query:
            continue
            
        results = engine.search(query)
        print(f"\nResults for '{query}':")
        if results:
            for r in results:
                print(f"  [{r['score']}] {r['title']} ({r['filename']})")
                # Optional: Print snippet if available
                content = engine.get_document_content(r['doc_id'])
                if content:
                    print(f"     Snippet: {content['abstract'][:100]}...")
        else:
            print("  No results found.")
        print("-" * 40)
