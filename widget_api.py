"""
PDBOT Widget API Server v3.3.4
==============================

A lightweight Flask API that bridges the React widget to the PDBOT RAG pipeline.
Optimized RAG: precision chunking, 100-word answers, dynamic value retrieval.

Features:
  - Contextual memory (session-based chat history)
  - RAG-powered responses from Manual for Development Projects 2024
  - Multi-class query classification (greeting, ambiguous, off-scope, red-line, abusive)
  - Suggested follow-up questions (ChatGPT-style)
  - Clarification prompts for vague queries
  - Source and passage tracking
  - Feedback collection
  - Admin status endpoint with Groq controls
  - Statistics dashboard endpoint
  - Production WSGI server (waitress)
  - Localtunnel for mobile access

Endpoints:
  POST /chat - Send a query and get a response
  POST /feedback/answer - Submit answer feedback
  POST /feedback/session - Submit session feedback
  POST /memory/clear - Clear session memory
  GET  /health - Health check
  GET  /admin/status - Backend status for admin panel
  GET  /admin/statistics - Detailed usage statistics
  GET  /admin/groq-status - Groq API status
  POST /admin/groq-toggle - Toggle force Groq mode

@author M. Hassan Arif Afridi
@version 3.3.0
"""

import os
import sys
import json
import socket
from datetime import datetime
from typing import Dict, List
from flask import Flask, request, jsonify, session
from flask_cors import CORS

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Admin password for secure features
ADMIN_PASSWORD = 'nufc'

# Import PDBOT modules
from rag_langchain import search_sentences
from models.local_model import LocalModel
from utils.text_utils import find_exact_locations

# Import classifier and templates for off-scope/red-line detection
from core.multi_classifier import MultiClassifier
from core.templates import get_guardrail_response
from core.comparisons import get_comparison_response

# Groq API support (optional)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("[Widget API] Groq not installed - Groq mode disabled")

# PDF path for exact mode
PDF_PATH = os.path.join(os.path.dirname(__file__), 'data', 'uploads', 'Manual-for-Development-Project-2024.pdf')
RAW_PAGES_CACHE = None

def load_pdf_pages():
    """Load PDF pages for exact mode search."""
    global RAW_PAGES_CACHE
    if RAW_PAGES_CACHE is not None:
        return RAW_PAGES_CACHE
    
    pages = []
    try:
        import fitz  # PyMuPDF
        if os.path.exists(PDF_PATH):
            doc = fitz.open(PDF_PATH)
            for i in range(len(doc)):
                pages.append(doc.load_page(i).get_text("text") or "")
            doc.close()
            print(f"[Widget API] Loaded {len(pages)} PDF pages for exact mode")
    except Exception as e:
        print(f"[Widget API] Could not load PDF: {e}")
    
    RAW_PAGES_CACHE = pages
    return pages

app = Flask(__name__)
app.secret_key = 'pcbot-secure-key-2026-nufc'  # Required for sessions
CORS(app, supports_credentials=True)  # Enable CORS with credentials for sessions

# Ensure UTF-8 output to avoid UnicodeEncodeError on Windows consoles when printing emojis
try:
    # Available in Python 3.7+ to reconfigure text streams
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    # If reconfigure isn't available (older Python) or fails, set PYTHONUTF8 flag as a fallback
    os.environ.setdefault('PYTHONUTF8', '1')
    # If sys.stdout encoding cannot be changed, also wrap prints that may contain emoji later
    # (This fallback ensures the environment prefers UTF-8 where possible.)

