#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE TEST SUITE FOR AI FEATURES
Tests all new AI endpoints and functionality
"""

import requests
import json
import sys
from typing import Dict, List, Any
from datetime import datetime

BASE_URL = "http://localhost:5000"
COLORS = {
    'HEADER': '\033[95m',
    'GREEN': '\033[92m',
    'RED': '\033[91m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'END': '\033[0m'
}

class TestRunner:
    """Run comprehensive tests on AI endpoints"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{COLORS['HEADER']}{'=' * 70}")
        print(f"  {text}")
        print(f"{'=' * 70}{COLORS['END']}\n")
    
    def print_test(self, name: str, status: bool, details: str = ""):
        """Print test result"""
        if status:
            print(f"{COLORS['GREEN']}✅ PASS{COLORS['END']}: {name}")
            self.passed += 1
        else:
            print(f"{COLORS['RED']}❌ FAIL{COLORS['END']}: {name}")
            if details:
                print(f"   {details}")
            self.failed += 1
            
    def run_test(self, endpoint: str, params: Dict, expected_keys: List[str]) -> bool:
        """Run single endpoint test"""
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code != 200:
                return False, f"Status: {response.status_code}"
            
            data = response.json()
            
            # Check all expected keys exist
            missing = [k for k in expected_keys if k not in data]
            if missing:
                return False, f"Missing keys: {missing}"
            
            return True, data
            
        except Exception as e:
            return False, str(e)
    
    def test_autocorrect(self):
        """Test autocorrection endpoint"""
        self.print_header("🔤 AUTOCORRECTION TESTS")
        
        test_cases = [
            {
                'query': 'machne',
                'name': 'Basic typo (machine)',
                'expect_word': 'machine'
            },
            {
                'query': 'learnning',
                'name': 'Double letter typo (learning)',
                'expect_word': 'learning'
            },
            {
                'query': 'algoritm',
                'name': 'Missing letter (algorithm)',
                'expect_word': 'algorithm'
            },
            {
                'query': 'dtabase',
                'name': 'Transposed letters (database)',
                'expect_word': 'database'
            }
        ]
        
        for test in test_cases:
            success, data = self.run_test(
                '/api/autocorrect',
                {'q': test['query']},
                ['corrections', 'original_word']
            )
            
            if success and isinstance(data, dict):
                corrections = data.get('corrections', [])
                found = any(c.get('word') == test['expect_word'] for c in corrections)
                self.print_test(
                    test['name'],
                    found,
                    f"Got: {corrections[0]['word'] if corrections else 'None'}"
                )
            else:
                self.print_test(test['name'], False, str(data))
    
    def test_suggestions(self):
        """Test smart suggestions endpoint"""
        self.print_header("💡 SMART SUGGESTIONS TESTS")
        
        test_cases = [
            {
                'query': 'neur',
                'name': 'Neural network prefix',
                'expect_words': ['neural', 'network', 'neurons']
            },
            {
                'query': 'algo',
                'name': 'Algorithm prefix',
                'expect_words': ['algorithm', 'algorithms']
            },
            {
                'query': 'data',
                'name': 'Data structures prefix',
                'expect_words': ['database', 'data']
            }
        ]
        
        for test in test_cases:
            success, data = self.run_test(
                '/api/smart-suggest',
                {'q': test['query'], 'limit': 10},
                ['suggestions', 'query']
            )
            
            if success and isinstance(data, dict):
                suggestions = data.get('suggestions', [])
                found_words = [s.get('word') for s in suggestions]
                has_expected = any(w in found_words for w in test['expect_words'])
                
                self.print_test(
                    test['name'],
                    has_expected,
                    f"Got: {found_words[:3]}"
                )
            else:
                self.print_test(test['name'], False, str(data))
    
    def test_query_analysis(self):
        """Test query analysis endpoint"""
        self.print_header("🔬 QUERY ANALYSIS TESTS")
        
        test_cases = [
            {
                'query': 'machine learning tutorials',
                'name': 'Simple search query',
                'expect_intent': 'search'
            },
            {
                'query': 'compare tensorflow vs pytorch',
                'name': 'Comparison query',
                'expect_intent': 'compare'
            },
            {
                'query': 'author:andrew ng topic:deep learning',
                'name': 'Filter query with author',
                'expect_intent': 'filter'
            }
        ]
        
        for test in test_cases:
            success, data = self.run_test(
                '/api/query-analysis',
                {'q': test['query']},
                ['intent', 'complexity', 'tokens', 'query']
            )
            
            if success and isinstance(data, dict):
                intent = data.get('intent', '')
                self.print_test(
                    test['name'],
                    intent == test['expect_intent'],
                    f"Got intent: {intent}"
                )
            else:
                self.print_test(test['name'], False, str(data))
    
    def test_enhanced_search(self):
        """Test enhanced search endpoint"""
        self.print_header("🔍 ENHANCED SEARCH TESTS")
        
        test_cases = [
            {
                'query': 'machne learnng',
                'name': 'Search with corrections',
                'should_correct': True
            },
            {
                'query': 'machine learning',
                'name': 'Correct query search',
                'should_correct': False
            }
        ]
        
        for test in test_cases:
            success, data = self.run_test(
                '/api/enhanced-search',
                {'q': test['query'], 'correct': 'true'},
                ['results', 'query', 'corrected_query', 'correction_applied']
            )
            
            if success and isinstance(data, dict):
                correction_applied = data.get('correction_applied', False)
                self.print_test(
                    test['name'],
                    isinstance(data.get('results'), list),
                    f"Correction applied: {correction_applied}"
                )
            else:
                self.print_test(test['name'], False, str(data))
    
    def test_basic_search(self):
        """Test basic search (existing functionality)"""
        self.print_header("🔎 BASIC SEARCH TESTS (Existing)")
        
        success, data = self.run_test(
            '/api/search',
            {'q': 'machine learning'},
            ['results', 'query', 'count']
        )
        
        if success:
            count = data.get('count', 0)
            self.print_test(
                'Basic search endpoint',
                count >= 0,
                f"Found {count} results"
            )
        else:
            self.print_test('Basic search endpoint', False, str(data))
    
    def test_autocomplete(self):
        """Test autocomplete endpoint"""
        self.print_header("📝 AUTOCOMPLETE TESTS (Existing)")
        
        success, data = self.run_test(
            '/api/suggest',
            {'q': 'mach'},
            ['suggestions', 'query']
        )
        
        if success:
            suggestions = data.get('suggestions', [])
            self.print_test(
                'Autocomplete endpoint',
                isinstance(suggestions, list),
                f"Found {len(suggestions)} suggestions"
            )
        else:
            self.print_test('Autocomplete endpoint', False, str(data))
    
    def test_status(self):
        """Test status endpoint"""
        self.print_header("📊 STATUS TESTS")
        
        success, data = self.run_test(
            '/api/status',
            {},
            ['indexed_documents', 'lexicon_size', 'index_type']
        )
        
        if success:
            doc_count = data.get('indexed_documents', 0)
            lex_size = data.get('lexicon_size', 0)
            self.print_test(
                'Status endpoint',
                doc_count > 0 and lex_size > 0,
                f"{doc_count} docs, {lex_size} terms"
            )
        else:
            self.print_test('Status endpoint', False, str(data))
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("📈 TEST SUMMARY")
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{COLORS['GREEN']}✅ Passed: {self.passed}{COLORS['END']}")
        print(f"{COLORS['RED']}❌ Failed: {self.failed}{COLORS['END']}")
        print(f"{COLORS['BLUE']}📊 Total:  {total}{COLORS['END']}")
        print(f"{COLORS['YELLOW']}📈 Success Rate: {percentage:.1f}%{COLORS['END']}")
        
        if self.failed == 0:
            print(f"\n{COLORS['GREEN']}🎉 ALL TESTS PASSED! 🎉{COLORS['END']}")
            return 0
        else:
            print(f"\n{COLORS['RED']}⚠️  {self.failed} test(s) failed{COLORS['END']}")
            return 1
    
    def run_all(self):
        """Run all tests"""
        print(f"\n{COLORS['HEADER']}")
        print("=" * 70)
        print("  🧪 AI SEARCH ENGINE - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"{COLORS['END']}")
        print(f"Testing: {BASE_URL}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Check if server is running
        try:
            requests.get(f"{BASE_URL}/", timeout=2)
        except:
            print(f"{COLORS['RED']}❌ ERROR: Server not running at {BASE_URL}{COLORS['END']}")
            print(f"   Start Flask server: cd Backend && python app.py")
            return 1
        
        print(f"{COLORS['GREEN']}✅ Server is running!{COLORS['END']}\n")
        
        # Run test suites
        self.test_autocorrect()
        self.test_suggestions()
        self.test_query_analysis()
        self.test_enhanced_search()
        self.test_basic_search()
        self.test_autocomplete()
        self.test_status()
        
        return self.print_summary()

if __name__ == "__main__":
    runner = TestRunner()
    sys.exit(runner.run_all())
