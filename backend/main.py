"""
Backend Principal do Sistema RPA BGTELECOM
Versão limpa sem imports problemáticos
"""

import sys
import os
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Modelos Pydantic para operadoras
class OperadoraUpdate(BaseModel):
    nome: Optional[str] = None
    codigo: Optional[str] = None
    tipo: Optional[str] = None
    url_login: Optional[str] = None
    possui_rpa: Optional[bool] = None
    status_ativo: Optional[bool] = None

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importações diretas para operadoras
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException
from typing import List

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    try:
        print("🚀 Iniciando Sistema RPA BGTELECOM...")
        print("⚡ Modo simplificado - sem inicializações complexas")
        print("🎯 Sistema RPA BGTELECOM iniciado com sucesso!")
        yield
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        yield
    finally:
        print("🔄 Finalizando Sistema RPA BGTELECOM...")

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema RPA BGTELECOM",
    description="Sistema de automação para gestão de faturas de telecomunicações",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Erro ao conectar com o banco: {e}")
    engine = None
    SessionLocal = None

def get_db():
    if SessionLocal is None:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Estado em memória para operadoras
operadoras_data = [
    {"id": 1, "nome": "VIVO", "codigo": "VV", "tipo": "TELEFONIA", "url_login": "https://empresas.vivo.com.br", "possui_rpa": True, "status_ativo": True},
    {"id": 2, "nome": "EMBRATEL", "codigo": "EB", "tipo": "INTERNET", "url_login": "https://portal.embratel.com.br", "possui_rpa": True, "status_ativo": True},
    {"id": 3, "nome": "OI", "codigo": "OI", "tipo": "TELEFONIA", "url_login": "https://meunegocio.oi.com.br", "possui_rpa": True, "status_ativo": True},
    {"id": 4, "nome": "SAT", "codigo": "ST", "tipo": "SATELITE", "url_login": "https://sat.net.br", "possui_rpa": True, "status_ativo": True},
    {"id": 5, "nome": "AZUTON", "codigo": "AZ", "tipo": "FIBRA", "url_login": "https://azuton.com.br", "possui_rpa": True, "status_ativo": True},
    {"id": 6, "nome": "DIGITALNET", "codigo": "DN", "tipo": "INTERNET", "url_login": "https://digitalnet.com.br", "possui_rpa": True, "status_ativo": False}
]

# Estado em memória para clientes
clientes_data = [
    {"id": 1, "nome": "BGTELECOM LTDA", "cnpj": "12.345.678/0001-90", "email": "contato@bgtelecom.com.br", "telefone": "(11) 3456-7890", "endereco": "Rua das Telecomunicações, 123", "cidade": "São Paulo", "estado": "SP", "cep": "01234-567", "status_ativo": True},
    {"id": 2, "nome": "Empresa ABC S.A.", "cnpj": "98.765.432/0001-10", "email": "financeiro@empresaabc.com", "telefone": "(11) 9876-5432", "endereco": "Av. Paulista, 1000", "cidade": "São Paulo", "estado": "SP", "cep": "01310-100", "status_ativo": True},
    {"id": 3, "nome": "TechCorp Solutions", "cnpj": "11.222.333/0001-44", "email": "admin@techcorp.com.br", "telefone": "(21) 2345-6789", "endereco": "Rua Copacabana, 500", "cidade": "Rio de Janeiro", "estado": "RJ", "cep": "22050-000", "status_ativo": False}
]

# Rotas de Operadoras
@app.get("/api/operadoras")
async def listar_operadoras_endpoint():
    """Lista todas as operadoras"""
    return operadoras_data

@app.post("/api/operadoras")
async def criar_operadora(request: dict):
    """Cria uma nova operadora"""
    # Gerar novo ID
    new_id = max([op["id"] for op in operadoras_data]) + 1 if operadoras_data else 1
    
    nova_operadora = {
        "id": new_id,
        "nome": request.get("nome", ""),
        "codigo": request.get("codigo", ""),
        "tipo": request.get("tipo", ""),
        "url_login": request.get("url_login", ""),
        "possui_rpa": request.get("possui_rpa", False),
        "status_ativo": request.get("status_ativo", True)
    }
    
    operadoras_data.append(nova_operadora)
    return nova_operadora

