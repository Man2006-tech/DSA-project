import os
import struct
import time
from collections import defaultdict

# Configuration
from config import OUTPUT_DIR

# Configuration
VERIDIA_CORE_DIR = OUTPUT_DIR
INPUT_INVERTED_TXT = os.path.join(VERIDIA_CORE_DIR, 'inverted_index.txt')
OUTPUT_OFFSETS_BIN = os.path.join(VERIDIA_CORE_DIR, 'word_offsets_barrels.bin')
OUTPUT_BARRELS_INFO = os.path.join(VERIDIA_CORE_DIR, 'barrels_info.txt')

NUM_BARRELS = 10  # Configurable number of barrels

def build_barrels():
    print(f"Building {NUM_BARRELS} barrels from {INPUT_INVERTED_TXT}...")
    start_time = time.time()
    
    if not os.path.exists(INPUT_INVERTED_TXT):
        print(f"Error: {INPUT_INVERTED_TXT} not found.")
        return

    # Prepare file handles for barrels
    barrel_files = {}
    for i in range(NUM_BARRELS):
        path = os.path.join(VERIDIA_CORE_DIR, f"barrel_{i}.bin")
        barrel_files[i] = open(path, 'wb')
        
    # Track offsets: WordID -> (BarrelID, Offset, Count)
    word_offsets = {}
    
    word_count = 0
    total_postings = 0
    
    with open(INPUT_INVERTED_TXT, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
                
            word_id = int(parts[0])
            doc_ids = [int(d) for d in parts[1].split()]
            count = len(doc_ids)
            
            # Key Logic: Determine Barrel ID
            # Simple modulo distribution ensures determinism and even spread
            barrel_id = word_id % NUM_BARRELS
            
            # Get current offset in that barrel
            bf = barrel_files[barrel_id]
            offset = bf.tell()
            
            # Write DocIDs to barrel (Binary: 4 bytes unsigned int per DocID)
            # packing 'I' * count
            data = struct.pack(f'<{count}I', *doc_ids)
            bf.write(data)
            
            # Store metadata
            word_offsets[word_id] = (barrel_id, offset, count)
            
            word_count += 1
            total_postings += count
            
            if word_count % 10000 == 0:
                print(f"Processed {word_count} words...", end='\r')

    # Close barrel files
    for f_obj in barrel_files.values():
        f_obj.close()
        
    print(f"\nBarrels created. Writing offsets map...")
    
    # Write Offsets Map (Binary)
    # Format: WordID (4B) | BarrelID (4B) | Offset (8B) | Count (4B) = 20 Bytes
    with open(OUTPUT_OFFSETS_BIN, 'wb') as f_out:
        # Sort by WordID for cleaner structure (optional but good)
        sorted_ids = sorted(word_offsets.keys())
        for wid in sorted_ids:
            bid, off, cnt = word_offsets[wid]
            f_out.write(struct.pack('<IIQI', wid, bid, off, cnt))
            
    # Write Info File
    with open(OUTPUT_BARRELS_INFO, 'w', encoding='utf-8') as f_info:
        f_info.write(f"Barrels Implementation Report\n")
        f_info.write(f"============================\n")
        f_info.write(f"Total Words: {word_count}\n")
        f_info.write(f"Total Postings: {total_postings}\n")
        f_info.write(f"Number of Barrels: {NUM_BARRELS}\n")
        f_info.write(f"Sharding Strategy: WordID % {NUM_BARRELS}\n")
        f_info.write(f"Binary Format for Offsets: WordID(4)|BarrelID(4)|Offset(8)|Count(4)\n")
        f_info.write(f"Generated Files:\n")
        for i in range(NUM_BARRELS):
             size = os.path.getsize(os.path.join(VERIDIA_CORE_DIR, f"barrel_{i}.bin"))
             f_info.write(f" - barrel_{i}.bin: {size} bytes\n")
        f_info.write(f" - word_offsets_barrels.bin: {os.path.getsize(OUTPUT_OFFSETS_BIN)} bytes\n")

    print(f"\n[4/4] Generating Zero-Latency Dense Index...")
    
    # Logic for dense index generation
    NEW_OFFSETS = os.path.join(VERIDIA_CORE_DIR, 'word_offsets_dense.bin')
    
    if word_offsets:
        max_id = max(word_offsets.keys())
        # Each slot: BarrelID(4) + Off(8) + Cnt(4) = 16 bytes
        array_size = (max_id + 1) * 16
        buffer = bytearray(array_size)
        
        for wid, (bid, off, cnt) in word_offsets.items():
            if wid <= max_id:
                struct.pack_into('<IQI', buffer, wid * 16, bid, off, cnt)
                
        with open(NEW_OFFSETS, 'wb') as f:
            f.write(buffer)
        print(f"  ✓ Created {NEW_OFFSETS} ({array_size/1024/1024:.1f} MB)")

    elapsed = time.time() - start_time
    print(f"Done in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    build_barrels()
