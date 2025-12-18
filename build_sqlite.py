import sqlite3
import os

DATA_DIR = os.path.abspath('VeridiaCore')
LEX_PATH = os.path.join(DATA_DIR, "lexicon.txt")
DB_PATH = os.path.join(DATA_DIR, "lexicon.db")

def build_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    print(f"Creating SQL Lexicon at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create tables
    # storing word and id. Index on word for fast lookup.
    c.execute('CREATE TABLE lexicon (word TEXT PRIMARY KEY, id INTEGER)')
    
    # Optimization settings
    c.execute('PRAGMA synchronous = OFF')
    c.execute('PRAGMA journal_mode = MEMORY')
    
    print("Reading lexicon.txt...")
    count = 0
    batch = []
    
    with open(LEX_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                batch.append((parts[0], int(parts[1])))
                count += 1
                
                if len(batch) >= 100000:
                    c.executemany('INSERT INTO lexicon VALUES (?,?)', batch)
                    conn.commit()
                    batch = []
                    print(f"  Processed {count:,} words...")
    
    if batch:
        c.executemany('INSERT INTO lexicon VALUES (?,?)', batch)
        conn.commit()
        
    print(f"Creating Index...")
    # Index is implicitly created by PRIMARY KEY, but good to be sure optimized
    
    conn.close()
    print(f"[OK] SQLite Lexicon built. Total: {count:,} words.")

if __name__ == '__main__':
    build_db()
