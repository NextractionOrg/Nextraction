import os
from typing import List, Optional
import numpy as np
from app.config import settings
from app.utils.logger import logger


class EmbeddingService:
    """Service for generating embeddings"""
    
    def __init__(self):
        self.embedding_provider = settings.embedding_provider
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dimension
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the embedding client based on provider"""
        if self.embedding_provider == "openai":
            try:
                from openai import AsyncOpenAI
                api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning("No OpenAI API key found, falling back to local")
                    self.embedding_provider = "local"
                else:
                    base_url = settings.openai_base_url or None
                    self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
                    logger.info("Initialized OpenAI embedding client")
            except ImportError:
                logger.warning("OpenAI library not installed, falling back to local")
                self.embedding_provider = "local"
        
        elif self.embedding_provider == "gemini":
            try:
                import google.generativeai as genai
                api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
                genai.configure(api_key=api_key)
                self._client = genai
                logger.info("Initialized Gemini embedding client")
            except ImportError:
                logger.warning("Gemini library not installed, falling back to local")
                self.embedding_provider = "local"
        
        if self.embedding_provider == "local":
            self._initialize_local_embedding()
    
    def _initialize_local_embedding(self):
        """Initialize local embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            # Use a lightweight model
            model_name = "all-MiniLM-L6-v2"  # 384 dimensions
            self._client = SentenceTransformer(model_name)
            self.dimension = 384  # Override for this model
            logger.info(f"Initialized local embedding model: {model_name}")
        except ImportError:
            logger.error("No embedding provider available. Install sentence-transformers for local embeddings")
            raise RuntimeError("No embedding provider available. Install sentence-transformers: pip install sentence-transformers")
    
    async def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        if not texts:
            return np.array([])
        
        if self.embedding_provider == "openai":
            return await self._embed_openai(texts)
        elif self.embedding_provider == "gemini":
            return await self._embed_gemini(texts)
        elif self.embedding_provider == "local":
            return self._embed_local(texts)
        else:
            raise ValueError(f"Unknown embedding provider: {self.embedding_provider}")
    
    async def _embed_openai(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using OpenAI"""
        try:
            response = await self._client.embeddings.create(
                model=self.model,
                input=texts
            )
            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings)
        except Exception as e:
            error_str = str(e).lower()
            # Check for quota/rate limit errors
            if "429" in error_str or "insufficient_quota" in error_str or "rate_limit" in error_str:
                logger.warning(f"OpenAI quota/rate limit exceeded: {str(e)}. Falling back to local embeddings.")
                # Switch to local embeddings
                self.embedding_provider = "local"
                self._initialize_local_embedding()
                return self._embed_local(texts)
            else:
                # Re-raise other errors
                logger.error(f"OpenAI embedding error: {str(e)}")
                raise
    
    async def _embed_gemini(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using Gemini"""
        # Gemini embedding API
        embeddings = []
        for text in texts:
            result = self._client.embed_content(
                model=f"models/{self.model}",
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
        return np.array(embeddings)
    
    def _embed_local(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using local model"""
        embeddings = self._client.encode(texts, show_progress_bar=False)
        return np.array(embeddings)
    
    async def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query"""
        embeddings = await self.embed_texts([query])
        return embeddings[0] if len(embeddings) > 0 else np.array([])

