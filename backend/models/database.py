"""
Configuração da conexão com o banco de dados PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL do banco PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/rpa_bgtelecom")

# Criar engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Criar session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para modelos
Base = declarative_base()

def get_db_session():
    """Retorna uma sessão do banco de dados"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def get_db():
    """Dependency para FastAPI - retorna sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()