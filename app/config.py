from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    api_title: str = "NexTraction Web RAG API"
    api_version: str = "1.0.0"
    
    # Embedding Configuration
    embedding_provider: str = "openai"  # openai, gemini, local
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None  # For proxy support
    gemini_api_key: Optional[str] = None
    
    # Vector Store Configuration
    vector_store_type: str = "faiss"  # faiss, pgvector
    faiss_index_path: str = "./data/faiss_index"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5
    
    # LLM Configuration
    llm_provider: str = "openai"  # openai, gemini
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 1000
    
    # Web Fetching Configuration
    fetch_timeout: int = 10
    fetch_max_retries: int = 3
    fetch_user_agent: str = "NexTraction-Bot/1.0 (Research Tool)"
    fetch_rate_limit: float = 1.0  # seconds between requests
    
    # Storage Configuration
    data_dir: str = "./data"
    chunks_dir: str = "./data/chunks"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"  # json, text
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

