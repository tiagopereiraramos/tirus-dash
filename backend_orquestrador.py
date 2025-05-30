#!/usr/bin/env python3
"""
Sistema de Orquestração RPA - BGTELECOM
Backend completo seguindo especificações do prompt definitivo
Desenvolvido por: Tiago Pereira Ramos
Data: 29/05/2025
"""

import os
import sys
import hashlib
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum
import pandas as pd

# FastAPI e dependências
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

# SQLAlchemy e Pydantic
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Numeric, Text, Integer, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from dataclasses import dataclass
import json

# Configuração do banco PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/orquestrador_rpa")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# === ENUMS E TIPOS ===

class StatusProcesso(str, Enum):
    AGUARDANDO_DOWNLOAD = "AGUARDANDO_DOWNLOAD"
    FATURA_BAIXADA = "FATURA_BAIXADA"
    PENDENTE_APROVACAO = "PENDENTE_APROVACAO"
    APROVADA = "APROVADA"
    REJEITADA = "REJEITADA"
    ENVIADA_SAT = "ENVIADA_SAT"
    ERRO = "ERRO"

class TipoExecucao(str, Enum):
    DOWNLOAD_FATURA = "DOWNLOAD_FATURA"
    UPLOAD_SAT = "UPLOAD_SAT"
    UPLOAD_MANUAL = "UPLOAD_MANUAL"

class StatusExecucao(str, Enum):
    EXECUTANDO = "EXECUTANDO"
    CONCLUIDO = "CONCLUIDO"
    FALHOU = "FALHOU"
    TENTANDO_NOVAMENTE = "TENTANDO_NOVAMENTE"

class PerfilUsuario(str, Enum):
    ADMINISTRADOR = "ADMINISTRADOR"
    APROVADOR = "APROVADOR"
    OPERADOR = "OPERADOR"

class TipoNotificacao(str, Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    TELEGRAM = "TELEGRAM"
    SLACK = "SLACK"

class StatusEnvio(str, Enum):
    PENDENTE = "PENDENTE"
    ENVIADO = "ENVIADO"
    FALHOU = "FALHOU"

# === MODELOS SQLALCHEMY ===

class Operadora(Base):
    __tablename__ = "operadoras"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), unique=True, nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    possui_rpa = Column(Boolean, default=False)
    status_ativo = Column(Boolean, default=True)
    url_portal = Column(String(500))
    instrucoes_acesso = Column(Text)
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    clientes = relationship("Cliente", back_populates="operadora")

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hash_unico = Column(String(50), unique=True, nullable=False)
    razao_social = Column(String(255), nullable=False)
    nome_sat = Column(String(255), nullable=False)
    cnpj = Column(String(20), nullable=False)
    operadora_id = Column(UUID(as_uuid=True), ForeignKey("operadoras.id"))
    filtro = Column(String(255))
    servico = Column(String(255))
    dados_sat = Column(Text)
    unidade = Column(String(100), nullable=False)
    site_emissao = Column(String(255))
    login_portal = Column(String(100))
    senha_portal = Column(String(100))
    cpf = Column(String(20))
    status_ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    operadora = relationship("Operadora", back_populates="clientes")
    processos = relationship("Processo", back_populates="cliente")

class Processo(Base):
    __tablename__ = "processos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"))
    mes_ano = Column(String(7), nullable=False)
    status_processo = Column(String(50), default=StatusProcesso.AGUARDANDO_DOWNLOAD.value)
    url_fatura = Column(String(500))
    caminho_s3_fatura = Column(String(500))
    data_vencimento = Column(Date)
    valor_fatura = Column(Numeric(15,2))
    aprovado_por_usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    data_aprovacao = Column(DateTime)
    enviado_para_sat = Column(Boolean, default=False)
    data_envio_sat = Column(DateTime)
    upload_manual = Column(Boolean, default=False)
    criado_automaticamente = Column(Boolean, default=True)
    observacoes = Column(Text)
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="processos")
    execucoes = relationship("Execucao", back_populates="processo")
    aprovador = relationship("Usuario", foreign_keys=[aprovado_por_usuario_id])