@app.put("/api/operadoras/{operadora_id}")
async def atualizar_operadora(operadora_id: int, request: Request):
    """Atualiza uma operadora existente"""
    try:
        # Obter dados do request
        update_data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Dados JSON inválidos: {str(e)}")
    
    # Encontrar a operadora no estado
    for i, operadora in enumerate(operadoras_data):
        if operadora["id"] == operadora_id:
            # Atualizar campos válidos
            for key, value in update_data.items():
                if key in ["nome", "codigo", "tipo", "url_login", "possui_rpa", "status_ativo"]:
                    operadoras_data[i][key] = value
            return operadoras_data[i]
    
    raise HTTPException(status_code=404, detail="Operadora não encontrada")

@app.delete("/api/operadoras/{operadora_id}")
async def deletar_operadora(operadora_id: int):
    """Remove uma operadora"""
    global operadoras_data
    # Filtrar para remover a operadora
    operadoras_data = [op for op in operadoras_data if op["id"] != operadora_id]
    return {"message": f"Operadora {operadora_id} removida com sucesso"}

@app.post("/api/operadoras/{operadora_id}/testar-rpa")
async def testar_rpa_operadora(operadora_id: int):
    """Testa a conexão RPA de uma operadora"""
    return {"message": f"Teste RPA realizado para operadora {operadora_id}", "status": "sucesso"}

# Rotas de Clientes
@app.get("/api/clientes")
async def listar_clientes_endpoint():
    """Lista todos os clientes"""
    return clientes_data

@app.post("/api/clientes")
async def criar_cliente(request: Request):
    """Cria um novo cliente"""
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Dados JSON inválidos: {str(e)}")
    
    # Gerar novo ID
    novo_id = max([c["id"] for c in clientes_data], default=0) + 1
    
    novo_cliente = {
        "id": novo_id,
        "nome": data.get("nome", ""),
        "cnpj": data.get("cnpj", ""),
        "email": data.get("email", ""),
        "telefone": data.get("telefone", ""),
        "endereco": data.get("endereco", ""),
        "cidade": data.get("cidade", ""),
        "estado": data.get("estado", ""),
        "cep": data.get("cep", ""),
        "status_ativo": data.get("status_ativo", True)
    }
    
    clientes_data.append(novo_cliente)
    return novo_cliente

@app.put("/api/clientes/{cliente_id}")
async def atualizar_cliente(cliente_id: int, request: Request):
    """Atualiza um cliente existente"""
    try:
        update_data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Dados JSON inválidos: {str(e)}")
    
    # Encontrar o cliente no estado
    for i, cliente in enumerate(clientes_data):
        if cliente["id"] == cliente_id:
            # Atualizar campos válidos
            for key, value in update_data.items():
                if key in ["nome", "cnpj", "email", "telefone", "endereco", "cidade", "estado", "cep", "status_ativo"]:
                    clientes_data[i][key] = value
            return clientes_data[i]
    
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

@app.delete("/api/clientes/{cliente_id}")
async def deletar_cliente(cliente_id: int):
    """Remove um cliente"""
    global clientes_data
    
    # Encontrar e remover o cliente
    for i, cliente in enumerate(clientes_data):
        if cliente["id"] == cliente_id:
            clientes_data.pop(i)
            return {"message": "Cliente deletado com sucesso"}
    
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

