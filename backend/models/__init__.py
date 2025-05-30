"""
Inicialização dos modelos SQLAlchemy
Importa todos os modelos para resolver dependências circulares
"""

from config.database import Base

# Importar todos os modelos para resolver relacionamentos
from .operadora import Operadora
from .usuario import Usuario  
from .cliente import Cliente
from .processo import Processo
from .execucao import Execucao
from .fatura import Fatura

# Exportar modelos
__all__ = [
    "Base",
    "Operadora", 
    "Usuario",
    "Cliente",
    "Processo", 
    "Execucao",
    "Fatura"
]