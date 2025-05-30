"""
Modelo de Processo
Conforme especificação do manual da BGTELECOM
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

from config.database import Base

class Processo(Base):
    """
    Modelo de Processo para gestão de faturas
    Representa o processo completo de download, aprovação e upload
    """
    __tablename__ = "processos"
    
    # Campos principais
    id = Column(String, primary_key=True)
    cliente_id = Column(String, ForeignKey("clientes.id"), nullable=False)
    mes_ano = Column(String, nullable=False)  # Formato: YYYY-MM
    
    # Status e controle
    status_processo = Column(String, nullable=False, default="aguardando_download")
    criado_automaticamente = Column(Boolean, default=False)
    upload_manual = Column(Boolean, default=False)
    
    # URLs e arquivos
    url_fatura = Column(String)
    caminho_s3_fatura = Column(String)
    nome_arquivo_original = Column(String)
    
    # Dados da fatura
    data_vencimento = Column(DateTime)
    valor_fatura = Column(Numeric(10, 2))
    
    # Aprovação
    aprovado_por_usuario_id = Column(String, ForeignKey("usuarios.id"))
    data_aprovacao = Column(DateTime)
    
    # Timestamps
    data_criacao = Column(DateTime, default=datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.now)
    
    # Observações e logs
    observacoes = Column(Text)
    logs_execucao = Column(Text)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="processos")
    aprovado_por = relationship("Usuario", foreign_keys=[aprovado_por_usuario_id])
    faturas = relationship("Fatura", back_populates="processo")
    
    def __repr__(self):
        return f"<Processo(id='{self.id}', cliente_id='{self.cliente_id}', status='{self.status_processo}')>"