#!/usr/bin/env python3
"""
Script de inicialização do backend FastAPI
Sistema de Orquestração RPA - BGTELECOM
"""

import os
import sys
import uvicorn
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Função principal para iniciar o servidor"""
    
    # Configurar variáveis de ambiente se não estiverem definidas
    if not os.getenv("DATABASE_URL"):
        print("⚠️ DATABASE_URL não definida, usando PostgreSQL padrão")
        os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5432/orquestrador_rpa"
    
    # Importar a aplicação
    from main import app
    
    print("🚀 Iniciando Sistema de Orquestração RPA - BGTELECOM")
    print("📊 Backend FastAPI na porta 8000")
    print("🔗 Frontend React na porta 5000")
    print("📖 Documentação: http://localhost:8000/docs")
    
    # Iniciar servidor
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Desabilitado para produção
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()