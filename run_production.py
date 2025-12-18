from waitress import serve
from Backend.app import app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('waitress')

if __name__ == "__main__":
    print("--- Veridia Search Engine (Production Mode) ---")
    print("Serving on http://127.0.0.1:5000")
    serve(app, host='127.0.0.1', port=5000, threads=8)
