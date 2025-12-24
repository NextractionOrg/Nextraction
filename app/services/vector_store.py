import os
import json
import pickle
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from app.config import settings
from app.utils.logger import logger


class VectorStore:
    """Service for managing vector storage and retrieval"""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.store_type = settings.vector_store_type
        self.index_path = Path(settings.data_dir) / "indices" / f"{job_id}"
        self.chunks_path = Path(settings.data_dir) / "chunks" / f"{job_id}.json"
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.chunks_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.index = None
        self.chunks: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None
    
    def _initialize_faiss(self, dimension: int):
        """Initialize FAISS index"""
        try:
            import faiss
            # Use L2 distance (Euclidean)
            self.index = faiss.IndexFlatL2(dimension)
            logger.info(f"Initialized FAISS index with dimension {dimension}")
        except ImportError:
            logger.error("FAISS not installed. Install with: pip install faiss-cpu")
            raise RuntimeError("FAISS not available")
    
    def add_chunks(self, chunks: List[Dict], embeddings: np.ndarray):
        """Add chunks and their embeddings to the store"""
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings must have the same length")
        
        self.chunks = chunks
        self.embeddings = embeddings
        
        # Initialize index if needed
        if self.index is None:
            dimension = embeddings.shape[1]
            self._initialize_faiss(dimension)
        
        # Normalize embeddings for cosine similarity (L2 normalization)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normalized_embeddings = embeddings / norms
        
        # Add to FAISS index
        self.index.add(normalized_embeddings.astype('float32'))
        
        logger.info(f"Added {len(chunks)} chunks to vector store")
    
    def search(self, query_embedding: np.ndarray, top_k: int) -> List[Tuple[Dict, float]]:
        """Search for similar chunks"""
        if self.index is None or len(self.chunks) == 0:
            return []
        
        # Normalize query embedding
        norm = np.linalg.norm(query_embedding)
        if norm == 0:
            return []
        normalized_query = (query_embedding / norm).astype('float32').reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(normalized_query, min(top_k, len(self.chunks)))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                # Convert L2 distance to similarity score (1 / (1 + distance))
                score = 1.0 / (1.0 + float(dist))
                results.append((self.chunks[idx], score))
        
        return results
    
    def save(self):
        """Persist the index and chunks to disk"""
        # Save FAISS index
        if self.index is not None:
            faiss_path = self.index_path / "index.faiss"
            import faiss
            faiss.write_index(self.index, str(faiss_path))
            logger.info(f"Saved FAISS index to {faiss_path}")
        
        # Save chunks metadata
        with open(self.chunks_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved chunks metadata to {self.chunks_path}")
        
        # Save embeddings info (dimension)
        if self.embeddings is not None:
            info = {
                "dimension": self.embeddings.shape[1],
                "num_chunks": len(self.chunks)
            }
            info_path = self.index_path / "info.json"
            with open(info_path, 'w') as f:
                json.dump(info, f)
    
    def load(self) -> bool:
        """Load the index and chunks from disk"""
        try:
            # Load chunks
            if self.chunks_path.exists():
                with open(self.chunks_path, 'r', encoding='utf-8') as f:
                    self.chunks = json.load(f)
                logger.info(f"Loaded {len(self.chunks)} chunks from {self.chunks_path}")
            else:
                return False
            
            # Load index info
            info_path = self.index_path / "info.json"
            if not info_path.exists():
                return False
            
            with open(info_path, 'r') as f:
                info = json.load(f)
            
            dimension = info["dimension"]
            
            # Load FAISS index
            faiss_path = self.index_path / "index.faiss"
            if faiss_path.exists():
                import faiss
                self.index = faiss.read_index(str(faiss_path))
                logger.info(f"Loaded FAISS index from {faiss_path}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def get_stats(self) -> Dict:
        """Get statistics about the store"""
        return {
            "num_chunks": len(self.chunks),
            "index_loaded": self.index is not None,
            "dimension": self.embeddings.shape[1] if self.embeddings is not None else None
        }

