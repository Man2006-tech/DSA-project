import os
import re
import time
import json

# Project: Veridia Search Engine
# Author: Abdullah
# Description: Builds Lexicon, Forward Index, and Inverted Index from PMC data.

# CONFIGURATION
# Adjust this path to match your actual data location
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "DATA", "PMC000xxxxxx")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. LANGUAGE MARKERS & STOP WORDS
STOP_WORDS_FILTER = {
    "a", "an", "the", "and", "or", "but", "if", "of", "at", "by", "for", "with", 
    "about", "against", "between", "into", "through", "during", "before", "after", 
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", 
    "under", "again", "further", "then", "once", "here", "there", "when", "where", 
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", 
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", 
    "very", "can", "will", "just", "don", "should", "now", "are", "is", "was", "were",
    "this", "that", "these", "those", "have", "has", "had", "which", "it", "its"
}

def clean_text(text):
    """
    Tokenizes and cleans text:
    - Lowercase
    - Keep only a-z characters
    - Filter stop words and short words
    """
    # Strict regex: Only letters a-z. 
    words = re.findall(r'[a-z]+', text.lower())
    
    filtered_words = []
    for w in words:
        # Keep word if > 2 chars and not in the stop list
        if len(w) > 2 and w not in STOP_WORDS_FILTER:
            filtered_words.append(w)
            
    return filtered_words

def parse_pmc_file(file_path):
    """
    Parses a PMC .txt file to extract Front (Metadata) and Body.
    Returns (title_text, body_text)
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Simple section extraction
    front_match = re.search(r'==== Front\s*(.*?)\s*==== Body', content, re.DOTALL)
    body_match = re.search(r'==== Body\s*(.*?)\s*(?:==== Refs|$)', content, re.DOTALL)

    front_text = front_match.group(1) if front_match else ""
    body_text = body_match.group(1) if body_match else ""
    
    # Fallback: if no sections found, treat whole file as body
    if not front_text and not body_text:
        body_text = content

    # Clean up title (take first non-empty line of front as title proxy)
    title = "Unknown Title"
    if front_text:
        lines = [l.strip() for l in front_text.split('\n') if l.strip()]
        if lines:
            # Heuristic: Title is often the longest line in the first few lines, 
            # or just take the first substantial line.
            # For now, let's take the first 200 chars of the front section as a preview.
            title = " ".join(lines)[:200] + "..."

    return title, front_text + " " + body_text

def build_indices():
    print(f"--- STARTING PMC INDEXING ---")
    print(f"Data Directory: {DATA_DIR}")
    start_time = time.time()

    lexicon = {}
    word_id_counter = 0
    
    # Output files
    forward_index_path = os.path.join(OUTPUT_DIR, "forward_index.txt")
    lexicon_path = os.path.join(OUTPUT_DIR, "lexicon.txt")
    metadata_path = os.path.join(OUTPUT_DIR, "document_metadata.txt")

    with open(forward_index_path, "w", encoding="utf-8") as f_fwd, \
         open(metadata_path, "w", encoding="utf-8") as f_meta:
        
        doc_id = 1
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt')]
        total_files = len(files)
        
        print(f"Found {total_files} files to process.")

        for filename in files:
            file_path = os.path.join(DATA_DIR, filename)
            
            try:
                title, full_text = parse_pmc_file(file_path)
                
                # Clean and Tokenize
                words = clean_text(full_text)
                
                if not words:
                    continue

                # Build Document -> WordID list
                doc_word_ids = []
                for word in words:
                    if word not in lexicon:
                        lexicon[word] = word_id_counter
                        word_id_counter += 1
                    
                    doc_word_ids.append(str(lexicon[word]))

                # Write to Forward Index: DocID \t WordID1 WordID2 ...
                f_fwd.write(f"{doc_id}\t{' '.join(doc_word_ids)}\n")
                
                # Write to Metadata: DocID | Filename | Title
                # Remove pipes from title to avoid delimiter collision
                safe_title = title.replace('|', ' ').replace('\n', ' ')
                f_meta.write(f"{doc_id}|{filename}|{safe_title}\n")

                if doc_id % 100 == 0:
                    print(f"Indexed {doc_id}/{total_files} documents...")
                
                doc_id += 1

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print("Saving Lexicon...")
    with open(lexicon_path, "w", encoding="utf-8") as f_lex:
        for word, w_id in lexicon.items():
            f_lex.write(f"{word}\t{w_id}\n")

    end_time = time.time()
    print(f"\n--- SUCCESS ---")
    print(f"Total Documents Indexed: {doc_id - 1}")
    print(f"Total Unique Words: {len(lexicon)}")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")

if __name__ == "__main__":
    build_indices()