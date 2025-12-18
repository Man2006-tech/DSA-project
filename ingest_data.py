import os
import time
from incremental_indexer import IncrementalIndexer
from config import DATA_DIR, OUTPUT_DIR

# Actual DATA dir containing text files is .../Veridia_Core/DATA
# config.py has DATA_DIR pointing to .../Veridia_Core/DATA
# incremental_indexer uses OUTPUT_DIR for indices (VeridiaCore)

import json
import re

def parse_xml_content(content):
    """Simple regex-based XML parser to extract text content"""
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
            if parts: return "\n".join(parts)
            return " ".join([str(v) for v in data.values() if isinstance(v, (str, int, float))])
        elif isinstance(data, list):
            return " ".join([str(x) for x in data if isinstance(x, (str, int, float))])
        return str(data)
    except:
        return content

def ingest_new_data():
    indexer = IncrementalIndexer(OUTPUT_DIR)
    
    # Load existing filenames from metadata to avoid duplicates
    indexed_files = set()
    if os.path.exists(indexer.metadata_path):
        with open(indexer.metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    indexed_files.add(parts[1])
                    
    print(f"Index contains {len(indexed_files)} documents.")
    print(f"Scanning {DATA_DIR} for new files (.txt, .json, .xml)...")
    
    new_docs = []
    
    # Walk through DATA_DIR
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            # Support multiple extensions
            ext = os.path.splitext(file)[1].lower()
            if ext in ['.txt', '.json', '.xml']:
                if file not in indexed_files:
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            raw_content = f.read()
                            
                        # Parse content
                        if ext == '.json':
                            content = parse_json_content(raw_content)
                        elif ext == '.xml':
                            content = parse_xml_content(raw_content)
                        else:
                            content = raw_content
                            
                        # Assumption: filename is ID/Title precursor
                        lines = content.split('\n')
                        title = lines[0][:100].strip() if lines else file
                        if not title: title = file
                        authors = "Unknown"
                        
                        new_docs.append({
                            'title': title,
                            'text': content,
                            'authors': authors,
                            'filename': file 
                        })
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
                        
    if new_docs:
        print(f"Found {len(new_docs)} new documents. Indexing...")
        indexer.add_documents(new_docs)
    else:
        print("No new documents found.")

if __name__ == "__main__":
    ingest_new_data()