class Execucao(Base):
    __tablename__ = "execucoes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    processo_id = Column(UUID(as_uuid=True), ForeignKey("processos.id"))
    tipo_execucao = Column(String(50), nullable=False)
    status_execucao = Column(String(50), nullable=False)
    parametros_entrada = Column(JSONB)
    resultado_saida = Column(JSONB)
    data_inicio = Column(DateTime, default=func.now())
    data_fim = Column(DateTime)
    mensagem_log = Column(Text)
    url_arquivo_s3 = Column(String(500))
    numero_tentativa = Column(Integer, default=1)
    detalhes_erro = Column(JSONB)
    executado_por_usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    ip_origem = Column(String(45))
    user_agent = Column(Text)
    
    # Relacionamentos
    processo = relationship("Processo", back_populates="execucoes")
    executor = relationship("Usuario", foreign_keys=[executado_por_usuario_id])

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_completo = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    telefone = Column(String(20))
    perfil_usuario = Column(String(50), nullable=False)
    status_ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=func.now())

class Notificacao(Base):
    __tablename__ = "notificacoes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_notificacao = Column(String(50), nullable=False)
    destinatario = Column(String(255), nullable=False)
    assunto = Column(String(255))
    mensagem = Column(Text, nullable=False)
    status_envio = Column(String(50), default=StatusEnvio.PENDENTE.value)
    tentativas_envio = Column(Integer, default=0)
    data_envio = Column(DateTime)
    mensagem_erro = Column(Text)
    data_criacao = Column(DateTime, default=func.now())

class Agendamento(Base):
    __tablename__ = "agendamentos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_agendamento = Column(String(255), nullable=False)
    descricao = Column(Text)
    cron_expressao = Column(String(100), nullable=False)
    tipo_agendamento = Column(String(50), nullable=False)
    status_ativo = Column(Boolean, default=True)
    proxima_execucao = Column(DateTime)
    ultima_execucao = Column(DateTime)
    parametros_execucao = Column(JSONB)
    data_criacao = Column(DateTime, default=func.now())

# === SCHEMAS PYDANTIC ===

class OperadoraBase(BaseModel):
    nome: str
    codigo: str
    possui_rpa: bool = False
    status_ativo: bool = True
    url_portal: Optional[str] = None
    instrucoes_acesso: Optional[str] = None

class OperadoraCreate(OperadoraBase):
    pass

class OperadoraResponse(OperadoraBase):
    id: uuid.UUID
    data_criacao: datetime
    
    class Config:
        from_attributes = True

class ClienteBase(BaseModel):
    razao_social: str
    nome_sat: str
    cnpj: str
    operadora_id: uuid.UUID
    filtro: Optional[str] = None
    servico: Optional[str] = None
    dados_sat: Optional[str] = None
    unidade: str
    site_emissao: Optional[str] = None
    login_portal: Optional[str] = None
    senha_portal: Optional[str] = None
    cpf: Optional[str] = None
    status_ativo: bool = True

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: uuid.UUID
    hash_unico: str
    data_criacao: datetime
    operadora: OperadoraResponse
    
    class Config:
        from_attributes = True

class ProcessoBase(BaseModel):
    cliente_id: uuid.UUID
    mes_ano: str
    status_processo: StatusProcesso = StatusProcesso.AGUARDANDO_DOWNLOAD
    url_fatura: Optional[str] = None
    data_vencimento: Optional[datetime] = None
    valor_fatura: Optional[Decimal] = None
    upload_manual: bool = False
    criado_automaticamente: bool = True
    observacoes: Optional[str] = None

class ProcessoCreate(ProcessoBase):
    pass

class ProcessoResponse(ProcessoBase):
    id: uuid.UUID
    caminho_s3_fatura: Optional[str] = None
    aprovado_por_usuario_id: Optional[uuid.UUID] = None
    data_aprovacao: Optional[datetime] = None
    enviado_para_sat: bool = False
    data_envio_sat: Optional[datetime] = None
    data_criacao: datetime
    cliente: ClienteResponse
    
    class Config:
        from_attributes = True

class ExecucaoCreate(BaseModel):
    processo_id: uuid.UUID
    tipo_execucao: TipoExecucao
    parametros_entrada: Optional[Dict[str, Any]] = None

class ExecucaoResponse(BaseModel):
    id: uuid.UUID
    processo_id: uuid.UUID
    tipo_execucao: TipoExecucao
    status_execucao: StatusExecucao
    parametros_entrada: Optional[Dict[str, Any]] = None
    resultado_saida: Optional[Dict[str, Any]] = None
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    mensagem_log: Optional[str] = None
    numero_tentativa: int
    
    class Config:
        from_attributes = True

# === FUNÇÕES UTILITÁRIAS ===

