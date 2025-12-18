import os
import json
import time
from config import DATA_DIR, OUTPUT_DIR

def convert_to_jsonl():
    print("=" * 60)
    print("VERIDIA SEARCH ENGINE - DATA CONVERTER (ROBUST MODE)")
    print("=" * 60)
    print(f"Source Directory: {DATA_DIR}")
    
    # Force correct output path
    output_path = os.path.join(os.path.dirname(DATA_DIR), "VeridiaCore", "dataset.jsonl")
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Output File: {output_path}")
    print("-" * 60)

    start_time = time.time()
    count = 0
    errors = 0
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f_out:
            for root, dirs, files in os.walk(DATA_DIR):
                for filename in files:
                    if filename.endswith(".txt"):
                        file_path = os.path.join(root, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f_in:
                                content = f_in.read()
                                
                                # Use filename as fallback title if first line is weird
                                lines = content.split('\n', 1)
                                if len(lines) > 0 and len(lines[0]) < 200:
                                    title = lines[0].strip()
                                    body = content
                                else:
                                    title = filename
                                    body = content
                                    
                                doc = {
                                    "id": count + 1,
                                    "title": title,
                                    "abstract": body, 
                                    "authors": "Veridia Corpus",
                                    "url": f"file://{filename}"
                                }
                                
                                f_out.write(json.dumps(doc) + '\n')
                                count += 1
                                
                                if count % 10000 == 0:
                                    elapsed = time.time() - start_time
                                    print(f"  Processed {count:,} files... ({count/elapsed:.0f} files/sec)")
                                    
                        except Exception as e:
                            errors += 1
                            
    except KeyboardInterrupt:
        print("\n⚠️ Conversion interrupted by user!")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")

    total_time = time.time() - start_time
    print("=" * 60)
    print(f"CONVERSION COMPLETE")
    print(f"Total Files Saved: {count:,}")
    print(f"Errors Skipped: {errors}")
    print(f"Time Taken: {total_time:.2f} seconds")
    print(f"Target: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    convert_to_jsonl()
