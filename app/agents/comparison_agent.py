"""
Comparison Agent - Side-by-Side Paper Analysis
Generates structured comparison tables for 2-5 papers
"""
import json
from ..utils.ai_config import generate_text

def compare_papers(papers_data):
    """
    Compare multiple research papers side-by-side
    
    Args:
        papers_data: List of dicts with 'title', 'abstract', and optionally 'summary'
    
    Returns:
        JSON string with comparison tables and analysis
    """
    if len(papers_data) < 2:
        return json.dumps({
            "error": "Need at least 2 papers to compare",
            "comparison": None
        })
    
    if len(papers_data) > 5:
        papers_data = papers_data[:5]  # Limit to 5 papers
    
    # Build comparison prompt
    prompt = f"""You are comparing {len(papers_data)} research papers for academic review.

Generate a COMPREHENSIVE side-by-side comparison in the following structure:

Return ONLY valid JSON (no markdown):
{{
  "overview": "2-3 sentence summary of what these papers have in common and how they differ",
  "methodology_comparison": {{
    "aspects": ["Approach", "Architecture", "Key Technique", "Novelty"],
    "papers": [
      {{
        "title": "Paper 1 title",
        "approach": "Main approach used",
        "architecture": "Model/system architecture",
        "key_technique": "Primary technical contribution",
        "novelty": "What makes this unique"
      }}
      // ... for each paper
    ]
  }},
  "experimental_comparison": {{
    "aspects": ["Dataset", "Baseline Methods", "Metrics", "Setup"],
    "papers": [
      {{
        "title": "Paper 1 title",
        "dataset": "Dataset name and size",
        "baselines": "What they compared against",
        "metrics": "Evaluation metrics used",
        "setup": "Key experimental details"
      }}
      // ... for each paper
    ]
  }},
  "results_comparison": {{
    "metrics": ["Accuracy", "Speed", "Other Key Metrics"],
    "papers": [
      {{
        "title": "Paper 1 title",
        "accuracy": "X.X% (if applicable)",
        "speed": "X ms/samples (if applicable)",
        "other": "Other notable results",
        "best_at": "What this paper excels at"
      }}
      // ... for each paper
    ],
    "winner": "Which paper performs best overall and why"
  }},
  "key_differences": [
    "Major difference 1",
    "Major difference 2",
    "Major difference 3"
  ],
  "trade_offs": [
    "Trade-off 1: Paper A is faster but less accurate",
    "Trade-off 2: Paper B requires more data but generalizes better",
    "etc."
  ],
  "recommendations": {{
    "use_paper_1_if": "When you need...",
    "use_paper_2_if": "When you need...",
    "use_paper_3_if": "When you need..."
  }}
}}

Papers to compare:
"""
    
    for i, paper in enumerate(papers_data, 1):
        prompt += f"\n{'='*60}\nPaper {i}:\nTitle: {paper.get('title', 'Untitled')}\n"
        
        # Include summary if available
        if paper.get('summary'):
            summary = paper['summary']
            prompt += f"Summary:\n"
            prompt += f"- Problem: {summary.get('research_problem', 'N/A')}\n"
            prompt += f"- Methodology: {summary.get('methodology', 'N/A')}\n"
            prompt += f"- Results: {summary.get('results', 'N/A')}\n"
        else:
            prompt += f"Abstract: {paper.get('abstract', 'No abstract')}\n"
    
    # Generate comparison
    try:
        print(f"[COMPARISON] Comparing {len(papers_data)} papers...")
        
        response = generate_text(prompt, max_tokens=8000)
        
        # Clean response
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        # Validate JSON
        comparison = json.loads(cleaned)
        
        print("[SUCCESS] Comparison generated!")
        return cleaned
        
    except Exception as e:
        print(f"[ERROR] Comparison failed: {e}")
        return json.dumps({
            "error": f"Comparison generation failed: {str(e)}",
            "comparison": None
        })
