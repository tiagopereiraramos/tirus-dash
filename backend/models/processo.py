"""
Modelo de Processo
Conforme especificação do manual da BGTELECOM
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from config.database import Base

class StatusProcesso(Enum):
    """Status possíveis para um processo"""
    AGUARDANDO_DOWNLOAD = "aguardando_download"
    EXECUTANDO = "executando"
    FATURA_BAIXADA = "fatura_baixada"
    PENDENTE_APROVACAO = "pendente_aprovacao"
    AGUARDANDO_APROVACAO = "aguardando_aprovacao"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    ENVIADA_SAT = "enviada_sat"
    ERRO = "erro"
    CONCLUIDA = "concluida"

class StatusExecucao(Enum):
    """Status possíveis para uma execução"""
    PENDENTE = "pendente"
    EXECUTANDO = "executando"
    SUCESSO = "sucesso"
    ERRO = "erro"
    CANCELADA = "cancelada"

class TipoExecucao(Enum):
    """Tipos de execução"""
    DOWNLOAD = "download"
    UPLOAD_SAT = "upload_sat"
    MANUAL = "manual"

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
    execucoes = relationship("Execucao", back_populates="processo")
    
    def __repr__(self):
        return f"<Processo(id='{self.id}', cliente_id='{self.cliente_id}', status='{self.status_processo}')>"

class Execucao(Base):
    """
    Modelo de Execução - representa cada tentativa de execução de um processo
    """
    __tablename__ = "execucoes"
    
    # Campos principais
    id = Column(String, primary_key=True)
    processo_id = Column(String, ForeignKey("processos.id"), nullable=False)
    session_id = Column(String, nullable=False)
    
    # Status e controle
    status_execucao = Column(String, nullable=False, default="pendente")
    operadora_codigo = Column(String, nullable=False)
    
    # Timestamps
    data_inicio = Column(DateTime, default=datetime.now)
    data_fim = Column(DateTime)
    data_criacao = Column(DateTime, default=datetime.now)
    
    # Logs e detalhes
    logs_detalhes = Column(Text)
    mensagem_erro = Column(Text)
    
    # Relacionamentos
    processo = relationship("Processo", back_populates="execucoes")
    
    def __repr__(self):
        return f"<Execucao(id='{self.id}', processo_id='{self.processo_id}', status='{self.status_execucao}')>"