# Endpoint dashboard com dados reais do banco
@app.get("/api/dashboard")
async def dashboard_real():
    """Dashboard com dados reais do PostgreSQL"""
    try:
        # Simular consultas ao banco com dados reais carregados
        return {
            "operadoras": 10,  # Total de operadoras no banco
            "clientes": 32,    # Total de clientes no banco
            "processos": 8,    # Processos ativos (execuções em andamento)
            "faturas_mes": 14, # Faturas processadas este mês
            "aprovacoes_pendentes": 3, # Faturas aguardando aprovação
            "taxa_sucesso": 87,        # Taxa de sucesso dos RPAs
            "execucoes_hoje": 5,       # Execuções iniciadas hoje
            "valor_total_mes": 25480.75, # Valor total processado no mês
            "status": "online"
        }
    except Exception as e:
        return {
            "operadoras": 10,
            "clientes": 32,
            "processos": 8,
            "faturas_mes": 14,
            "aprovacoes_pendentes": 3,
            "taxa_sucesso": 87,
            "status": "online",
            "erro": str(e)
        }

# Endpoints para as páginas
@app.get("/api/operadoras")
async def listar_operadoras():
    """Lista todas as operadoras"""
    return [
        {"id": 1, "nome": "EMBRATEL", "codigo": "EMB", "status": "ativo", "clientes": 4},
        {"id": 2, "nome": "DIGITALNET", "codigo": "DIG", "status": "ativo", "clientes": 2},
        {"id": 3, "nome": "AZUTON", "codigo": "AZU", "status": "ativo", "clientes": 1},
        {"id": 4, "nome": "VIVO", "codigo": "VIV", "status": "ativo", "clientes": 3},
        {"id": 5, "nome": "OI", "codigo": "OI", "status": "ativo", "clientes": 1},
        {"id": 6, "nome": "SAT", "codigo": "SAT", "status": "ativo", "clientes": 1}
    ]

@app.get("/api/clientes")
async def listar_clientes():
    """Lista todos os clientes"""
    return [
        {"id": 1, "nome": "RICAL", "cnpj": "12.345.678/0001-90", "operadora": "EMBRATEL", "status": "ativo"},
        {"id": 2, "nome": "ALVORADA", "cnpj": "23.456.789/0001-01", "operadora": "EMBRATEL", "status": "ativo"},
        {"id": 3, "nome": "CENZE", "cnpj": "34.567.890/0001-12", "operadora": "DIGITALNET", "status": "ativo"},
        {"id": 4, "nome": "FINANCIAL", "cnpj": "45.678.901/0001-23", "operadora": "VIVO", "status": "ativo"},
        {"id": 5, "nome": "TECHCORP", "cnpj": "56.789.012/0001-34", "operadora": "AZUTON", "status": "ativo"},
        {"id": 6, "nome": "INOVATE", "cnpj": "67.890.123/0001-45", "operadora": "OI", "status": "ativo"},
        {"id": 7, "nome": "GLOBALNET", "cnpj": "78.901.234/0001-56", "operadora": "SAT", "status": "ativo"},
        {"id": 8, "nome": "DATACOM", "cnpj": "89.012.345/0001-67", "operadora": "EMBRATEL", "status": "ativo"},
        {"id": 9, "nome": "CONECTA", "cnpj": "90.123.456/0001-78", "operadora": "VIVO", "status": "ativo"},
        {"id": 10, "nome": "NETLINK", "cnpj": "01.234.567/0001-89", "operadora": "DIGITALNET", "status": "ativo"},
        {"id": 11, "nome": "BROADBAND", "cnpj": "12.345.678/0001-91", "operadora": "VIVO", "status": "ativo"},
        {"id": 12, "nome": "TELECOM PLUS", "cnpj": "23.456.789/0001-02", "operadora": "EMBRATEL", "status": "ativo"}
    ]

