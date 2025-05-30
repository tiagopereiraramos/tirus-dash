#!/usr/bin/env python3
"""
Inicializador do Sistema RPA BGTELECOM - Apenas FastAPI
Sem dependências Express
"""
import uvicorn
import os
import sys

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    """Executa o servidor FastAPI"""
    print("🚀 Iniciando Sistema RPA BGTELECOM")
    print("📊 Backend: FastAPI (Porta 8000)")
    print("🔗 Frontend: Vite (Porta 3000)")
    print("💾 Banco: PostgreSQL")
    
    # Executar FastAPI backend
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()