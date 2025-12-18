from flask import Flask, render_template, request, jsonify
import sys
import os
import re
import time

# Add the parent directory to path to import engine
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from VeridiaCore.engine import SearchEngine
from incremental_indexer import IncrementalIndexer
from ai_suggestion_engine import (
    AIAutoCorrector, AISuggestionEngine, SemanticQueryAnalyzer,
    create_ai_corrector_from_engine, create_ai_suggestion_engine
)

# Correctly locate templates and static folders given the directory structure
# Backend/app.py -> templates are in ../templates, static is in ../static
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Initialize Search Engine
# Data is in Veridia_Core/VeridiaCore (where barrels are)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'VeridiaCore'))
search_engine = SearchEngine(DATA_DIR)

# Initialize Incremental Indexer
incremental_indexer = IncrementalIndexer(DATA_DIR)

# Initialize AI-Powered Components
print("\n[Init] Creating AI Corrector and Suggestion Engine...")
start_init = time.time()

try:
    ai_corrector = create_ai_corrector_from_engine(search_engine)
    ai_suggestions = create_ai_suggestion_engine(search_engine)
    semantic_analyzer = SemanticQueryAnalyzer(search_engine.vector_model)
    
    init_time = time.time() - start_init
    print(f"[Init] AI engines ready in {init_time:.2f}s")
except Exception as e:
    print(f"[Warning] Could not initialize AI components: {e}")
    ai_corrector = None
    ai_suggestions = None
    semantic_analyzer = None

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
    
    for suggestion in search_engine.get_suggestions(word_lower):
        distance = levenshtein_distance(word_lower, suggestion.lower())
        if distance <= max_distance and distance > 0:
            corrections.append({
                'word': suggestion,
                'distance': distance
            })
    
    # Sort by distance
    corrections.sort(key=lambda x: (x['distance'], x['word']))
    return corrections[:5]  # Return top 5

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    # --- NEW ROBUST SEARCH LOGIC ---
    # Replaces old strict-only logic as requested
    
    query = request.args.get('q',('').strip())
    semantic_param = request.args.get('semantic', 'true')
    use_semantic = semantic_param.lower() == 'true'

    if not query:
        return jsonify([])

    print(f"\n[Search API] Processing query: '{query}'")
    
    # helper for enriching results
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

    # Stage 1: Standard Search (Strict AND)
    # This is best for exact matches
    results = search_engine.search(query, use_semantic=use_semantic)
    print(f"  Stage 1 (Strict): Found {len(results)} results")

    # Stage 2: AI Auto-Correction
    # If Stage 1 failed/low results, try fixing typos
    if len(results) < 5 and ai_corrector:
        corrected_query = query
        words = query.split()
        new_words = []
        changed = False
        
        for word in words:
            if len(word) > 2:
                # Get correction
                corr = ai_corrector.correct_word(word, max_suggestions=1)
                best = corr['suggestions'][0][0] if corr['suggestions'] else word
                new_words.append(best)
                if best.lower() != word.lower():
                    changed = True
            else:
                new_words.append(word)
        
        if changed:
            corrected_query = " ".join(new_words)
            print(f"  Stage 2 (Correction): Retrying with '{corrected_query}'")
            corrected_results = search_engine.search(corrected_query, use_semantic=use_semantic)
            print(f"    Found {len(corrected_results)} results")
            
            # Merge results (preferring strictly matched ones)
            # Simple merge: existing results + new corrected ones
            current_ids = {r['doc_id'] for r in results}
            for res in corrected_results:
                if res['doc_id'] not in current_ids:
                    results.append(res)

    # Stage 3: Fallback "OR" Search (The Safety Net)
    # If we still have very few results and multiple words, search for ANY word
    if len(results) < 3 and len(query.split()) > 1:
        print(f"  Stage 3 (Fallback OR): searching words individually")
        
        # Use a dictionary to accumulate scores
        or_scores = {}
        # Pre-populate with existing results
        for res in results:
            or_scores[res['doc_id']] = res
        
        words = query.split()
        for word in words:
            if len(word) < 3: continue # Skip small stop words like 'is', 'of'
            
            # Search each word individually (no semantic for speed/relevance focus)
            word_res = search_engine.search(word, use_semantic=False)
            for res in word_res:
                did = res['doc_id']
                if did not in or_scores:
                    or_scores[did] = res
                    # Penalty for partial match compared to full match? 
                    # Actually engine.search already scores. 
                    # We might want to lower score since it's just one word match.
                    or_scores[did]['score'] *= 0.5 
                else:
                    # Boost score if multiple words match
                    or_scores[did]['score'] += res['score'] * 0.5 

        # Convert back to list and sort
        results = list(or_scores.values())
        results.sort(key=lambda x: x['score'], reverse=True)
        print(f"    After OR-Merge: {len(results)} total results")

    # Limit results
    results = results[:50]
    
    # Final Enrichment
    final_output = enrich(results)
    
    return jsonify(final_output)

