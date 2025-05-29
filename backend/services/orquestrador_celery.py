"""
Sistema de Orquestração Celery + Redis
Conforme especificação do manual da BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
Data: 29/05/2025
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from celery import Celery
from celery.result import AsyncResult

from ..rpa.rpa_base import (
    concentrador_rpa, 
    TipoOperacao, 
    ParametrosEntradaPadrao,
    StatusExecucao
)

# Configuração do Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "orquestrador_rpa",
    broker=redis_url,
    backend=redis_url,
    include=["backend.services.orquestrador_celery"]
)

# Configurações do Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_compression="gzip",
    result_compression="gzip",
)

logger = logging.getLogger(__name__)

class OrquestradorRPA:
    """
    Orquestrador principal de RPAs usando Celery + Redis
    Conforme especificação do manual da BGTELECOM
    """
    
    def __init__(self):
        self.celery = celery_app
        logger.info("Orquestrador RPA inicializado com Celery + Redis")
    
    def executar_download_fatura(
        self, 
        processo_id: str, 
        cliente_id: str, 
        operadora_codigo: str,
        dados_acesso: Dict[str, Any]
    ) -> str:
        """
        Executa download de fatura de forma assíncrona
        
        Args:
            processo_id: ID do processo
            cliente_id: ID do cliente
            operadora_codigo: Código da operadora
            dados_acesso: Dados de acesso (URL, login, senha, etc.)
            
        Returns:
            str: Task ID da execução
        """
        parametros = ParametrosEntradaPadrao(
            id_processo=processo_id,
            id_cliente=cliente_id,
            operadora_codigo=operadora_codigo,
            url_portal=dados_acesso.get("url_portal", ""),
            usuario=dados_acesso.get("usuario", ""),
            senha=dados_acesso.get("senha", ""),
            cpf=dados_acesso.get("cpf"),
            filtro=dados_acesso.get("filtro"),
            nome_sat=dados_acesso.get("nome_sat", ""),
            dados_sat=dados_acesso.get("dados_sat", ""),
            unidade=dados_acesso.get("unidade", ""),
            servico=dados_acesso.get("servico", "")
        )
        
        task = executar_download_rpa_task.delay(parametros.__dict__)
        logger.info(f"Download iniciado - Task ID: {task.id}, Processo: {processo_id}")
        return task.id
    
    def executar_upload_sat(
        self,
        processo_id: str,
        cliente_id: str,
        dados_cliente: Dict[str, Any]
    ) -> str:
        """
        Executa upload para SAT de forma assíncrona
        
        Args:
            processo_id: ID do processo
            cliente_id: ID do cliente  
            dados_cliente: Dados do cliente para SAT
            
        Returns:
            str: Task ID da execução
        """
        parametros = ParametrosEntradaPadrao(
            id_processo=processo_id,
            id_cliente=cliente_id,
            operadora_codigo="SAT",
            url_portal="",  # SAT tem URL própria
            usuario="",  # SAT tem credenciais próprias
            senha="",
            nome_sat=dados_cliente.get("nome_sat", ""),
            dados_sat=dados_cliente.get("dados_sat", ""),
            unidade=dados_cliente.get("unidade", ""),
            servico=dados_cliente.get("servico", "")
        )
        
        task = executar_upload_sat_task.delay(parametros.__dict__)
        logger.info(f"Upload SAT iniciado - Task ID: {task.id}, Processo: {processo_id}")
        return task.id
    
    def obter_status_execucao(self, task_id: str) -> Dict[str, Any]:
        """
        Obtém status de uma execução
        
        Args:
            task_id: ID da task
            
        Returns:
            Dict com informações do status
        """
        try:
            result = AsyncResult(task_id, app=self.celery)
            
            status_info = {
                "task_id": task_id,
                "status": result.status,
                "current": getattr(result, "current", 0),
                "total": getattr(result, "total", 1),
                "resultado": None,
                "erro": None
            }
            
            if result.ready():
                if result.successful():
                    status_info["resultado"] = result.result
                else:
                    status_info["erro"] = str(result.info)
            
            return status_info
            
        except Exception as e:
            logger.error(f"Erro ao obter status da task {task_id}: {e}")
            return {
                "task_id": task_id,
                "status": "ERRO",
                "erro": str(e)
            }
    
    def cancelar_execucao(self, task_id: str) -> bool:
        """
        Cancela uma execução em andamento
        
        Args:
            task_id: ID da task
            
        Returns:
            bool: True se cancelada com sucesso
        """
        try:
            self.celery.control.revoke(task_id, terminate=True)
            logger.info(f"Execução cancelada - Task ID: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao cancelar task {task_id}: {e}")
            return False
    
    def listar_execucoes_ativas(self) -> List[Dict[str, Any]]:
        """
        Lista todas as execuções ativas
        
        Returns:
            List de execuções ativas
        """
        try:
            inspect = self.celery.control.inspect()
            active_tasks = inspect.active()
            
            execucoes = []
            if active_tasks:
                for worker, tasks in active_tasks.items():
                    for task in tasks:
                        execucoes.append({
                            "task_id": task["id"],
                            "worker": worker,
                            "nome": task["name"],
                            "args": task.get("args", []),
                            "kwargs": task.get("kwargs", {}),
                            "timestamp": task.get("time_start")
                        })
            
            return execucoes
            
        except Exception as e:
            logger.error(f"Erro ao listar execuções ativas: {e}")
            return []

# ========== TASKS CELERY ==========

@celery_app.task(bind=True, name="executar_download_rpa")
def executar_download_rpa_task(self, parametros_dict: Dict[str, Any]):
    """
    Task Celery para executar download de fatura
    """
    try:
        # Atualiza progresso
        self.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "Iniciando download..."}
        )
        
        # Reconstrói parâmetros
        parametros = ParametrosEntradaPadrao(**parametros_dict)
        
        # Atualiza progresso
        self.update_state(
            state="PROGRESS", 
            meta={"current": 20, "total": 100, "status": "Conectando com operadora..."}
        )
        
        # Executa através do concentrador
        resultado = concentrador_rpa.executar_operacao(
            TipoOperacao.DOWNLOAD_FATURA,
            parametros
        )
        
        # Atualiza progresso
        self.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Finalizando..."}
        )
        
        # Retorna resultado
        return {
            "sucesso": resultado.sucesso,
            "status": resultado.status.value,
            "mensagem": resultado.mensagem,
            "arquivo_baixado": resultado.arquivo_baixado,
            "url_s3": resultado.url_s3,
            "dados_extraidos": resultado.dados_extraidos,
            "tempo_execucao": resultado.tempo_execucao_segundos,
            "timestamp_inicio": resultado.timestamp_inicio.isoformat() if resultado.timestamp_inicio else None,
            "timestamp_fim": resultado.timestamp_fim.isoformat() if resultado.timestamp_fim else None,
            "logs_execucao": resultado.logs_execucao
        }
        
    except Exception as e:
        logger.error(f"Erro na task de download: {e}")
        self.update_state(
            state="FAILURE",
            meta={"erro": str(e), "status": "Erro na execução"}
        )
        raise

@celery_app.task(bind=True, name="executar_upload_sat")
def executar_upload_sat_task(self, parametros_dict: Dict[str, Any]):
    """
    Task Celery para executar upload para SAT
    """
    try:
        # Atualiza progresso
        self.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "Iniciando upload SAT..."}
        )
        
        # Reconstrói parâmetros
        parametros = ParametrosEntradaPadrao(**parametros_dict)
        
        # Atualiza progresso
        self.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Conectando com SAT..."}
        )
        
        # Executa através do concentrador
        resultado = concentrador_rpa.executar_operacao(
            TipoOperacao.UPLOAD_SAT,
            parametros
        )
        
        # Atualiza progresso
        self.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Finalizando upload..."}
        )
        
        # Retorna resultado
        return {
            "sucesso": resultado.sucesso,
            "status": resultado.status.value,
            "mensagem": resultado.mensagem,
            "tempo_execucao": resultado.tempo_execucao_segundos,
            "timestamp_inicio": resultado.timestamp_inicio.isoformat() if resultado.timestamp_inicio else None,
            "timestamp_fim": resultado.timestamp_fim.isoformat() if resultado.timestamp_fim else None,
            "logs_execucao": resultado.logs_execucao
        }
        
    except Exception as e:
        logger.error(f"Erro na task de upload SAT: {e}")
        self.update_state(
            state="FAILURE",
            meta={"erro": str(e), "status": "Erro no upload SAT"}
        )
        raise

@celery_app.task(name="processar_agendamento")
def processar_agendamento_task(tipo_agendamento: str, parametros: Dict[str, Any]):
    """
    Task para processar agendamentos automáticos
    """
    try:
        logger.info(f"Processando agendamento: {tipo_agendamento}")
        
        if tipo_agendamento == "CRIAR_PROCESSOS_MENSAIS":
            return _criar_processos_mensais(parametros)
        elif tipo_agendamento == "EXECUTAR_DOWNLOADS":
            return _executar_downloads_agendados(parametros)
        elif tipo_agendamento == "ENVIAR_RELATORIOS":
            return _enviar_relatorios(parametros)
        else:
            raise ValueError(f"Tipo de agendamento não suportado: {tipo_agendamento}")
            
    except Exception as e:
        logger.error(f"Erro no agendamento {tipo_agendamento}: {e}")
        raise

def _criar_processos_mensais(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Cria processos mensais automaticamente"""
    # Implementar lógica para criar processos mensais
    logger.info("Criando processos mensais automaticamente")
    return {"processos_criados": 0, "status": "executado"}

def _executar_downloads_agendados(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Executa downloads agendados"""
    # Implementar lógica para executar downloads agendados
    logger.info("Executando downloads agendados")
    return {"downloads_executados": 0, "status": "executado"}

def _enviar_relatorios(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Envia relatórios agendados"""
    # Implementar lógica para enviar relatórios
    logger.info("Enviando relatórios agendados")
    return {"relatorios_enviados": 0, "status": "executado"}

# Instância global do orquestrador
orquestrador = OrquestradorRPA()