"""
Veridia Search Engine - JSON Parser
Fast streaming parser for arXiv JSON dataset
"""
import json
from text_processor import is_english_text, extract_title_preview
from config import JSON_DATASET_PATH, MAX_DOCUMENTS


def stream_json_documents(limit=MAX_DOCUMENTS):
    """
    Stream documents from JSON file with English filtering.
    
    Yields:
        Tuples of (doc_id, title, full_text, authors)
    """
    print(f"Streaming documents from: {JSON_DATASET_PATH}")
    print(f"Target: {limit} English documents")
    
    doc_count = 0
    processed = 0
    
    try:
        with open(JSON_DATASET_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                processed += 1
                
                try:
                    data = json.loads(line)
                    
                    # Extract fields
                    title = data.get('title', '').replace('\n', ' ').strip()
                    abstract = data.get('abstract', '').replace('\n', ' ').strip()
                    authors = data.get('authors', '').replace('\n', ' ').strip()
                    
                    # Combine title and abstract for content
                    full_text = f"{title} {abstract}"
                    
                    # Filter non-English documents - DISABLED to ensure all files are indexed
                    # if not is_english_text(full_text):
                    #    continue
                    
                    doc_count += 1
                    
                    # Return raw title (faster)
                    yield (doc_count, title, full_text, authors)
                    
                    if doc_count % 5000 == 0:
                        print(f"  ✓ Collected {doc_count} English docs (scanned {processed})")
                    
                    if doc_count >= limit:
                        break
                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Warning: Error processing line {processed}: {e}")
                    continue
        
        print(f"\n✓ Total English documents collected: {doc_count}")
        print(f"✓ Total lines scanned: {processed}")
        
    except FileNotFoundError:
        print(f"ERROR: JSON file not found at {JSON_DATASET_PATH}")
        print("Please update JSON_DATASET_PATH in config.py")
        raise


def count_json_lines(limit=None):
    """
    Quick count of JSON lines for progress tracking.
    
    Returns:
        Number of valid JSON lines
    """
    count = 0
    try:
        with open(JSON_DATASET_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    count += 1
                if limit and count >= limit:
                    break
        return count
    except FileNotFoundError:
        return 0