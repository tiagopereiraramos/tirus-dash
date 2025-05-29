"""
Schemas Pydantic para Operadora
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OperadoraBase(BaseModel):
    nome: str
    codigo: str
    possui_rpa: bool = False
    status_ativo: bool = True
    url_portal: Optional[str] = None
    instrucoes_acesso: Optional[str] = None

class OperadoraCreate(OperadoraBase):
    pass

class OperadoraUpdate(BaseModel):
    nome: Optional[str] = None
    codigo: Optional[str] = None
    possui_rpa: Optional[bool] = None
    status_ativo: Optional[bool] = None
    url_portal: Optional[str] = None
    instrucoes_acesso: Optional[str] = None

class OperadoraResponse(OperadoraBase):
    id: str
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True