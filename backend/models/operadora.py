"""
Modelo Operadora
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from config.database import Base


class Operadora(Base):
    """Modelo para operadoras de telecomunicações"""
    
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
    
    def __repr__(self):
        return f"<Operadora(nome='{self.nome}', codigo='{self.codigo}')>"