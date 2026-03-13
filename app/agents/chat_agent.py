"""
Chat/Q&A Agent - Updated to use unified AI config
"""
from ..utils.ai_config import generate_text, DISABLE_AI

def ask_question(query, context_text):
    """
    Answer questions about research papers with highlighted key points
    """
    if DISABLE_AI:
        return "AI features are disabled. Enable them in .env to use Q&A."
    
    prompt = f"""You are an expert research assistant helping an IIT professor analyze research papers.

Context (Research Papers):
{context_text[:6000]}

User Question: {query}

FORMATTING REQUIREMENTS:
1. Provide detailed answer (150-200 words minimum)
2. Use proper paragraph breaks (blank lines between paragraphs)
3. **CRITICAL**: Put paper titles in **bold** like: **"Bridging the Last-mile Gap in Climate Services"**
4. **CRITICAL**: Put key metrics, findings, and technical terms in **bold** for emphasis
5. Use bullet points or numbered lists when appropriate
6. Reference papers clearly (e.g., "According to **'Paper Title'**..." or "**Paper 1** demonstrates...")
7. Include technical details with **bold** formatting for important numbers/metrics
8. If information isn't in context, clearly state that
9. Use professional academic tone
10. Break response into SHORT paragraphs (2-4 sentences each)

EXAMPLE of good formatting:
"According to **'Bridging the Last-mile Gap in Climate Services'**, the hybrid framework achieved a **mean absolute error of 2.5 days** for wildfire prediction. The model uses **ResNet-18 architecture** combined with the **FGOALS-f2** climate system.

Similarly, **'Evaluating the Shanghai Typhoon Model'** shows **track errors below 200 km** up to **108 hours** forecast lead time."

Answer:"""

    try:
        answer = generate_text(prompt, max_tokens=2000)
        return answer
    except Exception as e:
        return f"Error generating answer: {str(e)}"
