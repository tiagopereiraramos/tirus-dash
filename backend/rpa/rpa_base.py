"""
RPA Base Concentrador - Sistema de Orquestração RPA BEG Telecomunicações
Padrão imutável de entrada/saída conforme especificação do manual
Desenvolvido por: Tiago Pereira Ramos
Data: 29/05/2025
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
from datetime import datetime

class TipoOperacao(Enum):
    """Tipos de operação suportados pelo RPA Base"""
    DOWNLOAD_FATURA = "download_fatura"
    UPLOAD_SAT = "upload_sat"

class StatusExecucao(Enum):
    """Status de execução padronizado"""
    INICIADO = "iniciado"
    EM_PROGRESSO = "em_progresso"
    SUCESSO = "sucesso"
    ERRO = "erro"
    TIMEOUT = "timeout"

@dataclass(frozen=True)
class ParametrosEntradaPadrao:
    """
    Estrutura imutável de entrada padronizada para todos os RPAs
    Conforme especificação do manual da BGTELECOM
    """
    id_processo: str
    id_cliente: str
    operadora_codigo: str
    url_portal: str
    usuario: str
    senha: str
    cpf: Optional[str] = None
    filtro: Optional[str] = None
    nome_sat: str = ""
    dados_sat: str = ""
    unidade: str = ""
    servico: str = ""

@dataclass
class ResultadoSaidaPadrao:
    """
    Estrutura padronizada de saída para todos os RPAs
    Conforme especificação do manual da BGTELECOM
    """
    sucesso: bool
    status: StatusExecucao
    mensagem: str
    arquivo_baixado: Optional[str] = None
    url_s3: Optional[str] = None
    dados_extraidos: Dict[str, Any] = field(default_factory=dict)
    tempo_execucao_segundos: float = 0.0
    tentativa_numero: int = 1
    timestamp_inicio: Optional[datetime] = None
    timestamp_fim: Optional[datetime] = None
    logs_execucao: List[str] = field(default_factory=list)
    screenshots_debug: List[str] = field(default_factory=list)
    dados_especificos: Dict[str, Any] = field(default_factory=dict)

class RPABase(ABC):
    """
    Classe base abstrata para todos os RPAs
    Padrão imutável conforme manual da BGTELECOM
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"RPA.{self.__class__.__name__}")
    
    @abstractmethod
    def executar_download(self, parametros: ParametrosEntradaPadrao) -> ResultadoSaidaPadrao:
        """
        Executa download de fatura da operadora
        
        Args:
            parametros: Parâmetros padronizados de entrada
            
        Returns:
            ResultadoSaidaPadrao: Resultado da execução
        """
        pass
    
    @abstractmethod
    def executar_upload_sat(self, parametros: ParametrosEntradaPadrao) -> ResultadoSaidaPadrao:
        """
        Executa upload de fatura para o SAT
        
        Args:
            parametros: Parâmetros padronizados de entrada
            
        Returns:
            ResultadoSaidaPadrao: Resultado da execução
        """
        pass
    
    def _log_operacao(self, operacao: str, parametros: ParametrosEntradaPadrao, resultado: ResultadoSaidaPadrao):
        """
        Registra log padronizado da operação
        """
        self.logger.info(f"""
        === LOG OPERAÇÃO RPA ===
        Operação: {operacao}
        Cliente: {parametros.id_cliente}
        Processo: {parametros.id_processo}
        Operadora: {parametros.operadora_codigo}
        Status: {resultado.status.value}
        Sucesso: {resultado.sucesso}
        Tempo: {resultado.tempo_execucao_segundos}s
        Mensagem: {resultado.mensagem}
        =======================
        """)

class ConcentradorRPA:
    """
    Concentrador central de RPAs seguindo padrão do manual da BGTELECOM
    Responsável por direcionar operações baseadas no filtro/operadora
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ConcentradorRPA")
        self.rpas_registrados: Dict[str, RPABase] = {}
        self._registrar_rpas_disponiveis()
    
    def _registrar_rpas_disponiveis(self) -> None:
        """
        Registra todos os RPAs disponíveis no sistema
        Preservando 100% do código legado conforme manual
        """
        try:
            # Import dos RPAs legados adaptados
            from .embratel_rpa import EmbratelRPA
            from .digitalnet_rpa import DigitalnetRPA
            from .azuton_rpa import AzutonRPA
            from .vivo_rpa import VivoRPA
            from .oi_rpa import OiRPA
            from .sat_rpa import SatRPA
            
            self.rpas_registrados = {
                "EMB": EmbratelRPA(),
                "EMBRATEL": EmbratelRPA(),
                "DIG": DigitalnetRPA(),
                "DIGITALNET": DigitalnetRPA(),
                "AZU": AzutonRPA(),
                "AZUTON": AzutonRPA(),
                "VIV": VivoRPA(),
                "VIVO": VivoRPA(),
                "OI": OiRPA(),
                "SAT": SatRPA(),
            }
            
            self.logger.info(f"RPAs registrados: {list(self.rpas_registrados.keys())}")
            
        except ImportError as e:
            self.logger.warning(f"Alguns RPAs não puderam ser importados: {e}")
    
    def executar_operacao(self, operacao: TipoOperacao, parametros: ParametrosEntradaPadrao) -> ResultadoSaidaPadrao:
        """
        Executa operação RPA baseada no tipo e operadora
        
        Args:
            operacao: Tipo de operação a ser executada
            parametros: Parâmetros padronizados de entrada
            
        Returns:
            ResultadoSaidaPadrao: Resultado da execução
        """
        timestamp_inicio = datetime.now()
        
        try:
            # Determina qual RPA usar baseado na operação
            codigo_rpa = "SAT" if operacao == TipoOperacao.UPLOAD_SAT else parametros.operadora_codigo.upper()
            
            if codigo_rpa not in self.rpas_registrados:
                return ResultadoSaidaPadrao(
                    sucesso=False,
                    status=StatusExecucao.ERRO,
                    mensagem=f"RPA não encontrado para código: {codigo_rpa}",
                    timestamp_inicio=timestamp_inicio,
                    timestamp_fim=datetime.now()
                )
            
            rpa = self.rpas_registrados[codigo_rpa]
            
            # Executa a operação baseada no tipo
            if operacao == TipoOperacao.DOWNLOAD_FATURA:
                resultado = rpa.executar_download(parametros)
            elif operacao == TipoOperacao.UPLOAD_SAT:
                resultado = rpa.executar_upload_sat(parametros)
            else:
                return ResultadoSaidaPadrao(
                    sucesso=False,
                    status=StatusExecucao.ERRO,
                    mensagem=f"Operação não suportada: {operacao.value}",
                    timestamp_inicio=timestamp_inicio,
                    timestamp_fim=datetime.now()
                )
            
            # Garante timestamps
            resultado.timestamp_inicio = resultado.timestamp_inicio or timestamp_inicio
            resultado.timestamp_fim = resultado.timestamp_fim or datetime.now()
            
            # Log da operação
            rpa._log_operacao(operacao.value, parametros, resultado)
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na execução RPA: {e}")
            return ResultadoSaidaPadrao(
                sucesso=False,
                status=StatusExecucao.ERRO,
                mensagem=f"Erro interno: {str(e)}",
                timestamp_inicio=timestamp_inicio,
                timestamp_fim=datetime.now()
            )
    
    def listar_rpas_disponiveis(self) -> List[str]:
        """
        Lista todos os RPAs registrados no concentrador
        
        Returns:
            List[str]: Lista de códigos de RPAs disponíveis
        """
        return list(self.rpas_registrados.keys())
    
    def verificar_rpa_disponivel(self, codigo_operadora: str) -> bool:
        """
        Verifica se existe RPA disponível para a operadora
        
        Args:
            codigo_operadora: Código da operadora
            
        Returns:
            bool: True se RPA disponível, False caso contrário
        """
        return codigo_operadora.upper() in self.rpas_registrados

# Instância global do concentrador
concentrador_rpa = ConcentradorRPA()