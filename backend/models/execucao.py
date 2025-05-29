"""
Modelo de Execução
Conforme especificação do manual da BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
Data: 29/05/2025
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..config.database import Base

class Execucao(Base):
    """
    Modelo de Execução para rastreamento detalhado de operações RPA
    Representa cada execução individual de RPA
    """
    __tablename__ = "execucoes"
    
    # Campos principais
    id = Column(String, primary_key=True)
    processo_id = Column(String, ForeignKey("processos.id"), nullable=False)
    cliente_id = Column(String, ForeignKey("clientes.id"), nullable=False)
    operadora_codigo = Column(String, nullable=False)
    
    # Tipo e status da execução
    tipo_execucao = Column(String, nullable=False)  # download_fatura, upload_sat
    status_execucao = Column(String, nullable=False, default="iniciado")
    
    # Controle de tentativas
    tentativa_numero = Column(Integer, default=1)
    max_tentativas = Column(Integer, default=3)
    
    # Timestamps detalhados
    data_inicio = Column(DateTime, default=datetime.now)
    data_fim = Column(DateTime)
    tempo_execucao_segundos = Column(Integer)
    
    # Resultados
    sucesso = Column(Boolean, default=False)
    arquivo_baixado = Column(String)
    url_s3 = Column(String)
    
    # Logs e erros
    logs_execucao = Column(Text)
    mensagem_erro = Column(Text)
    stack_trace = Column(Text)
    
    # Dados de debug
    xpath_utilizado = Column(Text)
    screenshot_erro = Column(String)
    html_pagina = Column(Text)
    
    # Task ID do Celery
    celery_task_id = Column(String)
    
    # Relacionamentos
    processo = relationship("Processo", back_populates="execucoes")
    cliente = relationship("Cliente", back_populates="execucoes")
    
    def __repr__(self):
        return f"<Execucao(id='{self.id}', tipo='{self.tipo_execucao}', status='{self.status_execucao}')>"
    
    def adicionar_log(self, mensagem: str):
        """Adiciona uma linha de log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nova_linha = f"[{timestamp}] {mensagem}"
        
        if self.logs_execucao:
            self.logs_execucao += f"\n{nova_linha}"
        else:
            self.logs_execucao = nova_linha
    
    def marcar_como_concluida(self, sucesso: bool, mensagem: str = None):
        """Marca execução como concluída"""
        self.data_fim = datetime.now()
        self.sucesso = sucesso
        
        if self.data_inicio:
            delta = self.data_fim - self.data_inicio
            self.tempo_execucao_segundos = int(delta.total_seconds())
        
        self.status_execucao = "concluido" if sucesso else "erro"
        
        if mensagem:
            if sucesso:
                self.adicionar_log(f"Sucesso: {mensagem}")
            else:
                self.mensagem_erro = mensagem
                self.adicionar_log(f"Erro: {mensagem}")
    
    def incrementar_tentativa(self):
        """Incrementa número da tentativa"""
        self.tentativa_numero += 1
        self.adicionar_log(f"Tentativa {self.tentativa_numero} iniciada")
    
    def atingiu_max_tentativas(self) -> bool:
        """Verifica se atingiu máximo de tentativas"""
        return self.tentativa_numero >= self.max_tentativas