"""
Configurações do sistema
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Configuracoes(BaseSettings):
    """Configurações da aplicação"""
    
    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Banco de dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/orquestrador_rpa")
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Autenticação
    SECRET_KEY: str = os.getenv("SECRET_KEY", "seu_secret_key_aqui")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MinIO/S3
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    BUCKET_NAME: str = os.getenv("BUCKET_NAME", "faturas-rpa")
    
    # Selenium
    SELENIUM_TIMEOUT: int = 30
    SELENIUM_HEADLESS: bool = True
    
    # Notificações
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # WhatsApp Evolution API
    EVOLUTION_API_URL: str = os.getenv("EVOLUTION_API_URL", "")
    EVOLUTION_API_KEY: str = os.getenv("EVOLUTION_API_KEY", "")
    
    class Config:
        env_file = ".env"


configuracoes = Configuracoes()