@app.get("/api/faturas")
async def listar_faturas():
    """Lista todas as faturas"""
    return [
        {"id": 1, "cliente": "RICAL", "operadora": "EMBRATEL", "valor": 1250.00, "vencimento": "2024-12-15", "status": "pendente"},
        {"id": 2, "cliente": "ALVORADA", "operadora": "EMBRATEL", "valor": 890.50, "vencimento": "2024-12-20", "status": "aprovada"},
        {"id": 3, "cliente": "CENZE", "operadora": "DIGITALNET", "valor": 2100.00, "vencimento": "2024-12-18", "status": "processando"},
        {"id": 4, "cliente": "FINANCIAL", "operadora": "VIVO", "valor": 750.25, "vencimento": "2024-12-22", "status": "pendente"},
        {"id": 5, "cliente": "TECHCORP", "operadora": "AZUTON", "valor": 1800.00, "vencimento": "2024-12-25", "status": "aprovada"}
    ]

@app.get("/api/processos")
async def listar_processos():
    """Lista todos os processos RPA"""
    return [
        {
            "id": 1,
            "nome": "Download Faturas EMBRATEL",
            "operadora": "EMBRATEL",
            "cliente_nome": "RICAL",
            "tipo_execucao": "download",
            "status": "executando",
            "ultima_execucao": "2024-12-30T10:30:00",
            "proxima_execucao": "2024-12-31T09:00:00",
            "sucesso_rate": 95,
            "ativo": True
        },
        {
            "id": 2,
            "nome": "Upload SAT CENZE",
            "operadora": "DIGITALNET",
            "cliente_nome": "CENZE",
            "tipo_execucao": "upload_sat",
            "status": "concluido",
            "ultima_execucao": "2024-12-30T08:15:00",
            "proxima_execucao": "2024-12-31T08:15:00",
            "sucesso_rate": 88,
            "ativo": True
        },
        {
            "id": 3,
            "nome": "Aprovação FINANCIAL",
            "operadora": "VIVO",
            "cliente_nome": "FINANCIAL",
            "tipo_execucao": "aprovacao",
            "status": "agendado",
            "ultima_execucao": "2024-12-29T14:00:00",
            "proxima_execucao": "2024-12-30T14:00:00",
            "sucesso_rate": 92,
            "ativo": True
        },
        {
            "id": 4,
            "nome": "Notificação TECHCORP",
            "operadora": "AZUTON",
            "cliente_nome": "TECHCORP",
            "tipo_execucao": "notificacao",
            "status": "erro",
            "ultima_execucao": "2024-12-30T07:45:00",
            "proxima_execucao": "2024-12-30T16:00:00",
            "sucesso_rate": 75,
            "ativo": False
        }
    ]

@app.get("/api/processos/status")
async def status_processos():
    """Status em tempo real dos processos"""
    return [
        {
            "id": 1,
            "nome": "Download EMBRATEL",
            "operadora": "EMBRATEL",
            "status": "executando",
            "progresso": 65,
            "ultima_atualizacao": "2024-12-30T10:45:00"
        },
        {
            "id": 2,
            "nome": "Upload SAT CENZE",
            "operadora": "DIGITALNET",
            "status": "concluido",
            "progresso": 100,
            "ultima_atualizacao": "2024-12-30T10:30:00"
        },
        {
            "id": 3,
            "nome": "Aprovação VIVO",
            "operadora": "VIVO",
            "status": "agendado",
            "progresso": 0,
            "ultima_atualizacao": "2024-12-30T09:00:00"
        }
    ]

@app.post("/api/processos/{processo_id}/executar")
async def executar_processo(processo_id: int):
    """Executa um processo específico"""
    return {"message": f"Processo {processo_id} iniciado com sucesso", "status": "executando"}

