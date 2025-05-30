#!/usr/bin/env python3
"""
Inicializador simplificado do Sistema RPA BGTELECOM
Executa apenas o FastAPI backend
"""
import uvicorn
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    print("Iniciando Sistema RPA BGTELECOM - FastAPI Backend")
    print("Porta: 8000")
    print("Documentação: http://localhost:8000/docs")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )