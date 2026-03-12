"""
Enhanced Search Agent with Progressive Knowledge Base
Local-first retrieval → API fallback → Store results
"""
from .api_client import search_semanticscholar
from .preprocess import normalize_papers
from .ranker import rank_papers
from ..database import store_papers_batch, search_papers_by_title, vector_store, get_paper_by_doi
from ..utils.embeddings import embed_texts
import numpy as np

def search_agent_logic(query, max_results=20, top_k=10, local_threshold=0.7, offset=0, seen_dois=None):
    """
    Progressive RAG search:
    1. Check local KB first (only on page 1)
    2. If insufficient or paginating, call APIs
    3. Store all new results
    4. Return ranked papers
    """
    if seen_dois is None:
        seen_dois = set()

    print(f"[SEARCH] Query: '{query}' | offset={offset}")
    
    local_papers = []
    
    # STEP 1: Local vector search (Skip if fetching more pages)
    if offset == 0:
        print("[KB] Searching local knowledge base...")
        query_embedding = embed_texts([query])[0]
        local_results = vector_store.search_similar(
        query_embedding, 
        top_k=top_k,
        threshold=local_threshold
    )
    
    if offset == 0:
        if local_results:
            print(f"[KB] Found {len(local_results)} papers locally (similarity >= {local_threshold})")
            # Fetch full paper data from DB
            from ..database.papers_store import get_all_papers
            all_stored = {p['id']: p for p in get_all_papers(limit=1000)}
            for paper_id, score in local_results:
                if paper_id in all_stored:
                    paper = all_stored[paper_id].copy()
                    paper['similarity_score'] = score
                    local_papers.append(paper)
        else:
            print("[KB] No local results found")
        
        # STEP 2: Check if local results are sufficient
        if len(local_papers) >= top_k:
            print(f"[OK] Sufficient local results ({len(local_papers)} papers) - skipping API")
            return local_papers[:top_k]
    
    # STEP 3: Fetch from APIs (need more results)
    needed = max_results - len(local_papers)
    print(f"[API] Fetching {needed} papers from external APIs (offset={offset})...")
    
    api_papers = search_semanticscholar(query, max_results=max_results, offset=offset)
    api_papers = normalize_papers(api_papers)
    
    # Filter out papers we have already seen this session
    if seen_dois:
        filtered = [p for p in api_papers if p.get('doi') and p.get('doi').lower() not in seen_dois]
        print(f"[DEDUP] {len(filtered)} papers remain after session deduplication")
        api_papers = filtered
        
    if not api_papers:
        print("[API] No API results found")
        return local_papers[:top_k] if local_papers else []
    
    print(f"[API] Retrieved {len(api_papers)} papers")
    
    # STEP 4: Store new papers in local KB
    print("[STORE] Storing new papers...")
    new_count, duplicate_count = store_papers_batch(api_papers)
    print(f"[STORE] New: {new_count}, Duplicates: {duplicate_count}")
    
    # STEP 5: Generate and store embeddings for new papers
    if new_count > 0:
        print(f"[EMBED] Generating embeddings for {new_count} new papers...")
        from ..database.papers_store import get_all_papers
        
        # Get recently added papers
        recently_added = get_all_papers(limit=new_count + 10)
        new_paper_texts = []
        new_paper_ids = []
        
        for paper in api_papers:
            doi = paper.get('doi', '')
            if doi:
                stored = get_paper_by_doi(doi)
                if stored and vector_store.get_embedding(stored['id']) is None:
                    text = stored['title'] + " " + stored.get('abstract', '')
                    new_paper_texts.append(text)
                    new_paper_ids.append(stored['id'])
        
        if new_paper_texts:
            embeddings = embed_texts(new_paper_texts)
            vector_store.add_embeddings_batch(new_paper_ids, embeddings)
            print(f"[EMBED] Stored {len(new_paper_ids)} embeddings")
    
    # STEP 6: Combine local + API results and rank
    combined_papers = local_papers + [p for p in api_papers if p not in local_papers]
    
    print(f"[RANK] Ranking {len(combined_papers)} combined papers...")
    ranked_papers = rank_papers(query, combined_papers, top_k=top_k)
    
    print(f"[OK] Returning top {len(ranked_papers)} papers")
    return ranked_papers