@app.route('/api/suggest')
def suggest():
    prefix = request.args.get('q', '')
    if not prefix:
        return jsonify([])
    
    suggestions = search_engine.get_suggestions(prefix)
    return jsonify(suggestions)

@app.route('/api/autocomplete')
def autocomplete():
    """Enhanced autocomplete with corrections and recommendations"""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 1:
        return jsonify({
            'suggestions': [],
            'corrections': [],
            'recommendations': []
        })
    
    # Use new AI engine if available
    if ai_suggestions:
        # Get smart suggestions replacing old prefix logic
        completions = ai_suggestions.get_query_completions(query, max_suggestions=8)
        suggestions = [s['word'] for s in completions]
        
        # Get recommendations (trending or related)
        recommendations = []
        if len(suggestions) < 3:
             trending = ai_suggestions.get_trending_suggestions(max_suggestions=3)
             recommendations = [t['word'] for t in trending]
    else:
        # Fallback to old logic
        words = query.split()
        last_word = words[-1].lower() if words else ''
        suggestions = search_engine.get_suggestions(last_word)[:8]
        recommendations = []

    # Use AI corrector for corrections
    corrections = {}
    if ai_corrector:
        words = query.split()
        if words:
            last_word = words[-1]
            if len(last_word) > 2:
                corr_res = ai_corrector.correct_word(last_word, max_suggestions=1)
                # Format to match expected frontend structure if possible, or simplified
                # Old frontend expects: corrections = {'word': 'suggestion', 'distance': 1}
                # But typically it expects a list or single object. 
                # script.js line 178 checks: if (corrections && corrections.word)
                if not corr_res['is_correct'] and corr_res['suggestions']:
                    corrections = {
                        'word': corr_res['suggestions'][0][0],
                        'distance': 0 # Dummy
                    }
    
    return jsonify({
        'suggestions': suggestions,
        'corrections': corrections,
        'recommendations': recommendations,
        'input_length': len(query)
    })


@app.route('/api/debug')
def debug():
    return jsonify({
        "data_dir": search_engine.data_dir,
        "lexicon_size": len(search_engine.lexicon),
        "offsets_size": len(search_engine.word_offsets),
        "metadata_size": len(search_engine.metadata),
        "cwd": os.getcwd(),
        "vector_model_loaded": search_engine.vector_model.loaded
    })

@app.route('/api/status')
def status():
    """Get indexing status"""
    return jsonify(incremental_indexer.get_status())

