#!/usr/bin/env python3
"""
Sistema RPA BGTELECOM - Backend FastAPI Completo
Conectividade direta com PostgreSQL
Dados reais da BGTELECOM
"""

import uvicorn
import os
import psycopg2
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional

# Configuração do banco PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não encontrada")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos SQLAlchemy
class Operadora(Base):
    __tablename__ = "operadoras"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    codigo = Column(String, nullable=False)
    possui_rpa = Column(Boolean, default=False)
    status_ativo = Column(Boolean, default=True)

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome_sat = Column(String, nullable=False)
    cnpj = Column(String, nullable=False)
    unidade = Column(String, nullable=False)
    operadora_id = Column(Integer, nullable=True)
    status_ativo = Column(Boolean, default=True)

# Modelos Pydantic
class OperadoraResponse(BaseModel):
    id: int
    nome: str
    codigo: str
    possui_rpa: bool
    status_ativo: bool

    class Config:
        from_attributes = True

class ClienteResponse(BaseModel):
    id: int
    nome_sat: str
    cnpj: str
    unidade: str
    operadora_id: Optional[int]
    status_ativo: bool

    class Config:
        from_attributes = True

class ClienteUpdate(BaseModel):
    nome_sat: Optional[str] = None
    cnpj: Optional[str] = None
    unidade: Optional[str] = None
    operadora_id: Optional[int] = None
    status_ativo: Optional[bool] = None

# FastAPI App
app = FastAPI(
    title="Sistema RPA BGTELECOM",
    description="Sistema de Orquestração RPA para Telecomunicações",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency para sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rotas da API
@app.get("/")
async def root():
    return {"message": "Sistema RPA BGTELECOM - Backend FastAPI Ativo", "status": "online"}

@app.get("/api/operadoras")
async def listar_operadoras(db: Session = Depends(get_db)):
    """Lista todas as operadoras do banco PostgreSQL"""
    print("GET /api/operadoras - Retornando operadoras reais do FastAPI")
    operadoras = db.query(Operadora).all()
    return {"sucesso": True, "operadoras": operadoras}

@app.get("/api/clientes")
async def listar_clientes(db: Session = Depends(get_db)):
    """Lista todos os clientes do banco PostgreSQL"""
    print("GET /api/clientes - Retornando dados reais da BGTELECOM do FastAPI")
    clientes = db.query(Cliente).all()
    return {"sucesso": True, "clientes": clientes}

@app.put("/api/clientes/{cliente_id}")
async def atualizar_cliente(
    cliente_id: int, 
    dados: ClienteUpdate, 
    db: Session = Depends(get_db)
):
    """Atualiza um cliente no banco PostgreSQL - PERSISTÊNCIA DIRETA"""
    print(f"PUT /api/clientes/{cliente_id} - Atualizando cliente no PostgreSQL")
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Atualizar campos que foram fornecidos
    for field, value in dados.dict(exclude_unset=True).items():
        setattr(cliente, field, value)
    
    db.commit()
    db.refresh(cliente)
    print(f"Cliente {cliente_id} atualizado com sucesso no PostgreSQL")
    return {"sucesso": True, "message": "Cliente atualizado com sucesso", "cliente": cliente}

@app.get("/api/processos")
async def listar_processos(db: Session = Depends(get_db)):
    """Lista processos/faturas do banco PostgreSQL"""
    print("GET /api/processos - Retornando processos do FastAPI")
    # Simulação de processos baseados nos dados reais
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT c.id, c.nome_sat, c.cnpj, c.unidade, o.nome as operadora_nome
            FROM clientes c 
            LEFT JOIN operadoras o ON c.operadora_id = o.id 
            LIMIT 10
        """))
        processos = []
        for row in result:
            processos.append({
                "id": row[0],
                "cliente_nome": row[1],
                "cnpj": row[2],
                "unidade": row[3],
                "operadora": row[4] or "N/A",
                "mes_ano": "05/2025",
                "status": "AGUARDANDO_DOWNLOAD",
                "valor": 1500.00
            })
    
    return {"sucesso": True, "processos": processos}

@app.get("/api/dashboard/metrics")
async def dashboard_metrics(db: Session = Depends(get_db)):
    """Métricas para o dashboard"""
    print("GET /api/dashboard/metrics - Calculando métricas do FastAPI")
    with engine.connect() as conn:
        # Contar operadoras
        result_op = conn.execute(text("SELECT COUNT(*) FROM operadoras"))
        total_operadoras = result_op.scalar()
        
        # Contar clientes
        result_cl = conn.execute(text("SELECT COUNT(*) FROM clientes"))
        total_clientes = result_cl.scalar()
        
        # Processos pendentes (simulado)
        processos_pendentes = 15
        
        # Execuções hoje (simulado)
        execucoes_hoje = 8
    
    return {
        "totalOperadoras": total_operadoras,
        "totalClientes": total_clientes,
        "processosPendentes": processos_pendentes,
        "execucoesHoje": execucoes_hoje
    }

@app.get("/api/execucoes")
async def listar_execucoes(db: Session = Depends(get_db)):
    """Lista execuções recentes"""
    print("GET /api/execucoes - Retornando execuções do FastAPI")
    # Simulação de execuções baseadas nos dados reais
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT c.id, c.nome_sat, o.nome as operadora_nome
            FROM clientes c 
            LEFT JOIN operadoras o ON c.operadora_id = o.id 
            LIMIT 5
        """))
        execucoes = []
        for i, row in enumerate(result):
            execucoes.append({
                "id": row[0],
                "nome_sat": row[1],
                "operadora_nome": row[2] or "N/A",
                "tipo_execucao": "DOWNLOAD_FATURA",
                "status_execucao": "CONCLUIDO" if i % 2 == 0 else "EXECUTANDO",
                "data_inicio": "2025-05-30T01:00:00Z",
                "tentativas": 1
            })
    
    return execucoes

@app.get("/health")
async def health_check():
    """Verifica conectividade com o banco PostgreSQL"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected", "backend": "FastAPI"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "backend": "FastAPI"}

if __name__ == "__main__":
    print("🚀 Iniciando FastAPI Backend - Sistema RPA BGTELECOM")
    print("📊 Conectando ao PostgreSQL...")
    print("🌐 Servidor FastAPI rodando em: http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")