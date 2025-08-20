import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # API Configuration
    app_name: str = "Hormozi AI Business Advisor"
    debug: bool = False
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    embedding_model: str = "text-embedding-ada-002"
    
    # Vector Database Configuration
    chroma_persist_directory: str = "./data/chroma"
    collection_name: str = "hormozi_knowledge"
    
    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_tokens: int = 2000
    temperature: float = 0.7
    top_k_results: int = 5
    
    # Database Configuration (if needed later)
    database_url: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

