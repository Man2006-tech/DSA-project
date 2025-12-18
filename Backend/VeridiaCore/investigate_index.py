import os
import struct
import sys

# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEXICON_FILE = os.path.join(BASE_DIR, "lexicon.txt")
OFFSETS_FILE = os.path.join(BASE_DIR, "word_offsets.bin")
INVERTED_FILE = os.path.join(BASE_DIR, "inverted_index.bin")

def check_word(target_word):
    print(f"--- INDEX INVESTIGATION: '{target_word}' ---")
    
    # 1. Check Lexicon
    word_id = None
    if os.path.exists(LEXICON_FILE):
        with open(LEXICON_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    if parts[0] == target_word:
                        word_id = int(parts[1])
                        print(f"[OK] Found in Lexicon: WordID = {word_id}")
                        break
    
    if word_id is None:
        print(f"[FAIL] Word '{target_word}' NOT found in Lexicon.")
        return

    # 2. Check Word Offsets
    offset_info = None
    if os.path.exists(OFFSETS_FILE):
        with open(OFFSETS_FILE, 'rb') as f:
            f.seek(0, 2) # End
            file_size = f.tell()
            f.seek(0)
            
            # Linear scan (slow but safe for debug) or just seek if we knew sorted? 
            # In engine.py it loads ALL into memory. Here let's just scan or seek if keys are sorted?
            # engine.py: self.word_offsets[word_id] = (offset, count).
            # The file is just a list of records?
            # build_inverted_index says:
            # f_off.write(struct.pack('<IQI', word_id, offset, count))
            # It's a sequence of records.
            
            record_size = 16
            num_records = file_size // record_size
            print(f"Scanning {num_records} offset records...")
            
            # Optimization: Read all? No, just loop.
            while True:
                data = f.read(record_size)
                if not data: break
                wid, off, cnt = struct.unpack('<IQI', data)
                if wid == word_id:
                    offset_info = (off, cnt)
                    print(f"[OK] Found in WordOffsets: Offset={off}, Count={cnt}")
                    break
                    
    if offset_info is None:
        print(f"[FAIL] WordID {word_id} NOT found in WordOffsets (Inverted Index missing?).")
        return

    # 3. Check Inverted Index
    offset, count = offset_info
    if count == 0:
        print("[WARN] Count is 0. No documents contain this word.")
        return
        
    if os.path.exists(INVERTED_FILE):
        with open(INVERTED_FILE, 'rb') as f:
            f.seek(offset)
            # Read 'count' integers
            doc_data = f.read(count * 4)
            if len(doc_data) != count * 4:
                print(f"[FAIL] Error reading postings. Expected {count*4} bytes, got {len(doc_data)}.")
                return
                
            doc_ids = struct.unpack(f'<{count}I', doc_data)
            print(f"[OK] Retrieved {len(doc_ids)} DocIDs from Inverted Index.")
            print(f"Sample DocIDs: {doc_ids[:10]} ...")
            
    else:
        print(f"❌ Inverted Index file not found.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        word = sys.argv[1].lower()
    else:
        word = "dengue" # Default test
    check_word(word)
