"""
Enhanced Flask App with Knowledge Base Statistics
"""
from flask import Flask, render_template, request, jsonify
from .agents.search_agent import search_agent_logic
from .agents.summarizer import summarize_papers
from .agents.chat_agent import ask_question
from .database import get_papers_stats, vector_store
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Search papers with progressive KB"""
    data = request.json
    query = data.get('query', '')
    offset = data.get('offset', 0)
    seen_dois = data.get('seen_dois', [])
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        results = search_agent_logic(query, offset=offset, seen_dois=set(seen_dois))
        return jsonify({"results": results})
    except Exception as e:
        print(f"Search Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    """Summar ize papers with comprehensive analysis"""
    data = request.json
    papers = data.get('papers', [])
    
    if not papers:
        return jsonify({"error": "No papers provided"}), 400
    
    try:
        summaries_json = summarize_papers(papers)
        summaries = json.loads(summaries_json)
        return jsonify({"summaries": summaries})
    except Exception as e:
        print(f"Summarization Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/compare', methods=['POST'])
def compare():
    """Compare multiple papers side-by-side"""
    from .agents.comparison_agent import compare_papers
    
    data = request.json
    papers = data.get('papers', [])
    
    if len(papers) < 2:
        return jsonify({"error": "Need at least 2 papers to compare"}), 400
    
    try:
        comparison_json = compare_papers(papers)
        comparison = json.loads(comparison_json)
        return jsonify(comparison)
    except Exception as e:
        print(f"Comparison Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Answer questions about papers"""
    data = request.json
    query = data.get('query', '')
    context = data.get('context', '{}')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        answer = ask_question(query, context)
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/intent', methods=['POST'])
def detect_intent():
    """Detect user intent and extract search keywords"""
    data = request.json
    message = data.get('message', '')
    papers_loaded = data.get('papers_loaded', False)
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        from .utils.ai_config import generate_text
        
        context_info = ""
        if papers_loaded:
            context_info = "\n**IMPORTANT CONTEXT**: The user already has research papers loaded in the system."
        
        prompt = f"""Analyze this user message and determine intent.

User Message: "{message}"{context_info}

Return ONLY valid JSON (no markdown):
{{
    "intent": "SEARCH_REQUEST" | "SUMMARY_REQUEST" | "QUESTION" | "CHITCHAT",
    "keywords": ["extracted", "search", "keywords"],
    "confidence": 0.95,
    "reasoning": "brief explanation"
}}

Intent types:
- SEARCH_REQUEST: User wants to find NEW research papers
- SUMMARY_REQUEST: User explicitly asks to generate summaries of loaded papers
- QUESTION: User asks a question about already-loaded papers
- CHITCHAT: General conversation

Extract 2-5 meaningful keywords for SEARCH_REQUEST only."""

        response = generate_text(prompt, max_tokens=200)
        
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        result = json.loads(cleaned)
        return jsonify(result)
        
    except Exception as e:
        print(f"Intent Detection Error: {e}")
        # Fallback logic
        summary_words = ['summary', 'summarize', 'summaries']
        if papers_loaded and any(w in message.lower() for w in summary_words):
            return jsonify({
                "intent": "SUMMARY_REQUEST",
                "keywords": [],
                "confidence": 0.7,
                "reasoning": "Fallback - detected summary keyword"
            })
        
        question_words = ['which', 'what', 'how', 'compare', 'tell', 'explain', 'show']
        if papers_loaded and any(message.lower().startswith(w) for w in question_words):
            return jsonify({
                "intent": "QUESTION",
                "keywords": [],
                "confidence": 0.6,
                "reasoning": "Fallback - detected question word"
            })
        
        # Smart keyword extraction: strip command/stop words, keep the topic
        STOP_WORDS = {
            'search', 'find', 'look', 'fetch', 'get', 'show', 'give', 'list',
            'for', 'me', 'on', 'about', 'regarding', 'related', 'to', 'in',
            'research', 'paper', 'papers', 'article', 'articles', 'study',
            'studies', 'literature', 'more', 'please', 'a', 'an', 'the',
            'some', 'any', 'with', 'of', 'and', 'or', 'is', 'are', 'that',
        }
        raw_words = message.lower().split()
        keywords = [w for w in raw_words if w not in STOP_WORDS and len(w) > 2]

        # If we stripped everything, fall back to the last 3 raw words
        if not keywords:
            keywords = message.split()[-3:]

        return jsonify({
            "intent": "SEARCH_REQUEST" if len(message.split()) > 2 else "CHITCHAT",
            "keywords": keywords[:6],
            "confidence": 0.5,
            "reasoning": "Fallback - intent detection failed, extracted topic keywords"
        })

@app.route('/stats', methods=['GET'])
def stats():
    """Get knowledge base statistics"""
    try:
        papers_stats = get_papers_stats()
        vector_stats = vector_store.get_stats()
        
        return jsonify({
            "knowledge_base": {
                **papers_stats,
                **vector_stats
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Research Compass RAG"})

if __name__ == '__main__':
    # Use stat reloader to avoid watchdog restart glitches on Windows
    app.run(
        debug=True, 
        port=5000,
        use_reloader=True,
        reloader_type='stat'  # Prevents watchdog restart loop issues
    )
