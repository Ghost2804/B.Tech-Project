
import numpy as np
from ..utils.utils import cosine_similarity
from ..utils.embeddings import embed_texts

def rank_papers(query, papers, top_k=10, min_threshold=0.25):
    """
    Rank papers by semantic similarity of title+abstract to query.
    Returns up to top_k papers that meet the strict min_threshold.
    """
    if not papers: return []
    
    # Prepare texts for embedding
    query_vec = embed_texts([query])[0]
    paper_texts = [p.get("title", "") + " " + p.get("abstract", "") for p in papers]
    paper_vecs = embed_texts(paper_texts)

    # Compute cosine similarity
    scores = []
    for i, p in enumerate(papers):
        sim = cosine_similarity(query_vec, paper_vecs[i])
        if sim >= min_threshold:
            p['similarity_score'] = float(sim)
            scores.append((sim, p))

    # Sort by similarity
    ranked = sorted(scores, key=lambda x: x[0], reverse=True)
    return [p for _, p in ranked[:top_k]]
