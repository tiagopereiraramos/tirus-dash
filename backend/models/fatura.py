"""
Modelo Fatura
Sistema RPA BGTELECOM
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from config.database import Base


class Fatura(Base):
    """Modelo para faturas processadas pelo sistema"""
    
    __tablename__ = "faturas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    processo_id = Column(UUID(as_uuid=True), ForeignKey("processos.id"), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    caminho_s3 = Column(String(500))
    url_download = Column(String(500))
    data_vencimento = Column(DateTime)
    valor_total = Column(Numeric(10, 2))
    mes_referencia = Column(String(7))  # YYYY-MM
    status_processamento = Column(String(50), default="pendente")
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    observacoes = Column(Text)
    
    # Relacionamento
    processo = relationship("Processo", back_populates="faturas")
    
    def __repr__(self):
        return f"<Fatura(nome_arquivo='{self.nome_arquivo}', processo_id='{self.processo_id}')>"