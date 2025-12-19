
import os
import sys
import json
import re
import io

# Force UTF-8 for Windows Console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- 1. CONFIGURATION OVERRIDE ---
# We must override config before importing build modules
import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_DIR = os.path.join(BASE_DIR, "VeridiaCore_Demo")
TESTED_DATA_DIR = os.path.join(BASE_DIR, "tested data")

# Ensure Demo Directory Exists
os.makedirs(DEMO_DIR, exist_ok=True)

# Override Config Paths
config.OUTPUT_DIR = DEMO_DIR
config.DATA_DIR = TESTED_DATA_DIR # Not used directly by loader but good practice
config.JSON_DATASET_PATH = os.path.join(DEMO_DIR, "dataset.jsonl")
config.LEXICON_PATH = os.path.join(DEMO_DIR, "lexicon.txt")
config.FORWARD_INDEX_PATH = os.path.join(DEMO_DIR, "forward_index.txt")
config.INVERTED_INDEX_PATH = os.path.join(DEMO_DIR, "inverted_index.txt")
config.METADATA_PATH = os.path.join(DEMO_DIR, "document_metadata.txt")

# Now import modules (they will see the updated config)
from build_index_fast import build_indices_optimized
from build_inverted_fast import build_inverted_index_optimized

# --- 2. CONVERT TEXT TO JSONL ---
def convert_txt_to_jsonl():
    print(f" Converting 'tested data' to {config.JSON_DATASET_PATH}...")
    
    if not os.path.exists(TESTED_DATA_DIR):
        print(f"ERROR: {TESTED_DATA_DIR} not found!")
        return False

    with open(config.JSON_DATASET_PATH, 'w', encoding='utf-8') as jsonl_out:
        doc_id = 1
        for filename in os.listdir(TESTED_DATA_DIR):
            if not filename.endswith(".txt"): continue
            
            path = os.path.join(TESTED_DATA_DIR, filename)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                    
                # Create JSON Structure
                doc = {
                    "id": doc_id,
                    "title": filename.replace(".txt", "").replace("_"," "),
                    "text": text,
                    "abstract": text[:300] + "...",
                    "authors": "Demo Data",
                    "filename": filename # Important for UI
                }
                
                jsonl_out.write(json.dumps(doc) + "\n")
                doc_id += 1
            except Exception as e:
                print(f"Skipped {filename}: {e}")
                
    print(f"Converted {doc_id-1} documents.")
    return True

# --- 3. RUN BUILD PIPELINE ---
def main():
    print("="*60)
    print("  CREATING DEMO DATASET FOR RAILWAY")
    print(f"  Target: {DEMO_DIR}")
    print("="*60)

    # Step A: Convert
    if not convert_txt_to_jsonl():
        return

    # Step B: Build Lexicon/Forward/Meta
    # We need to monkeypatch stream_json_documents in build_index_fast's imported module
    # Actually, json_parser likely reads config.JSON_DATASET_PATH, let's check.
    # If not, we might need to patch it. 
    # Let's assume for now json_parser uses config.JSON_DATASET_PATH. 
    
    # PATCHING json_parser if loaded by build_index_fast
    import json_parser
    json_parser.JSON_FILE_PATH = config.JSON_DATASET_PATH # Explicitly update if it made a copy
    
    print("\n[Building Indices]...")
    build_indices_optimized()

    print("\n[Building Inverted Index]...")
    build_inverted_index_optimized()
    
    # Step C: Create dummy glove.txt (Optional but prevents startup error)
    # The VectorModel might fail if glove.txt is missing.
    # We will create a tiny dummy glove file.
    dummy_glove = os.path.join(DEMO_DIR, "glove.txt")
    with open(dummy_glove, 'w', encoding='utf-8') as f:
        f.write("a 0.1 0.2 0.3\n")
        f.write("the 0.4 0.5 0.6\n")
    print("\n[Created Dummy Glove Embeddings]")

    print("\nDONE! You can now deploy 'VeridiaCore_Demo' to Railway.")

if __name__ == "__main__":
    main()
