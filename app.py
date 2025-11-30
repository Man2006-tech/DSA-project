from flask import Flask, render_template, request, jsonify
import sys
import os

# Add the inner directory to path to import engine
sys.path.append(os.path.join(os.path.dirname(__file__), 'VeridiaCore'))

from engine import SearchEngine

app = Flask(__name__)

# Initialize Search Engine
# Data is in VeridiaCore (where we outputted the indices)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'VeridiaCore')
search_engine = SearchEngine(DATA_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = search_engine.search(query)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
