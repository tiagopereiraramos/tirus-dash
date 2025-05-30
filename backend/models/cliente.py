"""
Modelo Cliente
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from config.database import Base


class Cliente(Base):
    """Modelo para clientes da BGTELECOM"""
    
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True)
    hash_unico = Column(String(50), unique=True, nullable=False)
    razao_social = Column(String(255), nullable=False)
    nome_sat = Column(String(255), nullable=False)
    cnpj = Column(String(20), nullable=False)
    operadora_id = Column(Integer, ForeignKey("operadoras.id"))
    filtro = Column(String(255))
    servico = Column(String(255))
    dados_sat = Column(Text)
    unidade = Column(String(100), nullable=False)
    site_emissao = Column(String(255))
    login_portal = Column(String(100))
    senha_portal = Column(String(100))
    cpf = Column(String(20))
    status_ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relacionamentos
    operadora = relationship("Operadora", back_populates="clientes")
    processos = relationship("Processo", back_populates="cliente")
    
    def __repr__(self):
        return f"<Cliente(razao_social='{self.razao_social}', hash='{self.hash_unico}')>"