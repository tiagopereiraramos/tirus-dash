"""
Schemas Pydantic para Processo
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ProcessoBase(BaseModel):
    cliente_id: str
    mes_ano: str
    status_processo: str = "aguardando_download"
    criado_automaticamente: bool = False
    upload_manual: bool = False
    url_fatura: Optional[str] = None
    data_vencimento: Optional[datetime] = None
    valor_fatura: Optional[Decimal] = None
    observacoes: Optional[str] = None

class ProcessoCreate(ProcessoBase):
    pass

class ProcessoUpdate(BaseModel):
    status_processo: Optional[str] = None
    url_fatura: Optional[str] = None
    caminho_s3_fatura: Optional[str] = None
    data_vencimento: Optional[datetime] = None
    valor_fatura: Optional[Decimal] = None
    aprovado_por_usuario_id: Optional[str] = None
    data_aprovacao: Optional[datetime] = None
    observacoes: Optional[str] = None

class ProcessoResponse(ProcessoBase):
    id: str
    caminho_s3_fatura: Optional[str] = None
    aprovado_por_usuario_id: Optional[str] = None
    data_aprovacao: Optional[datetime] = None
    logs_execucao: Optional[str] = None
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True