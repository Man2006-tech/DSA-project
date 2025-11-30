import json

# 1. UPDATE THIS PATH to where your 4GB file is located
dataset_path = r"C:\Users\Ehsan Ullah\Downloads\archive (4)\arxiv-metadata-oai-snapshot.json"


def process_arxiv_data(filepath, limit=45000):
    print(f"Opening dataset: {filepath}...")
    
    documents = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            count = 0
            
            # Read the file line by line (Streaming)
            for line in f:
                if not line.strip():
                    continue
                
                # Parse the JSON line
                doc = json.loads(line)
                
                # 2. EXTRACT DATA
                # We combine Title and Abstract to make the searchable text
                doc_id = doc.get('id')
                title = doc.get('title', '').replace('\n', ' ').strip()
                abstract = doc.get('abstract', '').replace('\n', ' ').strip()
                
                full_text = f"{title} {abstract}"
                
                # 3. Store or Process (For now, we just print/store in list)
                documents.append(full_text)
                
                count += 1
                if count % 1000 == 0:
                    print(f"Processed {count} documents...")
                
                # STOP after 45,000 documents (Project Requirement)
                if count >= limit:
                    break
                    
        print(f"\nSuccessfully loaded {len(documents)} documents.")
        return documents

    except FileNotFoundError:
        print("Error: File not found. Check the path.")
    except Exception as e:
        print(f"Error: {e}")

# Run the function
# This variable 'docs' now holds your text data
docs = process_arxiv_data(dataset_path)

# --- QUICK TEST: Show the first document ---
if docs:
    print("\n--- SAMPLE DOCUMENT 1 ---")
    print(docs[0][:500]) # Print first 500 characters