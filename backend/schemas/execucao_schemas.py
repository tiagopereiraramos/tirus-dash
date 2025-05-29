"""
Schemas Pydantic para Execução
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExecucaoBase(BaseModel):
    processo_id: str
    cliente_id: str
    operadora_codigo: str
    tipo_execucao: str
    status_execucao: str = "iniciado"
    tentativa_numero: int = 1
    max_tentativas: int = 3

class ExecucaoCreate(ExecucaoBase):
    pass

class ExecucaoUpdate(BaseModel):
    status_execucao: Optional[str] = None
    sucesso: Optional[bool] = None
    arquivo_baixado: Optional[str] = None
    url_s3: Optional[str] = None
    logs_execucao: Optional[str] = None
    mensagem_erro: Optional[str] = None
    data_fim: Optional[datetime] = None
    tempo_execucao_segundos: Optional[int] = None

class ExecucaoResponse(ExecucaoBase):
    id: str
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    tempo_execucao_segundos: Optional[int] = None
    sucesso: bool = False
    arquivo_baixado: Optional[str] = None
    url_s3: Optional[str] = None
    logs_execucao: Optional[str] = None
    mensagem_erro: Optional[str] = None
    celery_task_id: Optional[str] = None

    class Config:
        from_attributes = True