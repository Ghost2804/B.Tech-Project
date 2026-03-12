"""
Vector Store Module
Local embedding storage with fast similarity search
Migration-ready for Vertex AI Vector Search
"""
import numpy as np
import json
from pathlib import Path
from typing import List, Tuple

# Storage paths
VECTORS_DIR = Path(__file__).parent.parent.parent / "data" / "embeddings"
VECTORS_DIR.mkdir(parents=True, exist_ok=True)

VECTORS_FILE = VECTORS_DIR / "vectors.npy"
INDEX_FILE = VECTORS_DIR / "index.json"
METADATA_FILE = VECTORS_DIR / "metadata.json"

class VectorStore:
    def __init__(self):
        self.vectors = None
        self.index = {}  # {paper_id: vector_index}
        self.load()
    
    def load(self):
        """Load existing vectors and index"""
        if VECTORS_FILE.exists():
            self.vectors = np.load(str(VECTORS_FILE))
            print(f"[OK] Loaded {len(self.vectors)} embeddings from disk")
        else:
            self.vectors = np.array([]).reshape(0, 384)  # 384-dim for all-MiniLM-L6-v2
        
        if INDEX_FILE.exists():
            with open(INDEX_FILE, 'r') as f:
                self.index = json.load(f)
    
    def save(self):
        """Save vectors and index to disk"""
        np.save(str(VECTORS_FILE), self.vectors)
        with open(INDEX_FILE, 'w') as f:
            json.dump(self.index, f)
        
        # Save metadata
        with open(METADATA_FILE, 'w') as f:
            json.dump({
                'total_vectors': len(self.vectors),
                'embedding_dim': 384,
                'model': 'all-MiniLM-L6-v2'
            }, f, indent=2)
    
    def add_embedding(self, paper_id: int, embedding: np.ndarray):
        """
        Add a single embedding
        
        Args:
            paper_id: Database paper ID
            embedding: 768-dim numpy array
        """
        paper_id_str = str(paper_id)
        
        # Check if already exists
        if paper_id_str in self.index:
            return  # Already stored
        
        # Append to vectors
        if len(self.vectors) == 0:
            self.vectors = embedding.reshape(1, -1)
        else:
            self.vectors = np.vstack([self.vectors, embedding.reshape(1, -1)])
        
        # Update index
        vector_idx = len(self.vectors) - 1
        self.index[paper_id_str] = vector_idx
        
        # Save periodically
        if len(self.vectors) % 10 == 0:
            self.save()
    
    def add_embeddings_batch(self, paper_ids: List[int], embeddings: np.ndarray):
        """Add multiple embeddings efficiently"""
        for paper_id, embedding in zip(paper_ids, embeddings):
            self.add_embedding(paper_id, embedding)
        self.save()
    
    def get_embedding(self, paper_id: int) -> np.ndarray:
        """Get embedding for a paper. Returns None if not found or index is stale."""
        paper_id_str = str(paper_id)
        if paper_id_str in self.index:
            idx = self.index[paper_id_str]
            # Guard against stale index entries that point beyond the current array
            if self.vectors is not None and idx < len(self.vectors):
                return self.vectors[idx]
        return None
    
    def search_similar(self, query_embedding: np.ndarray, top_k: int = 10, threshold: float = 0.7) -> List[Tuple[int, float]]:
        """
        Find most similar papers using cosine similarity
        
        Args:
            query_embedding: 768-dim query vector
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1)
        
        Returns:
            List of (paper_id, similarity_score) tuples
        """
        if len(self.vectors) == 0:
            return []
        
        # Compute cosine similarity
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        vectors_norm = self.vectors / np.linalg.norm(self.vectors, axis=1, keepdims=True)
        
        similarities = np.dot(vectors_norm, query_norm)
        
        # Filter by threshold
        valid_indices = np.where(similarities >= threshold)[0]
        
        if len(valid_indices) == 0:
            return []
        
        # Sort and get top-k
        sorted_indices = valid_indices[np.argsort(-similarities[valid_indices])][:top_k]
        
        # Convert indices back to paper IDs
        index_to_paper = {v: int(k) for k, v in self.index.items()}
        
        results = []
        for idx in sorted_indices:
            paper_id = index_to_paper.get(int(idx))
            if paper_id:
                results.append((paper_id, float(similarities[idx])))
        
        return results
    
    def get_stats(self):
        """Get vector store statistics"""
        return {
            'total_vectors': len(self.vectors),
            'total_indexed': len(self.index),
            'embedding_dim': 384 if len(self.vectors) > 0 else 0
        }

# Global instance
vector_store = VectorStore()
