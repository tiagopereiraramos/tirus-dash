"""
Sistema de logging para RPAs
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class RPALogger:
    """Logger específico para RPAs"""
    
    def __init__(self, operadora: str):
        self.operadora = operadora
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configura logger específico para a operadora"""
        # Criar diretório de logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Nome do arquivo de log
        log_file = log_dir / f"rpa_{self.operadora.lower()}.log"
        
        # Configurar logger
        logger = logging.getLogger(f"RPA_{self.operadora}")
        logger.setLevel(logging.INFO)
        
        # Evitar duplicação de handlers
        if not logger.handlers:
            # Handler para arquivo
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Handler para console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formato das mensagens
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def info(self, mensagem: str):
        """Log de informação"""
        self.logger.info(f"[{self.operadora}] {mensagem}")
    
    def error(self, mensagem: str):
        """Log de erro"""
        self.logger.error(f"[{self.operadora}] {mensagem}")
    
    def warning(self, mensagem: str):
        """Log de aviso"""
        self.logger.warning(f"[{self.operadora}] {mensagem}")
    
    def debug(self, mensagem: str):
        """Log de debug"""
        self.logger.debug(f"[{self.operadora}] {mensagem}")