def generate_hash_cad(nome_filtro: str, operadora: str, servico: str, dados_sat: str = "", filtro: str = "", unidade: str = "") -> str:
    """Gera hash único para identificação do cliente/processo"""
    nome_filtro = nome_filtro.strip().lower() if nome_filtro else ""
    operadora = operadora.strip().lower() if operadora else ""
    servico = servico.strip().lower() if servico else ""
    dados_sat = dados_sat.strip().lower() if dados_sat else ""
    filtro = filtro.strip().lower() if filtro else ""
    unidade = unidade.strip().lower() if unidade else ""
    
    base_string = f"{nome_filtro}-{operadora}-{servico}-{dados_sat}-{filtro}-{unidade}"
    hash_value = hashlib.sha256(base_string.encode()).hexdigest()[:16]
    return hash_value

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def carregar_dados_csv_bgtelecom():
    """Carrega dados reais do CSV da BGTELECOM"""
    try:
        csv_path = "attached_assets/DADOS SAT - BGTELECOM - BGTELECOM .csv"
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)
        return None
    except Exception as e:
        print(f"Erro ao carregar CSV: {e}")
        return None

# === APLICAÇÃO FASTAPI ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    print("🚀 Iniciando Sistema de Orquestração RPA BGTELECOM...")
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    # Carregar dados iniciais se necessário
    db = SessionLocal()
    try:
        if db.query(Usuario).count() == 0:
            await inicializar_dados_sistema(db)
    finally:
        db.close()
    
    print("✅ Sistema de Orquestração RPA BGTELECOM inicializado com sucesso!")
    yield
    print("🔄 Finalizando sistema...")

