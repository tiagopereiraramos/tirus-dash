"""
Modelo de Usuário
Conforme especificação do manual da BGTELECOM
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text
from datetime import datetime

from ..config.database import Base

class Usuario(Base):
    """
    Modelo de Usuário para autenticação e controle de acesso
    """
    __tablename__ = "usuarios"
    
    # Campos principais
    id = Column(String, primary_key=True)
    nome_completo = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telefone = Column(String)
    
    # Controle de acesso
    perfil_usuario = Column(String, nullable=False)  # ADMINISTRADOR, APROVADOR, OPERADOR
    status_ativo = Column(Boolean, default=True)
    
    # Timestamps
    data_criacao = Column(DateTime, default=datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.now)
    
    # Configurações
    configuracoes_notificacao = Column(Text)  # JSON string
    
    def __repr__(self):
        return f"<Usuario(id='{self.id}', nome='{self.nome_completo}', perfil='{self.perfil_usuario}')>"