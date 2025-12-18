import os
import struct
import json
import psutil

# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = BASE_DIR
FORWARD_INDEX_FILE = os.path.join(OUTPUT_DIR, "forward_index.bin")
LEXICON_FILE = os.path.join(OUTPUT_DIR, "lexicon.txt")
OFFSETS_FILE = os.path.join(OUTPUT_DIR, "word_offsets_barrels.bin")

# Constants
BARREL_COUNT = 500 # Adjust based on memory/size, for small dummy data 10 is enough really but let's stick to logic
BARREL_COUNT = 10 

def load_lexicon():
    lexicon = {}
    if os.path.exists(LEXICON_FILE):
        with open(LEXICON_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    lexicon[parts[0]] = int(parts[1])
    return lexicon

def build_inverted_index():
    print("--- STARTING INVERTED INDEXING ---")
    
    if not os.path.exists(FORWARD_INDEX_FILE):
        print(f"Error: {FORWARD_INDEX_FILE} not found.")
        return

    # 1. Read Forward Index and Sort into Barrels
    # We really should just sort pairs (WordID, DocID) in memory if it fits
    # For a real system, we'd do external sort. 
    # Since we are making dummy data, it will fit in memory.
    
    print("Reading Forward Index...")
    temp_postings = {} # WordID -> [DocIDs...]
    
    with open(FORWARD_INDEX_FILE, 'rb') as f:
        while True:
            # Read header: DocID (4B) | NumWords (4B)
            header = f.read(8)
            if not header:
                break
            doc_id, num_words = struct.unpack('II', header)
            
            if num_words > 0:
                # Read words
                word_data = f.read(num_words * 4)
                word_ids = struct.unpack(f'{num_words}I', word_data)
                
                distinct_words = set(word_ids) # Simple occurence
                for wid in distinct_words:
                    if wid not in temp_postings:
                        temp_postings[wid] = []
                    temp_postings[wid].append(doc_id)
    
    print(f"Collected postings for {len(temp_postings)} words.")
    
    # 2. Write Barrels and Offsets
    print("Writing Barrels and Offsets...")
    
    # We'll just distribute word_ids modulo BARREL_COUNT
    barrels_content = {i: bytearray() for i in range(BARREL_COUNT)}
    word_offsets = {} # WordID -> (BarrelID, Offset, Count)
    
    sorted_word_ids = sorted(temp_postings.keys())
    
    for wid in sorted_word_ids:
        doc_ids = sorted(temp_postings[wid])
        count = len(doc_ids)
        barrel_id = wid % BARREL_COUNT
        
        offset = len(barrels_content[barrel_id])
        
        # Write DocIDs to barrel
        # Format: DocID1 (4B) | DocID2 (4B) ...
        barrels_content[barrel_id].extend(struct.pack(f'{count}I', *doc_ids))
        
        word_offsets[wid] = (barrel_id, offset, count)
        
    # Flush barrels to disk
    for bid, content in barrels_content.items():
        if len(content) > 0:
            path = os.path.join(OUTPUT_DIR, f"barrel_{bid}.bin")
            with open(path, 'wb') as f:
                f.write(content)
                
    # Write Offsets Map
    # Format: WordID (4B) | BarrelID (4B) | Offset (8B) | Count (4B)
    with open(OFFSETS_FILE, 'wb') as f:
        for wid, (bid, off, cnt) in word_offsets.items():
            f.write(struct.pack('<IIQI', wid, bid, off, cnt))
            
    print("--- SUCCESS: Inverted Index Built ---")

if __name__ == "__main__":
    build_inverted_index()
