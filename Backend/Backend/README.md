# Veridia Search Engine

A high-performance search engine for arXiv research papers with optimized indexing and sub-second query response times.

## 🚀 Features

- **Fast Indexing**: Processes 45,000+ documents in under 5 minutes
- **Quick Queries**: 
  - Single word: < 500ms
  - 5-word queries: < 1.5s
- **Memory Efficient**: < 2GB RAM for 45,000 documents
- **English Language Filtering**: Automatically filters non-English papers
- **Modern UI**: Clean, responsive search interface

## 📁 Project Structure

```
VeridiaCore/
Backend
├── config.py                    # Configuration settings
├── text_processor.py            # Text cleaning & tokenization
├── json_parser.py               # JSON streaming parser
├── build_index_fast.py          # Builds lexicon & forward index
├── build_inverted_fast.py       # Builds inverted index
├── build_all.py                 # Complete build pipeline
├── engine_optimized.py          # Search engine core
├── app.py                       # Flask web application
├── requirements.txt             # Python dependencies
├── build.bat                    # Windows build script
├── run.bat                      # Windows run script
├── static/
│   ├── style.css               # UI styles
│   └── script.js               # Frontend logic
└── templates/
    └── index.html              # Main search page
```

## 🛠️ Setup Instructions

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Data Path

Open `config.py` and update the path to your arXiv JSON file:

```python
JSON_DATASET_PATH = r"C:\path\to\your\arxiv-metadata-oai-snapshot.json"
```

### Step 3: Build Indices

**Option A: Windows (Easy)**
```bash
build.bat
```

**Option B: Manual**
```bash
python build_all.py
```

This will:
1. Parse JSON documents (English only)
2. Build lexicon and forward index
3. Build inverted index

Expected time: **3-5 minutes** for 45,000 documents

### Step 4: Start the Search Engine

**Option A: Windows (Easy)**
```bash
run.bat
```

**Option B: Manual**
```bash
python app.py
```

Open your browser to: **http://127.0.0.1:5000**

## 📊 Performance Benchmarks

| Metric | Target | Actual |
|--------|--------|--------|
| Indexing Time (45K docs) | < 10 min | ~3-4 min |
| Single Word Query | < 500ms | ~50-150ms |
| 5-Word Query | < 1.5s | ~200-500ms |
| RAM Usage | < 2GB | ~1.2-1.5GB |
| Documents Indexed | 45,000 | 45,000 |

## 🔧 Configuration Options

Edit `config.py` to customize:

- `MAX_DOCUMENTS`: Number of documents to index (default: 45,000)
- `BATCH_SIZE`: Batch size for I/O operations (default: 5,000)
- `MAX_RESULTS`: Maximum search results (default: 50)
- `MIN_WORD_LENGTH`: Minimum word length to index (default: 3)
- `STOP_WORDS`: Words to exclude from indexing

## 📝 File Descriptions

### Core Files (Required)

1. **config.py** - Central configuration
   - All paths and settings
   - Must be configured before building

2. **text_processor.py** - Text processing
   - Tokenization and cleaning
   - Language detection
   - Stop word filtering

3. **json_parser.py** - JSON parsing
   - Streams large JSON files
   - Filters non-English documents
   - Memory-efficient processing

4. **build_index_fast.py** - Index builder
   - Creates lexicon (word → word_id mapping)
   - Creates forward index (doc_id → word_ids)
   - Creates metadata (doc_id → title, authors)

5. **build_inverted_fast.py** - Inverted index builder
   - Creates inverted index (word_id → [doc_ids])
   - Optimized for search performance

6. **engine_optimized.py** - Search engine
   - Loads indices into memory
   - Processes search queries
   - LRU caching for frequent queries

7. **app.py** - Web application
   - Flask server
   - REST API endpoints
   - Serves search interface

### Support Files

8. **build_all.py** - Complete build script
   - Runs all indexing steps
   - Shows progress and statistics

9. **requirements.txt** - Python packages
   - Flask and dependencies

10. **build.bat** / **run.bat** - Windows shortcuts

## 🔍 How It Works

### Indexing Pipeline

1. **JSON Parsing**: Stream and filter English documents
2. **Text Processing**: Tokenize, clean, remove stop words
3. **Lexicon Building**: Map words to unique IDs
4. **Forward Index**: Map documents to word IDs
5. **Inverted Index**: Map word IDs to document lists
6. **Metadata**: Store titles and authors

### Search Process

1. **Query Processing**: Tokenize and clean query
2. **Word ID Lookup**: Convert words to IDs using lexicon
3. **Document Retrieval**: Find documents from inverted index
4. **Scoring**: Rank by term frequency
5. **Result Formatting**: Return top matches with metadata

## 🐛 Troubleshooting

### No search results?

1. Check that indices were built:
   ```bash
   dir VeridiaCore\*.txt
   ```
   You should see: `lexicon.txt`, `forward_index.txt`, `inverted_index.txt`, `document_metadata.txt`

2. Verify JSON path in `config.py`

3. Rebuild indices:
   ```bash
   python build_all.py
   ```

### Indexing too slow?

- Increase `BATCH_SIZE` in `config.py` (try 10000)
- Ensure JSON file is on SSD, not HDD
- Close other programs to free RAM

### Out of memory?

- Reduce `MAX_DOCUMENTS` in `config.py`
- Reduce `BATCH_SIZE` in `config.py`

### Port 5000 already in use?

Edit `app.py` and change:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Use different port
```

## 📈 Scaling Beyond 45,000 Documents

For larger datasets (100K+ documents):

1. **Increase RAM allocation**: Ensure 4GB+ available
2. **Use disk-based storage**: Consider SQLite for indices
3. **Implement sharding**: Split indices across multiple files
4. **Add compression**: Compress posting lists
5. **Use multiprocessing**: Parallelize indexing

## 🎯 Next Steps

- Add snippet generation in search results
- Implement phrase search ("exact match")
- Add filters (date, author, category)
- Implement relevance ranking (TF-IDF, BM25)
- Add search suggestions/autocomplete

## 📄 License

This project is for educational purposes.

## 👤 Author

Abdullah - Information Retrieval System Project