#!/usr/bin/env python3
"""
Sistema de Orquestração RPA - BGTELECOM
Arquivo principal do backend
Desenvolvido por: Tiago Pereira Ramos
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.database import engine, Base
from config.settings import configuracoes
from api.rotas import router_principal
from services.inicializacao_service import InicializacaoService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    print("🚀 Iniciando Sistema de Orquestração RPA BGTELECOM...")
    
    # Criar tabelas no banco
    Base.metadata.create_all(bind=engine)
    
    # Inicializar dados do sistema
    servico_inicializacao = InicializacaoService()
    await servico_inicializacao.inicializar_dados_sistema()
    
    print("✅ Sistema de Orquestração RPA BGTELECOM inicializado!")
    yield
    print("🔄 Finalizando sistema...")


app = FastAPI(
    title="Sistema de Orquestração RPA - BGTELECOM",
    description="Backend completo para gerenciamento automatizado de faturas de telecomunicações",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(router_principal, prefix="/api")

@app.get("/")
async def raiz():
    """Endpoint raiz do sistema"""
    return {
        "sistema": "Orquestrador RPA BGTELECOM",
        "versao": "1.0.0",
        "status": "ativo",
        "desenvolvido_por": "Tiago Pereira Ramos",
        "documentacao": "/docs"
    }

if __name__ == "__main__":
    print("🚀 Iniciando servidor FastAPI...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )