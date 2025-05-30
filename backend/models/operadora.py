"""
Modelo Operadora
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from config.database import Base


class Operadora(Base):
    """Modelo para operadoras de telecomunicações"""
    
    __tablename__ = "operadoras"
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), unique=True, nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    possui_rpa = Column(Boolean, default=False)
    status_ativo = Column(Boolean, default=True)
    url_portal = Column(String(500))
    instrucoes_acesso = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relacionamentos
    clientes = relationship("Cliente", back_populates="operadora")
    
    def __repr__(self):
        return f"<Operadora(nome='{self.nome}', codigo='{self.codigo}')>"