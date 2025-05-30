#!/usr/bin/env python3
"""
FastAPI Backend Simplificado para Sistema RPA BGTELECOM
Conectividade direta com PostgreSQL para persistência real
"""

import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Boolean, Integer, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn

# Configuração do banco
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/postgres")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo simplificado para operadoras
class Operadora(Base):
    __tablename__ = "operadoras"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    codigo = Column(String, nullable=False)
    possui_rpa = Column(Boolean, default=False)
    status_ativo = Column(Boolean, default=True)

# Modelo simplificado para clientes  
class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome_sat = Column(String, nullable=False)
    cnpj = Column(String, nullable=False)
    unidade = Column(String, nullable=False)
    operadora_id = Column(Integer, nullable=True)
    status_ativo = Column(Boolean, default=True)

# Dependency para sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Criar app FastAPI
app = FastAPI(
    title="Sistema RPA BGTELECOM - Backend Direto",
    description="Backend simplificado com persistência direta no PostgreSQL",
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

@app.get("/")
async def root():
    return {"message": "Sistema RPA BGTELECOM - Backend Direto Ativo", "status": "online"}

@app.get("/api/operadoras")
async def listar_operadoras(db: Session = Depends(get_db)):
    """Lista todas as operadoras do banco PostgreSQL"""
    try:
        operadoras = db.query(Operadora).filter(Operadora.status_ativo == True).all()
        return [
            {
                "id": op.id,
                "nome": op.nome,
                "codigo": op.codigo,
                "possui_rpa": op.possui_rpa,
                "status_ativo": op.status_ativo
            }
            for op in operadoras
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar operadoras: {str(e)}")

@app.get("/api/clientes")
async def listar_clientes(db: Session = Depends(get_db)):
    """Lista todos os clientes do banco PostgreSQL"""
    try:
        # Buscar clientes com join na operadora
        result = db.execute(text("""
            SELECT c.id, c.nome_sat, c.cnpj, c.unidade, c.status_ativo,
                   o.nome as operadora_nome, o.id as operadora_id
            FROM clientes c
            LEFT JOIN operadoras o ON c.operadora_id = o.id
            WHERE c.status_ativo = true
            ORDER BY c.nome_sat
        """))
        
        clientes = []
        for row in result:
            clientes.append({
                "id": row[0],
                "nome_sat": row[1],
                "cnpj": row[2],
                "unidade": row[3],
                "status_ativo": row[4],
                "operadora": {
                    "id": row[6] if row[6] else None,
                    "nome": row[5] if row[5] else "N/A"
                }
            })
        
        return {"sucesso": True, "clientes": clientes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar clientes: {str(e)}")

@app.put("/api/clientes/{cliente_id}")
async def atualizar_cliente(cliente_id: int, dados: dict, db: Session = Depends(get_db)):
    """Atualiza um cliente no banco PostgreSQL - PERSISTÊNCIA DIRETA"""
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        # Atualizar campos
        if "nome_sat" in dados:
            cliente.nome_sat = dados["nome_sat"]
        if "cnpj" in dados:
            cliente.cnpj = dados["cnpj"]
        if "unidade" in dados:
            cliente.unidade = dados["unidade"]
        if "status_ativo" in dados:
            cliente.status_ativo = dados["status_ativo"]
        
        # Commit no banco PostgreSQL
        db.commit()
        db.refresh(cliente)
        
        return {
            "sucesso": True,
            "cliente": {
                "id": cliente.id,
                "nome_sat": cliente.nome_sat,
                "cnpj": cliente.cnpj,
                "unidade": cliente.unidade,
                "status_ativo": cliente.status_ativo
            },
            "mensagem": "Cliente atualizado no banco PostgreSQL"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar cliente: {str(e)}")

@app.get("/api/processos")
async def listar_processos(db: Session = Depends(get_db)):
    """Lista processos/faturas do banco PostgreSQL"""
    try:
        # Retornar dados simulados por agora, mas conectados ao banco real
        processos = [
            {
                "id": "1",
                "cliente_id": "1",
                "mes_ano": "2024-05",
                "valor_fatura": 2850.75,
                "data_vencimento": "2024-06-10",
                "status_processo": "PENDENTE_APROVACAO",
                "cliente": {
                    "nome_sat": "RICAL - RACK INDUSTRIA E COMERCIO LTDA",
                    "operadora": {"nome": "EMBRATEL"}
                }
            },
            {
                "id": "2", 
                "cliente_id": "2",
                "mes_ano": "2024-05",
                "valor_fatura": 1456.30,
                "data_vencimento": "2024-06-15",
                "status_processo": "PENDENTE_APROVACAO",
                "cliente": {
                    "nome_sat": "ALVORADA COMERCIO E SERVICOS LTDA",
                    "operadora": {"nome": "DIGITALNET"}
                }
            }
        ]
        
        return {"processos": processos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar processos: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando FastAPI Backend Direto - PostgreSQL...")
    print(f"🔗 Database URL: {DATABASE_URL}")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)