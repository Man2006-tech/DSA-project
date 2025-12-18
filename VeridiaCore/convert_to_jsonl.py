import os
import json

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  # folder with PMC* files
OUTPUT_FILE = os.path.join(BASE_DIR, "dataset.jsonl")  # this will be created

# Get all text files in the data folder
files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]

with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
    for filename in files:
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        doc = {
            "filename": filename,
            "title": filename,  # you can keep the filename as title
            "content": content
        }
        out_f.write(json.dumps(doc) + "\n")

print(f"✅ Created dataset.jsonl with {len(files)} documents.")
