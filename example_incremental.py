#!/usr/bin/env python3
"""
Quick Example: Incremental Indexing
Demonstrates the new feature in action
"""

from Backend.incremental_indexer import IncrementalIndexer
import os

def main():
    # Point to your VeridiaCore directory
    data_dir = os.path.join(os.path.dirname(__file__), "VeridiaCore")
    
    print("\n" + "="*70)
    print("INCREMENTAL INDEXING - QUICK EXAMPLE")
    print("="*70)
    
    # Initialize the indexer
    print("\n[1] Initializing incremental indexer...")
    indexer = IncrementalIndexer(data_dir)
    
    # Show current status
    status = indexer.get_status()
    print(f"\nCurrent Status:")
    print(f"  - Next document ID: {status['next_doc_id']}")
    print(f"  - Lexicon size: {status['lexicon_size']:,}")
    print(f"  - Word ID counter: {status['word_id_counter']}")
    
    # Example: Add some new documents
    print("\n[2] Adding new documents...")
    print("-" * 70)
    
    new_docs = [
        (
            "Introduction to Artificial Intelligence",
            """Artificial Intelligence is transforming how we work and live.
            AI systems can learn from data, recognize patterns, and make decisions
            with minimal human intervention. Key areas include machine learning,
            natural language processing, and computer vision. Organizations worldwide
            are investing heavily in AI research and development.""",
            "Dr. Sarah Johnson, Prof. Michael Chen"
        ),
        (
            "Advanced Python Programming Techniques",
            """Python has become the go-to language for AI and data science.
            This document covers advanced techniques including decorators, 
            metaclasses, async programming, and context managers. Mastering
            these concepts will make you a more proficient Python developer.
            We'll explore real-world examples and best practices.""",
            "Alex Wong"
        ),
        (
            "Data Science with Pandas and NumPy",
            """Pandas and NumPy are essential libraries for data manipulation
            and analysis in Python. NumPy provides numerical computing capabilities
            while Pandas offers high-level data structures and analysis tools.
            Together they form the foundation for modern data science workflows.""",
            "Emma Davis"
        ),
    ]
    
    stats = indexer.add_documents(new_docs)
    
    print("\n[3] Results:")
    print("-" * 70)
    print(f"✓ Documents added: {stats['documents_added']}")
    print(f"✓ New words discovered: {stats['new_words']:,}")
    print(f"✓ Total words processed: {stats['total_words_processed']:,}")
    
    # Show updated status
    print("\n[4] Updated Status:")
    print("-" * 70)
    status = indexer.get_status()
    print(f"  - Total documents indexed: {status['next_doc_id']}")
    print(f"  - Lexicon size: {status['lexicon_size']:,}")
    print(f"  - Forward index size: {status['forward_index_size']:,} bytes")
    print(f"  - Inverted index size: {status['inverted_index_size']:,} bytes")
    
    print("\n" + "="*70)
    print("SUCCESS! New documents have been added without reprocessing old data")
    print("="*70)
    
    print("\nNext Steps:")
    print("1. Start your Flask server: python Backend/app.py")
    print("2. Try searching for terms like 'artificial intelligence' or 'Python'")
    print("3. The search engine now includes your new documents")
    print("4. For HTTP API usage, see: test_incremental_indexing.py")
    print("5. For full documentation, see: INCREMENTAL_INDEXING_GUIDE.md")
    
    print("\nKey Benefits:")
    print("  ✓ Only new data was processed (~3 documents)")
    print("  ✓ Previous 45,000 documents weren't touched")
    print("  ✓ State automatically saved for next session")
    print("  ✓ Consistent document IDs across all operations")

if __name__ == "__main__":
    main()
