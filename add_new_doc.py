import os
import time
from incremental_indexer import IncrementalIndexer
from config import OUTPUT_DIR

def add_single_document():
    print("="*60)
    print("      VERIDIA SEARCH - IMMEDIATE INDEXER")
    print("="*60)
    print("This tool adds a new document to the LIVE index in < 1 second.")
    print("No full rebuild required.\n")
    
    title = input("Enter Document Title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return
        
    print("\nEnter Document Text (Paste content, press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    text = "\n".join(lines)
    
    if not text.strip():
        print("Text cannot be empty.")
        return
        
    authors = input("\nEnter Authors (Optional): ").strip() or "Unknown"
    
    # Initialize indexer
    try:
        indexer = IncrementalIndexer(OUTPUT_DIR)
        
        print(f"\nAdding '{title}'...")
        start = time.time()
        
        # Add document
        indexer.add_documents([(title, text, authors)])
        
        elapsed = time.time() - start
        
        print("\n" + "="*60)
        print(f"SUCCESS! Document added in {elapsed:.2f} seconds.")
        print(f"New Index Size: {indexer.get_status()['next_doc_id']} documents")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error adding document: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_single_document()
    input("\nPress Enter to exit...")