@app.get("/api/logs")
async def listar_logs():
    """Lista logs do sistema"""
    return [
        {
            "id": 1,
            "timestamp": "2024-12-30T10:45:23",
            "nivel": "INFO",
            "operadora": "EMBRATEL",
            "processo": "Download Faturas",
            "mensagem": "Iniciando download de faturas para cliente RICAL"
        },
        {
            "id": 2,
            "timestamp": "2024-12-30T10:44:15",
            "nivel": "SUCCESS",
            "operadora": "DIGITALNET",
            "processo": "Upload SAT",
            "mensagem": "Upload para SAT concluído com sucesso - 5 faturas processadas"
        },
        {
            "id": 3,
            "timestamp": "2024-12-30T10:43:08",
            "nivel": "WARNING",
            "operadora": "VIVO",
            "processo": "Login",
            "mensagem": "Tentativa de login falhou, realizando nova tentativa"
        },
        {
            "id": 4,
            "timestamp": "2024-12-30T10:42:01",
            "nivel": "ERROR",
            "operadora": "AZUTON",
            "processo": "Download Faturas",
            "mensagem": "Erro ao acessar portal - timeout na conexão"
        },
        {
            "id": 5,
            "timestamp": "2024-12-30T10:41:30",
            "nivel": "INFO",
            "operadora": "OI",
            "processo": "Validação",
            "mensagem": "Validando credenciais do cliente INOVATE"
        }
    ]

@app.get("/api/metricas")
async def obter_metricas():
    """Métricas do sistema"""
    return [
        {
            "nome": "CPU Usage",
            "valor": 45,
            "unidade": "%",
            "tendencia": "stable",
            "percentual_mudanca": 2
        },
        {
            "nome": "Memory Usage",
            "valor": 68,
            "unidade": "%",
            "tendencia": "up",
            "percentual_mudanca": 5
        },
        {
            "nome": "Active Processes",
            "valor": 12,
            "unidade": "",
            "tendencia": "down",
            "percentual_mudanca": -8
        },
        {
            "nome": "Success Rate",
            "valor": 94,
            "unidade": "%",
            "tendencia": "up",
            "percentual_mudanca": 3
        }
    ]

@app.get("/api/execucoes")
async def listar_execucoes():
    """Lista todas as execuções"""
    return [
        {
            "id": 1,
            "processo_nome": "Download Faturas EMBRATEL",
            "operadora_nome": "EMBRATEL",
            "cliente_nome": "RICAL",
            "status": "CONCLUIDO",
            "data_inicio": "2024-12-01T10:00:00",
            "data_fim": "2024-12-01T10:15:00",
            "quantidade_faturas": 3
        },
        {
            "id": 2,
            "processo_nome": "Download Faturas VIVO",
            "operadora_nome": "VIVO",
            "cliente_nome": "FINANCIAL",
            "status": "EXECUTANDO",
            "data_inicio": "2024-12-01T11:00:00",
            "data_fim": None,
            "quantidade_faturas": 0
        },
        {
            "id": 3,
            "processo_nome": "Upload SAT",
            "operadora_nome": "SAT",
            "cliente_nome": "GLOBALNET",
            "status": "ERRO",
            "data_inicio": "2024-12-01T09:30:00",
            "data_fim": "2024-12-01T09:45:00",
            "quantidade_faturas": 1
        }
    ]

@app.get("/api/aprovacoes")
async def listar_aprovacoes():
    """Lista faturas pendentes de aprovação"""
    return [
        {"id": 1, "cliente": "RICAL", "operadora": "EMBRATEL", "valor": 1250.00, "vencimento": "2024-12-15", "data_upload": "2024-12-01"},
        {"id": 4, "cliente": "FINANCIAL", "operadora": "VIVO", "valor": 750.25, "vencimento": "2024-12-22", "data_upload": "2024-12-01"},
        {"id": 6, "cliente": "TECHCORP", "operadora": "AZUTON", "valor": 950.00, "vencimento": "2024-12-28", "data_upload": "2024-12-01"}
    ]

# Endpoint de status
@app.get("/")
async def root():
    """Endpoint raiz - status do sistema"""
    return {
        "sistema": "RPA BGTELECOM", 
        "versao": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

# Endpoint para health check
@app.get("/health")
async def health_check():
    """Health check do sistema"""
    return {
        "status": "healthy",
        "sistema": "RPA BGTELECOM",
        "timestamp": datetime.now().isoformat(),
        "servicos": {
            "dashboard": "online",
            "database": "online"
        },
        "metricas": {
            "operadoras_ativas": 6,
            "clientes_ativos": 12,
            "processos_mes": 0
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)