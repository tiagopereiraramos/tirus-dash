"""
Schemas Pydantic para Agendamento
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AgendamentoBase(BaseModel):
    nome_agendamento: str
    descricao: Optional[str] = None
    cron_expressao: str
    tipo_agendamento: str
    status_ativo: bool = True
    parametros_execucao: Optional[str] = None

class AgendamentoCreate(AgendamentoBase):
    pass

class AgendamentoUpdate(BaseModel):
    nome_agendamento: Optional[str] = None
    descricao: Optional[str] = None
    cron_expressao: Optional[str] = None
    tipo_agendamento: Optional[str] = None
    status_ativo: Optional[bool] = None
    proxima_execucao: Optional[datetime] = None
    ultima_execucao: Optional[datetime] = None
    parametros_execucao: Optional[str] = None

class AgendamentoResponse(AgendamentoBase):
    id: str
    proxima_execucao: Optional[datetime] = None
    ultima_execucao: Optional[datetime] = None
    data_criacao: datetime

    class Config:
        from_attributes = True