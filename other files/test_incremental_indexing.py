"""
INCREMENTAL INDEXING USAGE GUIDE
==================================

This guide shows how to use the new incremental indexing system to add
new documents without reprocessing previously indexed data.

KEY BENEFITS:
- New data only processed once
- Previous indices remain in memory
- Significantly faster for large datasets
- Persistent state tracking
"""

import requests
import json
import time

# Base URL for your Flask server
BASE_URL = "http://localhost:5000"

def test_single_document_addition():
    """Test adding a single document"""
    print("\n" + "="*60)
    print("TEST 1: Adding a Single Document")
    print("="*60)
    
    doc = {
        "title": "Machine Learning Basics",
        "text": "Machine learning is a subset of artificial intelligence. It involves training algorithms to learn patterns from data. Common techniques include supervised learning, unsupervised learning, and reinforcement learning.",
        "authors": "John Smith"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/add-document",
        json=doc,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    return response.status_code == 201

def test_multiple_documents_addition():
    """Test adding multiple documents at once"""
    print("\n" + "="*60)
    print("TEST 2: Adding Multiple Documents")
    print("="*60)
    
    docs = {
        "documents": [
            {
                "title": "Deep Learning Fundamentals",
                "text": "Deep learning uses neural networks with multiple layers. These networks can learn hierarchical representations of data. Applications include computer vision, natural language processing, and speech recognition.",
                "authors": "Jane Doe"
            },
            {
                "title": "Natural Language Processing",
                "text": "NLP enables computers to understand and process human language. Techniques include tokenization, lemmatization, named entity recognition, and sentiment analysis.",
                "authors": "Bob Johnson"
            },
            {
                "title": "Computer Vision Fundamentals",
                "text": "Computer vision focuses on enabling machines to understand images and videos. Key tasks include image classification, object detection, image segmentation, and pose estimation.",
                "authors": "Alice Williams"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/add-documents",
        json=docs,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    return response.status_code == 201

def test_search_after_addition(query="machine learning"):
    """Test searching after documents have been added"""
    print("\n" + "="*60)
    print(f"TEST 3: Searching for '{query}'")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/api/search",
        params={"q": query, "semantic": "true"}
    )
    
    print(f"Status Code: {response.status_code}")
    results = response.json()
    print(f"Found {len(results)} results")
    for i, result in enumerate(results[:3], 1):  # Show first 3
        print(f"\n  Result {i}:")
        print(f"    Score: {result.get('score')}")
        print(f"    Doc ID: {result.get('doc_id')}")
        print(f"    Abstract: {result.get('abstract', 'N/A')[:100]}...")

def test_get_status():
    """Get current indexing status"""
    print("\n" + "="*60)
    print("TEST 4: Checking Indexing Status")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/status")
    
    print(f"Status Code: {response.status_code}")
    status = response.json()
    print(json.dumps(status, indent=2))
    
    print("\nExplanation:")
    print(f"  - next_doc_id: {status['next_doc_id']} (next document will get this ID)")
    print(f"  - lexicon_size: {status['lexicon_size']} (unique words indexed)")
    print(f"  - word_id_counter: {status['word_id_counter']} (total word IDs assigned)")

def main():
    print("\n" + "="*80)
    print("INCREMENTAL INDEXING SYSTEM TEST")
    print("="*80)
    print("This test demonstrates the new incremental indexing capabilities")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=2)
        print("✓ Server is running and accessible")
    except:
        print("✗ ERROR: Server is not running!")
        print("  Start the Flask app first: python app.py")
        return
    
    # Run tests
    test_get_status()
    
    print("\n" + "="*80)
    print("Adding new documents (WITHOUT reprocessing previous data)...")
    print("="*80)
    
    # Add single document
    if test_single_document_addition():
        print("✓ Single document added successfully")
    else:
        print("✗ Failed to add single document")
    
    time.sleep(2)
    
    # Add multiple documents
    if test_multiple_documents_addition():
        print("✓ Multiple documents added successfully")
    else:
        print("✗ Failed to add multiple documents")
    
    time.sleep(2)
    
    # Check status after addition
    test_get_status()
    
    # Search to verify new documents are indexed
    test_search_after_addition("deep learning")
    test_search_after_addition("neural networks")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nKey Points:")
    print("1. Documents were added incrementally WITHOUT reprocessing all data")
    print("2. Lexicon and indices were updated automatically")
    print("3. Searches return results from both old and new documents")
    print("4. State is persisted (check VeridiaCore/indexing_state.json)")

if __name__ == "__main__":
    main()
