import os
import struct
import json
import time

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERIDIA_CORE = os.path.join(BASE_DIR, '..', 'VeridiaCore')
JSONL_PATH = os.path.join(VERIDIA_CORE, 'dataset.jsonl')
OFFSETS_PATH = os.path.join(VERIDIA_CORE, 'doc_offsets.bin')

def repair_offsets():
    print(f"Reparing/Generating {OFFSETS_PATH}...")
    
    if not os.path.exists(JSONL_PATH):
        print(f"Error: {JSONL_PATH} not found.")
        return

    start_time = time.time()
    count = 0
    
    # We need to map DocID -> ByteOffset
    # We assume DocIDs are sequential 1..N as they appear in the file
    # The first document (line) is DocID 1 (or 0?).
    # let's match build_index_fast.py which usually starts at 1? 
    # Actually wait, build_index_fast.py reads doc_id from json?
    # No, usually convert_fast.py writes "id": 0.
    # So build_index_fast.py generates IDs? 
    # Let's check json_parser.py.
    # Ah, json_parser.py generates IDs starting from 1.
    # So line 1 is DocID 1.
    # Offsets file: index 0 -> DocID 1.
    
    offsets = []
    
    with open(JSONL_PATH, 'r', encoding='utf-8') as f:
        while True:
            offset = f.tell()
            line = f.readline()
            if not line:
                break
            
            # Store offset for this doc
            offsets.append(offset)
            count += 1
            
            if count % 50000 == 0:
                print(f"  Scanned {count} docs...", end='\r')
                
    print(f"\nWriting {len(offsets)} offsets to binary file...")
    
    with open(OFFSETS_PATH, 'wb') as f_out:
        for off in offsets:
            f_out.write(struct.pack('Q', off))
            
    elapsed = time.time() - start_time
    print(f"Done in {elapsed:.2f}s.")
    print(f"Generated offsets for {count} documents.")

if __name__ == "__main__":
    repair_offsets()
