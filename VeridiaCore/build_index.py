import os
import json
import re
import time
import struct

# CONFIGURATION
# Assuming this script is in Veridia_Core/VeridiaCore/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DATA_DIR = os.path.join(BASE_DIR, 'DATA') # No longer used for direct scanning
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
JSONL_FILE = os.path.join(OUTPUT_DIR, "dataset.jsonl")

def clean_text(text):
    # Simple tokenization: lowercase and keep only letters
    return re.findall(r'[a-z]+', text.lower())

def build_indices():
    print(f"--- STARTING INDEXING FROM JSONL ---")
    print(f"Input File: {JSONL_FILE}")
    print(f"Output Directory: {OUTPUT_DIR}")
    
    if not os.path.exists(JSONL_FILE):
        print(f"ERROR: {JSONL_FILE} not found. Please run convert_to_jsonl.py first.")
        return

    start_time = time.time()

    lexicon = {} # word -> word_id
    word_id_counter = 0
    
    doc_metadata = {} # doc_id -> (filename, title)
    doc_id_counter = 1
    
    # We need to store the forward index in memory or write it temporarily
    # Since we need to write binary: DocID | NumWords | WordID1 | WordID2 ...
    # We can write directly to the binary file.
    
    forward_index_path = os.path.join(OUTPUT_DIR, "forward_index.bin")
    
    print("Processing JSONL file and building Forward Index...")
    
    with open(JSONL_FILE, 'r', encoding='utf-8') as f_in, \
         open(forward_index_path, 'wb') as f_out:
        
        count = 0
        for line in f_in:
            try:
                data = json.loads(line)
                filename = data.get('filename', 'unknown')
                title = data.get('title', 'No Title')
                content = data.get('content', '')
                
                # Assign Doc ID
                doc_id = doc_id_counter
                doc_id_counter += 1
                doc_metadata[doc_id] = (filename, title)
                
                # Tokenize
                tokens = clean_text(content)
                
                # Convert to Word IDs
                doc_word_ids = []
                for token in tokens:
                    if token not in lexicon:
                        lexicon[token] = word_id_counter
                        word_id_counter += 1
                    doc_word_ids.append(lexicon[token])
                
                # Write to Binary Forward Index
                # Format: DocID (4b) | NumWords (4b) | WordIDs...
                num_words = len(doc_word_ids)
                header = struct.pack('II', doc_id, num_words)
                f_out.write(header)
                
                if num_words > 0:
                    body = struct.pack(f'{num_words}I', *doc_word_ids)
                    f_out.write(body)
                
                count += 1
                if count % 1000 == 0:
                    print(f"Processed {count} documents...", end='\r')
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error processing line: {e}")
                continue

    print(f"\nProcessed {count} documents total.")

    # Save Lexicon
    print("Saving Lexicon (lexicon.txt)...")
    lexicon_path = os.path.join(OUTPUT_DIR, "lexicon.txt")
    with open(lexicon_path, "w", encoding="utf-8") as f:
        for word, wid in lexicon.items():
            f.write(f"{word}\t{wid}\n")

    # Save Metadata
    print("Saving Metadata (document_metadata.txt)...")
    meta_path = os.path.join(OUTPUT_DIR, "document_metadata.txt")
    with open(meta_path, "w", encoding="utf-8") as f:
        for did, (fname, title) in doc_metadata.items():
            # Sanitize title/filename to avoid pipe issues
            fname = fname.replace('|', '-')
            title = title.replace('|', '-').replace('\n', ' ')
            f.write(f"{did}|{fname}|{title}\n")

    end_time = time.time()
    print(f"\n--- SUCCESS ---")
    print(f"Total Docs: {len(doc_metadata)}")
    print(f"Total Words: {len(lexicon)}")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")

if __name__ == "__main__":
    build_indices()