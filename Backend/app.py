from flask import Flask, render_template, request, jsonify
import sys
import os
import json

# Add the parent directory to path to import engine
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from VeridiaCore.engine import SearchEngine

# Correctly locate templates and static folders given the directory structure
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Initialize Search Engine for Veridia
# Hardcoded path to ensure correct data loading
DATA_DIR = r"d:\Third Semester\DSA\Project\Search-Engine\VeridiaCore"
print(f"\n[App] Initializing Search Engine from: {DATA_DIR}")

search_engine = None
try:
    if not os.path.exists(DATA_DIR):
        print(f"[App] [CRITICAL ERROR] Data directory not found: {DATA_DIR}")
    else:
        search_engine = SearchEngine(DATA_DIR)
        print("[App] [OK] Search Engine Ready\n")
except Exception as e:
    print(f"[App] [ERR] Failed to initialize: {e}")
    import traceback
    traceback.print_exc()

@app.route('/')
def index():
    return render_template('index.html')

# Levenshtein distance for spell checking
def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

# Find corrections for a word
def find_corrections(word, max_distance=2):
    corrections = []
    word_lower = word.lower()
    
    if not search_engine: return []

    # Heuristic: use get_suggestions for prefix-based candidates
    suggestions = search_engine.get_suggestions(word_lower[:2]) 
    
    for suggestion in suggestions:
        distance = levenshtein_distance(word_lower, suggestion.lower())
        if distance <= max_distance and distance > 0:
            corrections.append({
                'word': suggestion,
                'distance': distance
            })
    
    # Sort by distance
    corrections.sort(key=lambda x: (x['distance'], x['word']))
    return corrections[:5]

@app.route('/api/search')
def search():
    """Main search endpoint with Fuzzy Logic matches"""
    if not search_engine:
        print("[API Search] Error: Engine is not initialized! Check console logs.")
        return jsonify({'error': 'Search engine not initialized. Check server console.'}), 500
    
    query = request.args.get('q', '').strip()
    semantic_param = request.args.get('semantic', 'true')
    use_semantic = semantic_param.lower() == 'true'

    if not query:
        return jsonify([])

    print(f"\n[API Search] Query: '{query}' (semantic={use_semantic})")
    
    try:
        # Stage 1: Standard Search
        results = search_engine.search(query, use_semantic=use_semantic)
        print(f"  Stage 1 (Exact/Semantic): Found {len(results)} results")

        # Stage 2: Fuzzy/Spelling Correction (if low results)
        if len(results) < 3:
            words = query.split()
            corrected_words = []
            changed = False
            
            for word in words:
                if len(word) > 3:
                    corrs = find_corrections(word, max_distance=2)
                    if corrs:
                        best = corrs[0]['word']
                        corrected_words.append(best)
                        if best.lower() != word.lower():
                            changed = True
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)
            
            if changed:
                corrected_query = " ".join(corrected_words)
                print(f"  Stage 2 (Correction): Retrying with '{corrected_query}'")
                tm_results = search_engine.search(corrected_query, use_semantic=use_semantic)
                if tm_results:
                    existing_ids = {r['doc_id'] for r in results}
                    for r in tm_results:
                        if r['doc_id'] not in existing_ids:
                            results.append(r)

        # Stage 3: Fallback "OR" Search
        if len(results) == 0 and len(query.split()) > 1:
            print(f"  Stage 3 (Fallback OR): Searching individual words")
            or_scores = {}
            words = query.split()
            for word in words:
                if len(word) < 3: continue
                w_results = search_engine.search(word, use_semantic=False)
                for res in w_results:
                    did = res['doc_id']
                    if did not in or_scores:
                        or_scores[did] = res
                        or_scores[did]['score'] *= 0.5 
                    else:
                        or_scores[did]['score'] += res['score'] * 0.3
            
            results = list(or_scores.values())
            results.sort(key=lambda x: x['score'], reverse=True)

        # Stage 4: Absolute Fallback
        if len(results) == 0:
            print(f"  Stage 4 (Absolute Fallback): Fetching trending/random documents")
            for i in range(1, 15):
                 doc_id = i
                 if doc_id in search_engine.metadata:
                     results.append({
                        "doc_id": doc_id,
                        "title": search_engine.metadata[doc_id]["title"],
                        "filename": search_engine.metadata[doc_id]["filename"],
                        "score": 0.1 
                     })

        # Limit results match
        results = results[:50]
        
        # Enrich with content
        enriched_results = []
        for res in results:
            doc_id = res['doc_id']
            try:
                content_data = search_engine.get_document_content(doc_id)
                if content_data:
                    res['abstract'] = content_data.get('abstract', 'No preview available')
                    res['filename'] = content_data.get('filename', res.get('filename', 'unknown'))
                else:
                    res['abstract'] = 'Content not available'
            except Exception as e2:
                res['abstract'] = 'Error loading content'
            
            enriched_results.append(res)
        
        return jsonify(enriched_results)
    
    except Exception as e:
        print(f"[API Search] CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/suggest')
def suggest():
    """Autocomplete suggestions (Legacy)"""
    if not search_engine:
        return jsonify([])
    
    prefix = request.args.get('q', '').strip()
    if not prefix:
        return jsonify([])
    
    try:
        suggestions = search_engine.get_suggestions(prefix)
        return jsonify(suggestions)
    except Exception as e:
        print(f"[API Suggest] Error: {e}")
        return jsonify([])

@app.route('/api/autocomplete')
def autocomplete():
    """Enhanced autocomplete with corrections and recommendations"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'suggestions': [], 'corrections': {}, 'recommendations': []})
    
    suggestions = []
    try:
        suggestions = search_engine.get_suggestions(query)[:8]
    except Exception: pass
        
    corrections = {}
    if len(suggestions) == 0 and len(query) > 3:
        try:
            corrs = find_corrections(query, max_distance=1)
            if corrs:
                corrections = {'word': corrs[0]['word'], 'distance': corrs[0]['distance']}
        except Exception: pass
            
    recommendations = []
    if len(suggestions) < 3:
        recommendations = ["latest research", "data science", "AI trends"]

    return jsonify({
        'suggestions': suggestions,
        'corrections': corrections,
        'recommendations': recommendations,
        'input_length': len(query)
    })

@app.route('/view/<int:doc_id>')
def view_document(doc_id):
    """Render formal document viewer"""
    if not search_engine:
        return "Engine not initialized", 500
    
    try:
        content = search_engine.get_document_content(doc_id)
        if not content:
            return "Document not found", 404
        return render_template('view.html', document=content)
    except Exception as e:
        print(f"View error: {e}")
        return str(e), 500

@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    """Handle file upload - INSTANT MODE (In-Memory)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not search_engine:
        return jsonify({'error': 'Engine not initialized'}), 500
    
    try:
        # Save to temp
        filename = file.filename
        content = file.read().decode('utf-8', errors='ignore')
        
        # Simple parsing
        text_content = content
        if filename.endswith('.json'):
             import json
             try:
                 data = json.loads(content)
                 text_content = str(data)
             except: pass
             
        # Use Dynamic In-Memory Index (INSTANT)
        doc_id = search_engine.add_document_dynamic(filename, text_content, filename)
        
        return jsonify({'success': True, 'message': f'Indexed {filename} (ID: {doc_id})'})
        
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-ready')
def api_check_ready():
    return jsonify({'ready': search_engine is not None})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  VERIDIA SEARCH ENGINE v2.0")
    print("  Server running on http://localhost:5001")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=True)
