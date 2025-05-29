"""
Sistema de Orquestração RPA - BGTELECOM
Backend FastAPI seguindo rigorosamente o manual
Desenvolvido por: Tiago Pereira Ramos
"""

import os
import csv
import hashlib
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from decimal import Decimal
from enum import Enum

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, Integer, Date, DECIMAL, ForeignKey, func, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, Field
import uvicorn

# Configuração do banco - Usar SQLite para desenvolvimento
DATABASE_URL = "sqlite:///./rpa_bgtelecom.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy.orm import declarative_base
Base = declarative_base()

# Enums conforme manual
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

# Modelos do banco seguindo rigorosamente o manual
class Operadora(Base):
    __tablename__ = "operadoras"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(100), unique=True, nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    possui_rpa = Column(Boolean, default=False)
    status_ativo = Column(Boolean, default=True)
    url_portal = Column(String(500))
    instrucoes_acesso = Column(Text)
    configuracao_rpa = Column(JSON)
    classe_rpa = Column(String(100))
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    
    clientes = relationship("Cliente", back_populates="operadora")

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hash_unico = Column(String(50), unique=True, nullable=False)
    razao_social = Column(String(255), nullable=False)
    nome_sat = Column(String(255), nullable=False)
    cnpj = Column(String(20), nullable=False)
    operadora_id = Column(String(36), ForeignKey("operadoras.id"))
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
    
    operadora = relationship("Operadora", back_populates="clientes")
    processos = relationship("Processo", back_populates="cliente")

class Processo(Base):
    __tablename__ = "processos"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String(36), ForeignKey("clientes.id"))
    mes_ano = Column(String(7), nullable=False)
    status_processo = Column(String(50), default=StatusProcesso.AGUARDANDO_DOWNLOAD.value)
    url_fatura = Column(String(500))
    caminho_s3_fatura = Column(String(500))
    data_vencimento = Column(Date)
    valor_fatura = Column(DECIMAL(15,2))
    aprovado_por_usuario_id = Column(String(36), ForeignKey("usuarios.id"))
    data_aprovacao = Column(DateTime)
    enviado_para_sat = Column(Boolean, default=False)
    data_envio_sat = Column(DateTime)
    upload_manual = Column(Boolean, default=False)
    criado_automaticamente = Column(Boolean, default=True)
    observacoes = Column(Text)
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    
    cliente = relationship("Cliente", back_populates="processos")
    execucoes = relationship("Execucao", back_populates="processo")

class Execucao(Base):
    __tablename__ = "execucoes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    processo_id = Column(String(36), ForeignKey("processos.id"))
    tipo_execucao = Column(String(50), nullable=False)
    status_execucao = Column(String(50), nullable=False)
    classe_rpa_utilizada = Column(String(100))
    parametros_entrada = Column(JSON)
    resultado_saida = Column(JSON)
    data_inicio = Column(DateTime, default=func.now())
    data_fim = Column(DateTime)
    mensagem_log = Column(Text)
    url_arquivo_s3 = Column(String(500))
    numero_tentativa = Column(Integer, default=1)
    detalhes_erro = Column(JSON)
    executado_por_usuario_id = Column(String(36), ForeignKey("usuarios.id"))
    ip_origem = Column(String(45))
    user_agent = Column(Text)
    
    processo = relationship("Processo", back_populates="execucoes")

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome_completo = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    telefone = Column(String(20))
    perfil_usuario = Column(String(50), nullable=False)
    status_ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=func.now())

# Schemas Pydantic
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
    id: str
    data_criacao: datetime
    
    class Config:
        from_attributes = True

class ClienteBase(BaseModel):
    razao_social: str
    nome_sat: str
    cnpj: str
    operadora_id: str
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
    id: str
    hash_unico: str
    data_criacao: datetime
    operadora: OperadoraResponse
    
    class Config:
        from_attributes = True

class ProcessoResponse(BaseModel):
    id: str
    cliente_id: str
    mes_ano: str
    status_processo: StatusProcesso
    data_criacao: datetime
    cliente: ClienteResponse
    
    class Config:
        from_attributes = True

