"""
Schemas Pydantic para Usuário
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    nome_completo: str
    email: EmailStr
    telefone: Optional[str] = None
    perfil_usuario: str  # ADMINISTRADOR, APROVADOR, OPERADOR
    status_ativo: bool = True

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nome_completo: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    perfil_usuario: Optional[str] = None
    status_ativo: Optional[bool] = None
    configuracoes_notificacao: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    id: str
    data_criacao: datetime
    data_atualizacao: datetime
    configuracoes_notificacao: Optional[str] = None

    class Config:
        from_attributes = True