@app.route('/api/add-document', methods=['POST'])
def add_document():
    """
    Add a single new document to the search engine.
    
    Expected JSON:
    {
        "title": "Document Title",
        "text": "Full text content of the document",
        "authors": "Author Names"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing required field: text'}), 400
        
        title = data.get('title', 'Untitled')
        text = data.get('text', '')
        authors = data.get('authors', 'Unknown')
        
        # Add document using incremental indexer
        stats = incremental_indexer.add_documents([
            (title, text, authors)
        ])
        
        # Reload the search engine with updated indices
        search_engine.load_indices()
        
        return jsonify({
            'success': True,
            'message': 'Document added successfully',
            'stats': stats,
            'new_doc_id': incremental_indexer.next_doc_id - 1
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-documents', methods=['POST'])
def add_documents():
    """
    Add multiple new documents to the search engine.
    
    Expected JSON:
    {
        "documents": [
            {
                "title": "Doc 1",
                "text": "Content 1",
                "authors": "Author 1"
            },
            {
                "title": "Doc 2",
                "text": "Content 2",
                "authors": "Author 2"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'documents' not in data:
            return jsonify({'error': 'Missing required field: documents'}), 400
        
        docs = data.get('documents', [])
        if not docs:
            return jsonify({'error': 'Documents list is empty'}), 400
        
        # Convert to expected format
        documents = []
        for doc in docs:
            title = doc.get('title', 'Untitled')
            text = doc.get('text', '')
            authors = doc.get('authors', 'Unknown')
            documents.append((title, text, authors))
        
        # Add documents using incremental indexer
        stats = incremental_indexer.add_documents(documents)
        
        # Reload the search engine with updated indices
        search_engine.load_indices()
        
        return jsonify({
            'success': True,
            'message': f'{len(documents)} document(s) added successfully',
            'stats': stats,
            'total_documents': incremental_indexer.next_doc_id
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-state', methods=['POST'])
def clear_state():
    """
    WARNING: Clear indexing state and start fresh.
    This will reset the incremental indexer state.
    """
    try:
        # Reset state
        incremental_indexer.next_doc_id = 0
        incremental_indexer.word_id_counter = 0
        incremental_indexer.lexicon.clear()
        incremental_indexer._save_state()
        
        return jsonify({
            'success': True,
            'message': 'Indexing state cleared'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/autocorrect', methods=['GET'])
def autocorrect():
    """
    AI-powered spell correction using multiple ML techniques
    Returns correction suggestions and confidence scores
    """
    try:
        if not ai_corrector:
            return jsonify({'error': 'AI corrector not initialized'}), 500
            
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 5))
        
        if not query:
            return jsonify({'corrections': []})
            
        # Split into words and correct each
        words = query.split()
        all_corrections = []
        
        for word in words:
            # Skip short words or numbers
            if len(word) < 3 or word.isdigit():
                continue
                
            # helper to get one best suggestion
            res = ai_corrector.correct_word(word, max_suggestions=limit)
            suggestions = res.get('suggestions', [])
            
            if suggestions and suggestions[0][0] != word.lower():
                all_corrections.append({
                    'original': word,
                    'corrections': [{'corrected_word': w, 'score': s} for w, s in suggestions]
                })
                
        return jsonify({
            'query': query,
            'corrections': all_corrections
        })
    except Exception as e:
        print(f"Error in autocorrect: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/smart-suggest', methods=['GET'])
def smart_suggest():
    """
    Intelligent suggestions based on context, frequency, and semantics.
    """
    try:
        if not ai_suggestions:
            # Fallback to simple suggestions
            return suggest()
            
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 8))
        
        if not query:
            return jsonify({'suggestions': [], 'trending': []})
            
        # 1. Prefix matches (primary)
        suggestions = ai_suggestions.get_query_completions(query, max_suggestions=limit)
        
        # 2. Trending (secondary)
        trending = ai_suggestions.get_trending_suggestions(max_suggestions=5)
        
        return jsonify({
            'suggestions': suggestions,
            'trending': trending
        })
        
    except Exception as e:
        print(f"Error in smart-suggest: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/query-analysis', methods=['GET'])
def query_analysis():
    """
    Analyze query intent and complexity.
    """
    try:
        if not semantic_analyzer:
            return jsonify({'error': 'Semantic analyzer not initialized'}), 500
            
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'analysis': {}})
            
        analysis = semantic_analyzer.analyze_query(query)
        
        return jsonify({
            'query': query,
            'analysis': analysis,
            'interpretation': f"You're comparing for: {', '.join(analysis['tokens'])}" # Simple interpretation
        })
        
    except Exception as e:
        print(f"Error in query-analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced-search', methods=['GET'])
def enhanced_search():
    """
    Smart search that applies auto-correction and semantic expansion automatically.
    """
    try:
        query = request.args.get('q', '').strip()
        use_semantic = request.args.get('semantic', 'true').lower() == 'true'
        use_correct = request.args.get('correct', 'true').lower() == 'true'
        
        if not query:
            return jsonify({'results': [], 'correction': None})
            
        final_query = query
        correction_info = None
        
        # 1. Apply Auto-correction if requested
        if use_correct and ai_corrector:
            # Simple full query correction logic
            words = query.split()
            corrected_words = []
            has_correction = False
            first_corr_list = []
            
            for word in words:
                if len(word) < 3:
                     corrected_words.append(word)
                     continue
                res = ai_corrector.correct_word(word, max_suggestions=1)
                suggs = res.get('suggestions', [])
                if suggs:
                     best_word = suggs[0][0]
                     corrected_words.append(best_word)
                     if best_word != word.lower():
                         has_correction = True
                         first_corr_list.append({'from': word, 'to': best_word, 'method': res.get('correction_type')})
                else:
                     corrected_words.append(word)
            
            if has_correction:
                final_query = " ".join(corrected_words)
                correction_info = {
                    'original': query,
                    'corrections': first_corr_list
                }
        
        # 2. Perform Search (using semantic engine)
        results = search_engine.search(final_query, use_semantic=use_semantic)
        
        # 3. Enrich Results
        enriched_results = []
        for res in results:
            doc_id = res['doc_id']
            content_data = search_engine.get_document_content(doc_id)
            if content_data:
                res['abstract'] = content_data.get('abstract', 'No Abstract')
                res['filename'] = content_data.get('filename', 'Unknown')
            enriched_results.append(res)
            
        return jsonify({
            'query': query,
            'corrected_query': final_query,
            'correction': correction_info,
            'results': enriched_results
        })
        
    except Exception as e:
        print(f"Error in enhanced-search: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
