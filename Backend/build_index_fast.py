"""
Veridia Search Engine - Fast Index Builder
Builds lexicon, forward index, and metadata efficiently
"""
import os
import time
from collections import defaultdict
from json_parser import stream_json_documents
from text_processor import clean_and_tokenize
from config import (
    OUTPUT_DIR, LEXICON_PATH, FORWARD_INDEX_PATH, 
    METADATA_PATH, BATCH_SIZE, PROGRESS_INTERVAL
)


def build_indices_optimized():
    """
    Build all indices in a single pass for maximum speed.
    Uses batched writing for better I/O performance.
    """
    print("=" * 60)
    print("VERIDIA SEARCH ENGINE - FAST INDEX BUILDER")
    print("=" * 60)
    
    start_time = time.time()
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Data structures
    lexicon = {}  # word -> word_id
    word_id_counter = 0
    
    # Buffers for batched writing
    forward_buffer = []
    metadata_buffer = []
    
    # Statistics
    total_docs = 0
    total_words = 0
    
    # Open files for writing
    print("\n[1/3] Processing documents and building indices...")
    
    with open(FORWARD_INDEX_PATH, 'w', encoding='utf-8') as f_fwd, \
         open(METADATA_PATH, 'w', encoding='utf-8') as f_meta:
        
        # Stream and process documents
        for doc_id, title, full_text, authors in stream_json_documents():
            
            # Tokenize and clean
            words = clean_and_tokenize(full_text)
            
            if not words:
                continue
            
            # Build lexicon and get word IDs
            word_ids = []
            for word in words:
                if word not in lexicon:
                    lexicon[word] = word_id_counter
                    word_id_counter += 1
                word_ids.append(str(lexicon[word]))
            
            # Add to buffers
            forward_buffer.append(f"{doc_id}\t{' '.join(word_ids)}\n")
            metadata_buffer.append(f"{doc_id}|{title}|{authors}\n")
            
            total_docs += 1
            total_words += len(words)
            
            # Write buffers when they reach batch size
            if len(forward_buffer) >= BATCH_SIZE:
                f_fwd.writelines(forward_buffer)
                f_meta.writelines(metadata_buffer)
                forward_buffer.clear()
                metadata_buffer.clear()
            
            # Progress update
            if total_docs % PROGRESS_INTERVAL == 0:
                elapsed = time.time() - start_time
                rate = total_docs / elapsed if elapsed > 0 else 0
                print(f"  Processed: {total_docs:,} docs | "
                      f"Lexicon: {len(lexicon):,} words | "
                      f"Rate: {rate:.0f} docs/sec")
        
        # Write remaining buffers
        if forward_buffer:
            f_fwd.writelines(forward_buffer)
            f_meta.writelines(metadata_buffer)
    
    print(f"\n[2/3] Saving lexicon...")
    
    # Write lexicon (sorted by word for easier debugging)
    with open(LEXICON_PATH, 'w', encoding='utf-8') as f_lex:
        # Sort by word_id for consistent ordering
        sorted_lexicon = sorted(lexicon.items(), key=lambda x: x[1])
        buffer = []
        
        for word, word_id in sorted_lexicon:
            buffer.append(f"{word}\t{word_id}\n")
            
            if len(buffer) >= BATCH_SIZE:
                f_lex.writelines(buffer)
                buffer.clear()
        
        if buffer:
            f_lex.writelines(buffer)
    
    # Calculate statistics
    end_time = time.time()
    elapsed = end_time - start_time
    
    print("\n" + "=" * 60)
    print("INDEX BUILD COMPLETE!")
    print("=" * 60)
    print(f"✓ Total Documents: {total_docs:,}")
    print(f"✓ Unique Words: {len(lexicon):,}")
    print(f"✓ Total Word Instances: {total_words:,}")
    print(f"✓ Time Elapsed: {elapsed:.2f} seconds")
    print(f"✓ Processing Rate: {total_docs/elapsed:.1f} docs/sec")
    print(f"✓ Average Words/Doc: {total_words/total_docs:.1f}")
    print("=" * 60)
    
    return {
        'docs': total_docs,
        'words': len(lexicon),
        'time': elapsed
    }


if __name__ == "__main__":
    try:
        stats = build_indices_optimized()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()