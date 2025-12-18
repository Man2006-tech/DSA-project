import os
import time
import json
import re
from incremental_indexer import IncrementalIndexer
from config import OUTPUT_DIR

def parse_xml_content(content):
    """Simple regex-based XML parser to extract text content"""
    # Remove tags
    text = re.sub(r'<[^>]+>', ' ', content)
    return " ".join(text.split())

def parse_json_content(content):
    """Try to extract meaningful text from JSON"""
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            # Try common fields
            parts = []
            for key in ['title', 'text', 'content', 'body', 'abstract', 'description']:
                if key in data and isinstance(data[key], str):
                    parts.append(data[key])
            
            if parts:
                return "\n".join(parts)
            
            # Fallback: dump values
            return " ".join([str(v) for v in data.values() if isinstance(v, (str, int, float))])
        elif isinstance(data, list):
            return " ".join([str(x) for x in data if isinstance(x, (str, int, float))])
        else:
            return str(data)
    except:
        return content

def add_file_document():
    print("="*60)
    print("      VERIDIA SEARCH - UNIVERSAL FILE INGESTER")
    print("="*60)
    print("Supports: .txt, .json, .xml")
    print("Adds to LIVE index in < 1 second.\n")
    
    file_path = input("Enter full path to file: ").strip()
    
    # Remove quotes if user copied path as "path"
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]
        
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {file_path}")
        return
        
    try:
        start_read = time.time()
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()
            
        # Parse based on extension
        if ext == '.json':
            print("  Detected JSON format...")
            content = parse_json_content(raw_content)
        elif ext == '.xml':
            print("  Detected XML format...")
            content = parse_xml_content(raw_content)
        else:
            # Default to text
            content = raw_content
            
        # Use filename as fallback title
        lines = content.split('\n')
        title = lines[0][:100].strip() if lines else filename
        if not title or len(title) < 3:
            title = filename
            
        authors = "Unknown"
        
        print(f"\nRead '{filename}' in {time.time() - start_read:.4f}s")
        print(f"Extracted {len(content)} characters of text.")
        
        # Initialize indexer
        indexer = IncrementalIndexer(OUTPUT_DIR)
        
        print(f"Adding '{title}' to index...")
        start_index = time.time()
        
        # Add document
        indexer.add_documents([(title, content, authors)])
        
        elapsed = time.time() - start_index
        
        print("\n" + "="*60)
        print(f"SUCCESS! File added in {elapsed:.2f} seconds.")
        print(f"New Index Size: {indexer.get_status()['next_doc_id']} documents")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error adding file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_file_document()
    input("\nPress Enter to exit...")
