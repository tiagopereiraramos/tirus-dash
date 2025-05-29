#!/usr/bin/env python3
"""
Inicialização do Backend FastAPI
Sistema de Orquestração RPA - BGTELECOM
"""

import os
import sys
import uvicorn
from pathlib import Path

# Adicionar diretório backend ao Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Configurar ambiente
os.environ.setdefault("DATABASE_URL", os.getenv("DATABASE_URL", ""))
os.environ.setdefault("SECRET_KEY", "rpa-bgtelecom-secret-key-2024")

def main():
    """Inicia o servidor FastAPI na porta 8000"""
    
    print("🚀 Sistema de Orquestração RPA - BGTELECOM")
    print("📊 Backend FastAPI: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")
    print("🔗 Frontend React: http://localhost:5000")
    
    # Usar o backend FastAPI completo implementado
    from backend.main import app
    
    # Iniciar servidor
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()