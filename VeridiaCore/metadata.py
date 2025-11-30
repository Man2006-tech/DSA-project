import json
import time

# CONFIGURATION
dataset_path = r"C:\Users\Ehsan Ullah\Downloads\archive (4)\arxiv-metadata-oai-snapshot.json"
limit = 2000000 

# LANGUAGE FILTERS (Must match indexer.py EXACTLY)
ENGLISH_STOP = {"the", "and", "is", "of", "in", "to", "with", "that", "for", "are", "this"}
GERMAN_STOP = {"der", "die", "und", "ist", "den", "von", "zu", "das", "sich", "des", "eine", "mit"}
FRENCH_STOP = {"le", "la", "et", "des", "en", "un", "une", "que", "dans", "pour", "sur", "qui"}

def is_strictly_english(text):
    words = text.lower().split()[:500]
    eng_score = 0
    foreign_score = 0
    
    for w in words:
        if w in ENGLISH_STOP: eng_score += 1
        elif w in GERMAN_STOP or w in FRENCH_STOP: foreign_score += 1

    if eng_score < 3: return False
    if foreign_score > (eng_score * 0.1): return False
    return True

def extract_metadata():
    print(f"--- EXTRACTING METADATA (ENGLISH ONLY) ---")
    start_time = time.time()
    
    with open("document_metadata.txt", "w", encoding="utf-8") as f_out, \
         open(dataset_path, 'r', encoding='utf-8') as f_in:
        
        doc_id = 1
        
        for line in f_in:
            if doc_id > limit: break
            if not line.strip(): continue

            try:
                data = json.loads(line)
                title = data.get('title', '').replace('\n', ' ').replace('|', '').strip()
                abstract = data.get('abstract', '').replace('\n', ' ').replace('|', '').strip()
                authors = data.get('authors', '').replace('\n', ' ').replace('|', '').strip()
                full_text = f"{title} {abstract}"

                # STRICT CHECK: Must match indexer.py logic
                if not is_strictly_english(full_text):
                    continue

                # Save Data
                f_out.write(f"{doc_id}|{title}|{authors}|{abstract}\n")

                if doc_id % 50000 == 0:
                    print(f"Processed {doc_id} documents...")
                
                doc_id += 1

            except Exception: pass

    print(f"--- SUCCESS: Metadata Synced ---")
    print(f"Time Taken: {round(time.time() - start_time, 2)}s")

extract_metadata()