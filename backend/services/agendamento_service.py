"""
Sistema de Agendamentos Automáticos
Cron jobs e criação automática de processos mensais
Conforme especificação do manual da BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
Data: 29/05/2025
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from celery import Celery
from celery.schedules import crontab

from ..main import get_db, Processo, Cliente, Operadora, StatusProcesso
from .orquestrador_celery import celery_app, orquestrador
from .notificacao_service import notificacao_service

logger = logging.getLogger(__name__)

class AgendamentoService:
    """
    Sistema completo de agendamentos automáticos
    Criação de processos mensais e execução automática de RPAs
    """
    
    def __init__(self):
        self.configurar_agendamentos()
        logger.info("Sistema de agendamentos inicializado")
    
    def configurar_agendamentos(self):
        """Configura agendamentos periódicos no Celery"""
        celery_app.conf.beat_schedule = {
            # Criar processos mensais - Todo dia 1 às 6:00
            'criar-processos-mensais': {
                'task': 'backend.services.agendamento_service.criar_processos_mensais_task',
                'schedule': crontab(hour=6, minute=0, day_of_month=1),
            },
            
            # Executar downloads automáticos - Todos os dias às 2:00
            'executar-downloads-automaticos': {
                'task': 'backend.services.agendamento_service.executar_downloads_automaticos_task',
                'schedule': crontab(hour=2, minute=0),
            },
            
            # Verificar pendências - A cada 4 horas
            'verificar-pendencias': {
                'task': 'backend.services.agendamento_service.verificar_pendencias_task',
                'schedule': crontab(minute=0, hour='*/4'),
            },
            
            # Limpeza de arquivos antigos - Todos os domingos às 3:00
            'limpeza-arquivos': {
                'task': 'backend.services.agendamento_service.limpeza_arquivos_task',
                'schedule': crontab(hour=3, minute=0, day_of_week=0),
            },
            
            # Relatório diário - Todos os dias às 8:00
            'relatorio-diario': {
                'task': 'backend.services.agendamento_service.relatorio_diario_task',
                'schedule': crontab(hour=8, minute=0),
            },
        }
        
        celery_app.conf.timezone = 'America/Sao_Paulo'
    
    def criar_processos_mensais_manual(self, mes_ano: str = None) -> Dict[str, Any]:
        """Cria processos mensais manualmente"""
        try:
            if not mes_ano:
                mes_ano = datetime.now().strftime("%Y-%m")
            
            db = next(get_db())
            
            # Buscar todos os clientes ativos
            clientes = db.query(Cliente).filter(Cliente.status == "ativo").all()
            
            processos_criados = 0
            processos_existentes = 0
            
            for cliente in clientes:
                # Verificar se já existe processo para este mês
                processo_existente = db.query(Processo).filter(
                    Processo.cliente_id == cliente.id,
                    Processo.mes_ano == mes_ano
                ).first()
                
                if not processo_existente:
                    # Criar novo processo
                    novo_processo = Processo(
                        id=f"{cliente.hash_unico}_{mes_ano}",
                        cliente_id=cliente.id,
                        mes_ano=mes_ano,
                        status_processo=StatusProcesso.AGUARDANDO_DOWNLOAD.value,
                        criado_automaticamente=True,
                        data_criacao=datetime.now()
                    )
                    
                    db.add(novo_processo)
                    processos_criados += 1
                else:
                    processos_existentes += 1
            
            db.commit()
            db.close()
            
            resultado = {
                "mes_ano": mes_ano,
                "processos_criados": processos_criados,
                "processos_existentes": processos_existentes,
                "total_clientes": len(clientes),
                "sucesso": True
            }
            
            logger.info(f"Processos mensais criados: {processos_criados} novos, {processos_existentes} existentes")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao criar processos mensais: {e}")
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def executar_downloads_automaticos_manual(self) -> Dict[str, Any]:
        """Executa downloads automáticos manualmente"""
        try:
            db = next(get_db())
            
            # Buscar processos pendentes de download
            processos_pendentes = db.query(Processo).filter(
                Processo.status_processo == StatusProcesso.AGUARDANDO_DOWNLOAD.value
            ).join(Cliente).join(Operadora).all()
            
            downloads_iniciados = 0
            downloads_erro = 0
            
            for processo in processos_pendentes:
                try:
                    cliente = processo.cliente
                    operadora = cliente.operadora
                    
                    # Verificar se operadora possui RPA
                    if not operadora.possui_rpa:
                        logger.warning(f"Operadora {operadora.nome} não possui RPA. Processo {processo.id} ignorado.")
                        continue
                    
                    # Preparar dados de acesso
                    dados_acesso = {
                        "url_portal": operadora.url_portal or "",
                        "usuario": cliente.login_portal or "",
                        "senha": cliente.senha_portal or "",
                        "cpf": cliente.cpf,
                        "filtro": cliente.filtro,
                        "nome_sat": cliente.nome_sat,
                        "dados_sat": cliente.dados_sat,
                        "unidade": cliente.unidade,
                        "servico": cliente.servico
                    }
                    
                    # Executar RPA
                    task_id = orquestrador.executar_download_fatura(
                        processo.id,
                        cliente.id,
                        operadora.codigo,
                        dados_acesso
                    )
                    
                    # Atualizar status do processo
                    processo.status_processo = StatusProcesso.EXECUTANDO.value
                    processo.data_atualizacao = datetime.now()
                    
                    downloads_iniciados += 1
                    logger.info(f"Download iniciado para {cliente.razao_social} - Task: {task_id}")
                    
                except Exception as e:
                    downloads_erro += 1
                    logger.error(f"Erro ao iniciar download para processo {processo.id}: {e}")
            
            db.commit()
            db.close()
            
            resultado = {
                "downloads_iniciados": downloads_iniciados,
                "downloads_erro": downloads_erro,
                "total_processos": len(processos_pendentes),
                "sucesso": True
            }
            
            logger.info(f"Downloads automáticos executados: {downloads_iniciados} iniciados, {downloads_erro} erros")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao executar downloads automáticos: {e}")
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def verificar_pendencias_manual(self) -> Dict[str, Any]:
        """Verifica pendências no sistema"""
        try:
            db = next(get_db())
            
            # Contar pendências por status
            pendencias = {
                "aguardando_download": db.query(Processo).filter(
                    Processo.status_processo == StatusProcesso.AGUARDANDO_DOWNLOAD.value
                ).count(),
                "executando": db.query(Processo).filter(
                    Processo.status_processo == StatusProcesso.EXECUTANDO.value
                ).count(),
                "pendente_aprovacao": db.query(Processo).filter(
                    Processo.status_processo == StatusProcesso.PENDENTE_APROVACAO.value
                ).count(),
                "erro": db.query(Processo).filter(
                    Processo.status_processo == StatusProcesso.ERRO.value
                ).count()
            }
            
            # Verificar processos travados (executando há mais de 2 horas)
            limite_tempo = datetime.now() - timedelta(hours=2)
            processos_travados = db.query(Processo).filter(
                Processo.status_processo == StatusProcesso.EXECUTANDO.value,
                Processo.data_atualizacao < limite_tempo
            ).all()
            
            # Reenviar processos travados para aguardando download
            for processo in processos_travados:
                processo.status_processo = StatusProcesso.AGUARDANDO_DOWNLOAD.value
                processo.data_atualizacao = datetime.now()
                logger.warning(f"Processo travado resetado: {processo.id}")
            
            db.commit()
            db.close()
            
            resultado = {
                "pendencias": pendencias,
                "processos_travados_resetados": len(processos_travados),
                "sucesso": True
            }
            
            logger.info(f"Verificação de pendências concluída: {resultado}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao verificar pendências: {e}")
            return {
                "sucesso": False,
                "erro": str(e)
            }

# ========== TASKS CELERY PARA AGENDAMENTOS ==========

@celery_app.task(name="backend.services.agendamento_service.criar_processos_mensais_task")
def criar_processos_mensais_task():
    """Task para criar processos mensais automaticamente"""
    try:
        agendamento_service = AgendamentoService()
        resultado = agendamento_service.criar_processos_mensais_manual()
        
        logger.info(f"Task criar_processos_mensais executada: {resultado}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na task criar_processos_mensais: {e}")
        return {"sucesso": False, "erro": str(e)}

@celery_app.task(name="backend.services.agendamento_service.executar_downloads_automaticos_task")
def executar_downloads_automaticos_task():
    """Task para executar downloads automáticos"""
    try:
        agendamento_service = AgendamentoService()
        resultado = agendamento_service.executar_downloads_automaticos_manual()
        
        logger.info(f"Task executar_downloads_automaticos executada: {resultado}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na task executar_downloads_automaticos: {e}")
        return {"sucesso": False, "erro": str(e)}

@celery_app.task(name="backend.services.agendamento_service.verificar_pendencias_task")
def verificar_pendencias_task():
    """Task para verificar pendências"""
    try:
        agendamento_service = AgendamentoService()
        resultado = agendamento_service.verificar_pendencias_manual()
        
        logger.info(f"Task verificar_pendencias executada: {resultado}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na task verificar_pendencias: {e}")
        return {"sucesso": False, "erro": str(e)}

@celery_app.task(name="backend.services.agendamento_service.limpeza_arquivos_task")
def limpeza_arquivos_task():
    """Task para limpeza de arquivos antigos"""
    try:
        from ..utils.file_manager import FileManager
        
        file_manager = FileManager()
        file_manager.limpar_downloads_antigos(dias=30)
        
        logger.info("Limpeza de arquivos antigos executada")
        return {"sucesso": True, "arquivos_removidos": "executado"}
        
    except Exception as e:
        logger.error(f"Erro na task limpeza_arquivos: {e}")
        return {"sucesso": False, "erro": str(e)}

@celery_app.task(name="backend.services.agendamento_service.relatorio_diario_task")
def relatorio_diario_task():
    """Task para relatório diário"""
    try:
        db = next(get_db())
        
        # Estatísticas do dia
        hoje = datetime.now().date()
        processos_criados_hoje = db.query(Processo).filter(
            Processo.data_criacao >= hoje
        ).count()
        
        faturas_aprovadas_hoje = db.query(Processo).filter(
            Processo.status_processo == StatusProcesso.APROVADA.value,
            Processo.data_aprovacao >= hoje
        ).count()
        
        db.close()
        
        # Enviar relatório por notificação
        mensagem_relatorio = f"""
📊 RELATÓRIO DIÁRIO RPA - {hoje.strftime('%d/%m/%Y')}

📋 Processos criados hoje: {processos_criados_hoje}
✅ Faturas aprovadas hoje: {faturas_aprovadas_hoje}

Sistema Orquestrador RPA - BGTELECOM
        """
        
        # Simular envio de relatório (em produção enviaria via notificação)
        logger.info(f"Relatório diário gerado: {mensagem_relatorio}")
        
        return {
            "sucesso": True,
            "processos_criados": processos_criados_hoje,
            "faturas_aprovadas": faturas_aprovadas_hoje
        }
        
    except Exception as e:
        logger.error(f"Erro na task relatorio_diario: {e}")
        return {"sucesso": False, "erro": str(e)}

# Instância global do serviço
agendamento_service = AgendamentoService()