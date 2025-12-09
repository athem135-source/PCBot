"""
PDBOT Answer Validation Harness
================================
Tests /chat endpoint against expected outputs from approval_limits.json.

Run: python tests/validate_answers.py
Requires: API running on localhost:5000
"""

import json
import os
import requests
import sys
from typing import Dict, List, Tuple

# Load limits from JSON (single source of truth)
LIMITS_FILE = os.path.join(os.path.dirname(__file__), '..', 'src', 'data', 'approval_limits.json')

def load_limits() -> Dict:
    with open(LIMITS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

LIMITS = load_limits()

# Test cases: (query, expected_substrings, must_not_contain)
TEST_CASES: List[Tuple[str, List[str], List[str]]] = [
    # Single forum limit queries
    ("What is the DDWP approval limit?", [LIMITS['DDWP']['limit_text']], ["CDWP", "ECNEC", "PDWP"]),
    ("What is PDWP limit?", [LIMITS['PDWP']['limit_text']], ["DDWP", "ECNEC"]),
    ("What is CDWP approval limit?", [LIMITS['CDWP']['limit_text']], ["DDWP", "PDWP"]),
    ("What is ECNEC limit?", [LIMITS['ECNEC']['limit_text']], ["DDWP", "PDWP"]),
    
    # Comparison queries (should include both values)
    ("What is the difference between CDWP and ECNEC?", 
     [LIMITS['CDWP']['limit_text'], LIMITS['ECNEC']['limit_text'], "CDWP", "ECNEC"], []),
    ("Difference between DDWP and CDWP",
     [LIMITS['DDWP']['limit_text'], LIMITS['CDWP']['limit_text']], []),
    
    # Full table queries
    ("What are all the approval limits?",
     ["DDWP", "PDWP", "CDWP", "ECNEC"], []),
    ("Show me project approval thresholds",
     ["DDWP", "PDWP", "CDWP", "ECNEC"], []),
    
    # PC form queries
    ("What is PC-I?", ["PC-I", "project"], []),
    ("What is PC-II used for?", ["PC-II", "feasibility"], []),
    ("What is PC-III?", ["PC-III", "progress"], []),
    ("What is PC-IV?", ["PC-IV", "completion"], []),
    ("Difference between PC forms", ["PC-I", "PC-II", "PC-III", "PC-IV"], []),
    
    # Definition queries
    ("What is PSDP?", ["PSDP", "Public Sector Development"], []),
    ("What is the Planning Commission?", ["Planning Commission"], []),
    
    # Greetings (should not trigger RAG)
    ("Hello", ["Assalam", "help"], []),
    ("Hi there", ["Assalam", "help"], []),
    
    # Off-scope (should be rejected)
    ("What is the weather today?", ["outside", "scope", "Manual"], []),
    ("Tell me a joke", ["outside", "scope", "Manual"], []),
    
    # Numeric queries
    ("How much can DDWP approve?", [LIMITS['DDWP']['limit_text']], []),
    ("What is the budget threshold for ECNEC?", [LIMITS['ECNEC']['limit_text']], []),
    
    # Project approval process
    ("What are the stages of project approval?", ["approval", "project"], []),
    ("How is a project approved?", ["approval", "project"], []),
    
    # Monitoring
    ("How is project progress monitored?", ["monitoring", "progress"], []),
    ("What is M&E?", ["monitoring", "evaluation"], []),
    
    # Additional coverage
    ("What documents are needed for PC-I?", ["PC-I", "document"], []),
    ("Who chairs ECNEC?", ["Prime Minister", "Finance"], []),
    ("Who chairs CDWP?", ["Deputy Chairman", "Planning"], []),
    ("What is ADP?", ["Annual Development", "Programme"], []),
    ("What is block allocation?", ["block", "allocation"], []),
    ("What is project revision?", ["revision", "project"], []),
    ("What is cost overrun?", ["cost", "overrun"], []),
    ("What is the project cycle?", ["cycle", "project"], []),
    ("What is contingency in projects?", ["contingency"], []),
    ("What is throwforward?", ["throw", "forward"], []),
    ("What is new approval?", ["new", "approval"], []),
    ("What is ongoing project?", ["ongoing", "project"], []),
    ("What is unapproved project?", ["unapproved"], []),
    ("What is foreign aid project?", ["foreign", "aid"], []),
    ("What is self-financing scheme?", ["self-financing", "scheme"], []),
    ("What is PPP project?", ["PPP", "Public Private"], []),
    ("How are provinces allocated funds?", ["province", "allocation"], []),
    ("What is sectoral allocation?", ["sector", "allocation"], []),
    ("What is federal project?", ["federal", "project"], []),
    ("What is provincial project?", ["provincial", "project"], []),
    ("What is district level project?", ["district", "project"], []),
    ("What is mega project?", ["mega", "project"], []),
]

API_URL = "http://localhost:5000/chat"

def test_query(query: str, expected: List[str], must_not: List[str]) -> Tuple[bool, str]:
    """Test a single query against expected substrings."""
    try:
        resp = requests.post(API_URL, json={"query": query, "session_id": "test"}, timeout=30)
        if resp.status_code != 200:
            return False, f"HTTP {resp.status_code}"
        
        data = resp.json()
        answer = data.get('answer', '').lower()
        
        # Check expected substrings
        for exp in expected:
            if exp.lower() not in answer:
                return False, f"Missing: '{exp}'"
        
        # Check must_not_contain (for single-forum queries)
        for bad in must_not:
            if bad.lower() in answer:
                return False, f"Unexpected: '{bad}'"
        
        return True, "OK"
    except requests.exceptions.ConnectionError:
        return False, "API not running"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("PDBOT Answer Validation Harness")
    print("=" * 60)
    print(f"Testing {len(TEST_CASES)} queries against {API_URL}")
    print()
    
    passed = 0
    failed = 0
    errors = []
    
    for i, (query, expected, must_not) in enumerate(TEST_CASES, 1):
        ok, msg = test_query(query, expected, must_not)
        status = "✓" if ok else "✗"
        print(f"[{i:02d}] {status} {query[:50]:<50} {msg}")
        
        if ok:
            passed += 1
        else:
            failed += 1
            errors.append((query, msg))
    
    print()
    print("=" * 60)
    print(f"Results: {passed}/{len(TEST_CASES)} passed ({100*passed/len(TEST_CASES):.1f}%)")
    print("=" * 60)
    
    if errors:
        print("\nFailed queries:")
        for q, e in errors:
            print(f"  - {q}: {e}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
