##Step 2

import html

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)        # Fix &amp; → &
    text = text.replace("\n", " ")    # Remove newlines
    return text.strip()

def normalize_papers(papers):
    """
    Clean abstracts/titles and enforce schema.
    Preserves all fields from the API so metadata is not lost.
    """
    cleaned = []
    for p in papers:
        paper = {
            "title":    clean_text(p["title"]),
            "abstract": clean_text(p["abstract"]),
            "authors":  p["authors"],
            "year":     p["year"],
            "url":      p["url"],
            "venue":    p["venue"],
            # Preserve all extra metadata fields if present
            "doi":      p.get("doi"),
            "issn":     p.get("issn"),
        }
        # Pass through any other fields the API returns
        for key in p:
            if key not in paper:
                paper[key] = p[key]
        cleaned.append(paper)
    return cleaned
