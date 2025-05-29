#!/usr/bin/env python3
"""
Iniciador do Backend com Integração Completa
Sistema RPA BGTELECOM - Dados Reais
"""

import os
import sys
import uvicorn
from backend.main_postgresql import app

if __name__ == "__main__":
    print("🚀 Iniciando Backend RPA BGTELECOM com dados reais...")
    print("📊 PostgreSQL conectado com dados autênticos")
    print("🔗 API disponível em: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n⚡ Backend finalizado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")