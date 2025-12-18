from flask import Flask, render_template, request, jsonify
from engine import SearchEngine
import os

app = Flask(__name__)

# Initialize Search Engine
print("Initializing Search Engine...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
engine = SearchEngine(BASE_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = engine.search(query)
    
    # Enrich results with snippets if possible
    enriched_results = []
    if results:
        for r in results:
            item = r.copy()
            content = engine.get_document_content(r['doc_id'])
            if content:
                item['snippet'] = content['abstract'][:150] + "..."
            else:
                item['snippet'] = "No preview available."
            enriched_results.append(item)
            
    return jsonify(enriched_results)

if __name__ == '__main__':
    app.run(debug=True)
