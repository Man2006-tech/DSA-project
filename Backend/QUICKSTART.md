# Veridia Search Engine - Quick Start

## ⚡ 5-Minute Setup

### 1️⃣ Install Dependencies (30 seconds)
```bash
pip install flask
```

### 2️⃣ Update Config (1 minute)

Open `config.py` and change this line:
```python
JSON_DATASET_PATH = r"C:\Users\Ehsan Ullah\Downloads\archive (4)\arxiv-metadata-oai-snapshot.json"
```
to your actual JSON file path.

### 3️⃣ Build Indices (3-4 minutes)

**Windows:**
```bash
build.bat
```

**Mac/Linux:**
```bash
python build_all.py
```

Wait for completion. You'll see:
```
✓ Total Documents Indexed: 45,000
✓ Unique Words: ~50,000
✓ Time Elapsed: ~200 seconds
```

### 4️⃣ Start Server (10 seconds)

**Windows:**
```bash
run.bat
```

**Mac/Linux:**
```bash
python app.py
```

### 5️⃣ Open Browser

Go to: **http://127.0.0.1:5000**

Search for something like: `machine learning` or `quantum physics`

---

## 🎯 What Gets Created

After building, you'll have these files in `VeridiaCore/`:

1. **lexicon.txt** - Word to ID mapping (~2-3 MB)
2. **forward_index.txt** - Document to words (~40-50 MB)
3. **inverted_index.txt** - Word to documents (~15-20 MB)
4. **document_metadata.txt** - Titles and authors (~1-2 MB)

Total: **~60-75 MB** for 45,000 documents

---

## 🔥 Performance Expectations

| Query Type | Expected Time |
|------------|---------------|
| "machine" | 50-100ms |
| "machine learning" | 100-200ms |
| "deep learning neural" | 200-400ms |
| "quantum computing algorithms" | 300-500ms |

All well under the requirements! ✅

---

## ❌ Common Issues

### Issue: "JSON file not found"
**Fix:** Update `JSON_DATASET_PATH` in `config.py`

### Issue: "No search results"
**Fix:** Run `build.bat` or `python build_all.py` first

### Issue: "Port 5000 in use"
**Fix:** In `app.py`, change port to 5001:
```python
app.run(debug=True, port=5001)
```

---

## 📊 Verify Your Setup

After building, run this to check:

```python
# test_setup.py
from engine_optimized import SearchEngine

engine = SearchEngine()
results = engine.search("machine learning")

print(f"✓ Found {len(results)} results")
for r in results[:3]:
    print(f"  - {r['title'][:60]}...")
```

Expected output:
```
✓ Found 50 results
  - Machine Learning: A Probabilistic Perspective...
  - Deep Learning for Computer Vision...
  - Introduction to Machine Learning Algorithms...
```

---

## 🎓 Understanding the Output

When you build indices, you'll see:

```
[1/3] Processing documents...
  ✓ Collected 5000 English docs
  ✓ Collected 10000 English docs
  ...
  
[2/3] Saving lexicon...

[3/3] Building inverted index...

✓ Total Documents: 45,000
✓ Unique Words: 52,341
✓ Time: 198.5 seconds
```

This means:
- **45,000** research papers indexed
- **52,341** unique words in vocabulary
- **~3.3 minutes** total time
- **227 docs/second** processing speed

---

## 🚀 Ready to Search!

Your search engine is now ready for queries like:

- `neural networks`
- `quantum computing`
- `machine learning algorithms`
- `gravitational waves`
- `climate change models`

Enjoy fast, accurate scientific paper search! 🎉