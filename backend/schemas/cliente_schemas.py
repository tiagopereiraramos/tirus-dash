"""
Schemas Pydantic para Cliente
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClienteBase(BaseModel):
    razao_social: str
    nome_sat: str
    cnpj: str
    operadora_id: str
    filtro: Optional[str] = None
    servico: Optional[str] = None
    dados_sat: Optional[str] = None
    unidade: str
    site_emissao: Optional[str] = None
    login_portal: Optional[str] = None
    senha_portal: Optional[str] = None
    cpf: Optional[str] = None
    status_ativo: bool = True

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    razao_social: Optional[str] = None
    nome_sat: Optional[str] = None
    cnpj: Optional[str] = None
    operadora_id: Optional[str] = None
    filtro: Optional[str] = None
    servico: Optional[str] = None
    dados_sat: Optional[str] = None
    unidade: Optional[str] = None
    site_emissao: Optional[str] = None
    login_portal: Optional[str] = None
    senha_portal: Optional[str] = None
    cpf: Optional[str] = None
    status_ativo: Optional[bool] = None

class ClienteResponse(ClienteBase):
    id: str
    hash_unico: str
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True