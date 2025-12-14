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
# Data is in VeridiaCore (../VeridiaCore)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'VeridiaCore')
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
    query = request.args.get('q', '')
    semantic_param = request.args.get('semantic', 'true')
    use_semantic = semantic_param.lower() == 'true'

    if not query:
        return jsonify([])
    
    # Updated to pass semantic flag
    results = search_engine.search(query, use_semantic=use_semantic)
    
    # Enrich results with content
    enriched_results = []
    for res in results:
        doc_id = res['doc_id']
        content_data = search_engine.get_document_content(doc_id)
        if content_data:
            res['abstract'] = content_data.get('abstract', 'No Abstract')
        
        enriched_results.append(res)

    return jsonify(enriched_results)

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
    
    # Get word suggestions
    words = query.split()
    last_word = words[-1].lower() if words else ''
    
    # Get suggestions for the last word
    suggestions = search_engine.get_suggestions(last_word)[:8]
    
    # Check if we need corrections for any word
    corrections = {}
    recommendations = []
    
    if len(last_word) > 2:
        # Find corrections for the last word
        corrected = find_corrections(last_word)
        if corrected:
            corrections = corrected[0] if corrected else {}
        
        # Get related recommendations
        if suggestions:
            recommendations = suggestions[:5]
    
    return jsonify({
        'suggestions': suggestions,
        'corrections': corrections,
        'recommendations': recommendations,
        'input_length': len(last_word)
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
        max_suggestions = int(request.args.get('limit', 5))
        
        if not query or len(query) < 1:
            return jsonify({
                'query': query,
                'corrections': [],
                'confidence': 0
            })
        
        # Get corrections for the last word
        words = query.split()
        last_word = words[-1] if words else ''
        
        if len(last_word) < 2:
            return jsonify({
                'query': query,
                'corrections': [],
                'confidence': 0
            })
        
        # Perform correction
        correction = ai_corrector.correct_word(last_word, max_suggestions=max_suggestions)
        
        # Build complete suggestions (replace last word in query)
        full_suggestions = []
        for sugg_word, score in correction['suggestions']:
            corrected_query = ' '.join(words[:-1] + [sugg_word])
            full_suggestions.append({
                'query': corrected_query,
                'corrected_word': sugg_word,
                'original_word': last_word,
                'score': float(score),
                'correction_type': correction['correction_type']
            })
        
        return jsonify({
            'query': query,
            'is_correct': correction['is_correct'],
            'corrections': full_suggestions,
            'correction_method': correction['correction_type'],
            'count': len(full_suggestions)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/smart-suggest', methods=['GET'])
def smart_suggest():
    """
    Advanced AI-powered suggestion engine
    Combines:
    - Prefix matching
    - Semantic relevance
    - Frequency analysis
    - Query intent detection
    """
    try:
        if not ai_suggestions:
            return jsonify({'error': 'Suggestion engine not initialized'}), 500
        
        query = request.args.get('q', '').strip()
        max_suggestions = int(request.args.get('limit', 8))
        
        if not query:
            return jsonify({
                'query': query,
                'suggestions': [],
                'trending': [],
                'insight': 'Enter a search term'
            })
        
        # Get query completions
        completions = ai_suggestions.get_query_completions(query, max_suggestions)
        
        # Get trending terms (if short query)
        trending = []
        if len(query.split()) == 1 and len(query) < 3:
            trending = ai_suggestions.get_trending_suggestions(max_suggestions=5)
        
        # Format suggestions
        formatted_suggestions = [
            {
                'word': sugg['word'],
                'score': sugg['score'],
                'frequency': sugg['frequency'],
                'type': sugg['type']
            }
            for sugg in completions
        ]
        
        return jsonify({
            'query': query,
            'suggestions': formatted_suggestions,
            'trending': [{'word': t['word'], 'frequency': t['frequency']} for t in trending],
            'count': len(formatted_suggestions)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query-analysis', methods=['GET'])
def query_analysis():
    """
    Analyze search query for intent and structure
    Provides insights on what the user is looking for
    """
    try:
        if not semantic_analyzer:
            return jsonify({'error': 'Query analyzer not initialized'}), 500
        
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Analyze the query
        analysis = semantic_analyzer.analyze_query(query)
        
        # Get related suggestions based on query intent
        if analysis['intent'] == 'search':
            related = ai_suggestions.get_related_suggestions(analysis['tokens'], max_suggestions=5) if ai_suggestions else []
        else:
            related = []
        
        return jsonify({
            'query': query,
            'analysis': {
                'intent': analysis['intent'],
                'complexity': analysis['complexity'],
                'token_count': len(analysis['tokens']),
                'tokens': analysis['tokens']
            },
            'related_suggestions': [s['word'] for s in related],
            'interpretation': f"You're {analysis['intent']}ing for: {', '.join(analysis['tokens'])}"
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced-search', methods=['GET'])
def enhanced_search():
    """
    Advanced search with automatic correction and better results
    Combines spell correction, semantic analysis, and intelligent ranking
    """
    try:
        query = request.args.get('q', '').strip()
        use_semantic = request.args.get('semantic', 'true').lower() == 'true'
        use_correction = request.args.get('correct', 'true').lower() == 'true'
        
        if not query:
            return jsonify([])
        
        # Step 1: Analyze query
        if semantic_analyzer:
            analysis = semantic_analyzer.analyze_query(query)
        else:
            analysis = {'tokens': query.split(), 'intent': 'search'}
        
        # Step 2: Attempt correction if enabled
        corrected_query = query
        correction_info = None
        
        if use_correction and ai_corrector:
            words = query.split()
            corrected_words = []
            corrections_made = []
            
            for word in words:
                correction = ai_corrector.correct_word(word, max_suggestions=1)
                if not correction['is_correct'] and correction['suggestions']:
                    corrected_words.append(correction['suggestions'][0][0])
                    corrections_made.append({
                        'from': word,
                        'to': correction['suggestions'][0][0],
                        'method': correction['correction_type']
                    })
                else:
                    corrected_words.append(word)
            
            if corrections_made:
                corrected_query = ' '.join(corrected_words)
                correction_info = {
                    'original': query,
                    'corrected': corrected_query,
                    'corrections': corrections_made
                }
        
        # Step 3: Perform search with corrected query
        results = search_engine.search(corrected_query, use_semantic=use_semantic)
        
        # Step 4: Enrich results
        enriched_results = []
        for res in results:
            doc_id = res['doc_id']
            content_data = search_engine.get_document_content(doc_id)
            if content_data:
                res['abstract'] = content_data.get('abstract', 'No Abstract')
            enriched_results.append(res)
        
        return jsonify({
            'query': query,
            'corrected_query': corrected_query if correction_info else None,
            'correction': correction_info,
            'analysis': {
                'intent': analysis['intent'],
                'complexity': analysis['complexity']
            },
            'results': enriched_results,
            'count': len(enriched_results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
