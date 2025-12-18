import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import DATA_DIR, OUTPUT_DIR

# Robust output path
OUTPUT_PATH = os.path.join(os.path.dirname(DATA_DIR), "VeridiaCore", "dataset.jsonl")

def process_file(file_info):
    """
    Process a single file. 
    Args: file_info is a tuple (root, filename)
    Returns: json string or None
    """
    root, filename = file_info
    file_path = os.path.join(root, filename)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f_in:
            content = f_in.read()
            
            # Use filename as fallback title
            lines = content.split('\n', 1)
            if len(lines) > 0 and len(lines[0]) < 200:
                title = lines[0].strip()
                body = content
            else:
                title = filename
                body = content
                
            doc = {
                "id": 0, # Placeholder, will be assigned on write
                "title": title,
                "abstract": body, 
                "authors": "Veridia Corpus",
                "url": f"file://{filename}"
            }
            return json.dumps(doc)
    except Exception:
        return None

def convert_fast():
    print("=" * 60)
    print("VERIDIA SEARCH - TURBO CONVERTER (MULTI-THREADED)")
    print("=" * 60)
    print(f"Source: {DATA_DIR}")
    print(f"Target: {OUTPUT_PATH}")
    print(f"Threads: 8")
    print("-" * 60)
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    start_time = time.time()
    all_files = []
    
    # Step 1: Collect files (fast)
    print("Scanning files...")
    for root, dirs, files in os.walk(DATA_DIR):
        for filename in files:
            if filename.endswith(".txt"):
                all_files.append((root, filename))
    
    total_files = len(all_files)
    print(f"Found {total_files:,} files. Starting parallel conversion...")

    count = 0
    batch_buffer = []
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f_out:
        with ThreadPoolExecutor(max_workers=8) as executor:
            # Submit all jobs
            future_to_file = {executor.submit(process_file, f): f for f in all_files}
            
            for future in as_completed(future_to_file):
                result = future.result()
                if result:
                    count += 1
                    # Inject ID (simple counter) - technically we are deserializing to inject ID? 
                    # Actually result is a string. To be safe/clean let's just write the string.
                    # ID isn't strictly needed for the parser as it generates doc_id on fly.
                    f_out.write(result + '\n')
                    
                    if count % 10000 == 0:
                        elapsed = time.time() - start_time
                        rate = count / elapsed if elapsed > 0 else 0
                        print(f"  Processed {count:,}/{total_files:,} ({rate:.0f} files/sec)")

    total_time = time.time() - start_time
    print("=" * 60)
    print(f"turbo CONVERSION COMPLETE")
    print(f"Total: {count:,} documents")
    print(f"Time: {total_time:.2f}s")
    print(f"Rate: {count/total_time:.0f} docs/sec")
    print("=" * 60)

if __name__ == "__main__":
    convert_fast()