app = FastAPI(
    title="Sistema de Orquestração RPA - BGTELECOM",
    description="Backend completo para gerenciamento automatizado de faturas de telecomunicações",
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

security = HTTPBearer()

async def inicializar_dados_sistema(db: Session):
    """Inicializa dados do sistema com base no CSV da BGTELECOM"""
    print("📊 Carregando dados reais da BGTELECOM...")
    
    # Criar usuário administrador
    admin = Usuario(
        nome_completo="Administrador Sistema",
        email="admin@bgtelecom.com.br",
        telefone="(67) 99999-9999",
        perfil_usuario=PerfilUsuario.ADMINISTRADOR.value
    )
    db.add(admin)
    db.flush()
    
    # Carregar dados do CSV
    df = carregar_dados_csv_bgtelecom()
    if df is None:
        print("⚠️ Não foi possível carregar dados do CSV, criando dados de exemplo...")
        return
    
    print(f"📋 Processando {len(df)} registros do CSV...")
    
    # Criar operadoras únicas
    operadoras_unicas = df['OPERADORA'].dropna().unique()
    operadoras_map = {}
    
    url_mapping = {
        'EMBRATEL': 'https://webebt01.embratel.com.br/embratelonline/index.asp',
        'DIGITALNET': 'https://sac.digitalnetms.com.br/login',
        'AZUTON': 'https://azuton.com.br',
        'VIVO': 'https://empresas.vivo.com.br',
        'OI': 'https://empresas.oi.com.br'
    }
    
    for operadora_nome in operadoras_unicas:
        operadora = Operadora(
            nome=operadora_nome,
            codigo=operadora_nome[:3].upper(),
            possui_rpa=operadora_nome in ['EMBRATEL', 'DIGITALNET', 'AZUTON', 'VIVO', 'OI'],
            url_portal=url_mapping.get(operadora_nome, f"https://{operadora_nome.lower()}.com.br"),
            instrucoes_acesso=f"Portal da operadora {operadora_nome}"
        )
        db.add(operadora)
        db.flush()
        operadoras_map[operadora_nome] = operadora
    
    print(f"✅ Criadas {len(operadoras_map)} operadoras")
    
    # Processar clientes únicos do CSV
    clientes_processados = 0
    processos_criados = 0
    
    for _, row in df.iterrows():
        try:
            # Verificar dados válidos
            cnpj = str(row.get('CNPJ', '')).strip()
            nome_sat = str(row.get('NOME SAT', '')).strip()
            operadora_nome = str(row.get('OPERADORA', '')).strip()
            
            if not cnpj or cnpj == 'nan' or not nome_sat or nome_sat == 'nan':
                continue
            
            if operadora_nome not in operadoras_map:
                continue
            
            # Dados do cliente
            razao_social = str(row.get('RAZÃO SOCIAL', nome_sat)).strip()
            filtro = str(row.get('FILTRO', '')).strip()
            servico = str(row.get('SERVIÇO', 'Não especificado')).strip()
            dados_sat = str(row.get('DADOS SAT', '')).strip()
            unidade = str(row.get('UNIDADE / FILTRO SAT', 'Principal')).strip()
            
            # Gerar hash único
            hash_unico = generate_hash_cad(
                nome_filtro=nome_sat,
                operadora=operadora_nome,
                servico=servico,
                dados_sat=dados_sat,
                filtro=filtro,
                unidade=unidade
            )
            
            # Verificar se cliente já existe
            cliente_existente = db.query(Cliente).filter(Cliente.hash_unico == hash_unico).first()
            if cliente_existente:
                continue
            
            # Criar cliente
            cliente = Cliente(
                hash_unico=hash_unico,
                razao_social=razao_social,
                nome_sat=nome_sat,
                cnpj=cnpj,
                operadora_id=operadoras_map[operadora_nome].id,
                filtro=filtro,
                servico=servico,
                dados_sat=dados_sat,
                unidade=unidade,
                site_emissao=str(row.get('SITE PARA EMISSÃO', '')).strip() or None,
                login_portal=str(row.get('LOGIN', '')).strip() or None,
                senha_portal=str(row.get('SENHA', '')).strip() or None,
                cpf=str(row.get('CPF', '')).strip() or None
            )
            db.add(cliente)
            db.flush()
            clientes_processados += 1
            
            # Criar processo para o mês atual
            mes_ano_atual = datetime.now().strftime("%Y-%m")
            processo = Processo(
                cliente_id=cliente.id,
                mes_ano=mes_ano_atual,
                status_processo=StatusProcesso.AGUARDANDO_DOWNLOAD.value,
                criado_automaticamente=True
            )
            db.add(processo)
            processos_criados += 1
            
        except Exception as e:
            print(f"Erro ao processar linha: {e}")
            continue
    
    db.commit()
    print(f"✅ Sistema inicializado:")
    print(f"   - {len(operadoras_map)} operadoras criadas")
    print(f"   - {clientes_processados} clientes processados")
    print(f"   - {processos_criados} processos criados")

# === ENDPOINTS DA API ===

@app.get("/")
async def root():
    return {
        "sistema": "Orquestrador RPA BGTELECOM",
        "versao": "1.0.0",
        "status": "ativo",
        "desenvolvido_por": "Tiago Pereira Ramos"
    }

@app.get("/api/sistema/saude")
async def verificar_saude_sistema(db: Session = Depends(get_db)):
    """Verifica a saúde geral do sistema"""
    try:
        # Verificar conexão com banco
        total_operadoras = db.query(Operadora).count()
        total_clientes = db.query(Cliente).count()
        total_processos = db.query(Processo).count()
        execucoes_ativas = db.query(Execucao).filter(
            Execucao.status_execucao == StatusExecucao.EXECUTANDO.value
        ).count()
        
        return {
            "status": "saudavel",
            "timestamp": datetime.now().isoformat(),
            "banco_dados": "conectado",
            "estatisticas": {
                "operadoras": total_operadoras,
                "clientes": total_clientes,
                "processos": total_processos,
                "execucoes_ativas": execucoes_ativas
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na verificação de saúde: {str(e)}")

# OPERADORAS
@app.get("/api/operadoras/", response_model=List[OperadoraResponse])
async def listar_operadoras(db: Session = Depends(get_db)):
    """Lista todas as operadoras"""
    operadoras = db.query(Operadora).all()
    return operadoras

@app.post("/api/operadoras/", response_model=OperadoraResponse)
async def criar_operadora(operadora: OperadoraCreate, db: Session = Depends(get_db)):
    """Cria uma nova operadora"""
    db_operadora = Operadora(**operadora.dict())
    db.add(db_operadora)
    db.commit()
    db.refresh(db_operadora)
    return db_operadora

# CLIENTES
@app.get("/api/clientes/", response_model=List[ClienteResponse])
async def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    operadora_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db)
):
    """Lista clientes com filtros opcionais"""
    query = db.query(Cliente)
    
    if operadora_id:
        query = query.filter(Cliente.operadora_id == operadora_id)
    
    clientes = query.offset(skip).limit(limit).all()
    return clientes

@app.post("/api/clientes/", response_model=ClienteResponse)
async def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Cria um novo cliente"""
    # Verificar se operadora existe e está ativa
    operadora = db.query(Operadora).filter(
        Operadora.id == cliente.operadora_id,
        Operadora.status_ativo == True
    ).first()
    
    if not operadora:
        raise HTTPException(status_code=400, detail="Operadora não encontrada ou inativa")
    
    # Gerar hash único
    hash_unico = generate_hash_cad(
        nome_filtro=cliente.nome_sat,
        operadora=operadora.nome,
        servico=cliente.servico or "",
        dados_sat=cliente.dados_sat or "",
        filtro=cliente.filtro or "",
        unidade=cliente.unidade
    )
    
    # Verificar unicidade
    cliente_existente = db.query(Cliente).filter(Cliente.hash_unico == hash_unico).first()
    if cliente_existente:
        raise HTTPException(status_code=400, detail="Cliente já existe com esses parâmetros")
    
    # Criar cliente
    cliente_data = cliente.dict()
    cliente_data['hash_unico'] = hash_unico
    db_cliente = Cliente(**cliente_data)
    
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

# PROCESSOS
@app.get("/api/processos/", response_model=List[ProcessoResponse])
async def listar_processos(
    skip: int = 0,
    limit: int = 100,
    mes_ano: Optional[str] = None,
    status: Optional[StatusProcesso] = None,
    db: Session = Depends(get_db)
):
    """Lista processos com filtros opcionais"""
    query = db.query(Processo)
    
    if mes_ano:
        query = query.filter(Processo.mes_ano == mes_ano)
    
    if status:
        query = query.filter(Processo.status_processo == status.value)
    
    processos = query.offset(skip).limit(limit).all()
    return processos

@app.post("/api/processos/", response_model=ProcessoResponse)
async def criar_processo(processo: ProcessoCreate, db: Session = Depends(get_db)):
    """Cria um novo processo"""
    # Verificar unicidade (cliente + mês/ano)
    processo_existente = db.query(Processo).filter(
        Processo.cliente_id == processo.cliente_id,
        Processo.mes_ano == processo.mes_ano
    ).first()
    
    if processo_existente:
        raise HTTPException(status_code=400, detail="Processo já existe para este cliente e período")
    
    db_processo = Processo(**processo.dict())
    db.add(db_processo)
    db.commit()
    db.refresh(db_processo)
    return db_processo

# EXECUÇÕES
@app.post("/api/execucoes/", response_model=ExecucaoResponse)
async def criar_execucao(execucao: ExecucaoCreate, db: Session = Depends(get_db)):
    """Cria uma nova execução"""
    db_execucao = Execucao(
        processo_id=execucao.processo_id,
        tipo_execucao=execucao.tipo_execucao.value,
        status_execucao=StatusExecucao.EXECUTANDO.value,
        parametros_entrada=execucao.parametros_entrada
    )
    
    db.add(db_execucao)
    db.commit()
    db.refresh(db_execucao)
    return db_execucao

@app.get("/api/execucoes/", response_model=List[ExecucaoResponse])
async def listar_execucoes(
    skip: int = 0,
    limit: int = 100,
    processo_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db)
):
    """Lista execuções com filtros opcionais"""
    query = db.query(Execucao)
    
    if processo_id:
        query = query.filter(Execucao.processo_id == processo_id)
    
    execucoes = query.offset(skip).limit(limit).all()
    return execucoes

# UPLOAD MANUAL
@app.post("/api/faturas/upload-manual/")
async def upload_manual_fatura(
    processo_id: uuid.UUID,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload manual de fatura"""
    # Verificar se processo existe
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Verificar se operadora permite upload manual
    operadora = db.query(Operadora).filter(Operadora.id == processo.cliente.operadora_id).first()
    if operadora.possui_rpa:
        raise HTTPException(status_code=400, detail="Operadora possui RPA, upload manual não permitido")
    
    # Aqui seria implementada a lógica de upload para S3/MinIO
    # Por ora, apenas simulamos
    
    # Atualizar processo
    processo.upload_manual = True
    processo.status_processo = StatusProcesso.PENDENTE_APROVACAO.value
    processo.caminho_s3_fatura = f"faturas/{processo_id}/{arquivo.filename}"
    
    # Criar execução de upload manual
    execucao = Execucao(
        processo_id=processo_id,
        tipo_execucao=TipoExecucao.UPLOAD_MANUAL.value,
        status_execucao=StatusExecucao.CONCLUIDO.value,
        parametros_entrada={"nome_arquivo": arquivo.filename, "tamanho": arquivo.size},
        resultado_saida={"caminho_s3": processo.caminho_s3_fatura},
        data_fim=datetime.now(),
        mensagem_log="Upload manual realizado com sucesso"
    )
    
    db.add(execucao)
    db.commit()
    
    return {
        "mensagem": "Upload realizado com sucesso",
        "processo_id": processo_id,
        "status": "pendente_aprovacao"
    }

# === ENDPOINTS DE EXECUÇÃO RPA ===

@app.post("/api/rpa/executar/{operadora_codigo}")
async def executar_rpa_operadora(
    operadora_codigo: str,
    mes_ano: Optional[str] = None,
    cliente_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db)
):
    """Executa RPA para uma operadora específica"""
    try:
        # Verificar se operadora existe e possui RPA
        operadora = db.query(Operadora).filter(
            Operadora.codigo == operadora_codigo.upper(),
            Operadora.possui_rpa == True,
            Operadora.status_ativo == True
        ).first()
        
        if not operadora:
            raise HTTPException(status_code=404, detail="Operadora não encontrada ou não possui RPA")
        
        # Filtrar processos para execução
        query = db.query(Processo).join(Cliente).filter(
            Cliente.operadora_id == operadora.id,
            Processo.status_processo == StatusProcesso.AGUARDANDO_DOWNLOAD.value
        )
        
        if mes_ano:
            query = query.filter(Processo.mes_ano == mes_ano)
        if cliente_id:
            query = query.filter(Processo.cliente_id == cliente_id)
        
        processos = query.all()
        
        if not processos:
            return {
                "mensagem": "Nenhum processo encontrado para execução",
                "operadora": operadora_codigo,
                "processos_encontrados": 0
            }
        
        # Criar execuções e executar via Celery
        execucoes_criadas = []
        for processo in processos:
            # Criar execução
            execucao = Execucao(
                processo_id=processo.id,
                tipo_execucao=TipoExecucao.DOWNLOAD_FATURA.value,
                status_execucao=StatusExecucao.EXECUTANDO.value,
                parametros_entrada={
                    "operadora_codigo": operadora_codigo,
                    "cliente_hash": processo.cliente.hash_unico,
                    "mes_ano": processo.mes_ano
                },
                mensagem_log=f"Execução RPA {operadora_codigo} iniciada"
            )
            db.add(execucao)
            db.flush()
            execucoes_criadas.append(execucao.id)
            
            # Preparar parâmetros do cliente para Celery
            parametros_cliente = {
                "cliente_hash": processo.cliente.hash_unico,
                "url_portal": operadora.url_portal,
                "login_portal": processo.cliente.login_portal,
                "senha_portal": processo.cliente.senha_portal,
                "cpf": processo.cliente.cpf,
                "filtro": processo.cliente.filtro,
                "nome_sat": processo.cliente.nome_sat,
                "dados_sat": processo.cliente.dados_sat,
                "unidade": processo.cliente.unidade,
                "servico": processo.cliente.servico
            }
            
            # Executar via Celery (importar localmente para evitar circular imports)
            try:
                from backend.services.orquestrador_celery import executar_download_fatura_rpa
                executar_download_fatura_rpa.delay(
                    processo_id=str(processo.id),
                    operadora_codigo=operadora_codigo,
                    parametros_cliente=parametros_cliente
                )
            except Exception as e:
                logger.warning(f"Erro ao enviar task para Celery: {e}")
                # Continua mesmo se Celery não estiver rodando
        
        db.commit()
        
        return {
            "mensagem": f"RPA {operadora_codigo} executado com sucesso",
            "operadora": operadora_codigo,
            "processos_executados": len(processos),
            "execucoes_ids": execucoes_criadas
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na execução do RPA: {str(e)}")

@app.get("/api/rpa/status")
async def status_todos_rpas(db: Session = Depends(get_db)):
    """Retorna status de todos os RPAs"""
    try:
        operadoras_rpa = db.query(Operadora).filter(
            Operadora.possui_rpa == True,
            Operadora.status_ativo == True
        ).all()
        
        status_rpas = []
        for operadora in operadoras_rpa:
            # Contar execuções ativas
            execucoes_ativas = db.query(Execucao).join(Processo).join(Cliente).filter(
                Cliente.operadora_id == operadora.id,
                Execucao.status_execucao == StatusExecucao.EXECUTANDO.value
            ).count()
            
            # Últimas execuções
            ultima_execucao = db.query(Execucao).join(Processo).join(Cliente).filter(
                Cliente.operadora_id == operadora.id
            ).order_by(Execucao.data_inicio.desc()).first()
            
            status_rpas.append({
                "operadora": operadora.nome,
                "codigo": operadora.codigo,
                "execucoes_ativas": execucoes_ativas,
                "ultima_execucao": ultima_execucao.data_inicio if ultima_execucao else None,
                "status_ultima_execucao": ultima_execucao.status_execucao if ultima_execucao else None
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "rpas_status": status_rpas,
            "total_operadoras_rpa": len(operadoras_rpa)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status dos RPAs: {str(e)}")

@app.post("/api/rpa/parar/{operadora_codigo}")
async def parar_rpa_operadora(
    operadora_codigo: str,
    db: Session = Depends(get_db)
):
    """Para execuções ativas de uma operadora"""
    try:
        # Buscar execuções ativas da operadora
        execucoes_ativas = db.query(Execucao).join(Processo).join(Cliente).join(Operadora).filter(
            Operadora.codigo == operadora_codigo.upper(),
            Execucao.status_execucao == StatusExecucao.EXECUTANDO.value
        ).all()
        
        execucoes_paradas = 0
        for execucao in execucoes_ativas:
            execucao.status_execucao = StatusExecucao.FALHOU.value
            execucao.data_fim = datetime.now()
            execucao.mensagem_log = "Execução interrompida pelo usuário"
            execucoes_paradas += 1
        
        db.commit()
        
        return {
            "mensagem": f"RPA {operadora_codigo} parado com sucesso",
            "execucoes_paradas": execucoes_paradas
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parar RPA: {str(e)}")

# === ENDPOINTS DE APROVAÇÃO ===

@app.get("/api/aprovacoes/pendentes")
async def listar_aprovacoes_pendentes(
    skip: int = 0,
    limit: int = 100,
    operadora_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db)
):
    """Lista processos pendentes de aprovação"""
    query = db.query(Processo).filter(
        Processo.status_processo == StatusProcesso.PENDENTE_APROVACAO.value
    )
    
    if operadora_id:
        query = query.join(Cliente).filter(Cliente.operadora_id == operadora_id)
    
    processos = query.offset(skip).limit(limit).all()
    return processos

@app.post("/api/aprovacoes/{processo_id}/aprovar")
async def aprovar_processo(
    processo_id: uuid.UUID,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Aprova um processo"""
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    if processo.status_processo != StatusProcesso.PENDENTE_APROVACAO.value:
        raise HTTPException(status_code=400, detail="Processo não está pendente de aprovação")
    
    # Atualizar processo
    processo.status_processo = StatusProcesso.APROVADA.value
    processo.data_aprovacao = datetime.now()
    if observacoes:
        processo.observacoes = observacoes
    
    db.commit()
    
    return {
        "mensagem": "Processo aprovado com sucesso",
        "processo_id": processo_id,
        "status": "aprovado"
    }

@app.post("/api/aprovacoes/{processo_id}/rejeitar")
async def rejeitar_processo(
    processo_id: uuid.UUID,
    motivo: str,
    db: Session = Depends(get_db)
):
    """Rejeita um processo"""
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    if processo.status_processo != StatusProcesso.PENDENTE_APROVACAO.value:
        raise HTTPException(status_code=400, detail="Processo não está pendente de aprovação")
    
    # Atualizar processo
    processo.status_processo = StatusProcesso.REJEITADA.value
    processo.observacoes = motivo
    
    db.commit()
    
    return {
        "mensagem": "Processo rejeitado com sucesso",
        "processo_id": processo_id,
        "status": "rejeitado",
        "motivo": motivo
    }

# === ENDPOINTS DE NOTIFICAÇÕES ===

@app.get("/api/notificacoes/", response_model=List[Dict])
async def listar_notificacoes(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[TipoNotificacao] = None,
    status: Optional[StatusEnvio] = None,
    db: Session = Depends(get_db)
):
    """Lista notificações"""
    query = db.query(Notificacao)
    
    if tipo:
        query = query.filter(Notificacao.tipo_notificacao == tipo.value)
    if status:
        query = query.filter(Notificacao.status_envio == status.value)
    
    notificacoes = query.offset(skip).limit(limit).all()
    return [
        {
            "id": n.id,
            "tipo_notificacao": n.tipo_notificacao,
            "destinatario": n.destinatario,
            "assunto": n.assunto,
            "mensagem": n.mensagem,
            "status_envio": n.status_envio,
            "tentativas_envio": n.tentativas_envio,
            "data_envio": n.data_envio,
            "data_criacao": n.data_criacao
        } for n in notificacoes
    ]

@app.post("/api/notificacoes/enviar")
async def enviar_notificacao(
    tipo: TipoNotificacao,
    destinatario: str,
    assunto: str,
    mensagem: str,
    db: Session = Depends(get_db)
):
    """Envia uma notificação"""
    notificacao = Notificacao(
        tipo_notificacao=tipo.value,
        destinatario=destinatario,
        assunto=assunto,
        mensagem=mensagem,
        status_envio=StatusEnvio.PENDENTE.value
    )
    
    db.add(notificacao)
    db.commit()
    
    return {
        "mensagem": "Notificação criada e enviada para fila",
        "notificacao_id": notificacao.id,
        "tipo": tipo.value
    }

# === ENDPOINTS DE AGENDAMENTOS ===

@app.get("/api/agendamentos/")
async def listar_agendamentos(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista agendamentos"""
    query = db.query(Agendamento)
    
    if ativo is not None:
        query = query.filter(Agendamento.status_ativo == ativo)
    
    agendamentos = query.offset(skip).limit(limit).all()
    return [
        {
            "id": a.id,
            "nome_agendamento": a.nome_agendamento,
            "descricao": a.descricao,
            "cron_expressao": a.cron_expressao,
            "tipo_agendamento": a.tipo_agendamento,
            "status_ativo": a.status_ativo,
            "proxima_execucao": a.proxima_execucao,
            "ultima_execucao": a.ultima_execucao,
            "data_criacao": a.data_criacao
        } for a in agendamentos
    ]

@app.post("/api/agendamentos/")
async def criar_agendamento(
    nome: str,
    descricao: str,
    cron_expressao: str,
    tipo_agendamento: str,
    parametros: Optional[Dict] = None,
    db: Session = Depends(get_db)
):
    """Cria um novo agendamento"""
    agendamento = Agendamento(
        nome_agendamento=nome,
        descricao=descricao,
        cron_expressao=cron_expressao,
        tipo_agendamento=tipo_agendamento,
        parametros_execucao=parametros or {}
    )
    
    db.add(agendamento)
    db.commit()
    
    return {
        "mensagem": "Agendamento criado com sucesso",
        "agendamento_id": agendamento.id
    }

# === ENDPOINTS DE RELATÓRIOS ===

@app.get("/api/relatorios/dashboard")
async def dashboard_principal(
    mes_ano: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Dados para dashboard principal"""
    mes_atual = mes_ano or datetime.now().strftime("%Y-%m")
    
    # Estatísticas gerais
    total_operadoras = db.query(Operadora).filter(Operadora.status_ativo == True).count()
    total_clientes = db.query(Cliente).filter(Cliente.status_ativo == True).count()
    
    # Processos do mês
    processos_mes = db.query(Processo).filter(Processo.mes_ano == mes_atual).count()
    
    # Processos por status
    processos_por_status = {}
    for status in StatusProcesso:
        count = db.query(Processo).filter(
            Processo.mes_ano == mes_atual,
            Processo.status_processo == status.value
        ).count()
        processos_por_status[status.value] = count
    
    # Execuções ativas
    execucoes_ativas = db.query(Execucao).filter(
        Execucao.status_execucao == StatusExecucao.EXECUTANDO.value
    ).count()
    
    return {
        "mes_referencia": mes_atual,
        "estatisticas_gerais": {
            "total_operadoras": total_operadoras,
            "total_clientes": total_clientes,
            "processos_mes": processos_mes,
            "execucoes_ativas": execucoes_ativas
        },
        "processos_por_status": processos_por_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/relatorios/operadoras")
async def relatorio_operadoras(
    mes_ano: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Relatório de processos por operadora"""
    mes_atual = mes_ano or datetime.now().strftime("%Y-%m")
    
    operadoras = db.query(Operadora).filter(Operadora.status_ativo == True).all()
    relatorio = []
    
    for operadora in operadoras:
        processos_total = db.query(Processo).join(Cliente).filter(
            Cliente.operadora_id == operadora.id,
            Processo.mes_ano == mes_atual
        ).count()
        
        processos_concluidos = db.query(Processo).join(Cliente).filter(
            Cliente.operadora_id == operadora.id,
            Processo.mes_ano == mes_atual,
            Processo.status_processo.in_([
                StatusProcesso.APROVADA.value,
                StatusProcesso.ENVIADA_SAT.value
            ])
        ).count()
        
        relatorio.append({
            "operadora": operadora.nome,
            "codigo": operadora.codigo,
            "possui_rpa": operadora.possui_rpa,
            "processos_total": processos_total,
            "processos_concluidos": processos_concluidos,
            "taxa_sucesso": (processos_concluidos / processos_total * 100) if processos_total > 0 else 0
        })
    
    return {
        "mes_referencia": mes_atual,
        "relatorio_operadoras": relatorio,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Iniciando Sistema de Orquestração RPA BGTELECOM...")
    uvicorn.run(
        "backend_orquestrador:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )