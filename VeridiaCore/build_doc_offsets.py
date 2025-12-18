import os
import struct
import time

# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSONL_FILE = os.path.join(BASE_DIR, "dataset.jsonl")
OUTPUT_FILE = os.path.join(BASE_DIR, "doc_offsets.bin")

def build_doc_offsets():
    print(f"--- BUILDING DOCUMENT OFFSETS INDEX ---")
    print(f"Input: {JSONL_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    
    if not os.path.exists(JSONL_FILE):
        print(f"ERROR: {JSONL_FILE} not found.")
        return

    start_time = time.time()
    
    # We need to map DocID -> ByteOffset
    # DocIDs are 1-based integers (assumed sequential from 1)
    # We will just write a sequence of 8-byte integers (Long Long)
    # The index in the binary file determines the DocID (index 0 = DocID 1, index 1 = DocID 2...)
    
    offsets = []
    
    with open(JSONL_FILE, 'rb') as f_in:
        offset = 0
        count = 0
        
        # We need to read line by line but keep track of binary offset
        # Iterating over f_in yielded lines might buffer, so f_in.tell() might be tricky if not careful.
        # But usually 'for line in f' works with valid offsets if we sum up len(line).
        # Let's be safer and use readline()
        
        while True:
            # Current position is the start of the document
            current_offset = f_in.tell()
            line = f_in.readline()
            if not line:
                break
                
            offsets.append(current_offset)
            count += 1
            
            if count % 10000 == 0:
                print(f"Mapped {count} documents...", end='\r')

    print(f"\nMapped {len(offsets)} documents.")
    
    print("Writing binary offset file...")
    with open(OUTPUT_FILE, 'wb') as f_out:
        # Write all offsets as unsigned long long (8 bytes)
        # Format: 'Q' * len(offsets)
        f_out.write(struct.pack(f'{len(offsets)}Q', *offsets))
        
    end_time = time.time()
    print(f"\n--- SUCCESS ---")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")

if __name__ == "__main__":
    build_doc_offsets()
