"""
Modelo de Agendamento
Conforme especificação do manual da BGTELECOM
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text
from datetime import datetime

from ..config.database import Base

class Agendamento(Base):
    """
    Modelo de Agendamento para tarefas automáticas
    """
    __tablename__ = "agendamentos"
    
    # Campos principais
    id = Column(String, primary_key=True)
    nome_agendamento = Column(String, nullable=False)
    descricao = Column(Text)
    cron_expressao = Column(String, nullable=False)
    tipo_agendamento = Column(String, nullable=False)
    
    # Status e controle
    status_ativo = Column(Boolean, default=True)
    proxima_execucao = Column(DateTime)
    ultima_execucao = Column(DateTime)
    parametros_execucao = Column(Text)  # JSON string
    
    # Timestamps
    data_criacao = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Agendamento(id='{self.id}', nome='{self.nome_agendamento}', ativo={self.status_ativo})>"