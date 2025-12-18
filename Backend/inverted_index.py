import os
import time
import struct
from collections import defaultdict

# CONFIGURATION
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
FORWARD_INDEX_PATH = os.path.join(OUTPUT_DIR, "forward_index.bin")
INVERTED_INDEX_PATH = os.path.join(OUTPUT_DIR, "inverted_index.bin")
LEXICON_PATH = os.path.join(OUTPUT_DIR, "lexicon.txt")

def build_inverted_index():
    print("--- STARTING BINARY INVERTED INDEX GENERATION ---")
    start_time = time.time()

    inverted_index = defaultdict(list)

    if not os.path.exists(FORWARD_INDEX_PATH):
        print(f"Error: Forward index not found at {FORWARD_INDEX_PATH}")
        return

    print("Reading Binary Forward Index...")
    with open(FORWARD_INDEX_PATH, 'rb') as f:
        while True:
            # Read DocID (4 bytes) and NumWords (4 bytes)
            header = f.read(8)
            if not header:
                break
            
            doc_id, num_words = struct.unpack('II', header)
            
            # Read WordIDs (num_words * 4 bytes)
            word_data = f.read(num_words * 4)
            word_ids = struct.unpack(f'{num_words}I', word_data)
            
            for word_id in word_ids:
                inverted_index[word_id].append(doc_id)

    print(f"Inverting {len(inverted_index)} unique words...")
    
    print("Saving Binary Inverted Index...")
    # Format: WordID (4 bytes) | Offset (8 bytes) | Count (4 bytes)
    # But wait, to search, we need to look up by WordID.
    # So we should store the Postings List contiguously and have a separate "Offset Table"
    # Or, we can just store:
    # WordID | Count | DocID1 | DocID2 ...
    # And have the engine scan/seek.
    # BETTER:
    # 1. Write all postings lists to `inverted_index.bin`.
    # 2. Write a `word_offsets.bin` that maps WordID -> (Offset, Count).
    
    # Let's stick to a single file for simplicity if possible, but an offset table is faster.
    # Let's write:
    # inverted_index.bin: [DocID, DocID...] [DocID...]
    # word_offsets.bin: WordID (4b) | Offset (8b) | Count (4b)
    
    offsets_path = os.path.join(OUTPUT_DIR, "word_offsets.bin")
    
    with open(INVERTED_INDEX_PATH, 'wb') as f_inv, open(offsets_path, 'wb') as f_off:
        sorted_word_ids = sorted(inverted_index.keys())
        
        for word_id in sorted_word_ids:
            doc_ids = inverted_index[word_id]
            count = len(doc_ids)
            
            offset = f_inv.tell()
            
            # Write Postings: DocID1 DocID2 ... (all 4 bytes)
            f_inv.write(struct.pack(f'<{count}I', *doc_ids))
            
            # Write Offset: WordID | Offset | Count
            f_off.write(struct.pack('<IQI', word_id, offset, count))

    end_time = time.time()
    print(f"\n--- SUCCESS ---")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")

if __name__ == "__main__":
    build_inverted_index()