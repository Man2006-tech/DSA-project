from flask import Flask, render_template, request, jsonify
import sys
import os
import re
import time
import threading

# Add the parent directory to path to import engine
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from VeridiaCore.engine import SearchEngine
from incremental_indexer import IncrementalIndexer
from ai_suggestion_engine import (
    AIAutoCorrector, AISuggestionEngine, SemanticQueryAnalyzer,
    create_ai_corrector_from_engine, create_ai_suggestion_engine
)

# Correctly locate templates and static folders given the directory structure
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Global State
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'VeridiaCore'))
search_engine = None
incremental_indexer = None
ai_corrector = None
ai_suggestions = None
semantic_analyzer = None
IS_READY = False

def init_engine():
    global search_engine, incremental_indexer, ai_corrector, ai_suggestions, semantic_analyzer, IS_READY
    
def init_engine():
    global search_engine, incremental_indexer, ai_corrector, ai_suggestions, semantic_analyzer, IS_READY
    
    try:
        print("\n[Init] Starting Background Initialization...")
        
        # Initialize Search Engine
        search_engine = SearchEngine(DATA_DIR)
        
        # Initialize Incremental Indexer
        incremental_indexer = IncrementalIndexer(DATA_DIR)
        
        # Initialize AI Components
        print("[Init] Loading AI Models (Lazy)...")
        start_init = time.time()
        try:
            ai_corrector = create_ai_corrector_from_engine(search_engine)
            ai_suggestions = create_ai_suggestion_engine(search_engine)
            semantic_analyzer = SemanticQueryAnalyzer(search_engine.vector_model)
            print(f"[Init] AI engines ready in {time.time() - start_init:.2f}s")
        except Exception as e:
            print(f"[Warning] Could not initialize AI components: {e}")
        
        IS_READY = True
        print("\n[Init] System READY. Serving requests.")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[CRITICAL] Init failed: {e}")

# Start Background Init
# threading.Thread(target=init_engine, daemon=True).start()

# Sync init enabled for reliability
init_engine()

def check_ready():
    if not IS_READY:
        return jsonify({
            'error': 'System is initializing...', 
            'ready': False,
            'status': 'Loading indices and AI models'
        }), 503
    return None

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    """Get indexing status"""
    if not IS_READY: return jsonify({'status': 'initializing'})
    return jsonify(incremental_indexer.get_status())

@app.route('/api/check-ready')
def api_check_ready():
    return jsonify({'ready': IS_READY})

@app.route('/api/search')
def search():
    not_ready = check_ready()
    if not_ready: return not_ready

    query = request.args.get('q',('').strip())
    semantic_param = request.args.get('semantic', 'true')
    use_semantic = semantic_param.lower() == 'true'

    if not query:
        return jsonify([])

    print(f"\n[Search API] Processing query: '{query}'")
    
    def enrich(results):
        enriched = []
        seen_ids = set()
        for res in results:
            doc_id = res['doc_id']
            if doc_id in seen_ids: continue
            seen_ids.add(doc_id)
            
            content_data = search_engine.get_document_content(doc_id)
            if content_data:
                res['abstract'] = content_data.get('abstract', 'No Abstract')
                res['filename'] = content_data.get('filename', 'Unknown')
            enriched.append(res)
        return enriched

    results = search_engine.search(query, use_semantic=use_semantic)

    if len(results) < 5 and ai_corrector:
        # Correction logic
        corrected_query = query
        words = query.split()
        new_words = []
        changed = False
        
        for word in words:
            if len(word) > 2:
                corr = ai_corrector.correct_word(word, max_suggestions=1)
                best = corr['suggestions'][0][0] if corr['suggestions'] else word
                new_words.append(best)
                if best.lower() != word.lower(): changed = True
            else:
                new_words.append(word)
        
        if changed:
            corrected_query = " ".join(new_words)
            corrected_results = search_engine.search(corrected_query, use_semantic=use_semantic)
            current_ids = {r['doc_id'] for r in results}
            for res in corrected_results:
                if res['doc_id'] not in current_ids:
                    results.append(res)

    if len(results) < 3 and len(query.split()) > 1:
        or_scores = {}
        for res in results: or_scores[res['doc_id']] = res
        
        for word in query.split():
            if len(word) < 3: continue
            word_res = search_engine.search(word, use_semantic=False)
            for res in word_res:
                did = res['doc_id']
                if did not in or_scores:
                    or_scores[did] = res
                    or_scores[did]['score'] *= 0.5 
                else:
                    or_scores[did]['score'] += res['score'] * 0.5 
        results = list(or_scores.values())
        results.sort(key=lambda x: x['score'], reverse=True)

    results = results[:50]
    final_output = enrich(results)
    return jsonify(final_output)

@app.route('/api/suggest')
def suggest():
    not_ready = check_ready()
    if not_ready: return jsonify([])
    
    prefix = request.args.get('q', '')
    if not prefix: return jsonify([])
    
    suggestions = search_engine.get_suggestions(prefix)
    return jsonify(suggestions)

@app.route('/api/autocomplete')
def autocomplete():
    not_ready = check_ready()
    if not_ready: 
         return jsonify({'suggestions': [], 'corrections': [], 'recommendations': [], 'note': 'System Initializing'})

    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'suggestions': [], 'corrections': [], 'recommendations': []})
    
    suggestions = []
    recommendations = []
    
    if ai_suggestions:
        completions = ai_suggestions.get_query_completions(query, max_suggestions=8)
        suggestions = [s['word'] for s in completions]
        if len(suggestions) < 3:
             trending = ai_suggestions.get_trending_suggestions(max_suggestions=3)
             recommendations = [t['word'] for t in trending]
    else:
        words = query.split()
        last_word = words[-1].lower() if words else ''
        suggestions = search_engine.get_suggestions(last_word)[:8]

    corrections = {}
    if ai_corrector:
        words = query.split()
        if words:
            last_word = words[-1]
            if len(last_word) > 2:
                corr_res = ai_corrector.correct_word(last_word, max_suggestions=1)
                if not corr_res['is_correct'] and corr_res['suggestions']:
                    corrections = {'word': corr_res['suggestions'][0][0], 'distance': 0}
    
    return jsonify({
        'suggestions': suggestions,
        'corrections': corrections,
        'recommendations': recommendations,
        'input_length': len(query)
    })

@app.route('/api/add-document', methods=['POST'])
def add_document():
    not_ready = check_ready()
    if not_ready: return not_ready
    try:
        data = request.get_json()
        if not data or 'text' not in data: return jsonify({'error': 'Missing text'}), 400
        stats = incremental_indexer.add_documents([(data.get('title',''), data.get('text',''), data.get('authors',''))])
        search_engine.load_indices()
        return jsonify({'success': True, 'stats': stats}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Disable debug reloader for instant start loop prevention
    app.run(host='0.0.0.0', port=5000, debug=False)
