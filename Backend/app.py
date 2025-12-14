from flask import Flask, render_template, request, jsonify
import sys
import os
import re

# Add the parent directory to path to import engine
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from VeridiaCore.engine import SearchEngine

# Correctly locate templates and static folders given the directory structure
# Backend/app.py -> templates are in ../templates, static is in ../static
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Initialize Search Engine
# Data is in VeridiaCore (../VeridiaCore)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'VeridiaCore')
search_engine = SearchEngine(DATA_DIR)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
