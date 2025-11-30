import os
import time
from collections import defaultdict

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
FORWARD_INDEX_PATH = os.path.join(OUTPUT_DIR, "forward_index.txt")
INVERTED_INDEX_PATH = os.path.join(OUTPUT_DIR, "inverted_index.txt")

def build_inverted_index():
    print("--- STARTING INVERTED INDEX GENERATION ---")
    start_time = time.time()

    inverted_index = defaultdict(list)

    if not os.path.exists(FORWARD_INDEX_PATH):
        print(f"Error: Forward index not found at {FORWARD_INDEX_PATH}")
        return

    print("Reading Forward Index...")
    with open(FORWARD_INDEX_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
            
            doc_id = parts[0]
            word_ids = parts[1].split()
            
            # Using a set to avoid duplicate doc_ids for the same word in the same doc
            unique_word_ids = set(word_ids)
            
            for word_id in unique_word_ids:
                inverted_index[word_id].append(doc_id)

    print(f"Inverting {len(inverted_index)} unique words...")
    
    print("Saving Inverted Index...")
    with open(INVERTED_INDEX_PATH, 'w', encoding='utf-8') as f_out:
        # Sort by WordID for cleaner output (optional but nice)
        # Assuming WordIDs are integers, let's sort them numerically
        sorted_word_ids = sorted(inverted_index.keys(), key=lambda x: int(x))
        
        for word_id in sorted_word_ids:
            doc_ids = inverted_index[word_id]
            f_out.write(f"{word_id}\t{' '.join(doc_ids)}\n")

    end_time = time.time()
    print(f"\n--- SUCCESS ---")
    print(f"Inverted Index Saved to {INVERTED_INDEX_PATH}")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")

if __name__ == "__main__":
    build_inverted_index()