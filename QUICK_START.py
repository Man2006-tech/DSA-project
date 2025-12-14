#!/usr/bin/env python3
"""
⚡ QUICK START - AI Search Engine in 5 Minutes
Get up and running immediately with the new AI features
"""

import subprocess
import sys
import time

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}".ljust(70))
    print("=" * 70 + "\n")

def print_step(number, text):
    """Print step"""
    print(f"\n[Step {number}] {text}")
    print("-" * 70)

def main():
    print_header("🚀 AI SEARCH ENGINE - QUICK START GUIDE")
    
    print("""
This guide will get you started with your new AI-powered search engine
in just 5 minutes. Everything is already implemented - this just shows
you how to use it!

NEW FEATURES ADDED TODAY:
✨ AI Autocorrection (Fuzzy + Semantic)
✨ Smart Suggestions (Frequency-based)
✨ Query Analysis (Intent detection)
✨ Enhanced Search (Auto-correction)
""")
    
    print_step(1, "Install Required Libraries (2 minutes)")
    print("""
Install the ML libraries needed for AI features:

    pip install thefuzz python-Levenshtein nltk textblob
    
Or run:
    pip install -r Backend/requirements.txt
    
(If requirements.txt doesn't have them, install them manually above)
""")
    
    input("Press Enter after installing libraries...")
    
    print_step(2, "Start the Flask Server (1 minute)")
    print("""
Open a terminal and run:

    cd Backend
    python app.py
    
The server should start on: http://localhost:5000

Keep this terminal open! Open a NEW terminal for the next steps.
""")
    
    input("Press Enter when Flask server is running...")
    
    print_step(3, "Test the AI Autocorrection")
    print("""
In a new terminal, test spell correction:

TYPO TEST:
    curl "http://localhost:5000/api/autocorrect?q=machne"
    
EXPECTED OUTPUT:
    - Shows corrections with scores
    - "machine" should be the top suggestion
    - Confidence score ~0.95
    
Try it now or copy the URL into your browser!
""")
    
    response = input("\nDid it work? (y/n): ").lower()
    if response == 'y':
        print("✅ Autocorrection working!\n")
    
    print_step(4, "Test Smart Suggestions")
    print("""
Test intelligent suggestions:

SUGGESTION TEST:
    curl "http://localhost:5000/api/smart-suggest?q=neur&limit=5"
    
EXPECTED OUTPUT:
    - "neural", "network", "neurons", "neuron"
    - Each with frequency scores
    - Trending terms shown
    
You can also test in browser:
    http://localhost:5000/api/smart-suggest?q=neur&limit=5
""")
    
    print_step(5, "Test Query Analysis")
    print("""
Test intent detection:

ANALYSIS TEST:
    curl "http://localhost:5000/api/query-analysis?q=compare+tensorflow+vs+pytorch"
    
EXPECTED OUTPUT:
    - Intent: "compare"
    - Complexity: "advanced"
    - Tokens extracted correctly
""")
    
    print_step(6, "Try Enhanced Search")
    print("""
Test complete smart search (with auto-correction):

SEARCH TEST:
    curl "http://localhost:5000/api/enhanced-search?q=machne+lerning&correct=true"
    
EXPECTED OUTPUT:
    - Original query shown
    - Corrected query shown
    - Results with corrections applied
""")
    
    print_header("✅ QUICK START COMPLETE!")
    
    print("""
NEXT STEPS:

1. Read the Documentation:
   - Start: FINAL_SUMMARY.md
   - For AI: AI_AUTOCORRECT_SUMMARY.md
   - For Details: AI_SUGGESTIONS_GUIDE.md

2. Integrate with Your Frontend:
   - See: AI_SUGGESTIONS_GUIDE.md (JavaScript section)
   - Copy code examples for your UI
   - Add suggestion dropdown to search

3. Test Incremental Indexing (Optional):
   - Run: python example_incremental.py
   - Or: python test_incremental_indexing.py

4. Check All Features:
   - See: FEATURE_CHECKLIST.md
   - Project status: PROJECT_AUDIT_AND_RECOMMENDATIONS.md

AVAILABLE ENDPOINTS:

AI FEATURES (NEW):
  GET  /api/autocorrect         - Spell correction
  GET  /api/smart-suggest       - Smart suggestions
  GET  /api/query-analysis      - Intent detection
  GET  /api/enhanced-search     - Smart search with correction

SEARCH:
  GET  /api/search              - Basic search
  GET  /api/suggest             - Prefix suggestions
  GET  /api/autocomplete        - Autocomplete

DOCUMENT MANAGEMENT:
  POST /api/add-document        - Add single document
  POST /api/add-documents       - Batch add documents
  GET  /api/status              - Check indexing status

USEFUL URLS:

Home:
  http://localhost:5000/

Test Autocorrect:
  http://localhost:5000/api/autocorrect?q=machne

Test Suggestions:
  http://localhost:5000/api/smart-suggest?q=neur

Test Analysis:
  http://localhost:5000/api/query-analysis?q=compare+models

Test Search:
  http://localhost:5000/api/search?q=machine+learning

DOCUMENTATION FILES:

Quick Reference:
  - FINAL_SUMMARY.md
  - AI_AUTOCORRECT_SUMMARY.md
  - INCREMENTAL_QUICK_REFERENCE.md

Complete Guides:
  - AI_SUGGESTIONS_GUIDE.md
  - INCREMENTAL_INDEXING_GUIDE.md
  - PROJECT_AUDIT_AND_RECOMMENDATIONS.md

Status & Checklists:
  - FEATURE_CHECKLIST.md
  - VERIFICATION_CHECKLIST.py
  - DOCUMENTATION_INDEX.md

PYTHON USAGE (In Your Code):

# Autocorrect
import requests
resp = requests.get('http://localhost:5000/api/autocorrect?q=machne')
print(resp.json()['corrections'])

# Suggestions
resp = requests.get('http://localhost:5000/api/smart-suggest?q=neur')
print([s['word'] for s in resp.json()['suggestions']])

# Enhanced Search
resp = requests.get('http://localhost:5000/api/enhanced-search?q=machne&correct=true')
results = resp.json()['results']
print(f"Found {len(results)} results")

JAVASCRIPT USAGE (In Your Frontend):

// Autocorrect
fetch('/api/autocorrect?q=machne')
  .then(r => r.json())
  .then(data => console.log(data.corrections))

// Suggestions
fetch('/api/smart-suggest?q=neur')
  .then(r => r.json())
  .then(data => displaySuggestions(data.suggestions))

// Enhanced Search
fetch('/api/enhanced-search?q=machne&correct=true')
  .then(r => r.json())
  .then(data => displayResults(data.results))

TROUBLESHOOTING:

"AI corrector not initialized"
  → Install missing libraries:
    pip install thefuzz python-Levenshtein nltk

"No suggestions returned"
  → Make sure you have indexed documents
  → Run: curl http://localhost:5000/api/status
  → Check lexicon size is > 1000

"Server won't start"
  → Port 5000 in use? Change in app.py
  → Check Python version (need 3.7+)
  → Check all dependencies installed

For more help, see:
  - Troubleshooting sections in guide files
  - PROJECT_AUDIT_AND_RECOMMENDATIONS.md
  - Source code comments in Backend/ai_suggestion_engine.py

YOU'RE READY! 🚀

Your AI-powered search engine is now live and ready to use!

Questions? Check the documentation files - everything is covered!

Happy searching! 🔍
""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
