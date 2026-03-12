"""
Enhanced Summarization Agent - Comprehensive Academic Analysis
Provides detailed, professor-grade summaries (500-750 words per paper)
"""
import json
from ..utils.ai_config import generate_text, DISABLE_AI

def _inject_metadata(summaries, papers):
    """
    Force-inject paper metadata from original paper objects into summary dicts.
    Uses direct assignment (not setdefault) so null/None values from the AI
    are always overwritten with the real paper data from the search API.
    """
    # Build a title->paper lookup for safe matching (AI may reorder titles)
    title_map = {p.get('title', '').strip().lower(): p for p in papers}

    for idx, summary in enumerate(summaries):
        # First try to match by title, then fall back to positional index
        ai_title = summary.get('title', '').strip().lower()
        p = title_map.get(ai_title) or (papers[idx] if idx < len(papers) else {})

        # Always overwrite — do NOT use setdefault (won't replace null)
        summary['journal']  = p.get('venue') or None
        summary['doi']      = p.get('doi') or None
        summary['issn']     = p.get('issn') or None
        summary['year']     = p.get('year') or None
        summary['url']      = p.get('url') or None
        summary['website']  = p.get('url') or None

        # Authors: keep AI-generated list if it has content, else use paper data
        ai_authors = summary.get('authors')
        if not ai_authors:
            summary['authors'] = p.get('authors', [])

        # Scopus indexing flag
        if p.get('scopus_indexed'):
            summary['scopus'] = 'Yes'
        else:
            summary['scopus'] = p.get('scopus') or None

