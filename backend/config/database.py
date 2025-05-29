"""
Configuração do banco de dados PostgreSQL
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import configuracoes

# Criar engine do banco
engine = create_engine(
    configuracoes.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=configuracoes.DEBUG
)

# Criar SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def obter_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()