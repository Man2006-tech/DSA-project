"""
Veridia Search Engine - Fast Inverted Index Builder
Builds inverted index from forward index efficiently
"""
import os
import time
from collections import defaultdict
from config import (
    FORWARD_INDEX_PATH, INVERTED_INDEX_PATH, 
    BATCH_SIZE, PROGRESS_INTERVAL
)


def build_inverted_index_optimized():
    """
    Build inverted index using memory-efficient streaming approach.
    """
    print("=" * 60)
    print("BUILDING INVERTED INDEX")
    print("=" * 60)
    
    start_time = time.time()
    
    if not os.path.exists(FORWARD_INDEX_PATH):
        print(f"ERROR: Forward index not found at {FORWARD_INDEX_PATH}")
        print("Please run build_index_fast.py first!")
        return
    
    # Use defaultdict for automatic list creation
    inverted_index = defaultdict(set)
    
    print("\n[1/2] Reading forward index and inverting...")
    
    line_count = 0
    
    with open(FORWARD_INDEX_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line_count += 1
            
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
            
            doc_id = parts[0]
            word_ids = parts[1].split()
            
            # Add doc_id to each word's posting list
            # Using set to avoid duplicates
            for word_id in set(word_ids):  # set removes duplicates within document
                inverted_index[word_id].add(doc_id)
            
            if line_count % PROGRESS_INTERVAL == 0:
                elapsed = time.time() - start_time
                rate = line_count / elapsed if elapsed > 0 else 0
                print(f"  Processed: {line_count:,} documents | "
                      f"Rate: {rate:.0f} docs/sec")
    
    print(f"\n[2/2] Writing inverted index...")
    print(f"  Total unique words: {len(inverted_index):,}")
    
    # Write inverted index
    with open(INVERTED_INDEX_PATH, 'w', encoding='utf-8') as f:
        buffer = []
        
        # Sort word_ids numerically for better lookup performance
        sorted_word_ids = sorted(inverted_index.keys(), key=lambda x: int(x))
        
        for i, word_id in enumerate(sorted_word_ids, 1):
            doc_ids = sorted(inverted_index[word_id], key=lambda x: int(x))
            buffer.append(f"{word_id}\t{' '.join(doc_ids)}\n")
            
            if len(buffer) >= BATCH_SIZE:
                f.writelines(buffer)
                buffer.clear()
            
            if i % PROGRESS_INTERVAL == 0:
                print(f"  Written: {i:,} / {len(inverted_index):,} words")
        
        # Write remaining
        if buffer:
            f.writelines(buffer)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Calculate average posting list size
    avg_postings = sum(len(docs) for docs in inverted_index.values()) / len(inverted_index)
    
    print("\n" + "=" * 60)
    print("INVERTED INDEX BUILD COMPLETE!")
    print("=" * 60)
    print(f"✓ Documents Processed: {line_count:,}")
    print(f"✓ Unique Words: {len(inverted_index):,}")
    print(f"✓ Average Postings/Word: {avg_postings:.1f}")
    print(f"✓ Time Elapsed: {elapsed:.2f} seconds")
    print(f"✓ Processing Rate: {line_count/elapsed:.1f} docs/sec")
    print("=" * 60)


if __name__ == "__main__":
    try:
        build_inverted_index_optimized()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()