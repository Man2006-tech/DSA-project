from flask import Flask, render_template, request, jsonify
import sys
import os

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
