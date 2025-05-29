"""
Schemas Pydantic para Notificação
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificacaoBase(BaseModel):
    tipo_notificacao: str  # EMAIL, WHATSAPP, TELEGRAM, SLACK
    destinatario: str
    assunto: Optional[str] = None
    mensagem: str

class NotificacaoCreate(NotificacaoBase):
    pass

class NotificacaoUpdate(BaseModel):
    status_envio: Optional[str] = None
    tentativas_envio: Optional[int] = None
    data_envio: Optional[datetime] = None
    mensagem_erro: Optional[str] = None

class NotificacaoResponse(NotificacaoBase):
    id: str
    status_envio: str = "PENDENTE"
    tentativas_envio: int = 0
    data_envio: Optional[datetime] = None
    mensagem_erro: Optional[str] = None
    data_criacao: datetime

    class Config:
        from_attributes = True