def generate_hash_cad(nome_filtro: str, operadora: str, servico: str, dados_sat: str = "", filtro: str = "", unidade: str = "") -> str:
    """Gera hash único conforme especificação do manual"""
    concatenated = f"{nome_filtro}_{operadora}_{servico}_{dados_sat}_{filtro}_{unidade}"
    return hashlib.md5(concatenated.encode()).hexdigest()[:16]

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def carregar_dados_csv_bgtelecom():
    """Carrega dados reais do CSV da BGTELECOM"""
    dados = []
    csv_path = "attached_assets/DADOS SAT - BGTELECOM - BGTELECOM .csv"
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                dados.append(row)
    except FileNotFoundError:
        print(f"Arquivo CSV não encontrado: {csv_path}")
        return []
    
    return dados

# Criação da aplicação FastAPI
app = FastAPI(
    title="Sistema de Orquestração RPA - BGTELECOM",
    description="Sistema completo de orquestração de RPAs para gestão de faturas de telecomunicações",
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

# Eventos de inicialização
@app.on_event("startup")
async def inicializar_dados_sistema():
    """Inicializa dados do sistema com base no CSV da BGTELECOM"""
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Verificar se já existem operadoras
        operadoras_existentes = db.query(Operadora).count()
        if operadoras_existentes > 0:
            print("Dados já inicializados")
            return
        
        print("Inicializando dados do sistema...")
        
        # Criar operadoras baseadas no CSV
        operadoras_data = {
            "EMBRATEL": {"possui_rpa": True, "url": "https://webebt01.embratel.com.br/embratelonline/index.asp"},
            "DIGITALNET": {"possui_rpa": True, "url": "https://sac.digitalnetms.com.br/login"},
            "AZUTON": {"possui_rpa": False, "url": None},
            "VIVO": {"possui_rpa": True, "url": None},
            "OI": {"possui_rpa": True, "url": None},
            "SAT": {"possui_rpa": True, "url": None}
        }
        
        operadoras_criadas = {}
        for codigo, info in operadoras_data.items():
            operadora = Operadora(
                nome=codigo,
                codigo=codigo,
                possui_rpa=info["possui_rpa"],
                url_portal=info["url"],
                status_ativo=True
            )
            db.add(operadora)
            db.flush()
            operadoras_criadas[codigo] = operadora
        
        # Carregar dados do CSV
        dados_csv = carregar_dados_csv_bgtelecom()
        
        for row in dados_csv:
            hash_original = row.get("HASH", "").strip()
            if not hash_original:
                continue
                
            operadora_codigo = row.get("OPERADORA", "").strip().upper()
            if operadora_codigo not in operadoras_criadas:
                continue
            
            # Criar cliente baseado nos dados reais
            cliente = Cliente(
                hash_unico=hash_original,
                razao_social=row.get("RAZÃO SOCIAL", "").strip(),
                nome_sat=row.get("NOME SAT", "").strip(),
                cnpj=row.get("CNPJ", "").strip(),
                operadora_id=operadoras_criadas[operadora_codigo].id,
                filtro=row.get("FILTRO", "").strip(),
                servico=row.get("SERVIÇO", "").strip(),
                dados_sat=row.get("DADOS SAT", "").strip(),
                unidade=row.get("UNIDADE / FILTRO SAT", "").strip(),
                site_emissao=row.get("SITE PARA EMISSÃO", "").strip(),
                login_portal=row.get("LOGIN", "").strip(),
                senha_portal=row.get("SENHA", "").strip(),
                cpf=row.get("CPF", "").strip(),
                status_ativo=True
            )
            db.add(cliente)
        
        db.commit()
        print("Dados inicializados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao inicializar dados: {e}")
        db.rollback()
    finally:
        db.close()

# Rotas da API
@app.get("/")
async def root():
    return {
        "sistema": "Orquestrador RPA BGTELECOM",
        "versao": "1.0.0",
        "status": "ativo",
        "desenvolvido_por": "Tiago Pereira Ramos"
    }

@app.get("/api/health")
async def verificar_saude_sistema(db: Session = Depends(get_db)):
    """Verifica a saúde geral do sistema"""
    try:
        # Contar registros principais
        total_operadoras = db.query(Operadora).count()
        total_clientes = db.query(Cliente).count()
        total_processos = db.query(Processo).count()
        
        return {
            "status": "saudavel",
            "database": "conectado",
            "total_operadoras": total_operadoras,
            "total_clientes": total_clientes,
            "total_processos": total_processos,
            "rpas": {
                "VIVO": "parado",
                "OI": "parado",
                "EMBRATEL": "parado",
                "SAT": "parado",
                "AZUTON": "parado",
                "DIGITALNET": "parado"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na verificação de saúde: {str(e)}")

@app.get("/api/operadoras", response_model=List[OperadoraResponse])
async def listar_operadoras(db: Session = Depends(get_db)):
    """Lista todas as operadoras"""
    operadoras = db.query(Operadora).filter(Operadora.status_ativo == True).all()
    return operadoras

@app.post("/api/operadoras", response_model=OperadoraResponse)
async def criar_operadora(operadora: OperadoraCreate, db: Session = Depends(get_db)):
    """Cria uma nova operadora"""
    db_operadora = Operadora(**operadora.dict())
    db.add(db_operadora)
    db.commit()
    db.refresh(db_operadora)
    return db_operadora

@app.get("/api/clientes", response_model=List[ClienteResponse])
async def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    operadora_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db)
):
    """Lista clientes com filtros opcionais"""
    query = db.query(Cliente).filter(Cliente.status_ativo == True)
    
    if operadora_id:
        query = query.filter(Cliente.operadora_id == operadora_id)
    
    clientes = query.offset(skip).limit(limit).all()
    return clientes

@app.post("/api/clientes", response_model=ClienteResponse)
async def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Cria um novo cliente"""
    
    # Gerar hash único
    hash_unico = generate_hash_cad(
        cliente.razao_social,
        cliente.operadora_id,
        cliente.servico or "",
        cliente.dados_sat or "",
        cliente.filtro or "",
        cliente.unidade
    )
    
    db_cliente = Cliente(
        **cliente.dict(),
        hash_unico=hash_unico
    )
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.get("/api/processos", response_model=List[ProcessoResponse])
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

@app.get("/api/dashboard/resumo")
async def dashboard_resumo(db: Session = Depends(get_db)):
    """Resumo para o dashboard"""
    try:
        total_operadoras = db.query(Operadora).filter(Operadora.status_ativo == True).count()
        total_clientes = db.query(Cliente).filter(Cliente.status_ativo == True).count()
        total_processos = db.query(Processo).count()
        
        # Clientes por operadora
        clientes_por_operadora = {}
        operadoras = db.query(Operadora).filter(Operadora.status_ativo == True).all()
        
        for operadora in operadoras:
            count = db.query(Cliente).filter(
                Cliente.operadora_id == operadora.id,
                Cliente.status_ativo == True
            ).count()
            clientes_por_operadora[operadora.codigo] = count
        
        return {
            "total_operadoras": total_operadoras,
            "total_clientes": total_clientes,
            "total_processos": total_processos,
            "clientes_por_operadora": clientes_por_operadora,
            "status_rpas": {
                "VIVO": "parado",
                "OI": "parado",
                "EMBRATEL": "parado",
                "SAT": "parado",
                "AZUTON": "parado",
                "DIGITALNET": "parado"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no resumo do dashboard: {str(e)}")

# ========== APIS DE ORQUESTRAÇÃO RPA ==========

@app.post("/api/executar-rpa")
async def executar_rpa_endpoint(
    operadora: str,
    cliente_id: str,
    tipo_operacao: str = "download",
    db: Session = Depends(get_db)
):
    """Executa RPA para uma operadora específica"""
    try:
        # Busca dados do cliente
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        # Busca dados da operadora
        operadora_obj = db.query(Operadora).filter(Operadora.codigo == operadora.upper()).first()
        if not operadora_obj:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        
        # Verifica se operadora possui RPA
        if not operadora_obj.possui_rpa and tipo_operacao == "download":
            raise HTTPException(
                status_code=400, 
                detail="Operadora não possui RPA homologado. Use upload manual."
            )
        
        # Cria processo se não existir
        mes_atual = datetime.now().strftime("%Y-%m")
        processo = db.query(Processo).filter(
            Processo.cliente_id == cliente_id,
            Processo.mes_ano == mes_atual
        ).first()
        
        if not processo:
            processo = Processo(
                id=str(uuid.uuid4()),
                cliente_id=cliente_id,
                mes_ano=mes_atual,
                status_processo=StatusProcesso.AGUARDANDO_DOWNLOAD.value,
                criado_automaticamente=True,
                data_criacao=datetime.now()
            )
            db.add(processo)
            db.commit()
        
        return {
            "sucesso": True,
            "processo_id": processo.id,
            "operadora": operadora,
            "tipo_operacao": tipo_operacao,
            "mensagem": f"RPA {operadora} iniciado com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/aprovacoes/pendentes")
async def listar_aprovacoes_pendentes(db: Session = Depends(get_db)):
    """Lista faturas pendentes de aprovação"""
    try:
        processos = db.query(Processo).filter(
            Processo.status_processo == StatusProcesso.PENDENTE_APROVACAO.value
        ).join(Cliente).join(Operadora).all()
        
        faturas_pendentes = []
        for processo in processos:
            faturas_pendentes.append({
                "processo_id": processo.id,
                "cliente_id": processo.cliente_id,
                "cliente_nome": processo.cliente.razao_social,
                "operadora_nome": processo.cliente.operadora.nome,
                "mes_ano": processo.mes_ano,
                "url_fatura": processo.url_fatura,
                "data_criacao": processo.data_criacao.isoformat(),
                "observacoes": processo.observacoes
            })
        
        return {
            "faturas_pendentes": faturas_pendentes,
            "total": len(faturas_pendentes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/aprovacoes/{processo_id}")
async def processar_aprovacao(
    processo_id: str,
    acao: str,
    usuario_aprovador_id: str,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Processa aprovação/rejeição de fatura"""
    try:
        # Busca o processo
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        
        if not processo:
            raise HTTPException(status_code=404, detail="Processo não encontrado")
        
        # Busca o usuário aprovador
        usuario = db.query(Usuario).filter(Usuario.id == usuario_aprovador_id).first()
        
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário aprovador não encontrado")
        
        # Processa a ação
        if acao == "aprovar":
            processo.status_processo = StatusProcesso.APROVADA.value
            processo.data_aprovacao = datetime.now()
            mensagem = "Fatura aprovada com sucesso"
            
        elif acao == "rejeitar":
            processo.status_processo = StatusProcesso.REJEITADA.value
            processo.data_aprovacao = datetime.now()
            mensagem = "Fatura rejeitada"
        else:
            raise HTTPException(status_code=400, detail="Ação inválida. Use: aprovar, rejeitar")
        
        # Adiciona observações
        if observacoes:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            nova_observacao = f"[{timestamp}] {usuario.nome_completo}: {observacoes}"
            processo.observacoes = nova_observacao
        
        processo.data_atualizacao = datetime.now()
        db.commit()
        
        return {
            "sucesso": True,
            "processo_id": processo_id,
            "acao": acao,
            "status": processo.status_processo,
            "mensagem": mensagem,
            "aprovado_por": usuario.nome_completo
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rpas-disponiveis")
async def listar_rpas_disponiveis():
    """Lista RPAs disponíveis no sistema"""
    try:
        # Lista operadoras com RPA disponível conforme manual
        rpas_disponiveis = [
            {"codigo": "EMB", "nome": "EMBRATEL", "ativo": True},
            {"codigo": "DIG", "nome": "DIGITALNET", "ativo": True},
            {"codigo": "AZU", "nome": "AZUTON", "ativo": True},
            {"codigo": "VIV", "nome": "VIVO", "ativo": True},
            {"codigo": "OI", "nome": "OI", "ativo": True},
            {"codigo": "SAT", "nome": "SAT", "ativo": True}
        ]
        
        return {
            "rpas_disponiveis": rpas_disponiveis,
            "total": len(rpas_disponiveis)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)