def summarize_papers(papers):
    """
    Generate comprehensive academic summaries for research papers
    Target: 500-750 words per paper with full technical details
    """
    # Check if AI is disabled
    if DISABLE_AI:
        print("AI features disabled. Returning abstracts as summaries.")
        return json.dumps([{
            "title": p.get('title', 'Unknown'),
            "journal": p.get('venue', None),
            "doi": p.get('doi', None),
            "issn": p.get('issn', None),
            "year": p.get('year', None),
            "authors": p.get('authors', []),
            "scopus": "Yes" if p.get('scopus_indexed') else p.get('scopus', None),
            "website": p.get('url', None),
            "url": p.get('url', None),
            "overview": "AI disabled - see abstract",
            "research_problem": p.get('abstract', 'No abstract available')[:150],
            "methodology": "Enable AI to generate detailed summaries",
            "experimental_setup": "N/A",
            "results": f"Year: {p.get('year', 'N/A')} | Venue: {p.get('venue', 'N/A')}",
            "limitations": "Enable AI in .env file",
            "key_takeaways": ["AI features are currently disabled"]
        } for p in papers[:5]])
    
    # Limit papers per batch
    MAX_PAPERS_PER_BATCH = 5  # Increased to 5 for professor requirement
    papers = papers[:MAX_PAPERS_PER_BATCH]
    
    # Check cache
    from ..utils.cache import cache_manager
    sorted_papers = sorted(papers, key=lambda x: x.get('title', ''))
    content_key = json.dumps([{
        'title': p.get('title'), 
        'abstract': p.get('abstract')
    } for p in sorted_papers])
    
    cached = cache_manager.get(content_key, model_suffix="_summary_v4_comprehensive")
    if cached:
        print("[CACHE] Comprehensive summary found!")
        # Still inject fresh metadata even from cache (paper data is never stored in cache)
        try:
            cached_summaries = json.loads(cached)
            _inject_metadata(cached_summaries, papers)
            return json.dumps(cached_summaries)
        except Exception:
            return cached  # Return raw cached if injection fails
    

    # Build comprehensive analysis prompt
    prompt = """You are a senior research analyst at an IIT research institution, preparing detailed paper analyses for professors and Ph.D. students.

Your task: Provide COMPREHENSIVE, DETAILED analysis of each research paper. This is for academic evaluation, NOT casual reading.

**CRITICAL REQUIREMENTS:**
1. Be thorough and technical - assume the reader is a domain expert
2. Include ALL quantitative results with exact numbers
3. Explain methodologies in detail (algorithms, architectures, techniques)
4. Cite specific datasets, model sizes, hyperparameters when available
5. Target 500-750 words PER PAPER
6. Be precise with technical terminology

Return ONLY valid JSON (no markdown, no ```):
[
  {
    "title": "Exact paper title",
    "overview": "2-3 sentence high-level summary of what this paper accomplishes and why it matters",
    "research_problem": "What specific problem does this paper address? What gap in existing research? (60-80 words)",
    "methodology": "DETAILED explanation of approach - Include: (1) Main algorithm/technique names, (2) Model architecture details, (3) Mathematical frameworks used, (4) Training procedures, (5) Novel innovations introduced. Be specific and technical. (150-200 words)",
    "experimental_setup": "Complete experimental details - Datasets (name, size, source, splits), Baseline methods compared against, Evaluation metrics used, Implementation details (frameworks, hardware), Any ablation studies. (100-120 words)",
    "results": "COMPREHENSIVE quantitative results - Report ALL key metrics with exact numbers, Compare to baselines showing % improvements, Statistical significance if reported, Performance on different data subsets, Best/worst case scenarios. Be quantitative and specific. (120-150 words)",
    "limitations": "Critical analysis - Acknowledged limitations, Computational constraints, Generalization concerns, Dataset biases, Assumptions made, Suggested future work. Be honest and analytical. (60-80 words)",
    "key_takeaways": ["3-5 bullet points of MOST IMPORTANT findings - what a researcher MUST know from this paper"],
    "potential_research_topics": ["2-3 bullet points suggesting new research questions or future directions based on this paper."]
  }
]

Papers to analyze:
"""
    
    for i, p in enumerate(papers, 1):
        abstract = p.get('abstract', 'No abstract available')
        # Include more context if available
        prompt += f"\n{'='*60}\nPaper {i}:\nTitle: {p.get('title', 'Untitled')}\n"
        prompt += f"Authors: {', '.join(p.get('authors', [])[:5]) if p.get('authors') else 'Not listed'}\n"
        prompt += f"Year: {p.get('year', 'N/A')} | Venue: {p.get('venue', 'N/A')}\n"
        prompt += f"\nAbstract:\n{abstract}\n"
    
    # Generate comprehensive summary
    try:
        print(f"[SUMMARIZER] Generating comprehensive analysis for {len(papers)} papers...")
        print(f"[SUMMARIZER] Target: 500-750 words per paper")
        
        response = generate_text(
            prompt, 
            max_tokens=12000  # Significantly increased for detailed summaries
        )
        
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
        summaries = json.loads(cleaned)
        
        # Always inject fresh metadata from paper objects (overrides any null from AI)
        _inject_metadata(summaries, papers)
        
        # Log summary lengths for quality check
        for idx, summary in enumerate(summaries):
            word_count = sum([
                len(summary.get('overview', '').split()),
                len(summary.get('research_problem', '').split()),
                len(summary.get('methodology', '').split()),
                len(summary.get('experimental_setup', '').split()),
                len(summary.get('results', '').split()),
                len(summary.get('limitations', '').split())
            ])
            print(f"[QUALITY] Paper {idx+1}: ~{word_count} words")
        
        # Cache the raw AI text only (NOT with injected metadata — metadata is injected fresh each time)
        cache_manager.set(content_key, cleaned, model_suffix="_summary_v4_comprehensive")
        print("[SUCCESS] Comprehensive summaries generated!")
        return json.dumps(summaries)  # Return metadata-enriched version
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing failed: {e}")
        print(f"[DEBUG] Response preview: {cleaned[:200] if 'cleaned' in locals() else 'N/A'}")
        return _fallback_summary(papers, "Invalid JSON response")
        
    except Exception as e:
        print(f"[ERROR] Summary generation failed: {e}")
        return _fallback_summary(papers, str(e))

def _fallback_summary(papers, error_msg):
    """Generate fallback summary when AI fails"""
    return json.dumps([{
        "title": p.get('title', 'Unknown'),
        "journal": p.get('venue', None),
        "doi": p.get('doi', None),
        "issn": p.get('issn', None),
        "year": p.get('year', None),
        "authors": p.get('authors', []),
        "scopus": "Yes" if p.get('scopus_indexed') else p.get('scopus', None),
        "website": p.get('url', None),
        "url": p.get('url', None),
        "overview": "Summary generation encountered an error",
        "research_problem": p.get('abstract', 'Abstract not available')[:200] + "...",
        "methodology": f"Error: {error_msg[:100]}",
        "experimental_setup": f"Year: {p.get('year', 'N/A')} | Venue: {p.get('venue', 'N/A')}",
        "results": "Please regenerate summary or check API configuration",
        "limitations": "AI service temporarily unavailable",
        "key_takeaways": ["Summary generation failed", "Please try again"],
        "potential_research_topics": ["Enable AI to see potential research topics"]
    } for p in papers[:3]])
