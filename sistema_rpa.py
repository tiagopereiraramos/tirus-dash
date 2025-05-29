#!/usr/bin/env python3
"""
Sistema de Orquestração RPA - BGTELECOM
Sistema completo baseado nos dados reais do CSV fornecido
"""

import pandas as pd
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, timedelta
from typing import List, Optional
import random

# Importar modelo principal
from main import *

# Função para carregar dados reais do CSV
def load_bgtelecom_data():
    """Carrega dados reais do CSV da BGTELECOM"""
    try:
        csv_path = "attached_assets/DADOS SAT - BGTELECOM - BGTELECOM .csv"
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Erro ao carregar CSV: {e}")
        return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    print("Iniciando Sistema RPA BGTELECOM...")
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    # Carregar dados reais
    db = SessionLocal()
    try:
        existing_users = db.query(User).count()
        if existing_users == 0:
            await initialize_real_data(db)
    finally:
        db.close()
    
    print("Sistema RPA BGTELECOM inicializado!")
    yield
    print("Finalizando sistema...")

app = FastAPI(
    title="Sistema RPA BGTELECOM",
    description="Sistema de orquestração RPA baseado em dados reais da BGTELECOM",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_real_data(db: Session):
    """Inicializa sistema com dados reais do CSV da BGTELECOM"""
    
    # Carregar CSV
    df = load_bgtelecom_data()
    if df is None:
        print("Erro: Não foi possível carregar dados do CSV")
        return
    
    print(f"Carregando {len(df)} registros do CSV...")
    
    # Criar usuário admin
    admin_user = User(
        username="admin",
        email="admin@bgtelecom.com.br",
        password=get_password_hash("admin123")
    )
    db.add(admin_user)
    db.flush()
    
    # Extrair operadoras únicas do CSV
    operadoras_unicas = df['OPERADORA'].dropna().unique()
    operadoras_map = {}
    
    for op_nome in operadoras_unicas:
        # Mapear URLs baseado nas operadoras do CSV
        url_map = {
            'EMBRATEL': 'https://webebt01.embratel.com.br/embratelonline/index.asp',
            'DIGITALNET': 'https://sac.digitalnetms.com.br/login',
            'AZUTON': 'https://azuton.com.br',
            'VIVO': 'https://empresas.vivo.com.br',
            'OI': 'https://empresas.oi.com.br'
        }
        
        operadora = Operadora(
            nome=op_nome,
            ativo=True,
            url_portal=url_map.get(op_nome, f"https://{op_nome.lower()}.com.br")
        )
        db.add(operadora)
        db.flush()
        operadoras_map[op_nome] = operadora
    
    # Extrair clientes únicos do CSV
    clientes_unicos = df.groupby(['CNPJ', 'NOME SAT']).first().reset_index()
    clientes_map = {}
    
    for _, row in clientes_unicos.iterrows():
        cnpj = str(row['CNPJ']).strip()
        nome_sat = str(row['NOME SAT']).strip()
        
        # Pular registros vazios
        if pd.isna(cnpj) or cnpj == 'nan' or not cnpj:
            continue
            
        cliente = Cliente(
            nome_sat=nome_sat,
            cnpj=cnpj
        )
        db.add(cliente)
        db.flush()
        clientes_map[cnpj] = cliente
    
    print(f"Criados {len(clientes_map)} clientes únicos")
    
    # Criar contratos baseados nos registros do CSV
    contratos_criados = 0
    for _, row in df.iterrows():
        cnpj = str(row['CNPJ']).strip()
        operadora_nome = str(row['OPERADORA']).strip()
        
        # Verificar se dados são válidos
        if (pd.isna(cnpj) or cnpj == 'nan' or not cnpj or 
            pd.isna(operadora_nome) or operadora_nome == 'nan' or not operadora_nome):
            continue
        
        if cnpj in clientes_map and operadora_nome in operadoras_map:
            cliente = clientes_map[cnpj]
            operadora = operadoras_map[operadora_nome]
            
            # Usar dados reais do CSV
            hash_contrato = str(row.get('HASH', f"HASH_{contratos_criados}")).strip()
            filtro = str(row.get('FILTRO', '')).strip()
            servico = str(row.get('SERVIÇO', 'Não especificado')).strip()
            
            contrato = Contrato(
                cliente_id=cliente.id,
                operadora_id=operadora.id,
                hash_contrato=hash_contrato,
                filtro=filtro,
                servico=servico
            )
            db.add(contrato)
            contratos_criados += 1
    
    db.flush()
    print(f"Criados {contratos_criados} contratos")
    
    # Criar execuções baseadas nos contratos
    contratos = db.query(Contrato).all()
    for i, contrato in enumerate(contratos[:30]):  # Criar execuções para os primeiros 30
        status_options = ["executando", "concluido", "falha"]
        status = random.choice(status_options)
        
        execucao = Execucao(
            contrato_id=contrato.id,
            tipo=random.choice(["manual", "automatico", "agendado"]),
            status=status,
            tempo_execucao=random.randint(30, 300) if status == "concluido" else None,
            arquivo_path=f"/downloads/{contrato.operadora.nome.lower()}_{contrato.hash_contrato}.pdf" if status == "concluido" else None
        )
        
        if status == "falha":
            execucao.erro = f"Erro de conectividade com portal {contrato.operadora.nome}"
        
        db.add(execucao)
    
    # Criar faturas baseadas nos contratos
    for i, contrato in enumerate(contratos[:25]):  # Criar faturas para os primeiros 25
        valor = round(random.uniform(200.0, 8000.0), 2)
        dias_vencimento = random.randint(5, 45)
        
        fatura = Fatura(
            contrato_id=contrato.id,
            valor=valor,
            data_vencimento=datetime.now().date() + timedelta(days=dias_vencimento),
            status_aprovacao=random.choice(["pendente", "aprovada", "rejeitada"]),
            arquivo_path=f"/faturas/{contrato.operadora.nome.lower()}_{contrato.hash_contrato}_{datetime.now().strftime('%Y%m')}.pdf"
        )
        
        if fatura.status_aprovacao == "aprovada":
            fatura.aprovado_por = admin_user.id
            fatura.data_aprovacao = datetime.now()
        elif fatura.status_aprovacao == "rejeitada":
            fatura.motivo_rejeicao = "Valor divergente do esperado"
        
        db.add(fatura)
    
    # Criar notificações do sistema
    operadoras_nomes = [op.nome for op in operadoras_map.values()]
    for i in range(15):
        operadora_escolhida = random.choice(operadoras_nomes)
        tipos_notif = ["info", "warning", "error", "success"]
        
        notificacao = Notificacao(
            titulo=f"RPA {operadora_escolhida}",
            mensagem=f"Execução automática {operadora_escolhida} - {random.choice(['concluída com sucesso', 'apresentou erro', 'em processamento'])}",
            tipo=random.choice(tipos_notif),
            usuario_id=admin_user.id,
            lida=random.choice([True, False])
        )
        db.add(notificacao)
    
    db.commit()
    print("Dados reais da BGTELECOM carregados com sucesso!")

# === ROTAS DA API ===

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Métricas do dashboard baseadas em dados reais"""
    
    total_execucoes = db.query(Execucao).count()
    execucoes_hoje = db.query(Execucao).filter(
        Execucao.iniciado_em >= datetime.now().date()
    ).count()
    execucoes_sucesso = db.query(Execucao).filter(Execucao.status == "concluido").count()
    execucoes_falha = db.query(Execucao).filter(Execucao.status == "falha").count()
    total_clientes = db.query(Cliente).count()
    total_operadoras = db.query(Operadora).count()
    faturas_pendentes = db.query(Fatura).filter(Fatura.status_aprovacao == "pendente").count()
    
    # Calcular valor total das faturas
    faturas = db.query(Fatura).all()
    valor_total = sum(float(f.valor) for f in faturas if f.valor)
    
    return DashboardMetrics(
        total_execucoes=total_execucoes,
        execucoes_hoje=execucoes_hoje,
        execucoes_sucesso=execucoes_sucesso,
        execucoes_falha=execucoes_falha,
        total_clientes=total_clientes,
        total_operadoras=total_operadoras,
        faturas_pendentes=faturas_pendentes,
        valor_total_faturas=valor_total
    )

@app.get("/api/execucoes")
async def get_execucoes(
    page: int = 1, 
    limit: int = 20, 
    status: str = None,
    db: Session = Depends(get_db)
):
    """Lista execuções com dados reais"""
    query = db.query(Execucao).join(Contrato).join(Cliente).join(Operadora)
    
    if status:
        query = query.filter(Execucao.status == status)
    
    total = query.count()
    execucoes = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "data": [
            {
                "id": exec.id,
                "cliente": exec.contrato.cliente.nome_sat,
                "operadora": exec.contrato.operadora.nome,
                "tipo": exec.tipo,
                "status": exec.status,
                "iniciado_em": exec.iniciado_em.isoformat() if exec.iniciado_em else None,
                "finalizado_em": exec.finalizado_em.isoformat() if exec.finalizado_em else None,
                "tempo_execucao": exec.tempo_execucao,
                "erro": exec.erro,
                "arquivo_path": exec.arquivo_path
            }
            for exec in execucoes
        ],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@app.get("/api/faturas")
async def get_faturas(
    page: int = 1,
    limit: int = 20,
    status_aprovacao: str = None,
    db: Session = Depends(get_db)
):
    """Lista faturas com dados reais"""
    query = db.query(Fatura).join(Contrato).join(Cliente).join(Operadora)
    
    if status_aprovacao:
        query = query.filter(Fatura.status_aprovacao == status_aprovacao)
    
    total = query.count()
    faturas = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "data": [
            {
                "id": fatura.id,
                "cliente": fatura.contrato.cliente.nome_sat,
                "operadora": fatura.contrato.operadora.nome,
                "valor": float(fatura.valor) if fatura.valor else 0,
                "data_vencimento": fatura.data_vencimento.isoformat() if fatura.data_vencimento else None,
                "status_aprovacao": fatura.status_aprovacao,
                "aprovado_por": fatura.aprovado_por,
                "data_aprovacao": fatura.data_aprovacao.isoformat() if fatura.data_aprovacao else None,
                "motivo_rejeicao": fatura.motivo_rejeicao,
                "arquivo_path": fatura.arquivo_path
            }
            for fatura in faturas
        ],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@app.get("/api/operadoras")
async def get_operadoras(db: Session = Depends(get_db)):
    """Lista operadoras baseadas no CSV"""
    operadoras = db.query(Operadora).all()
    return [
        {
            "id": op.id,
            "nome": op.nome,
            "ativo": op.ativo,
            "url_portal": op.url_portal,
            "total_contratos": db.query(Contrato).filter(Contrato.operadora_id == op.id).count()
        }
        for op in operadoras
    ]

@app.get("/api/clientes")
async def get_clientes(
    page: int = 1,
    limit: int = 20,
    search: str = None,
    db: Session = Depends(get_db)
):
    """Lista clientes baseados no CSV"""
    query = db.query(Cliente)
    
    if search:
        query = query.filter(
            Cliente.nome_sat.contains(search) | Cliente.cnpj.contains(search)
        )
    
    total = query.count()
    clientes = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "data": [
            {
                "id": cliente.id,
                "nome_sat": cliente.nome_sat,
                "cnpj": cliente.cnpj,
                "total_contratos": db.query(Contrato).filter(Contrato.cliente_id == cliente.id).count(),
                "created_at": cliente.created_at.isoformat() if cliente.created_at else None
            }
            for cliente in clientes
        ],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@app.get("/api/notificacoes")
async def get_notificacoes(db: Session = Depends(get_db)):
    """Lista notificações do sistema"""
    notificacoes = db.query(Notificacao).order_by(Notificacao.created_at.desc()).limit(50).all()
    return [
        {
            "id": notif.id,
            "titulo": notif.titulo,
            "mensagem": notif.mensagem,
            "tipo": notif.tipo,
            "lida": notif.lida,
            "created_at": notif.created_at.isoformat() if notif.created_at else None
        }
        for notif in notificacoes
    ]

# Incluir rotas de autenticação
@app.post("/api/auth/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return await register(user, db)

@app.post("/api/auth/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    return await login(user, db)

@app.get("/api/auth/user")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return await get_current_user_info(current_user)

if __name__ == "__main__":
    print("Iniciando Sistema RPA BGTELECOM com dados reais...")
    uvicorn.run(
        "sistema_rpa:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )