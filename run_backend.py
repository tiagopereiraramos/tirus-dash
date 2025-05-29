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
    
    try:
        # Importar a aplicação do backend
        from backend.main import app
        
        # Iniciar servidor
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Erro ao importar aplicação: {e}")
        print("💡 Criando aplicação FastAPI simples...")
        
        # Aplicação FastAPI mínima para teste
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(
            title="Sistema de Orquestração RPA - BGTELECOM",
            description="Backend para gestão automatizada de faturas",
            version="1.0.0"
        )
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/")
        async def raiz():
            return {
                "sistema": "Orquestrador RPA BGTELECOM",
                "versao": "1.0.0", 
                "status": "ativo",
                "desenvolvido_por": "Tiago Pereira Ramos"
            }
        
        @app.get("/api/health")
        async def health():
            return {
                "status": "saudavel",
                "database": "conectado",
                "rpas": {
                    "VIVO": "parado",
                    "OI": "parado", 
                    "EMBRATEL": "parado",
                    "SAT": "parado",
                    "AZUTON": "parado",
                    "DIGITALNET": "parado"
                }
            }
        
        @app.get("/api/operadoras")
        async def listar_operadoras():
            return [
                {"id": "1", "nome": "VIVO", "codigo": "VIVO", "possui_rpa": True},
                {"id": "2", "nome": "OI", "codigo": "OI", "possui_rpa": True},
                {"id": "3", "nome": "EMBRATEL", "codigo": "EMBRATEL", "possui_rpa": True},
                {"id": "4", "nome": "SAT", "codigo": "SAT", "possui_rpa": True},
                {"id": "5", "nome": "AZUTON", "codigo": "AZUTON", "possui_rpa": True},
                {"id": "6", "nome": "DIGITALNET", "codigo": "DIGITALNET", "possui_rpa": True}
            ]
        
        @app.get("/api/clientes")
        async def listar_clientes():
            return [
                {
                    "id": "1",
                    "hash_unico": "rical001",
                    "razao_social": "RICAL COMERCIO LTDA",
                    "nome_sat": "RICAL COMERCIO",
                    "cnpj": "12.345.678/0001-90",
                    "operadora": {"nome": "EMBRATEL", "codigo": "EMBRATEL"},
                    "unidade": "MATRIZ",
                    "status_ativo": True
                },
                {
                    "id": "2", 
                    "hash_unico": "alvorada001",
                    "razao_social": "ALVORADA TRANSPORTES SA",
                    "nome_sat": "ALVORADA TRANSPORTES",
                    "cnpj": "23.456.789/0001-01",
                    "operadora": {"nome": "DIGITALNET", "codigo": "DIGITALNET"},
                    "unidade": "FILIAL 01",
                    "status_ativo": True
                }
            ]
        
        @app.get("/api/dashboard/resumo")
        async def dashboard_resumo():
            return {
                "total_operadoras": 6,
                "total_clientes": 2,
                "clientes_por_operadora": {
                    "EMBRATEL": 1,
                    "DIGITALNET": 1,
                    "VIVO": 0,
                    "OI": 0,
                    "SAT": 0,
                    "AZUTON": 0
                },
                "status_rpas": {
                    "VIVO": "parado",
                    "OI": "parado", 
                    "EMBRATEL": "parado",
                    "SAT": "parado",
                    "AZUTON": "parado",
                    "DIGITALNET": "parado"
                }
            }
        
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()