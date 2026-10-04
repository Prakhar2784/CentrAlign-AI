import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    APP_NAME: str = "CentrAlign AI - Autonomous Task Worker"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    DATABASE_URL: str = "sqlite:///./centralign_task_worker.db"
    
    # LLM Settings
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "auto"  # 'gemini', 'openai', 'mock', 'auto'
    LLM_MODEL: str = "gemini-2.5-flash"
    
    # Demo and Failure simulation triggers
    FAIL_FIRST_UPDATE: bool = False
    FAIL_VERIFICATION: bool = False
    
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "*"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()