# Serve mobile page at root for Cloudflare tunnel
@app.route('/')
def serve_landing():
    """Serve landing page with all options"""
    try:
        with open('public/html/landing.html', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        return jsonify({"error": "Landing page not found", "status": "ok", "api": "/chat"}), 200

@app.route('/mobile.html')
def serve_mobile():
    """Serve mobile-friendly chat page"""
    try:
        with open('public/html/mobile.html', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        return jsonify({"error": "Mobile page not found", "status": "ok", "api": "/chat"}), 200

# Serve the standalone widget page
@app.route('/widget-standalone.html')
def serve_widget_standalone():
    """Serve the standalone shareable widget page"""
    try:
        with open('public/html/widget-standalone.html', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        return jsonify({"error": "Widget standalone page not found"}), 404

# Serve the full Widget UI from the API server (password protected)
@app.route('/widget')
def serve_widget():
    """Serve the full React widget UI (dev mode - requires admin access)"""
    # Check if user is authenticated
    if not session.get('admin_authenticated'):
        # Return password protection page
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>PCBot Development Widget - Admin Access</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #1a472a 0%, #2d5f3f 100%);
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 400px;
        }
        h1 { color: #1a472a; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 30px; }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus { border-color: #1a472a; outline: none; }
        button {
            width: 100%;
            padding: 12px;
            background: #1a472a;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover { background: #2d5f3f; }
        .error { color: #d32f2f; margin-top: 10px; display: none; }
        .back-link { margin-top: 20px; }
        .back-link a { color: #1a472a; text-decoration: none; }
        .back-link a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🔒 Admin Access Required</h1>
        <p class="subtitle">PCBot Development Widget</p>
        <form id="loginForm">
            <input type="password" id="password" placeholder="Enter admin code" required>
            <button type="submit">Access Widget</button>
        </form>
        <p class="error" id="error">❌ Invalid code. Please try again.</p>
        <div class="back-link">
            <a href="/">← Back to Landing Page</a>
        </div>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const password = document.getElementById('password').value;
            
            const response = await fetch('/admin/authenticate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ password })
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.location.reload();
            } else {
                document.getElementById('error').style.display = 'block';
                document.getElementById('password').value = '';
            }
        });
    </script>
</body>
</html>
        ''', 200, {'Content-Type': 'text/html'}
    
    try:
        # Serve widget-dev.html which loads the built widget
        with open('public/html/widget-dev.html', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        return "Widget dev page not found. Make sure widget-dev.html exists.", 404

# Serve widget static assets (JS, CSS)
@app.route('/src/<path:filename>')
def serve_widget_src(filename):
    """Serve widget source files for dev mode"""
    from flask import send_from_directory
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'frontend-widget', 'src'), filename)

@app.route('/dist/<path:filename>')
def serve_widget_dist(filename):
    """Serve widget dist files"""
    from flask import send_from_directory
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'frontend-widget', 'dist'), filename)

@app.route('/assets/<path:filename>')
def serve_widget_assets(filename):
    """Serve widget assets (logos, images)"""
    from flask import send_from_directory
    # Try public/assets first, then fallback to frontend-widget assets
    public_assets = os.path.join(os.path.dirname(__file__), 'public', 'assets')
    if os.path.exists(os.path.join(public_assets, filename)):
        return send_from_directory(public_assets, filename)
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'frontend-widget', 'src', 'assets'), filename)

@app.route('/@<path:rest>')
def serve_vite_deps(rest):
    """Handle Vite dev dependencies"""
    return "Dev mode not supported via API", 404

# Initialize model and classifier
model = None
groq_client = None
classifier = None

# Session memory store (in-memory, per-session chat history)
# Format: { session_id: [ { "role": "user/bot", "content": "...", "timestamp": "..." }, ... ] }
session_memory: Dict[str, List[Dict]] = {}
# Map session_id -> username for admin reporting
session_users: Dict[str, str] = {}

# Maximum messages to keep in memory per session
MAX_MEMORY_MESSAGES = 20

def get_classifier():
    """Lazy load the classifier"""
    global classifier
    if classifier is None:
        classifier = MultiClassifier()
    return classifier

def get_model():
    """Lazy load the model"""
    global model
    if model is None:
        model = LocalModel()
    return model

def get_groq_client():
    """Lazy load Groq client"""
    global groq_client
    if groq_client is None and GROQ_AVAILABLE:
        api_key = os.environ.get('GROQ_API_KEY')
        if api_key:
            groq_client = Groq(api_key=api_key)
        else:
            print("[Widget API] Warning: GROQ_API_KEY not set")
    return groq_client

def generate_groq_response(query: str, context: str, page: int = 0) -> str:
    """
    v3.3.0: Generate response using Groq API with strict formatting.
    Same guardrails as local model - 45-70 words, direct answer first.
    """
    client = get_groq_client()
    if not client:
        return "⚠️ Groq API not available. Please set GROQ_API_KEY environment variable."
    
    try:
        # v3.3.0: Strict system prompt matching local model
        system_prompt = """You are PCBot, the official Planning Commission assistant for the Manual for Development Projects 2024.
Your answers must ALWAYS follow these rules:

1. Length: 45-70 words maximum.
2. Use ONLY the retrieved context. No outside knowledge.
3. Give the direct answer FIRST, no background theory.
4. No warnings, no disclaimers, no template markers.
5. If numbers exist in the context, extract them completely.
6. If answer truly not found, say: "Not found in the Manual."

Always end with one line:
Source: Manual for Development Projects 2024, p.<page>"""

        # v3.3.0: Strict user prompt
        user_prompt = f"""Context from the Manual:
{context[:2500]}

Question: {query}

Answer in 45-70 words. Extract numbers if present. Direct answer first:"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,  # Reduced from 500 to prevent over-explanation
            temperature=0.2   # Lower temp for more focused answers
        )
        
        answer = response.choices[0].message.content or ""
        
        # v3.3.2: Apply sanitization - allow up to 100 words for complete answers
        import re
        
        # Remove existing citations (we'll add clean one)
        answer = re.sub(r"\n*Source:.*$", "", answer, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove filler phrases
        fillers = [
            r"^(?:According to the (?:provided )?(?:context|manual|text),?\s*)",
            r"^(?:Based on the (?:provided )?(?:context|manual|text),?\s*)",
        ]
        for filler in fillers:
            answer = re.sub(filler, "", answer, flags=re.IGNORECASE)
        
        # v4.0.0/v4.0.2: Restore strict length target (45-70 words) while preventing currency/number cutoffs.
        words = answer.split()
        WORD_LIMIT = 70  # enforce upper bound 45-70 words; use 70 as truncation cutoff
        if len(words) > WORD_LIMIT:
            truncated = " ".join(words[:WORD_LIMIT])
            # Prefer to end at the last sentence boundary (., !, ?) within truncated text
            last_punct = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
            if last_punct != -1 and last_punct > int(len(truncated) * 0.4):
                answer = truncated[:last_punct+1]
            else:
                answer = truncated
            # Avoid leaving trailing isolated currency markers like 'Rs.' or 'Rs'
            currency_markers = ('Rs.', 'Rs', 'Rupees', 'rupees', 'Rs,', 'Rs;', '₹', 'PKR')
            if answer.rstrip().endswith(currency_markers):
                # Append following words until a numeric token is included (or up to 5 words)
                remaining_words = words[WORD_LIMIT:WORD_LIMIT+5]
                appended = []
                for w in remaining_words:
                    appended.append(w)
                    if re.search(r'\d', w):
                        break
                if appended:
                    answer = answer + " " + " ".join(appended)
            # Ensure sentence termination
            if not answer.rstrip().endswith(('.', '!', '?')):
                answer = answer.rstrip(".!?,;") + "."

        answer = answer.strip()
        
        # Add clean citation
        doc_name = "Manual for Development Projects 2024"
        if page and page > 0:
            answer += f"\n\nSource: {doc_name}, p.{page}"
        else:
            answer += f"\n\nSource: {doc_name}"
        
        return answer
        
    except Exception as e:
        print(f"[Groq API] Error: {e}")
        return f"⚠️ Groq API error: {str(e)}"

def get_session_history(session_id: str) -> List[Dict]:
    """Get chat history for a session"""
    if session_id not in session_memory:
        session_memory[session_id] = []
    return session_memory[session_id]

def add_to_session_history(session_id: str, role: str, content: str):
    """Add a message to session history"""
    history = get_session_history(session_id)
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    # Keep only last N messages to prevent memory overflow
    if len(history) > MAX_MEMORY_MESSAGES:
        session_memory[session_id] = history[-MAX_MEMORY_MESSAGES:]

def build_context_with_memory(session_id: str, current_query: str) -> str:
    """Build context string including recent chat history for contextual understanding"""
    history = get_session_history(session_id)
    
    if not history:
        return ""
    
    # Get last 3 exchanges (6 messages) for context
    recent = history[-6:]
    
    context_parts = []
    for msg in recent:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        context_parts.append(f"{role_label}: {msg['content'][:200]}")
    
    return "Previous conversation:\n" + "\n".join(context_parts)

def clear_session_memory(session_id: str):
    """Clear memory for a session"""
    if session_id in session_memory:
        del session_memory[session_id]


# =====================================================
# SUGGESTED FOLLOW-UP QUESTIONS (ChatGPT-style)
# =====================================================

# v2.5.0-patch1: Comprehensive topic-based question suggestions
FOLLOW_UP_QUESTIONS = {
    "greeting": [
        "What is PC-I?",
        "What are the DDWP approval limits?",
        "How does project approval work?",
        "What is ECNEC?",
    ],
    "ambiguous": [
        "What is the purpose of PC-I?",
        "What is the approval hierarchy for projects?",
        "What are the different project phases?",
        "How is project cost estimated?",
    ],
    # PC-I related
    "pc-i": [
        "What are the components of PC-I?",
        "How to prepare a PC-I document?",
        "What is the approval process for PC-I?",
        "What attachments are required for PC-I?",
        "What is the difference between PC-I and PC-II?",
    ],
    # PC-II related  
    "pc-ii": [
        "When is PC-II required?",
        "What is the purpose of feasibility studies in PC-II?",
        "What cost limits apply to PC-II?",
        "How to submit PC-II for approval?",
    ],
    # PC-III related
    "pc-iii": [
        "What is PC-III used for?",
        "How often should PC-III be submitted?",
        "What information is included in PC-III?",
        "Who reviews PC-III reports?",
    ],
    # PC-IV related
    "pc-iv": [
        "What is PC-IV?",
        "When is PC-IV prepared?",
        "What is project completion report?",
        "What metrics are in PC-IV?",
    ],
    # PC-V related
    "pc-v": [
        "What is PC-V evaluation?",
        "When is PC-V conducted?",
        "What is post-completion evaluation?",
        "How is project impact measured?",
    ],
    # Approval bodies
    "ddwp": [
        "What is the DDWP approval limit?",
        "Who chairs the DDWP meeting?",
        "What projects go to DDWP?",
        "How is DDWP different from CDWP?",
    ],
    "cdwp": [
        "What is the CDWP approval threshold?",
        "Who are the members of CDWP?",
        "What projects require CDWP approval?",
        "How to submit projects to CDWP?",
    ],
    "ecnec": [
        "What is the ECNEC approval limit?",
        "Who chairs ECNEC meetings?",
        "What projects go to ECNEC?",
        "What is the ECNEC approval process?",
    ],
    # Numeric/financial queries
    "numeric_query": [
        "What are the threshold limits for CDWP?",
        "What is the ECNEC approval limit?",
        "What is the maximum DDWP approval limit?",
        "How is project cost calculated?",
    ],
    # Definition queries
    "definition_query": [
        "What are the types of PC proformas?",
        "What is the difference between PC-I and PC-II?",
        "What is PSDP?",
        "How is a project defined in the Manual?",
    ],
    # Comparison queries
    "comparison_query": [
        "What is the difference between DDWP and CDWP?",
        "How does PC-I differ from PC-II?",
        "What is the difference between federal and provincial projects?",
        "How is ADP different from PSDP?",
    ],
    # Procedure queries
    "procedure_query": [
        "What are the stages of project approval?",
        "What documents are required for PC-I?",
        "How does project revision work?",
        "What is the project cycle?",
    ],
    # Compliance queries
    "compliance_query": [
        "What are the audit requirements?",
        "How is project transparency ensured?",
        "What records must be maintained?",
        "What are the PC-I format requirements?",
    ],
    # Monitoring queries
    "monitoring_evaluation": [
        "What are the project monitoring KPIs?",
        "How is project progress tracked?",
        "What is the role of M&E Division?",
        "How often are projects reviewed?",
    ],
    # Budget/PSDP
    "budget": [
        "What is PSDP?",
        "How are funds allocated to projects?",
        "What is the budget release process?",
        "How is project cost overrun handled?",
    ],
    # General
    "general": [
        "What is the role of Planning Commission?",
        "What is PSDP?",
        "How are federal projects approved?",
        "What is project monitoring?",
        "What is the project approval hierarchy?",
    ],
}


def get_suggested_questions(query_class: str, query: str = "") -> List[str]:
    """
    Generate suggested follow-up questions based on query type.
    
    Args:
        query_class: Classification result
        query: Original query for context
        
    Returns:
        List of 3 suggested questions
    """
    import random
    
    # Check if query mentions specific topics
    q_lower = query.lower()
    pool = []
    
    # v2.5.0-patch1: Better topic detection
    if "pc-i" in q_lower or "pc1" in q_lower or "pc 1" in q_lower:
        pool = FOLLOW_UP_QUESTIONS.get("pc-i", [])
    elif "pc-ii" in q_lower or "pc2" in q_lower or "pc 2" in q_lower:
        pool = FOLLOW_UP_QUESTIONS.get("pc-ii", [])
    elif "pc-iii" in q_lower or "pc3" in q_lower or "pc 3" in q_lower:
        pool = FOLLOW_UP_QUESTIONS.get("pc-iii", [])
    elif "pc-iv" in q_lower or "pc4" in q_lower or "pc 4" in q_lower:
        pool = FOLLOW_UP_QUESTIONS.get("pc-iv", [])
    elif "pc-v" in q_lower or "pc5" in q_lower or "pc 5" in q_lower:
        pool = FOLLOW_UP_QUESTIONS.get("pc-v", [])
    elif "ddwp" in q_lower:
        pool = FOLLOW_UP_QUESTIONS.get("ddwp", [])
    elif "cdwp" in q_lower:
        pool = FOLLOW_UP_QUESTIONS.get("cdwp", [])
    elif "ecnec" in q_lower or "nec" in q_lower:
        pool = FOLLOW_UP_QUESTIONS.get("ecnec", [])
    elif "psdp" in q_lower or "budget" in q_lower or "fund" in q_lower:
        pool = FOLLOW_UP_QUESTIONS.get("budget", [])
    elif "monitor" in q_lower or "evaluation" in q_lower or "m&e" in q_lower:
        pool = FOLLOW_UP_QUESTIONS.get("monitoring_evaluation", [])
    elif "differ" in q_lower or "compare" in q_lower or "vs" in q_lower:
        pool = FOLLOW_UP_QUESTIONS.get("comparison_query", [])
    elif query_class in FOLLOW_UP_QUESTIONS:
        pool = FOLLOW_UP_QUESTIONS[query_class]
    else:
        pool = FOLLOW_UP_QUESTIONS.get("general", [])
    
    # Add some variety by mixing with general questions
    general = FOLLOW_UP_QUESTIONS.get("general", [])
    combined = list(set(pool + general))
    
    # Return 3 random questions, avoiding the current query
    suggestions = [q for q in combined if q.lower() not in query.lower()]
    random.shuffle(suggestions)
    return suggestions[:3]


def generate_contextual_followups(query: str, answer: str, query_class: str) -> List[str]:
    """
    Generate contextual follow-up questions based on the answer.
    
    Args:
        query: Original user query
        answer: Bot's response
        query_class: Classification result
        
    Returns:
        List of 3 contextual follow-up questions
    """
    followups = []
    q_lower = query.lower()
    a_lower = answer.lower()
    
    # v2.5.0-patch1: Enhanced contextual suggestions
    # PC proformas
    if "pc-i" in a_lower and "pc-i" not in q_lower:
        followups.append("What are the mandatory sections of PC-I?")
    if "pc-ii" in a_lower and "pc-ii" not in q_lower:
        followups.append("When is PC-II required?")
    if "pc-iii" in a_lower and "pc-iii" not in q_lower:
        followups.append("What is PC-III used for?")
    if "pc-iv" in a_lower and "pc-iv" not in q_lower:
        followups.append("What is the purpose of PC-IV?")
    if "pc-v" in a_lower and "pc-v" not in q_lower:
        followups.append("When is PC-V evaluation conducted?")
    
    # Approval bodies
    if "ddwp" in a_lower and "ddwp" not in q_lower:
        followups.append("What is the DDWP approval threshold?")
    if "cdwp" in a_lower and "cdwp" not in q_lower:
        followups.append("What projects go to CDWP?")
    if "ecnec" in a_lower and "ecnec" not in q_lower:
        followups.append("What is the ECNEC approval limit?")
    
    # Financial/process topics
    if ("approval" in a_lower or "approved" in a_lower) and "approval" not in q_lower:
        followups.append("What is the project approval hierarchy?")
    if ("cost" in a_lower or "budget" in a_lower) and "cost" not in q_lower:
        followups.append("How is project cost estimated?")
    if "monitoring" in a_lower and "monitoring" not in q_lower:
        followups.append("What are the project monitoring KPIs?")
    if "psdp" in a_lower and "psdp" not in q_lower:
        followups.append("How are PSDP funds allocated?")
    if "revision" in a_lower and "revision" not in q_lower:
        followups.append("What is the project revision process?")
    
    # For comparison queries, suggest related comparisons
    if query_class in ["comparison_query", "numeric_query", "definition_query"]:
        if "ddwp" in q_lower or "cdwp" in q_lower:
            followups.append("What is the difference between CDWP and ECNEC?")
        if "pc-i" in q_lower or "pc-ii" in q_lower:
            followups.append("What are the different PC proformas?")
    
    # Fill remaining slots with topic-based suggestions
    if len(followups) < 3:
        additional = get_suggested_questions(query_class, query)
        for q in additional:
            if q not in followups:
                followups.append(q)
            if len(followups) >= 3:
                break
    
    return followups[:3]


# v2.5.0-patch1: Long answer handling
MAX_ANSWER_WORDS = 250  # If answer exceeds this, suggest manual reference

def handle_long_answer(answer: str, sources: List[Dict], query: str) -> str:
    """
    Check if answer is too long and add page reference suggestion.
    
    Args:
        answer: The generated answer
        sources: List of source dictionaries with page info
        query: Original user query
        
    Returns:
        Modified answer with page reference if too long
    """
    word_count = len(answer.split())
    
    if word_count > MAX_ANSWER_WORDS:
        # Get unique page numbers from sources
        pages = list(set(str(s.get('page', '?')) for s in sources if s.get('page')))
        pages_str = ", ".join(sorted(pages)) if pages else "the relevant sections"
        
        # Add a note about detailed information
        truncation_note = f"\n\n📖 **Note:** This is a summary. For detailed information, please refer to **pages {pages_str}** in the Manual for Development Projects 2024."
        answer += truncation_note
    
    return answer


@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat requests from the widget with contextual memory.
    
    Request:
        {
            "query": "What is PC-I?",
            "session_id": "uuid",
            "clear_memory": false,  // Optional: clear session memory
            "exact_mode": false,    // Optional: return raw passages
            "use_groq": false       // Optional: use Groq API
        }
    
    Response:
        {
            "answer": "...",
            "sources": [...],
            "passages": [...],
            "mode": "local|exact|groq"
        }
    """
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        # Prefer client-provided session_id, else use server-side session id, else create one
        session_id = data.get('session_id') or session.get('session_id')
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        clear_memory = data.get('clear_memory', False)
        exact_mode = data.get('exact_mode', False)
        use_groq = data.get('use_groq', False)
        
        # Handle memory clear request
        if clear_memory:
            clear_session_memory(session_id)
            return jsonify({
                'answer': 'Chat memory cleared.',
                'sources': [],
                'passages': []
            })
        
        if not query:
            return jsonify({
                'answer': 'Please enter a question.',
                'sources': [],
                'passages': []
            }), 400
        
        print(f"[Widget API] Query: {query[:50]}... (Session: {session_id[:8]}...)")
        
        # =====================================================
        # STEP 1: CLASSIFY QUERY (before RAG)
        # =====================================================
        query_classifier = get_classifier()
        classification = query_classifier.classify(query)
        query_class = classification.query_class
        
        print(f"[Widget API] Classification: {query_class}/{classification.subcategory}")
        
        # Handle guardrail classes (greeting, ambiguous, off-scope, red-line, abusive)
        if query_class in ["greeting", "ambiguous", "off_scope", "red_line", "abusive"]:
            guardrail_response = get_guardrail_response(query_class, classification.subcategory or "", query)
            add_to_session_history(session_id, "user", query)
            add_to_session_history(session_id, "bot", guardrail_response)
            
            return jsonify({
                'answer': guardrail_response,
                'sources': [],
                'passages': [],
                'mode': 'guardrail',
                'classification': query_class,
                'suggested_questions': get_suggested_questions(query_class) if query_class in ["greeting", "ambiguous"] else []
            })
        

        # =====================================================
        # STEP 2: CHECK FOR COMPARISON QUERY (use pre-built templates)
        # =====================================================
        if query_class in ["comparison_query", "numeric_query", "definition_query"]:
            comparison_response = get_comparison_response(query)
            if comparison_response:
                add_to_session_history(session_id, "user", query)
                add_to_session_history(session_id, "bot", comparison_response)
                followups = get_suggested_questions(query_class, query)
                return jsonify({
                    'answer': comparison_response,
                    'sources': [{'title': 'Manual for Development Projects 2024', 'page': 'Various', 'relevance': 100}],
                    'passages': [],
                    'mode': 'comparison_template',
                    'classification': query_class,
                    'suggested_questions': followups
                })
            # If no template match, fall through to RAG

        # Get conversation context from memory
        conversation_context = build_context_with_memory(session_id, query)
        
        # Add user message to memory
        add_to_session_history(session_id, "user", query)
        
        # Get RAG results
        rag_results = search_sentences(query, top_k=3)
        
        if not rag_results:
            no_result_answer = "I couldn't find relevant information in the manual for your question. Please try rephrasing or ask about Planning & Development topics."
            add_to_session_history(session_id, "bot", no_result_answer)
            return jsonify({
                'answer': no_result_answer,
                'sources': [],
                'passages': []
            })
        
        # Build context from RAG results
        context_parts = []
        sources = []
        passages = []  # Store full passage details
        for i, result in enumerate(rag_results[:3]):
            text = result.get('text', result.get('content', ''))
            page = result.get('page', result.get('metadata', {}).get('page', 'N/A'))
            score = result.get('score', result.get('relevance', 0))
            source = f"Manual for Development Projects 2024, p.{page}"
            
            context_parts.append(f"[{i+1}] {text}")
            sources.append({
                'title': 'Manual for Development Projects 2024',
                'page': page,
                'relevance': round(score * 100) if score else 0
            })
            passages.append({
                'text': text,
                'page': page,
                'relevance': round(score * 100) if score else 0
            })
        
        rag_context = "\n\n".join(context_parts)
        
        # EXACT MODE: Find exact locations like Streamlit version
        if exact_mode:
            pdf_pages = load_pdf_pages()
            exact_locations = find_exact_locations(query, pdf_pages, max_results=5)
            
            if exact_locations:
                exact_answer = "✅ **Answer:**\n\n"
                for loc in exact_locations[:3]:
                    page = loc.get('page', '?')
                    para = loc.get('paragraph', '?')
                    line = loc.get('line', '?')
                    sentence = loc.get('sentence', '')
                    exact_answer += f"**Pg {page}, Para {para}, Line {line}:** \"{sentence}\"\n\n"
                
                exact_answer += "📘 **Source:**\n"
                for loc in exact_locations[:3]:
                    exact_answer += f"Page {loc.get('page', '?')} – Paragraph {loc.get('paragraph', '?')} – Line {loc.get('line', '?')}\n"
                
                exact_sources = [{
                    'title': 'Manual for Development Projects 2024',
                    'page': loc.get('page', '?'),
                    'paragraph': loc.get('paragraph', '?'),
                    'line': loc.get('line', '?')
                } for loc in exact_locations[:3]]
                
                exact_passages = [{
                    'text': loc.get('sentence', ''),
                    'page': loc.get('page', '?'),
                    'paragraph': loc.get('paragraph', '?'),
                    'line': loc.get('line', '?')
                } for loc in exact_locations[:3]]
            else:
                exact_answer = "📖 **No exact match found. Here are related passages:**\n\n"
                for i, p in enumerate(passages, 1):
                    exact_answer += f"**[{i}] Page {p['page']}** (Relevance: {p['relevance']}%)\n"
                    exact_answer += f"{p['text']}\n\n"
                exact_sources = sources
                exact_passages = passages
            
            add_to_session_history(session_id, "bot", exact_answer)
            print(f"[Widget API] Exact Mode response")
            
            return jsonify({
                'answer': exact_answer,
                'sources': exact_sources,
                'passages': exact_passages,
                'mode': 'exact'
            })
        
        # Combine conversation context with RAG context for better understanding
        full_context = rag_context
        if conversation_context:
            full_context = f"{conversation_context}\n\n---\n\nRelevant information from Manual:\n{rag_context}"
        
        # Extract page from first source for citation
        first_page = sources[0].get('page', 0) if sources else 0
        
        # GROQ MODE: Use Groq API for responses
        # v3.3.0: Check global force Groq mode OR request-level use_groq
        if use_groq or FORCE_GROQ_MODE:
            answer = generate_groq_response(query, full_context, page=first_page)
            response_mode = 'groq'
        else:
            # Generate answer using local model
            # Use higher max_new_tokens to avoid truncation
            llm = get_model()
            answer = llm.generate_response(query, full_context, max_new_tokens=200, page=first_page)
            response_mode = 'local'
        
        # Clean up answer
        if answer:
            answer = answer.strip()
            # Remove any prefix like "Answer:" if present
            for prefix in ["Answer:", "✅ Answer:", "Response:"]:
                if answer.startswith(prefix):
                    answer = answer[len(prefix):].strip()
        
        final_answer = answer or "I couldn't generate a response. Please try again."
        
        # v2.5.0-patch1: Handle long answers by adding page reference
        final_answer = handle_long_answer(final_answer, sources, query)
        
        # Add bot response to memory
        add_to_session_history(session_id, "bot", final_answer)
        
        # Generate contextual follow-up questions
        suggested_questions = generate_contextual_followups(query, final_answer, query_class)
        
        print(f"[Widget API] Response generated ({len(final_answer)} chars, mode: {response_mode})")
        # Detailed logging for auditing: who asked, session id, classification, mode, answer snippet
        try:
            user_ip = request.remote_addr or 'unknown'
        except Exception:
            user_ip = 'unknown'
        print(f"[Widget API][AUDIT] Session:{session_id[:12]} UserIP:{user_ip} Class:{query_class}/{getattr(classification, 'subcategory', '')} Mode:{response_mode} AnswerLen:{len(final_answer)}")
        print(f"[Widget API][AUDIT] Answer snippet: {final_answer[:140].replace('\n',' ')}")
        
        return jsonify({
            'answer': final_answer,
            'sources': sources,
            'passages': passages,
            'mode': response_mode,
            'suggested_questions': suggested_questions
        })
        
    except Exception as e:
        print(f"[Widget API] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'answer': f'Sorry, an error occurred: {str(e)}',
            'sources': [],
            'passages': []
        }), 500


@app.route('/feedback/answer', methods=['POST'])
def answer_feedback():
    """
    Save feedback for a specific answer.
    
    Request:
        {
            "messageId": "...",
            "query": "...",
            "answer": "...",
            "type": "like" | "dislike",
            "reasonId": "...",
            "sessionId": "...",
            "timestamp": "..."
        }
    """
    try:
        data = request.get_json()
        
        # Create feedback directory if needed
        feedback_dir = os.path.join(os.path.dirname(__file__), 'feedback', 'widget_answers')
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Save feedback
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"answer_{timestamp}_{data.get('type', 'unknown')}.json"
        filepath = os.path.join(feedback_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[Widget API] Answer feedback saved: {filename}")
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[Widget API] Feedback error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/feedback/session', methods=['POST'])
def session_feedback():
    """
    Save session feedback (rating, review).
    
    Request:
        {
            "rating": 1-3,
            "username": "...",
            "review": "...",
            "sessionId": "...",
            "timestamp": "..."
        }
    """
    try:
        data = request.get_json()
        rating = data.get('rating', 0)
        
        # Create feedback directory based on rating
        feedback_dir = os.path.join(os.path.dirname(__file__), 'feedback', f'{rating}_star')
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Save feedback
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        username = data.get('username', 'Widget_User').replace(' ', '_')[:20]
        filename = f"{timestamp}_{username}.json"
        filepath = os.path.join(feedback_dir, filename)
        
        # Also save as txt for compatibility with existing feedback
        txt_content = f"""Session Feedback (Widget)
========================
Rating: {rating} star(s)
Username: {data.get('username', 'Anonymous')}
Review: {data.get('review', 'No review')}
Messages: {data.get('messageCount', 0)}
Session ID: {data.get('sessionId', 'unknown')}
Timestamp: {data.get('timestamp', timestamp)}
"""
        
        txt_filepath = filepath.replace('.json', '.txt')
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[Widget API] Session feedback saved: {filename}")
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[Widget API] Session feedback error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/memory/clear', methods=['POST'])
def clear_memory():
    """
    Clear chat memory for a session.
    
    Request:
        {
            "session_id": "uuid"
        }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'widget-session')
        clear_session_memory(session_id)
        print(f"[Widget API] Memory cleared for session: {session_id[:8]}...")
        return jsonify({'success': True, 'message': 'Chat memory cleared'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'PDBOT Widget API',
        'version': '2.5.0',
        'features': ['contextual_memory', 'rag_retrieval', 'feedback_collection', 'admin_panel', 'suggested_questions', 'greeting_detection']
    })


@app.route('/admin/status', methods=['GET'])
def admin_status():
    """
    Admin endpoint - returns detailed backend status.
    Only accessible with admin code verification on frontend.
    """
    try:
        # Get memory usage
        import psutil
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
    except:
        memory_mb = 0
    
    # Count active sessions
    active_sessions = len(session_memory)
    total_messages = sum(len(msgs) for msgs in session_memory.values())
    
    # Check Qdrant status
    qdrant_status = "unknown"
    try:
        from qdrant_client import QdrantClient
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6338")
        client = QdrantClient(url=qdrant_url, timeout=2)
        collections = client.get_collections()
        qdrant_status = "connected"
    except Exception as e:
        qdrant_status = f"error: {str(e)[:50]}"
    
    # Check Ollama status
    ollama_status = "unknown"
    try:
        import requests
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            ollama_status = "connected"
        else:
            ollama_status = "error"
    except:
        ollama_status = "not running"
    
    # v3.3.0: Check Groq status
    groq_status = "unknown"
    groq_api_key = os.environ.get('GROQ_API_KEY', '')
    if not groq_api_key:
        groq_status = "no_api_key"
    elif GROQ_AVAILABLE:
        try:
            import requests
            headers = {"Authorization": f"Bearer {groq_api_key}", "Content-Type": "application/json"}
            test_payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5}
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=test_payload, timeout=5)
            if resp.status_code == 200:
                groq_status = "connected"
            else:
                groq_status = f"error: {resp.status_code}"
        except Exception as e:
            groq_status = f"error: {str(e)[:30]}"
    else:
        groq_status = "library_not_installed"
    
    return jsonify({
        'status': 'ok',
        'version': '3.3.0',
        'uptime': datetime.now().isoformat(),
        'memory_mb': round(memory_mb, 2),
        'active_sessions': active_sessions,
        'total_messages_in_memory': total_messages,
        'max_memory_per_session': MAX_MEMORY_MESSAGES,
        'qdrant_status': qdrant_status,
        'ollama_status': ollama_status,
        'groq_status': groq_status,
        'groq_available': GROQ_AVAILABLE and bool(groq_api_key),
        'qdrant_url': os.getenv("QDRANT_URL", "http://localhost:6338"),
        'debug_mode': app.debug,
        'model_loaded': model is not None,
        'embedding_ready': True
    })


@app.route('/admin/statistics', methods=['GET'])
def admin_statistics():
    """
    Admin endpoint - returns comprehensive usage statistics.
    For dashboard monitoring.
    """
    try:
        import psutil
        import glob
        
        # System stats
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent()
        
        # Session stats
        active_sessions = len(session_memory)
        total_messages = sum(len(msgs) for msgs in session_memory.values())
        
        # Per-session breakdown
        session_details = []
        for sid, msgs in session_memory.items():
            username = session_users.get(sid, session.get('user_name', 'Anonymous'))
            session_details.append({
                'session_id': sid[:12] + '...',
                'username': username,
                'message_count': len(msgs),
                'last_activity': msgs[-1].get('timestamp', 'N/A') if msgs else 'N/A'
            })
        
        # Feedback stats (count files in feedback folders)
        feedback_dir = os.path.join(os.path.dirname(__file__), 'feedback')
        feedback_stats = {}
        for star in ['1_star', '2_star', '3_star', '4_star', '5_star']:
            star_dir = os.path.join(feedback_dir, star)
            if os.path.exists(star_dir):
                feedback_stats[star] = len(os.listdir(star_dir))
            else:
                feedback_stats[star] = 0
        
        # Log stats
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        log_count = len(glob.glob(os.path.join(log_dir, '*.log'))) if os.path.exists(log_dir) else 0
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'system': {
                'version': '2.5.0',
                'memory_mb': round(memory_mb, 2),
                'cpu_percent': round(cpu_percent, 2),
                'pid': os.getpid()
            },
            'sessions': {
                'active_count': active_sessions,
                'total_messages': total_messages,
                'max_per_session': MAX_MEMORY_MESSAGES,
                'details': session_details[:10]  # Top 10 sessions
            },
            'feedback': feedback_stats,
            'logs': {
                'log_files': log_count
            },
            'services': {
                'model_loaded': model is not None,
                'classifier_loaded': classifier is not None,
                'groq_available': GROQ_AVAILABLE
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    """
    Admin endpoint - returns comprehensive usage statistics.
    For dashboard monitoring.
    """
    try:
        import psutil
        import glob
        
        # System stats
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent()
        
        # Session stats
        active_sessions = len(session_memory)
        total_messages = sum(len(msgs) for msgs in session_memory.values())
        
        # Per-session breakdown
        session_details = []
        for sid, msgs in session_memory.items():
            session_details.append({
                'session_id': sid[:12] + '...',
                'message_count': len(msgs),
                'last_activity': msgs[-1].get('timestamp', 'N/A') if msgs else 'N/A'
            })
        
        # Feedback stats (count files in feedback folders)
        feedback_dir = os.path.join(os.path.dirname(__file__), 'feedback')
        feedback_stats = {}
        for star in ['1_star', '2_star', '3_star', '4_star', '5_star']:
            star_dir = os.path.join(feedback_dir, star)
            if os.path.exists(star_dir):
                feedback_stats[star] = len(os.listdir(star_dir))
            else:
                feedback_stats[star] = 0
        
        # Log stats
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        log_count = len(glob.glob(os.path.join(log_dir, '*.log'))) if os.path.exists(log_dir) else 0
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'system': {
                'version': '2.5.0',
                'memory_mb': round(memory_mb, 2),
                'cpu_percent': round(cpu_percent, 2),
                'pid': os.getpid()
            },
            'sessions': {
                'active_count': active_sessions,
                'total_messages': total_messages,
                'max_per_session': MAX_MEMORY_MESSAGES,
                'details': session_details[:10]  # Top 10 sessions
            },
            'feedback': feedback_stats,
            'logs': {
                'log_files': log_count
            },
            'services': {
                'model_loaded': model is not None,
                'classifier_loaded': classifier is not None,
                'groq_available': GROQ_AVAILABLE
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/clear-all-memory', methods=['POST'])
def admin_clear_all_memory():
    """Admin endpoint to clear all session memory"""
    try:
        count = len(session_memory)
        session_memory.clear()
        return jsonify({
            'success': True,
            'message': f'Cleared {count} sessions from memory'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# v3.3.0: Groq force-enable state (runtime toggle)
FORCE_GROQ_MODE = False


@app.route('/admin/groq-status', methods=['GET'])
def admin_groq_status():
    """
    Admin endpoint - returns detailed Groq API status.
    For admin panel Groq force-enable button.
    """
    global FORCE_GROQ_MODE
    
    groq_api_key = os.environ.get('GROQ_API_KEY', '')
    status = {
        'available': GROQ_AVAILABLE,
        'api_key_set': bool(groq_api_key),
        'force_mode': FORCE_GROQ_MODE,
        'connection': 'unknown'
    }
    
    if groq_api_key and GROQ_AVAILABLE:
        try:
            import requests
            headers = {"Authorization": f"Bearer {groq_api_key}", "Content-Type": "application/json"}
            test_payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5}
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=test_payload, timeout=5)
            if resp.status_code == 200:
                status['connection'] = 'connected'
            else:
                status['connection'] = f'error_{resp.status_code}'
        except Exception as e:
            status['connection'] = f'error: {str(e)[:30]}'
    elif not groq_api_key:
        status['connection'] = 'no_api_key'
    else:
        status['connection'] = 'library_not_installed'
    
    return jsonify(status)


@app.route('/admin/dashboard')
def admin_dashboard_page():
    """Serve a simple admin dashboard page showing live stats and session usernames. Requires admin auth."""
    if not session.get('admin_authenticated'):
        return "<h2>Unauthorized</h2><p>Please authenticate as admin to view this dashboard.</p>", 401
    try:
        with open(os.path.join(os.path.dirname(__file__), 'public', 'html', 'admin-dashboard.html'), 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/feedback/submit', methods=['POST'])
def feedback_submit():
    """
    Accept feedback submissions from users.
    Request JSON: { rating: int (1-5), feedback: str (optional), session_id: str (optional), name: str (optional) }
    Writes to feedback/feedback.jsonl
    """
    try:
        data = request.get_json() or {}
        rating = int(data.get('rating', 0))
        feedback_text = data.get('feedback', '').strip()
        session_id = data.get('session_id') or session.get('session_id') or 'unknown'
        name = data.get('name') or session.get('user_name') or session_users.get(session_id) or 'Anonymous'

        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'error': 'Rating must be between 1 and 5'}), 400

        feedback_dir = os.path.join(os.path.dirname(__file__), 'feedback')
        if not os.path.exists(feedback_dir):
            os.makedirs(feedback_dir, exist_ok=True)
        out_path = os.path.join(feedback_dir, 'feedback.jsonl')
        entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'name': name,
            'rating': rating,
            'feedback': feedback_text
        }
        with open(out_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        print(f"[Widget API] Feedback saved: session {session_id[:8]} name={name} rating={rating}")
        return jsonify({'success': True, 'message': 'Thanks for your feedback'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500




@app.route('/admin/feedback-count')
def admin_feedback_count():
    """Return total submitted feedback count."""
    feedback_dir = os.path.join(os.path.dirname(__file__), 'feedback')
    out_path = os.path.join(feedback_dir, 'feedback.jsonl')
    count = 0
    if os.path.exists(out_path):
        try:
            with open(out_path, 'r', encoding='utf-8') as f:
                for _ in f:
                    count += 1
        except Exception:
            count = -1
    return jsonify({'count': count})


@app.route('/admin/groq-toggle', methods=['POST'])
def admin_groq_toggle():
    """
    Admin endpoint - toggle force Groq mode.
    When enabled, all responses use Groq API instead of local Ollama.
    """
    global FORCE_GROQ_MODE
    
    try:
        data = request.get_json() or {}
        enable = data.get('enable', not FORCE_GROQ_MODE)  # Toggle if not specified
        
        if enable and not GROQ_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Groq library not installed. Run: pip install groq',
                'force_mode': FORCE_GROQ_MODE
            }), 400
        
        if enable and not os.environ.get('GROQ_API_KEY'):
            return jsonify({
                'success': False,
                'error': 'GROQ_API_KEY not set in environment',
                'force_mode': FORCE_GROQ_MODE
            }), 400
        
        FORCE_GROQ_MODE = bool(enable)
        
        return jsonify({
            'success': True,
            'force_mode': FORCE_GROQ_MODE,
            'message': f"Groq force mode {'enabled' if FORCE_GROQ_MODE else 'disabled'}"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/authenticate', methods=['POST'])
def admin_authenticate():
    """
    Authenticate admin user and create session.
    Used for accessing password-protected features.
    """
    try:
        data = request.get_json() or {}
        password = data.get('password', '')
        
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return jsonify({'success': True, 'message': 'Authentication successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid password'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    """Logout admin user and clear session."""
    session.pop('admin_authenticated', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@app.route('/admin/check-auth', methods=['GET'])
def admin_check_auth():
    """Check if user is authenticated."""
    return jsonify({'authenticated': session.get('admin_authenticated', False)})


@app.route('/admin/open-chat-admin', methods=['POST'])
def admin_open_chat_admin():
    """
    Returns instructions for opening admin panel in chat.
    (Actual panel is triggered by typing 'nufc' in the chat interface)
    """
    try:
        data = request.get_json() or {}
        password = data.get('password', '')
        
        if password != ADMIN_PASSWORD:
            return jsonify({'success': False, 'message': 'Invalid password'}), 401
        
        return jsonify({
            'success': True,
            'action': 'open_url',
            'url': '/widget-standalone.html',
            'message': 'Opening chat interface. Type "nufc" in the chat to access admin panel.',
            'instructions': [
                'The chat interface will open',
                'Type "nufc" (without quotes) in the chat input',
                'The admin panel will appear automatically',
                'Admin panel includes: system status, session management, memory clearing, API testing'
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/run-stats', methods=['POST'])
def admin_run_stats():
    """
    Launch the statistics dashboard PowerShell script.
    """
    import subprocess
    
    try:
        data = request.get_json() or {}
        password = data.get('password', '')
        
        if password != ADMIN_PASSWORD:
            return jsonify({'success': False, 'message': 'Invalid password'}), 401
        
        # Start stats dashboard in new PowerShell window
        # Use dynamic base path to work on any PC
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, 'scripts', 'setup', 'stats_dashboard.ps1')
        
        # Fallback: try root directory if not in scripts/setup
        if not os.path.exists(script_path):
            script_path = os.path.join(base_dir, '..', 'scripts', 'setup', 'stats_dashboard.ps1')
            script_path = os.path.abspath(script_path)
        
        if not os.path.exists(script_path):
            return jsonify({
                'success': False,
                'error': f'Stats dashboard script not found. Searched: {script_path}'
            }), 404
        
        # Launch in new PowerShell window
        subprocess.Popen([
            'powershell.exe',
            '-NoExit',
            '-ExecutionPolicy', 'Bypass',
            '-File', script_path
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        return jsonify({
            'success': True,
            'message': 'Statistics dashboard launched successfully',
            'details': 'A new PowerShell window has opened with the stats dashboard'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/run-calibration', methods=['POST'])
def admin_run_calibration():
    """
    Launch the calibration test suite (300 questions).
    """
    import subprocess
        
    try:
        data = request.get_json() or {}
        password = data.get('password', '')
            
        if password != ADMIN_PASSWORD:
            return jsonify({'success': False, 'message': 'Invalid password'}), 401
            
        # Start calibration test in new window
        # Use dynamic base path to work on any PC
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bat_path = os.path.join(base_dir, 'scripts', 'setup', 'run_calibration_test.bat')
            
        # Fallback: try root directory if not in scripts/setup
        if not os.path.exists(bat_path):
            bat_path = os.path.join(base_dir, '..', 'scripts', 'setup', 'run_calibration_test.bat')
            bat_path = os.path.abspath(bat_path)
            
        if not os.path.exists(bat_path):
            return jsonify({
                'success': False,
                'error': f'Calibration test script not found. Searched: {bat_path}'
            }), 404
            
        # Launch in new CMD window
        subprocess.Popen([
            'cmd.exe',
            '/c',
            'start',
            'cmd.exe',
            '/k',
            bat_path
        ])
            
        return jsonify({
            'success': True,
            'message': 'Calibration test launched successfully',
            'details': 'A new window has opened. The test will run 300 questions and generate reports. Expected duration: 20-30 minutes.',
            'warning': 'Do not close the window until the test completes.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/run-quick-test', methods=['POST'])
def admin_run_quick_test():
    """
    Launch the quick 25-question smoke test in a new window.
    """
    import subprocess
    try:
        data = request.get_json() or {}
        password = data.get('password', '')
            
        if password != ADMIN_PASSWORD:
            return jsonify({'success': False, 'message': 'Invalid password'}), 401
            
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, 'tests', 'quick_25_test.py')
        if not os.path.exists(script_path):
            return jsonify({'success': False, 'error': f'Quick test not found at {script_path}'}), 404
            
        # Launch python quick test in new CMD window so output is visible
        subprocess.Popen([
            'cmd.exe', '/c', 'start', 'cmd.exe', '/k', 'python', script_path
        ])
            
        return jsonify({'success': True, 'message': 'Quick test launched in a new window', 'details': '25-question smoke test is running.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/session/set-name', methods=['POST'])
def session_set_name():
    """
    Set the display name for the current session (stored in Flask session and session_users map).
    Request: { "name": "User Name", "session_id": "optional-uuid" }
    """
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        session_id = data.get('session_id')
        if not name:
            return jsonify({'success': False, 'error': 'Name required'}), 400
            
        # Ensure session has an id
        if not session_id:
            # use stored session id or create one
            if not session.get('session_id'):
                import uuid
                session['session_id'] = str(uuid.uuid4())
            session_id = session['session_id']
        else:
            session['session_id'] = session_id
        
        session['user_name'] = name
        session_users[session_id] = name
        print(f"[Widget API] Session name set: {session_id[:8]} => {name}")
        return jsonify({'success': True, 'session_id': session_id, 'name': name})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/open-dev-widget', methods=['POST'])
def admin_open_dev_widget():
    """
    Open the development widget (password-protected route).
    """
    try:
        data = request.get_json() or {}
        password = data.get('password', '')
        
        if password != ADMIN_PASSWORD:
            return jsonify({'success': False, 'message': 'Invalid password'}), 401
        
        # Set session authentication
        session['admin_authenticated'] = True
        
        return jsonify({
            'success': True,
            'action': 'open_url',
            'url': '/widget',
            'message': 'Opening development widget interface',
            'details': 'You have been authenticated. The widget will open in a new tab.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def get_local_ip():
    """Get the local IP address for network access"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 5001
    
    print("\n" + "="*60)
    print("  PDBOT Widget API Server v2.5.0")
    print("  Developed by M. Hassan Arif Afridi")
    print("="*60)
    print(f"\n  🌐 Local:   http://localhost:{port}")
    print(f"  📱 Network: http://{local_ip}:{port}")
    
    # Warm up models (load embedding model, reranker, and classifier)
    print("\n  🔄 Warming up models...")
    try:
        from src.rag_langchain import get_embedder, get_reranker
        embedder = get_embedder()
        reranker = get_reranker()
        clf = get_classifier()
        
        if embedder:
            print("  ✅ Embedding model loaded")
        else:
            print("  ⚠️  Embedding model not available - install: pip install sentence-transformers")
        
        if reranker:
            print("  ✅ Reranker model loaded")
        
        if clf:
            print("  ✅ Classifier loaded")
    except Exception as e:
        print(f"  ⚠️  Model warmup warning: {e}")
    
    # Try localtunnel for external access (open source, free)
    use_tunnel = os.environ.get('USE_TUNNEL', '').lower() == 'true'
    if use_tunnel:
        import subprocess
        import threading
        def start_tunnel():
            try:
                # Use localtunnel (npm install -g localtunnel)
                process = subprocess.Popen(
                    ['lt', '--port', str(port), '--subdomain', 'pdbot-giki'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                for line in process.stdout:
                    if 'your url is:' in line.lower() or 'https://' in line:
                        print(f"\n  🌍 PUBLIC URL (for phone/external access):")
                        print(f"     {line.strip()}")
                        print("\n  ⚠️  Share this URL to access from any network!")
                        break
            except Exception as e:
                print(f"\n  ⚠️  localtunnel not available: {e}")
                print("     Install with: npm install -g localtunnel")
        
        tunnel_thread = threading.Thread(target=start_tunnel, daemon=True)
        tunnel_thread.start()
    else:
        print(f"\n  To access from phone (same network): http://{local_ip}:{port}")
        print("  For external access, set USE_TUNNEL=true (requires: npm install -g localtunnel)")
    
    print("\n  Endpoints:")
    print("    POST /chat           - Chat with PDBOT (with memory)")
    print("    POST /feedback/*     - Feedback endpoints")
    print("    POST /memory/clear   - Clear session memory")
    print("    GET  /health         - Health check")
    print("    GET  /admin/status   - Backend status (admin)")
    print("\n" + "="*60)
    
    # Check if waitress is available for production server
    try:
        from waitress import serve
        print("\n  ✅ Using Waitress (production WSGI server)")
        print("="*60 + "\n")
        serve(app, host='0.0.0.0', port=port, threads=4)
    except ImportError:
        print("\n  ⚠️  Waitress not installed. Using Flask dev server.")
        print("     Install with: pip install waitress")
        print("="*60 + "\n")
        app.run(host='0.0.0.0', port=port, debug=False)

