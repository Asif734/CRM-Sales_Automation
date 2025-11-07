from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration"""
    
    # App Info
    app_name: str = "AI Sales Campaign CRM"
    app_version: str = "1.0.0"
    environment: str = "development"
    
    # Groq LLM
    groq_api_key: str
    groq_model: str = "mixtral-8x7b-32768"
    groq_temperature: float = 0.7
    groq_max_tokens: int = 1024
    
    # SMTP
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    smtp_from_email: str = "sales@yourcompany.com"
    smtp_from_name: str = "Sales Team"
    
    # File Paths
    leads_input_path: str = "./data/leads.csv"
    leads_output_path: str = "./data/leads_processed.csv"
    report_output_dir: str = "./reports"
    
    # Processing
    batch_size: int = 5
    max_retries: int = 3
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()