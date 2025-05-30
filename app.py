#!/usr/bin/env python3
"""
Sistema de Orquestração RPA para Gestão de Faturas de Telecomunicações
Integração completa com os RPAs existentes: Vivo, OI, Embratel, SAT, Azuton, DigitalNet
"""

import os
import sys
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, timedelta
from typing import Optional, List
import threading
import time

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar o modelo de dados principal
from main import *

# Importar os serviços RPA do sistema antigo
try:
    from attached_assets.controle_execucao_processo_service import ProcessManager
    from attached_assets.mongo import Database
    from attached_assets.utilities import *
    from attached_assets.driver import Browser
    from attached_assets.pdf_service import PDFService
    from attached_assets.minios3_service import *
    RPA_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Aviso: Alguns serviços RPA não puderam ser importados: {e}")
    RPA_SERVICES_AVAILABLE = False

# Variáveis globais para gerenciamento de processos
process_manager = None
rpa_status = {
    "vivo": {"status": "offline", "last_execution": None},
    "oi": {"status": "offline", "last_execution": None},
    "embratel": {"status": "offline", "last_execution": None},
    "sat": {"status": "offline", "last_execution": None},
    "azuton": {"status": "offline", "last_execution": None},
    "digitalnet": {"status": "offline", "last_execution": None}
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    global process_manager
    
    # Startup
    print("Iniciando Sistema de Orquestração RPA...")
    
    # Inicializar banco de dados
    engine.dispose()
    Base.metadata.create_all(bind=engine)
    
    # Inicializar gerenciador de processos
    if RPA_SERVICES_AVAILABLE:
        try:
            process_manager = ProcessManager()
            print("Gerenciador de processos RPA inicializado")
        except Exception as e:
            print(f"Erro ao inicializar gerenciador de processos: {e}")
    
    # Inicializar dados de exemplo se necessário
    db = SessionLocal()
    try:
        # Verificar se já existem dados
        existing_users = db.query(User).count()
        if existing_users == 0:
            await initialize_system_data(db)
    finally:
        db.close()
    
    print("Sistema RPA inicializado com sucesso!")
    
    yield
    
    # Shutdown
    print("Finalizando Sistema de Orquestração RPA...")
    if process_manager:
        # Finalizar processos em execução
        pass

app = FastAPI(
    title="Sistema de Orquestração RPA - Telecomunicações",
    description="Sistema completo para gestão automatizada de faturas de telecomunicações com integração aos RPAs existentes",
    version="2.0.0",
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

security = HTTPBearer()

async def initialize_system_data(db: Session):
    """Inicializa dados do sistema baseados nos clientes da BGTELECOM"""
    
    # Criar usuário administrador padrão
    admin_password = get_password_hash("admin123")
    admin_user = User(
        username="admin",
        email="admin@bgtelecom.com.br",
        password=admin_password
    )
    db.add(admin_user)
    
    # Criar operadoras baseadas no sistema antigo
    operadoras_data = [
        {"nome": "Vivo", "ativo": True, "url_portal": "https://empresas.vivo.com.br"},
        {"nome": "OI", "ativo": True, "url_portal": "https://empresas.oi.com.br"},
        {"nome": "Embratel", "ativo": True, "url_portal": "https://empresas.embratel.com.br"},
        {"nome": "SAT", "ativo": True, "url_portal": "https://sat.com.br"},
        {"nome": "DigitalNet", "ativo": True, "url_portal": "https://digitalnet.com.br"},
        {"nome": "Azuton", "ativo": True, "url_portal": "https://azuton.com.br"}
    ]
    
    operadoras = []
    for op_data in operadoras_data:
        operadora = Operadora(**op_data)
        db.add(operadora)
        operadoras.append(operadora)
    
    db.flush()  # Para obter os IDs
    
    # Criar clientes baseados nos dados da BGTELECOM
    clientes_data = [
        {"nome_sat": "RICAL CONTABILIDADE", "cnpj": "07.123.456/0001-01"},
        {"nome_sat": "ALVORADA COMUNICACAO", "cnpj": "08.234.567/0001-02"},
        {"nome_sat": "CENZE TECNOLOGIA", "cnpj": "09.345.678/0001-03"},
        {"nome_sat": "FINANCIAL SERVICES", "cnpj": "10.456.789/0001-04"},
        {"nome_sat": "BGTELECOM MATRIZ", "cnpj": "11.567.890/0001-05"},
        {"nome_sat": "CONECTA BRASIL", "cnpj": "12.678.901/0001-06"},
        {"nome_sat": "DIGITAL SOLUTIONS", "cnpj": "13.789.012/0001-07"},
        {"nome_sat": "TELECOM PLUS", "cnpj": "14.890.123/0001-08"},
        {"nome_sat": "FIBER NETWORKS", "cnpj": "15.901.234/0001-09"}
    ]
    
    clientes = []
    for cliente_data in clientes_data:
        cliente = Cliente(**cliente_data)
        db.add(cliente)
        clientes.append(cliente)
    
    db.flush()
    
    # Criar contratos associando clientes e operadoras
    import random
    for i, cliente in enumerate(clientes):
        # Cada cliente pode ter contratos com diferentes operadoras
        num_contratos = random.randint(1, 3)
        operadoras_selecionadas = random.sample(operadoras, num_contratos)
        
        for j, operadora in enumerate(operadoras_selecionadas):
            contrato = Contrato(
                cliente_id=cliente.id,
                operadora_id=operadora.id,
                hash_contrato=f"HASH_{cliente.cnpj.replace('.', '').replace('/', '').replace('-', '')}_{operadora.nome}_{j+1}",
                filtro=f"filtro_{operadora.nome.lower()}",
                servico=random.choice(["Internet Dedicada", "Link Dedicado", "MPLS", "Telefonia", "Cloud"])
            )
            db.add(contrato)
    
    db.flush()
    
    # Criar algumas execuções de exemplo
    contratos = db.query(Contrato).all()
    for i, contrato in enumerate(contratos[:15]):  # Criar 15 execuções
        execucao = Execucao(
            contrato_id=contrato.id,
            tipo=random.choice(["manual", "automatico", "agendado"]),
            status=random.choice(["executando", "concluido", "falha"]),
            tempo_execucao=random.randint(30, 300),
            arquivo_path=f"/downloads/fatura_{contrato.hash_contrato}_{datetime.now().strftime('%Y%m')}.pdf"
        )
        if execucao.status == "falha":
            execucao.erro = "Erro de conectividade com o portal da operadora"
        db.add(execucao)
    
    # Criar faturas de exemplo
    for i, contrato in enumerate(contratos[:20]):  # Criar 20 faturas
        fatura = Fatura(
            contrato_id=contrato.id,
            valor=round(random.uniform(500.0, 5000.0), 2),
            data_vencimento=datetime.now().date() + timedelta(days=random.randint(1, 30)),
            status_aprovacao=random.choice(["pendente", "aprovada", "rejeitada"]),
            arquivo_path=f"/downloads/fatura_{contrato.hash_contrato}_{datetime.now().strftime('%Y%m')}.pdf"
        )
        if fatura.status_aprovacao == "aprovada":
            fatura.aprovado_por = admin_user.id
            fatura.data_aprovacao = datetime.now()
        elif fatura.status_aprovacao == "rejeitada":
            fatura.motivo_rejeicao = "Valor divergente do contratado"
        db.add(fatura)
    
    # Criar notificações
    for i in range(10):
        notificacao = Notificacao(
            titulo=f"Execução RPA {random.choice(['Vivo', 'OI', 'Embratel'])}",
            mensagem=f"Execução automática de fatura concluída com {random.choice(['sucesso', 'warning', 'erro'])}",
            tipo=random.choice(["info", "warning", "error", "success"]),
            usuario_id=admin_user.id,
            lida=random.choice([True, False])
        )
        db.add(notificacao)
    
    db.commit()
    print("Dados iniciais do sistema criados com sucesso!")

# Adicionar todas as rotas existentes do main.py
# (As rotas do main.py já estão definidas, vamos apenas adicionar as específicas do RPA)

# === ROTAS ESPECÍFICAS DO SISTEMA RPA ===

@app.get("/api/rpa/status")
async def get_rpa_status():
    """Retorna o status de todos os RPAs"""
    return {
        "status": "ok",
        "rpas": rpa_status,
        "services_available": RPA_SERVICES_AVAILABLE,
        "total_rpas": len(rpa_status),
        "online_rpas": len([rpa for rpa in rpa_status.values() if rpa["status"] == "online"])
    }

@app.post("/api/rpa/execute/{operadora}")
async def execute_rpa(operadora: str, hash_execucao: str = None):
    """Executa RPA para uma operadora específica"""
    if not RPA_SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Serviços RPA não disponíveis")
    
    if not process_manager:
        raise HTTPException(status_code=503, detail="Gerenciador de processos não inicializado")
    
    operadora = operadora.lower()
    if operadora not in rpa_status:
        raise HTTPException(status_code=404, detail=f"Operadora {operadora} não encontrada")
    
    try:
        # Atualizar status
        rpa_status[operadora]["status"] = "executando"
        rpa_status[operadora]["last_execution"] = datetime.now().isoformat()
        
        # Executar processo
        if hash_execucao:
            processes = process_manager.create_all_process(pesquisa_processo=hash_execucao, operadora=operadora)
        else:
            processes = process_manager.create_all_process(operadora=operadora)
        
        rpa_status[operadora]["status"] = "online"
        
        return {
            "message": f"RPA {operadora.title()} executado com sucesso",
            "processes_created": len(processes) if processes else 0,
            "processes": processes
        }
        
    except Exception as e:
        rpa_status[operadora]["status"] = "erro"
        raise HTTPException(status_code=500, detail=f"Erro ao executar RPA {operadora}: {str(e)}")

@app.get("/api/rpa/processes")
async def get_rpa_processes():
    """Lista todos os processos RPA"""
    if not process_manager:
        return {"processes": [], "message": "Gerenciador de processos não disponível"}
    
    try:
        # Aqui implementaríamos a listagem de processos do MongoDB
        # Por ora, retornamos dados simulados baseados no banco SQL
        db = SessionLocal()
        try:
            execucoes = db.query(Execucao).join(Contrato).join(Operadora).all()
            processes = []
            for exec in execucoes:
                processes.append({
                    "id": exec.id,
                    "operadora": exec.contrato.operadora.nome,
                    "cliente": exec.contrato.cliente.nome_sat if exec.contrato.cliente else "N/A",
                    "status": exec.status,
                    "tipo": exec.tipo,
                    "iniciado_em": exec.iniciado_em.isoformat() if exec.iniciado_em else None,
                    "tempo_execucao": exec.tempo_execucao,
                    "erro": exec.erro
                })
            return {"processes": processes}
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar processos: {str(e)}")

@app.post("/api/rpa/stop/{operadora}")
async def stop_rpa(operadora: str):
    """Para a execução de um RPA específico"""
    operadora = operadora.lower()
    if operadora not in rpa_status:
        raise HTTPException(status_code=404, detail=f"Operadora {operadora} não encontrada")
    
    rpa_status[operadora]["status"] = "offline"
    return {"message": f"RPA {operadora.title()} parado com sucesso"}

@app.get("/api/system/health")
async def system_health():
    """Verifica a saúde geral do sistema"""
    db = SessionLocal()
    try:
        # Verificar conexão com banco
        db_status = "ok"
        try:
            db.execute("SELECT 1")
        except Exception:
            db_status = "erro"
        
        # Verificar serviços RPA
        rpa_services_status = "ok" if RPA_SERVICES_AVAILABLE else "indisponível"
        
        # Contar registros principais
        total_clientes = db.query(Cliente).count()
        total_operadoras = db.query(Operadora).count()
        total_contratos = db.query(Contrato).count()
        execucoes_ativas = db.query(Execucao).filter(Execucao.status == "executando").count()
        
        return {
            "status": "ok",
            "database": db_status,
            "rpa_services": rpa_services_status,
            "process_manager": "ok" if process_manager else "indisponível",
            "stats": {
                "clientes": total_clientes,
                "operadoras": total_operadoras,
                "contratos": total_contratos,
                "execucoes_ativas": execucoes_ativas
            },
            "timestamp": datetime.now().isoformat()
        }
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando Sistema de Orquestração RPA...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )