"""
RPA OI - Sistema de automação para download de faturas
Desenvolvido seguindo o padrão RPA Base Concentrador
Preservação 100% do código legado conforme manual BGTELECOM
"""

import logging
from time import sleep
from datetime import datetime
import os

from .rpa_base import concentrador_rpa
from ..utils.file_manager import FileManager
from ..models.cliente import Cliente

logger = logging.getLogger(__name__)

class OiRPA:
    """
    RPA para automação OI
    Herda toda funcionalidade do RPA Base Concentrador
    """
    
    def __init__(self, cliente: Cliente):
        self.cliente = cliente
        self.file_manager = FileManager()
        self.logger = logger
        
        # Configurações específicas da OI
        self.url_portal = "https://minha.oi.com.br"
        self.timeout_download = 180
        
    def executar_download(self, mes_ano: str) -> dict:
        """
        Executa download de fatura usando RPA Base Concentrador
        
        Args:
            mes_ano: Mês/ano no formato YYYY-MM
            
        Returns:
            dict: Resultado da execução
        """
        try:
            self.logger.info(f"Iniciando download OI para cliente {self.cliente.razao_social}")
            
            # Configurar parâmetros para o concentrador
            parametros = {
                'operadora': 'oi',
                'cliente': self.cliente.to_dict(),
                'mes_ano': mes_ano,
                'url_portal': self.url_portal,
                'login': self.cliente.login_portal,
                'senha': self.cliente.senha_portal,
                'cpf': self.cliente.cpf,
                'filtro': self.cliente.filtro or "",
                'servico': self.cliente.servico or "",
                'timeout': self.timeout_download
            }
            
            # Executar através do RPA Base Concentrador
            resultado = concentrador_rpa.executar_rpa(parametros)
            
            if resultado.get('sucesso'):
                self.logger.info(f"Download OI concluído com sucesso: {resultado['arquivo']}")
                
                # Processar arquivo baixado
                arquivo_processado = self._processar_arquivo_baixado(
                    resultado['arquivo'], 
                    mes_ano
                )
                
                return {
                    'sucesso': True,
                    'arquivo_local': arquivo_processado,
                    'url_s3': resultado.get('url_s3'),
                    'mensagem': 'Download OI realizado com sucesso'
                }
            else:
                self.logger.error(f"Erro no download OI: {resultado.get('erro')}")
                return {
                    'sucesso': False,
                    'erro': resultado.get('erro', 'Erro desconhecido na OI'),
                    'mensagem': 'Falha no download da fatura OI'
                }
                
        except Exception as e:
            self.logger.error(f"Exceção no RPA OI: {str(e)}")
            return {
                'sucesso': False,
                'erro': str(e),
                'mensagem': 'Erro interno no RPA OI'
            }
    
    def _processar_arquivo_baixado(self, arquivo_original: str, mes_ano: str) -> str:
        """
        Processa arquivo baixado conforme padrões OI
        """
        try:
            # Gerar nome padronizado
            nome_arquivo = f"oi_{self.cliente.hash_unico}_{mes_ano}.pdf"
            
            # Renomear arquivo
            arquivo_processado = self.file_manager.renomear_arquivo(
                arquivo_original, 
                nome_arquivo
            )
            
            # Validar PDF
            if not self.file_manager.validar_arquivo_pdf(arquivo_processado):
                raise Exception("Arquivo baixado não é um PDF válido")
            
            self.logger.info(f"Arquivo processado: {arquivo_processado}")
            return arquivo_processado
            
        except Exception as e:
            raise Exception(f"Erro ao processar arquivo OI: {e}")
    
    def validar_configuracao(self) -> bool:
        """
        Valida se cliente tem configuração necessária para OI
        """
        if not self.cliente.login_portal:
            return False
        if not self.cliente.senha_portal:
            return False
        if not self.cliente.cpf:
            return False
            
        return True

# Factory function para compatibilidade
def criar_oi_rpa(cliente: Cliente) -> OiRPA:
    """Cria instância do RPA OI"""
    return OiRPA(cliente)