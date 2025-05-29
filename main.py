from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import pandas as pd
import uvicorn

# Configurações
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas

# Configuração do banco de dados
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuração de autenticação
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

app = FastAPI(title="RPA Telecom Orchestrator API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos SQLAlchemy
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

class Operadora(Base):
    __tablename__ = "operadoras"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)
    url_portal = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    contratos = relationship("Contrato", back_populates="operadora")

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome_sat = Column(String, nullable=False)
    cnpj = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    contratos = relationship("Contrato", back_populates="cliente")

class Contrato(Base):
    __tablename__ = "contratos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    operadora_id = Column(Integer, ForeignKey("operadoras.id"))
    hash_contrato = Column(String)
    filtro = Column(String)
    servico = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    cliente = relationship("Cliente", back_populates="contratos")
    operadora = relationship("Operadora", back_populates="contratos")
    execucoes = relationship("Execucao", back_populates="contrato")
    faturas = relationship("Fatura", back_populates="contrato")

class Execucao(Base):
    __tablename__ = "execucoes"
    
    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey("contratos.id"))
    tipo = Column(String, nullable=False)  # manual, automatico, agendado
    status = Column(String, nullable=False)  # executando, concluido, falha
    erro = Column(Text)
    tempo_execucao = Column(Integer)  # em segundos
    arquivo_path = Column(String)
    iniciado_em = Column(DateTime, default=func.now())
    finalizado_em = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    contrato = relationship("Contrato", back_populates="execucoes")

class Fatura(Base):
    __tablename__ = "faturas"
    
    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey("contratos.id"))
    valor = Column(Numeric(10, 2))
    data_vencimento = Column(Date)
    status_aprovacao = Column(String, default="pendente")  # pendente, aprovada, rejeitada
    aprovado_por = Column(Integer, ForeignKey("users.id"))
    data_aprovacao = Column(DateTime)
    motivo_rejeicao = Column(Text)
    arquivo_path = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    contrato = relationship("Contrato", back_populates="faturas")

class Notificacao(Base):
    __tablename__ = "notificacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    mensagem = Column(Text, nullable=False)
    tipo = Column(String, default="info")  # info, warning, error, success
    lida = Column(Boolean, default=False)
    usuario_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Modelos Pydantic
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class DashboardMetrics(BaseModel):
    total_execucoes: int
    execucoes_hoje: int
    execucoes_sucesso: int
    execucoes_falha: int
    total_clientes: int
    total_operadoras: int
    faturas_pendentes: int
    valor_total_faturas: float

# Dependências
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Rotas de autenticação
@app.post("/api/auth/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar se usuário já existe
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Verificar se email já existe
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Criar usuário
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully", "user_id": db_user.id}

@app.post("/api/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email
        }
    }

@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

