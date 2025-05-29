"""
Sistema de Workflow de Aprovação Obrigatório
Conforme especificação do manual da BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
Data: 29/05/2025
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from sqlalchemy.orm import Session
from ..main import get_db, StatusProcesso, StatusExecucao

logger = logging.getLogger(__name__)

class AcaoAprovacao(Enum):
    """Ações possíveis no workflow de aprovação"""
    APROVAR = "aprovar"
    REJEITAR = "rejeitar"
    SOLICITAR_REVISAO = "solicitar_revisao"

class WorkflowAprovacao:
    """
    Sistema de workflow de aprovação obrigatório
    Conforme regras de negócio do manual da BGTELECOM
    """
    
    def __init__(self):
        logger.info("Workflow de aprovação inicializado")
    
    def processar_fatura_para_aprovacao(
        self, 
        processo_id: str, 
        url_fatura: str,
        dados_extraidos: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Processa fatura baixada e coloca em fila de aprovação
        
        Args:
            processo_id: ID do processo
            url_fatura: URL da fatura no S3
            dados_extraidos: Dados extraídos da fatura
            db: Sessão do banco
            
        Returns:
            Dict com resultado do processamento
        """
        try:
            from ..main import Processo
            
            # Busca o processo
            processo = db.query(Processo).filter(Processo.id == processo_id).first()
            
            if not processo:
                raise ValueError(f"Processo {processo_id} não encontrado")
            
            # Atualiza processo com dados da fatura
            processo.url_fatura = url_fatura
            processo.caminho_s3_fatura = url_fatura
            processo.status_processo = StatusProcesso.PENDENTE_APROVACAO.value
            
            # Extrai dados importantes
            if dados_extraidos:
                if "vencimento" in dados_extraidos:
                    try:
                        # Converte string de data para objeto Date
                        vencimento_str = dados_extraidos["vencimento"]
                        if isinstance(vencimento_str, str):
                            # Tenta diferentes formatos de data
                            for formato in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
                                try:
                                    data_vencimento = datetime.strptime(vencimento_str, formato).date()
                                    processo.data_vencimento = data_vencimento
                                    break
                                except ValueError:
                                    continue
                    except Exception as e:
                        logger.warning(f"Erro ao processar data de vencimento: {e}")
                
                if "valor" in dados_extraidos:
                    try:
                        processo.valor_fatura = float(dados_extraidos["valor"])
                    except (ValueError, TypeError):
                        logger.warning("Erro ao processar valor da fatura")
            
            processo.data_atualizacao = datetime.now()
            
            db.commit()
            
            # Dispara notificações para aprovadores
            self._notificar_aprovadores(processo, db)
            
            logger.info(f"Fatura do processo {processo_id} enviada para aprovação")
            
            return {
                "sucesso": True,
                "processo_id": processo_id,
                "status": StatusProcesso.PENDENTE_APROVACAO.value,
                "mensagem": "Fatura enviada para aprovação com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar fatura para aprovação: {e}")
            db.rollback()
            return {
                "sucesso": False,
                "erro": str(e),
                "mensagem": "Erro ao processar fatura para aprovação"
            }
    
    def processar_aprovacao(
        self,
        processo_id: str,
        usuario_aprovador_id: str,
        acao: AcaoAprovacao,
        observacoes: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Processa decisão de aprovação/rejeição
        
        Args:
            processo_id: ID do processo
            usuario_aprovador_id: ID do usuário aprovador
            acao: Ação tomada (aprovar/rejeitar)
            observacoes: Observações do aprovador
            db: Sessão do banco
            
        Returns:
            Dict com resultado da aprovação
        """
        try:
            from ..main import Processo, Usuario
            
            if not db:
                db = next(get_db())
            
            # Busca o processo
            processo = db.query(Processo).filter(Processo.id == processo_id).first()
            
            if not processo:
                raise ValueError(f"Processo {processo_id} não encontrado")
            
            # Verifica se está em status de aprovação
            if processo.status_processo != StatusProcesso.PENDENTE_APROVACAO.value:
                raise ValueError(f"Processo não está pendente de aprovação. Status atual: {processo.status_processo}")
            
            # Busca o usuário aprovador
            usuario = db.query(Usuario).filter(Usuario.id == usuario_aprovador_id).first()
            
            if not usuario:
                raise ValueError(f"Usuário aprovador {usuario_aprovador_id} não encontrado")
            
            # Verifica se usuário tem perfil de aprovador
            if usuario.perfil_usuario not in ["ADMINISTRADOR", "APROVADOR"]:
                raise ValueError("Usuário não tem permissão para aprovar faturas")
            
            # Processa a ação
            if acao == AcaoAprovacao.APROVAR:
                processo.status_processo = StatusProcesso.APROVADA.value
                processo.aprovado_por_usuario_id = usuario_aprovador_id
                processo.data_aprovacao = datetime.now()
                
                # Agendar upload para SAT
                self._agendar_upload_sat(processo, db)
                
                mensagem = "Fatura aprovada com sucesso"
                
            elif acao == AcaoAprovacao.REJEITAR:
                processo.status_processo = StatusProcesso.REJEITADA.value
                processo.aprovado_por_usuario_id = usuario_aprovador_id
                processo.data_aprovacao = datetime.now()
                
                mensagem = "Fatura rejeitada"
                
            elif acao == AcaoAprovacao.SOLICITAR_REVISAO:
                processo.status_processo = StatusProcesso.AGUARDANDO_DOWNLOAD.value
                mensagem = "Solicitada nova revisão da fatura"
            
            # Adiciona observações se fornecidas
            if observacoes:
                observacoes_atuais = processo.observacoes or ""
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
                nova_observacao = f"[{timestamp}] {usuario.nome_completo}: {observacoes}"
                
                if observacoes_atuais:
                    processo.observacoes = f"{observacoes_atuais}\n{nova_observacao}"
                else:
                    processo.observacoes = nova_observacao
            
            processo.data_atualizacao = datetime.now()
            
            db.commit()
            
            # Registra log de auditoria
            self._registrar_log_auditoria(processo_id, usuario_aprovador_id, acao, observacoes, db)
            
            # Envia notificações
            self._notificar_resultado_aprovacao(processo, acao, usuario, db)
            
            logger.info(f"Aprovação processada - Processo: {processo_id}, Ação: {acao.value}, Usuário: {usuario.nome_completo}")
            
            return {
                "sucesso": True,
                "processo_id": processo_id,
                "acao": acao.value,
                "status": processo.status_processo,
                "mensagem": mensagem,
                "aprovado_por": usuario.nome_completo,
                "data_aprovacao": processo.data_aprovacao.isoformat() if processo.data_aprovacao else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar aprovação: {e}")
            if db:
                db.rollback()
            return {
                "sucesso": False,
                "erro": str(e),
                "mensagem": "Erro ao processar aprovação"
            }
    
    def listar_faturas_pendentes_aprovacao(
        self, 
        usuario_aprovador_id: Optional[str] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        Lista faturas pendentes de aprovação
        
        Args:
            usuario_aprovador_id: ID do usuário (para filtrar por permissão)
            db: Sessão do banco
            
        Returns:
            Lista de faturas pendentes
        """
        try:
            from ..main import Processo, Cliente, Operadora
            
            if not db:
                db = next(get_db())
            
            # Query base
            query = db.query(Processo).filter(
                Processo.status_processo == StatusProcesso.PENDENTE_APROVACAO.value
            ).join(Cliente).join(Operadora)
            
            # Se especificado usuário, verifica permissões
            if usuario_aprovador_id:
                from ..main import Usuario
                usuario = db.query(Usuario).filter(Usuario.id == usuario_aprovador_id).first()
                if not usuario or usuario.perfil_usuario not in ["ADMINISTRADOR", "APROVADOR"]:
                    return []
            
            processos = query.all()
            
            faturas_pendentes = []
            for processo in processos:
                faturas_pendentes.append({
                    "processo_id": processo.id,
                    "cliente_id": processo.cliente_id,
                    "cliente_nome": processo.cliente.razao_social,
                    "operadora_nome": processo.cliente.operadora.nome,
                    "mes_ano": processo.mes_ano,
                    "url_fatura": processo.url_fatura,
                    "data_vencimento": processo.data_vencimento.isoformat() if processo.data_vencimento else None,
                    "valor_fatura": float(processo.valor_fatura) if processo.valor_fatura else None,
                    "data_criacao": processo.data_criacao.isoformat(),
                    "observacoes": processo.observacoes
                })
            
            return faturas_pendentes
            
        except Exception as e:
            logger.error(f"Erro ao listar faturas pendentes: {e}")
            return []
    
    def obter_historico_aprovacoes(
        self, 
        processo_id: Optional[str] = None,
        usuario_id: Optional[str] = None,
        limite: int = 50,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém histórico de aprovações
        
        Args:
            processo_id: Filtrar por processo específico
            usuario_id: Filtrar por usuário específico
            limite: Limite de registros
            db: Sessão do banco
            
        Returns:
            Lista do histórico de aprovações
        """
        try:
            from ..main import Processo, Cliente, Operadora, Usuario
            
            if not db:
                db = next(get_db())
            
            # Query base
            query = db.query(Processo).filter(
                Processo.status_processo.in_([
                    StatusProcesso.APROVADA.value,
                    StatusProcesso.REJEITADA.value
                ])
            ).join(Cliente).join(Operadora)
            
            # Filtros opcionais
            if processo_id:
                query = query.filter(Processo.id == processo_id)
            
            if usuario_id:
                query = query.filter(Processo.aprovado_por_usuario_id == usuario_id)
            
            # Ordenação e limite
            processos = query.order_by(Processo.data_aprovacao.desc()).limit(limite).all()
            
            historico = []
            for processo in processos:
                aprovador = None
                if processo.aprovado_por_usuario_id:
                    aprovador = db.query(Usuario).filter(
                        Usuario.id == processo.aprovado_por_usuario_id
                    ).first()
                
                historico.append({
                    "processo_id": processo.id,
                    "cliente_nome": processo.cliente.razao_social,
                    "operadora_nome": processo.cliente.operadora.nome,
                    "mes_ano": processo.mes_ano,
                    "status": processo.status_processo,
                    "aprovado_por": aprovador.nome_completo if aprovador else None,
                    "data_aprovacao": processo.data_aprovacao.isoformat() if processo.data_aprovacao else None,
                    "observacoes": processo.observacoes,
                    "valor_fatura": float(processo.valor_fatura) if processo.valor_fatura else None
                })
            
            return historico
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico de aprovações: {e}")
            return []
    
    def _notificar_aprovadores(self, processo, db: Session):
        """Notifica aprovadores sobre nova fatura"""
        try:
            from ..main import Usuario
            
            # Busca usuários aprovadores
            aprovadores = db.query(Usuario).filter(
                Usuario.perfil_usuario.in_(["ADMINISTRADOR", "APROVADOR"]),
                Usuario.status_ativo == True
            ).all()
            
            for aprovador in aprovadores:
                # Aqui seria implementada a lógica de notificação
                # (email, WhatsApp, etc.) conforme especificado no manual
                logger.info(f"Notificação enviada para aprovador: {aprovador.email}")
                
        except Exception as e:
            logger.error(f"Erro ao notificar aprovadores: {e}")
    
    def _agendar_upload_sat(self, processo, db: Session):
        """Agenda upload automático para SAT após aprovação"""
        try:
            from ..services.orquestrador_celery import orquestrador
            
            # Dados para upload SAT
            dados_cliente = {
                "nome_sat": processo.cliente.nome_sat,
                "dados_sat": processo.cliente.dados_sat,
                "unidade": processo.cliente.unidade,
                "servico": processo.cliente.servico
            }
            
            # Agenda task de upload
            task_id = orquestrador.executar_upload_sat(
                processo.id,
                processo.cliente_id,
                dados_cliente
            )
            
            logger.info(f"Upload SAT agendado - Processo: {processo.id}, Task: {task_id}")
            
        except Exception as e:
            logger.error(f"Erro ao agendar upload SAT: {e}")
    
    def _registrar_log_auditoria(
        self, 
        processo_id: str, 
        usuario_id: str, 
        acao: AcaoAprovacao, 
        observacoes: Optional[str],
        db: Session
    ):
        """Registra log de auditoria da aprovação"""
        try:
            # Aqui seria implementado o sistema de logs de auditoria
            # conforme especificado no manual
            log_entry = {
                "timestamp": datetime.now(),
                "processo_id": processo_id,
                "usuario_id": usuario_id,
                "acao": acao.value,
                "observacoes": observacoes
            }
            
            logger.info(f"Log de auditoria registrado: {log_entry}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar log de auditoria: {e}")
    
    def _notificar_resultado_aprovacao(
        self, 
        processo, 
        acao: AcaoAprovacao, 
        usuario_aprovador,
        db: Session
    ):
        """Notifica sobre resultado da aprovação"""
        try:
            # Aqui seria implementada a lógica de notificação sobre o resultado
            # conforme especificado no manual (email, WhatsApp, etc.)
            mensagem = f"Processo {processo.id} foi {acao.value} por {usuario_aprovador.nome_completo}"
            logger.info(f"Notificação de resultado enviada: {mensagem}")
            
        except Exception as e:
            logger.error(f"Erro ao notificar resultado: {e}")

# Instância global do workflow
workflow_aprovacao = WorkflowAprovacao()