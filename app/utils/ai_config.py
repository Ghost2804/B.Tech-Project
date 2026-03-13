"""
Unified AI Configuration
Supports both Groq and Gemini providers
"""
import os
from typing import Literal

# AI Provider selection
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()
DISABLE_AI = os.getenv("DISABLE_AI", "false").lower() == "true"

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Models
GROQ_MODEL = "llama-3.3-70b-versatile"  # Fast, high quality
GEMINI_MODEL = "gemini-2.0-flash-lite"

def get_ai_client():
    """Get the appropriate AI client based on provider"""
    if DISABLE_AI:
        return None
    
    if AI_PROVIDER == "groq":
        from groq import Groq
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        return Groq(api_key=GROQ_API_KEY)
    
    elif AI_PROVIDER == "gemini":
        import google.generativeai as genai
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        genai.configure(api_key=GOOGLE_API_KEY)
        return genai
    
    else:
        raise ValueError(f"Unknown AI_PROVIDER: {AI_PROVIDER}")

def generate_text(prompt: str, max_tokens: int = 2000) -> str:
    """
    Universal text generation function
    Works with both Groq and Gemini
    """
    if DISABLE_AI:
        return "AI is disabled in configuration"
    
    client = get_ai_client()
    
    if AI_PROVIDER == "groq":
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    elif AI_PROVIDER == "gemini":
        import time
        time.sleep(2)  # Rate limiting for Gemini
        model = client.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text