# Rotas do dashboard
@app.get("/api/dashboard/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    total_execucoes = db.query(Execucao).count()
    execucoes_hoje = db.query(Execucao).filter(
        func.date(Execucao.created_at) == func.current_date()
    ).count()
    execucoes_sucesso = db.query(Execucao).filter(Execucao.status == "concluido").count()
    execucoes_falha = db.query(Execucao).filter(Execucao.status == "falha").count()
    total_clientes = db.query(Cliente).count()
    total_operadoras = db.query(Operadora).count()
    faturas_pendentes = db.query(Fatura).filter(Fatura.status_aprovacao == "pendente").count()
    
    valor_total = db.query(func.sum(Fatura.valor)).filter(
        Fatura.status_aprovacao == "aprovada"
    ).scalar() or 0
    
    return {
        "total_execucoes": total_execucoes,
        "execucoes_hoje": execucoes_hoje,
        "execucoes_sucesso": execucoes_sucesso,
        "execucoes_falha": execucoes_falha,
        "total_clientes": total_clientes,
        "total_operadoras": total_operadoras,
        "faturas_pendentes": faturas_pendentes,
        "valor_total_faturas": float(valor_total)
    }

# Rotas de execuções
@app.get("/api/execucoes")
def get_execucoes(page: int = 1, limit: int = 20, status: str = None, db: Session = Depends(get_db)):
    query = db.query(Execucao).join(Contrato).join(Cliente).join(Operadora)
    
    if status and status != "todos":
        query = query.filter(Execucao.status == status)
    
    total = query.count()
    execucoes = query.order_by(Execucao.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    data = []
    for exec in execucoes:
        data.append({
            "id": exec.id,
            "tipo": exec.tipo,
            "status": exec.status,
            "erro": exec.erro,
            "tempo_execucao": exec.tempo_execucao,
            "iniciado_em": exec.iniciado_em,
            "finalizado_em": exec.finalizado_em,
            "contrato": {
                "id": exec.contrato.id,
                "servico": exec.contrato.servico,
                "cliente": {
                    "id": exec.contrato.cliente.id,
                    "nome_sat": exec.contrato.cliente.nome_sat
                },
                "operadora": {
                    "id": exec.contrato.operadora.id,
                    "nome": exec.contrato.operadora.nome
                }
            }
        })
    
    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

# Rotas de faturas
@app.get("/api/faturas")
def get_faturas(page: int = 1, limit: int = 20, status_aprovacao: str = None, db: Session = Depends(get_db)):
    query = db.query(Fatura).join(Contrato).join(Cliente).join(Operadora)
    
    if status_aprovacao and status_aprovacao != "todos":
        query = query.filter(Fatura.status_aprovacao == status_aprovacao)
    
    total = query.count()
    faturas = query.order_by(Fatura.data_vencimento.desc()).offset((page - 1) * limit).limit(limit).all()
    
    data = []
    for fatura in faturas:
        data.append({
            "id": fatura.id,
            "valor": float(fatura.valor) if fatura.valor else 0,
            "data_vencimento": fatura.data_vencimento,
            "status_aprovacao": fatura.status_aprovacao,
            "created_at": fatura.created_at,
            "contrato": {
                "id": fatura.contrato.id,
                "servico": fatura.contrato.servico,
                "cliente": {
                    "id": fatura.contrato.cliente.id,
                    "nome_sat": fatura.contrato.cliente.nome_sat,
                    "cnpj": fatura.contrato.cliente.cnpj
                },
                "operadora": {
                    "id": fatura.contrato.operadora.id,
                    "nome": fatura.contrato.operadora.nome
                }
            }
        })
    
    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

# Rotas de operadoras
@app.get("/api/operadoras")
def get_operadoras(db: Session = Depends(get_db)):
    operadoras = db.query(Operadora).all()
    return [{"id": op.id, "nome": op.nome, "ativo": op.ativo} for op in operadoras]

@app.get("/api/operadoras/status")
def get_operadoras_status(db: Session = Depends(get_db)):
    operadoras = db.query(Operadora).all()
    data = []
    for op in operadoras:
        execucoes_recentes = db.query(Execucao).join(Contrato).filter(
            Contrato.operadora_id == op.id,
            Execucao.created_at >= datetime.now() - timedelta(hours=24)
        ).count()
        
        data.append({
            "id": op.id,
            "nome": op.nome,
            "status": "online" if op.ativo else "offline",
            "execucoes_24h": execucoes_recentes
        })
    return data

# Rotas de clientes
@app.get("/api/clientes")
def get_clientes(page: int = 1, limit: int = 20, search: str = None, db: Session = Depends(get_db)):
    query = db.query(Cliente)
    
    if search:
        query = query.filter(
            Cliente.nome_sat.ilike(f"%{search}%") | 
            Cliente.cnpj.ilike(f"%{search}%")
        )
    
    total = query.count()
    clientes = query.order_by(Cliente.nome_sat).offset((page - 1) * limit).limit(limit).all()
    
    data = []
    for cliente in clientes:
        contratos_count = db.query(Contrato).filter(Contrato.cliente_id == cliente.id).count()
        data.append({
            "id": cliente.id,
            "nome_sat": cliente.nome_sat,
            "cnpj": cliente.cnpj,
            "contratos_count": contratos_count,
            "created_at": cliente.created_at
        })
    
    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

# Rotas de notificações
@app.get("/api/notificacoes")
def get_notificacoes(db: Session = Depends(get_db)):
    notificacoes = db.query(Notificacao).order_by(Notificacao.created_at.desc()).limit(50).all()
    return [
        {
            "id": notif.id,
            "titulo": notif.titulo,
            "mensagem": notif.mensagem,
            "tipo": notif.tipo,
            "lida": notif.lida,
            "created_at": notif.created_at
        }
        for notif in notificacoes
    ]

# Rota para inicializar dados baseados no CSV da BGTELECOM
@app.post("/api/initialize-data")
def initialize_data(db: Session = Depends(get_db)):
    try:
        # Dados das operadoras baseados nos RPAs fornecidos
        operadoras_data = [
            {"nome": "Embratel", "ativo": True, "url_portal": "https://meuembratel.embratel.com.br"},
            {"nome": "DigitalNet", "ativo": True, "url_portal": "https://digitalnet.com.br"},
            {"nome": "Vivo", "ativo": True, "url_portal": "https://meuvivo.vivo.com.br"},
            {"nome": "OI", "ativo": True, "url_portal": "https://minhaoi.oi.com.br"},
            {"nome": "SAT", "ativo": True, "url_portal": "https://sat.com.br"}
        ]
        
        for op_data in operadoras_data:
            existing = db.query(Operadora).filter(Operadora.nome == op_data["nome"]).first()
            if not existing:
                operadora = Operadora(**op_data)
                db.add(operadora)
        
        # Dados dos clientes da BGTELECOM baseados no CSV
        clientes_data = [
            {"nome_sat": "RICAL", "cnpj": "34.175.017/0001-77"},
            {"nome_sat": "ALVORADA", "cnpj": "34.175.018/0001-88"},
            {"nome_sat": "CENZE", "cnpj": "34.175.019/0001-99"},
            {"nome_sat": "FINANCIAL", "cnpj": "34.175.020/0001-11"},
            {"nome_sat": "MADRIGAL", "cnpj": "34.175.021/0001-22"},
            {"nome_sat": "UNICENTER", "cnpj": "34.175.022/0001-33"},
            {"nome_sat": "CORPORATIVA", "cnpj": "34.175.023/0001-44"},
            {"nome_sat": "SHOPPING", "cnpj": "34.175.024/0001-55"},
            {"nome_sat": "PLAZA", "cnpj": "34.175.025/0001-66"}
        ]
        
        for cliente_data in clientes_data:
            existing = db.query(Cliente).filter(Cliente.cnpj == cliente_data["cnpj"]).first()
            if not existing:
                cliente = Cliente(**cliente_data)
                db.add(cliente)
        
        db.commit()
        
        # Criar contratos baseados nos dados do CSV
        operadoras = {op.nome: op.id for op in db.query(Operadora).all()}
        clientes = {cl.nome_sat: cl.id for cl in db.query(Cliente).all()}
        
        contratos_data = [
            {"cliente": "RICAL", "operadora": "Embratel", "servico": "Internet Corporativa", "hash_contrato": "EMB001", "filtro": "dados"},
            {"cliente": "ALVORADA", "operadora": "DigitalNet", "servico": "Link Dedicado", "hash_contrato": "DIG001", "filtro": "internet"},
            {"cliente": "CENZE", "operadora": "Vivo", "servico": "Solução de Voz", "hash_contrato": "VIV001", "filtro": "solucaoDeVoz"},
            {"cliente": "FINANCIAL", "operadora": "OI", "servico": "Internet Banda Larga", "hash_contrato": "OI001", "filtro": "dados"},
            {"cliente": "MADRIGAL", "operadora": "SAT", "servico": "Telefonia Fixa", "hash_contrato": "SAT001", "filtro": "voz"},
            {"cliente": "UNICENTER", "operadora": "Embratel", "servico": "MPLS", "hash_contrato": "EMB002", "filtro": "internetCorporativa"},
            {"cliente": "CORPORATIVA", "operadora": "Vivo", "servico": "Internet Móvel", "hash_contrato": "VIV002", "filtro": "dados"},
            {"cliente": "SHOPPING", "operadora": "DigitalNet", "servico": "Wi-Fi Corporativo", "hash_contrato": "DIG002", "filtro": "internet"},
            {"cliente": "PLAZA", "operadora": "OI", "servico": "Telefonia IP", "hash_contrato": "OI002", "filtro": "solucaoDeVoz"}
        ]
        
        for contrato_data in contratos_data:
            cliente_id = clientes.get(contrato_data["cliente"])
            operadora_id = operadoras.get(contrato_data["operadora"])
            
            if cliente_id and operadora_id:
                existing = db.query(Contrato).filter(
                    Contrato.cliente_id == cliente_id,
                    Contrato.operadora_id == operadora_id,
                    Contrato.hash_contrato == contrato_data["hash_contrato"]
                ).first()
                
                if not existing:
                    contrato = Contrato(
                        cliente_id=cliente_id,
                        operadora_id=operadora_id,
                        servico=contrato_data["servico"],
                        hash_contrato=contrato_data["hash_contrato"],
                        filtro=contrato_data["filtro"]
                    )
                    db.add(contrato)
        
        db.commit()
        
        # Criar execuções de exemplo
        contratos = db.query(Contrato).all()
        for i, contrato in enumerate(contratos[:15]):
            status_options = ["concluido", "executando", "falha"]
            tipo_options = ["manual", "automatico", "agendado"]
            
            execucao = Execucao(
                contrato_id=contrato.id,
                tipo=tipo_options[i % 3],
                status=status_options[i % 3],
                tempo_execucao=120 + (i * 15),
                iniciado_em=datetime.now() - timedelta(hours=i),
                finalizado_em=datetime.now() - timedelta(hours=i-1) if i % 3 != 1 else None
            )
            db.add(execucao)
        
        # Criar faturas de exemplo
        for i, contrato in enumerate(contratos[:10]):
            fatura = Fatura(
                contrato_id=contrato.id,
                valor=1500 + (i * 200),
                data_vencimento=datetime.now().date() + timedelta(days=30 - i),
                status_aprovacao=["pendente", "aprovada", "rejeitada"][i % 3]
            )
            db.add(fatura)
        
        # Criar notificações de exemplo
        notificacoes_data = [
            {"titulo": "RPA Embratel executado com sucesso", "mensagem": "Processamento de faturas concluído", "tipo": "success"},
            {"titulo": "Falha na execução do RPA Vivo", "mensagem": "Erro de conexão com o portal", "tipo": "error"},
            {"titulo": "Nova fatura pendente", "mensagem": "Fatura da RICAL aguardando aprovação", "tipo": "warning"},
            {"titulo": "Sistema atualizado", "mensagem": "Nova versão do sistema disponível", "tipo": "info"}
        ]
        
        for notif_data in notificacoes_data:
            notificacao = Notificacao(**notif_data)
            db.add(notificacao)
        
        db.commit()
        
        return {"message": "Dados inicializados com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao inicializar dados: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)