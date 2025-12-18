"""
Veridia Search Engine - Incremental Indexer
Supports adding new documents without reprocessing existing data
Tracks indexed document IDs and maintains persistent state
"""
import os
import json
import struct
import time
from collections import defaultdict
from text_processor import clean_and_tokenize
from config import OUTPUT_DIR, BATCH_SIZE, PROGRESS_INTERVAL


from build_barrels import build_barrels

class IncrementalIndexer:
    # ... (existing code)

    def add_documents(self, documents):
        # ... (existing code)
        
        print(f"\n[3/3] Rebuilding inverted index...")
        self._rebuild_inverted_index()
        
        print(f"\n[4/4] Updating Barrels...")
        build_barrels()
        
        # Save state
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.lexicon = {}
        self.word_id_counter = 0
        self.next_doc_id = 0
        self.state_file = os.path.join(self.data_dir, "indexing_state.json")
        self.indexed_docs_file = os.path.join(self.data_dir, "indexed_documents.txt")
        
        # Paths to index files
        self.lexicon_path = os.path.join(self.data_dir, "lexicon.txt")
        self.forward_index_path = os.path.join(self.data_dir, "forward_index.txt")
        self.metadata_path = os.path.join(self.data_dir, "document_metadata.txt")
        self.inverted_index_path = os.path.join(self.data_dir, "inverted_index.txt")
        
        # Load existing state
        self._load_state()
    
    def _load_state(self):
        """Load lexicon, word counter, and indexed document IDs from existing files"""
        print("[STATE] Loading indexing state...")
        
        # Load lexicon and word counter
        if os.path.exists(self.lexicon_path):
            with open(self.lexicon_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        word = parts[0]
                        word_id = int(parts[1])
                        self.lexicon[word] = word_id
                        self.word_id_counter = max(self.word_id_counter, word_id + 1)
            print(f"  [OK] Loaded lexicon: {len(self.lexicon):,} words")
        
        # Load next document ID from state file
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.next_doc_id = state.get('next_doc_id', 0)
                self.word_id_counter = state.get('word_id_counter', self.word_id_counter)
            print(f"  [OK] Loaded state: next_doc_id={self.next_doc_id}, word_ids={self.word_id_counter}")
        else:
            # Infer next_doc_id from existing metadata if available
            if os.path.exists(self.metadata_path):
                max_doc_id = -1
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split('|')
                        if parts:
                            try:
                                doc_id = int(parts[0])
                                max_doc_id = max(max_doc_id, doc_id)
                            except:
                                pass
                self.next_doc_id = max_doc_id + 1
                print(f"  [OK] Inferred next_doc_id from metadata: {self.next_doc_id}")
    
    def _save_state(self):
        """Save current indexing state to file"""
        state = {
            'next_doc_id': self.next_doc_id,
            'word_id_counter': self.word_id_counter,
            'timestamp': time.time(),
            'total_words': len(self.lexicon)
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def add_documents(self, documents):
        """
        Add new documents incrementally.
        
        Args:
            documents: List of tuples (title, full_text, authors)
                      or list of dicts with 'title', 'text', 'authors' keys
        
        Returns:
            dict with statistics about the indexing operation
        """
        print("\n" + "=" * 60)
        print("INCREMENTAL INDEXING - ADDING NEW DOCUMENTS")
        print("=" * 60)
        
        start_time = time.time()
        stats = {
            'documents_added': 0,
            'new_words': 0,
            'total_words_processed': 0
        }
        
        # Append to indices instead of overwriting
        print(f"\n[1/3] Processing new documents (starting from doc_id {self.next_doc_id})...")
        
        # For lexicon updates
        lexicon_updates = {}
        forward_buffer = []
        metadata_buffer = []
        
        for i, doc in enumerate(documents):
            # Parse document format
            if isinstance(doc, dict):
                title = doc.get('title', '')
                full_text = doc.get('text', '')
                authors = doc.get('authors', '')
            else:
                title, full_text, authors = doc[0], doc[1], doc[2]
            
            # Clean and tokenize
            words = clean_and_tokenize(full_text)
            if not words:
                continue
            
            # Build word IDs (create new IDs for unknown words)
            word_ids = []
            for word in words:
                if word not in self.lexicon and word not in lexicon_updates:
                    # New word found
                    lexicon_updates[word] = self.word_id_counter
                    self.word_id_counter += 1
                    stats['new_words'] += 1
                
                # Get the word ID (from lexicon or updates)
                word_id = self.lexicon.get(word, lexicon_updates.get(word))
                word_ids.append(str(word_id))
            
            # Add to buffers
            forward_buffer.append(f"{self.next_doc_id}\t{' '.join(word_ids)}\n")
            metadata_buffer.append(f"{self.next_doc_id}|{title}|{authors}\n")
            
            stats['documents_added'] += 1
            stats['total_words_processed'] += len(words)
            self.next_doc_id += 1
            
            if (i + 1) % PROGRESS_INTERVAL == 0:
                print(f"  Processed: {i + 1:,} documents | "
                      f"New words: {stats['new_words']:,}")
            
            # Flush buffers periodically
            if len(forward_buffer) >= BATCH_SIZE:
                self._flush_to_indices(forward_buffer, metadata_buffer, 'a')
                forward_buffer.clear()
                metadata_buffer.clear()
        
        # Flush remaining data
        if forward_buffer:
            self._flush_to_indices(forward_buffer, metadata_buffer, 'a')
        
        print(f"\n[2/3] Updating lexicon with {stats['new_words']:,} new words...")
        self._update_lexicon(lexicon_updates)
        
        print(f"\n[3/3] Rebuilding inverted index...")
        self._rebuild_inverted_index()
        
        # Save state
        self._save_state()
        
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print("INCREMENTAL INDEXING COMPLETE")
        print("=" * 60)
        print(f"  Documents added: {stats['documents_added']:,}")
        print(f"  New words: {stats['new_words']:,}")
        print(f"  Total words processed: {stats['total_words_processed']:,}")
        print(f"  Total lexicon size: {len(self.lexicon) + len(lexicon_updates):,}")
        print(f"  Time elapsed: {elapsed:.2f}s")
        
        return stats
    
    def _flush_to_indices(self, forward_buffer, metadata_buffer, mode='a'):
        """Append buffers to index files"""
        with open(self.forward_index_path, mode, encoding='utf-8') as f_fwd, \
             open(self.metadata_path, mode, encoding='utf-8') as f_meta:
            f_fwd.writelines(forward_buffer)
            f_meta.writelines(metadata_buffer)
    
    def _update_lexicon(self, new_words_dict):
        """Append new words to lexicon file"""
        if new_words_dict:
            with open(self.lexicon_path, 'a', encoding='utf-8') as f:
                for word in sorted(new_words_dict.keys()):
                    word_id = new_words_dict[word]
                    f.write(f"{word}\t{word_id}\n")
                    self.lexicon[word] = word_id
    
    def _rebuild_inverted_index(self):
        """
        Rebuild the inverted index from scratch (efficient - reads forward index once).
        This is necessary after adding new documents.
        """
        if not os.path.exists(self.forward_index_path):
            print("ERROR: Forward index not found!")
            return
        
        inverted_index = defaultdict(set)
        
        print("  Reading forward index...")
        with open(self.forward_index_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                parts = line.strip().split('\t')
                if len(parts) < 2:
                    continue
                
                doc_id = parts[0]
                word_ids = parts[1].split()
                
                for word_id in set(word_ids):
                    inverted_index[word_id].add(doc_id)
                
                if line_num % PROGRESS_INTERVAL == 0:
                    print(f"    Processed: {line_num:,} documents")
        
        print(f"  Writing inverted index ({len(inverted_index):,} unique words)...")
        with open(self.inverted_index_path, 'w', encoding='utf-8') as f:
            buffer = []
            sorted_word_ids = sorted(inverted_index.keys(), key=lambda x: int(x))
            
            for i, word_id in enumerate(sorted_word_ids, 1):
                doc_ids = sorted(inverted_index[word_id], key=lambda x: int(x))
                buffer.append(f"{word_id}\t{' '.join(doc_ids)}\n")
                
                if len(buffer) >= BATCH_SIZE:
                    f.writelines(buffer)
                    buffer.clear()
                
                if i % PROGRESS_INTERVAL == 0:
                    print(f"    Written: {i:,} / {len(inverted_index):,} words")
            
            if buffer:
                f.writelines(buffer)
    
    def get_status(self):
        """Get current indexing status"""
        return {
            'next_doc_id': self.next_doc_id,
            'lexicon_size': len(self.lexicon),
            'word_id_counter': self.word_id_counter,
            'forward_index_size': os.path.getsize(self.forward_index_path) if os.path.exists(self.forward_index_path) else 0,
            'inverted_index_size': os.path.getsize(self.inverted_index_path) if os.path.exists(self.inverted_index_path) else 0
        }


if __name__ == "__main__":
    # Test the incremental indexer
    indexer = IncrementalIndexer(OUTPUT_DIR)
    
    # Example: add some test documents
    test_docs = [
        ("Test Doc 1", "This is a test document about machine learning algorithms.", "Author One"),
        ("Test Doc 2", "Another test document covering deep neural networks.", "Author Two"),
    ]
    
    stats = indexer.add_documents(test_docs)
    print("\nStatus:", indexer.get_status())
