"""
Modelo de Notificação
Conforme especificação do manual da BGTELECOM
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from datetime import datetime

from ..config.database import Base

class Notificacao(Base):
    """
    Modelo de Notificação para controle de envios
    """
    __tablename__ = "notificacoes"
    
    # Campos principais
    id = Column(String, primary_key=True)
    tipo_notificacao = Column(String, nullable=False)  # EMAIL, WHATSAPP, TELEGRAM, SLACK
    destinatario = Column(String, nullable=False)
    assunto = Column(String)
    mensagem = Column(Text, nullable=False)
    
    # Status e controle
    status_envio = Column(String, default="PENDENTE")  # PENDENTE, ENVIADO, FALHOU
    tentativas_envio = Column(Integer, default=0)
    data_envio = Column(DateTime)
    mensagem_erro = Column(Text)
    
    # Timestamps
    data_criacao = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Notificacao(id='{self.id}', tipo='{self.tipo_notificacao}', status='{self.status_envio}')>"