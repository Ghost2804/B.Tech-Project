
import numpy as np
import os
from .cache import cache_manager

# Lazy-loaded model
_model = None

def _get_model():
    """Lazy load the SentenceTransformer model"""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print("Loading SentenceTransformer model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully")
    return _model

def embed_texts(texts):
    """
    Takes a list of strings and returns embeddings using local SentenceTransformer model.
    Returns numpy array of shape (n, 384) for all-MiniLM-L6-v2 model.
    """
    embeddings = [None] * len(texts)
    texts_to_fetch = []
    indices_to_fetch = []

    # 1. Check Cache
    print(f"Checking cache for {len(texts)} texts...")
    for i, text in enumerate(texts):
        cached_emb = cache_manager.get(text, model_suffix="_embedding_local")
        if cached_emb:
            embeddings[i] = cached_emb
        else:
            texts_to_fetch.append(text)
            indices_to_fetch.append(i)

    if not texts_to_fetch:
        print("All embeddings found in cache!")
        return np.array(embeddings)

    print(f"Generating {len(texts_to_fetch)} embeddings using local model...")

    # 2. Generate embeddings using local model
    try:
        # Use lazy-loaded model
        model = _get_model()

        # Generate embeddings in batch
        batch_embeddings = model.encode(texts_to_fetch, convert_to_numpy=True)

        # Store results and cache
        for i, (text, embedding) in enumerate(zip(texts_to_fetch, batch_embeddings)):
            global_idx = indices_to_fetch[i]
            embeddings[global_idx] = embedding

            # Cache the result
            cache_manager.set(text, embedding.tolist(), model_suffix="_embedding_local")

        print(f"Successfully generated {len(texts_to_fetch)} embeddings")

    except Exception as e:
        print(f"Embedding generation error: {e}")
        # Fallback: return zero vectors
        for idx in indices_to_fetch:
            if embeddings[idx] is None:
                embeddings[idx] = np.zeros(384)  # all-MiniLM-L6-v2 has 384 dimensions

    return np.array(embeddings)
