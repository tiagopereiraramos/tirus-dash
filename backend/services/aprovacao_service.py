"""
Serviço de Aprovação de Faturas
Sistema RPA BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..models.database import get_db_session
from ..models.processo import (
    Processo, Execucao, Cliente, Operadora, Usuario,
    StatusProcesso, StatusExecucao
)

logger = logging.getLogger(__name__)

class AprovacaoService:
    """Serviço para gerenciamento de aprovação de faturas"""

    @staticmethod
    def obter_faturas_pendentes_aprovacao(
        operadora_id: str = None,
        valor_minimo: float = None,
        valor_maximo: float = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Obtém faturas pendentes de aprovação"""
        try:
            with get_db_session() as db:
                query = db.query(Processo)\
                    .join(Cliente)\
                    .join(Operadora)\
                    .filter(
                        and_(
                            Processo.status_processo == StatusProcesso.AGUARDANDO_APROVACAO.value,
                            Processo.caminho_s3_fatura.isnot(None),
                            Processo.valor_fatura.isnot(None)
                        )
                    )
                
                # Aplicar filtros
                if operadora_id:
                    query = query.filter(Cliente.operadora_id == operadora_id)
                
                if valor_minimo is not None:
                    query = query.filter(Processo.valor_fatura >= valor_minimo)
                
                if valor_maximo is not None:
                    query = query.filter(Processo.valor_fatura <= valor_maximo)
                
                # Contar total
                total = query.count()
                
                # Aplicar paginação e ordenação
                processos = query.order_by(desc(Processo.data_criacao))\
                    .offset(skip).limit(limit).all()
                
                # Formatar resultados
                faturas_pendentes = []
                for processo in processos:
                    faturas_pendentes.append({
                        "id": str(processo.id),
                        "mes_ano": processo.mes_ano,
                        "valor_fatura": float(processo.valor_fatura),
                        "data_vencimento": processo.data_vencimento.isoformat() if processo.data_vencimento else None,
                        "caminho_s3_fatura": processo.caminho_s3_fatura,
                        "data_criacao": processo.data_criacao.isoformat(),
                        "cliente": {
                            "id": str(processo.cliente.id),
                            "nome_sat": processo.cliente.nome_sat,
                            "razao_social": processo.cliente.razao_social,
                            "cnpj": processo.cliente.cnpj
                        },
                        "operadora": {
                            "id": str(processo.cliente.operadora.id),
                            "nome": processo.cliente.operadora.nome,
                            "codigo": processo.cliente.operadora.codigo
                        },
                        "observacoes": processo.observacoes
                    })
                
                return {
                    "sucesso": True,
                    "faturas_pendentes": faturas_pendentes,
                    "total": total,
                    "pagina_atual": skip // limit + 1 if limit > 0 else 1,
                    "total_paginas": (total + limit - 1) // limit if limit > 0 else 1
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter faturas pendentes: {str(e)}")
            raise

    @staticmethod
    def aprovar_fatura(
        processo_id: str,
        usuario_id: str,
        observacoes_aprovacao: str = None
    ) -> Dict[str, Any]:
        """Aprova uma fatura"""
        try:
            with get_db_session() as db:
                # Buscar processo
                processo = db.query(Processo).filter(Processo.id == processo_id).first()
                
                if not processo:
                    raise ValueError(f"Processo {processo_id} não encontrado")
                
                if processo.status_processo != StatusProcesso.AGUARDANDO_APROVACAO.value:
                    raise ValueError(f"Processo não está aguardando aprovação (status: {processo.status_processo})")
                
                # Buscar usuário
                usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
                if not usuario:
                    raise ValueError(f"Usuário {usuario_id} não encontrado")
                
                # Atualizar processo
                processo.status_processo = StatusProcesso.APROVADA.value
                processo.aprovado_por_usuario_id = usuario_id
                processo.data_aprovacao = datetime.now()
                processo.data_atualizacao = datetime.now()
                
                if observacoes_aprovacao:
                    processo.observacoes = observacoes_aprovacao
                
                db.commit()
                
                logger.info(f"Fatura aprovada: processo {processo_id} por usuário {usuario_id}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Fatura aprovada com sucesso",
                    "processo_id": processo_id,
                    "aprovado_por": usuario.nome,
                    "data_aprovacao": processo.data_aprovacao.isoformat(),
                    "valor_fatura": float(processo.valor_fatura) if processo.valor_fatura else None
                }
                
        except Exception as e:
            logger.error(f"Erro ao aprovar fatura: {str(e)}")
            raise

    @staticmethod
    def rejeitar_fatura(
        processo_id: str,
        usuario_id: str,
        motivo_rejeicao: str
    ) -> Dict[str, Any]:
        """Rejeita uma fatura"""
        try:
            with get_db_session() as db:
                # Buscar processo
                processo = db.query(Processo).filter(Processo.id == processo_id).first()
                
                if not processo:
                    raise ValueError(f"Processo {processo_id} não encontrado")
                
                if processo.status_processo != StatusProcesso.AGUARDANDO_APROVACAO.value:
                    raise ValueError(f"Processo não está aguardando aprovação (status: {processo.status_processo})")
                
                # Buscar usuário
                usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
                if not usuario:
                    raise ValueError(f"Usuário {usuario_id} não encontrado")
                
                # Atualizar processo
                processo.status_processo = StatusProcesso.REJEITADA.value
                processo.aprovado_por_usuario_id = usuario_id
                processo.data_aprovacao = datetime.now()
                processo.data_atualizacao = datetime.now()
                processo.observacoes = f"REJEITADA - {motivo_rejeicao}"
                
                db.commit()
                
                logger.info(f"Fatura rejeitada: processo {processo_id} por usuário {usuario_id}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Fatura rejeitada",
                    "processo_id": processo_id,
                    "rejeitado_por": usuario.nome,
                    "data_rejeicao": processo.data_aprovacao.isoformat(),
                    "motivo_rejeicao": motivo_rejeicao
                }
                
        except Exception as e:
            logger.error(f"Erro ao rejeitar fatura: {str(e)}")
            raise

    @staticmethod
    def obter_historico_aprovacoes(
        usuario_id: str = None,
        data_inicio: datetime = None,
        data_fim: datetime = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Obtém histórico de aprovações"""
        try:
            with get_db_session() as db:
                query = db.query(Processo)\
                    .join(Cliente)\
                    .join(Operadora)\
                    .filter(
                        Processo.status_processo.in_([
                            StatusProcesso.APROVADA.value,
                            StatusProcesso.REJEITADA.value
                        ])
                    )
                
                # Aplicar filtros
                if usuario_id:
                    query = query.filter(Processo.aprovado_por_usuario_id == usuario_id)
                
                if data_inicio:
                    query = query.filter(Processo.data_aprovacao >= data_inicio)
                
                if data_fim:
                    query = query.filter(Processo.data_aprovacao <= data_fim)
                
                # Contar total
                total = query.count()
                
                # Aplicar paginação
                processos = query.order_by(desc(Processo.data_aprovacao))\
                    .offset(skip).limit(limit).all()
                
                # Formatar resultados
                historico = []
                for processo in processos:
                    # Buscar dados do usuário que aprovou
                    usuario_aprovador = None
                    if processo.aprovado_por_usuario_id:
                        usuario_aprovador = db.query(Usuario)\
                            .filter(Usuario.id == processo.aprovado_por_usuario_id)\
                            .first()
                    
                    historico.append({
                        "id": str(processo.id),
                        "mes_ano": processo.mes_ano,
                        "status": processo.status_processo,
                        "valor_fatura": float(processo.valor_fatura) if processo.valor_fatura else None,
                        "data_aprovacao": processo.data_aprovacao.isoformat() if processo.data_aprovacao else None,
                        "aprovado_por": {
                            "id": str(usuario_aprovador.id) if usuario_aprovador else None,
                            "nome": usuario_aprovador.nome if usuario_aprovador else "Usuário não encontrado"
                        },
                        "cliente": {
                            "nome_sat": processo.cliente.nome_sat,
                            "razao_social": processo.cliente.razao_social
                        },
                        "operadora": {
                            "nome": processo.cliente.operadora.nome,
                            "codigo": processo.cliente.operadora.codigo
                        },
                        "observacoes": processo.observacoes
                    })
                
                return {
                    "sucesso": True,
                    "historico_aprovacoes": historico,
                    "total": total,
                    "pagina_atual": skip // limit + 1 if limit > 0 else 1,
                    "total_paginas": (total + limit - 1) // limit if limit > 0 else 1
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter histórico de aprovações: {str(e)}")
            raise

    @staticmethod
    def obter_estatisticas_aprovacao() -> Dict[str, Any]:
        """Obtém estatísticas de aprovação"""
        try:
            with get_db_session() as db:
                # Contadores gerais
                total_pendentes = db.query(Processo)\
                    .filter(Processo.status_processo == StatusProcesso.AGUARDANDO_APROVACAO.value)\
                    .count()
                
                total_aprovadas = db.query(Processo)\
                    .filter(Processo.status_processo == StatusProcesso.APROVADA.value)\
                    .count()
                
                total_rejeitadas = db.query(Processo)\
                    .filter(Processo.status_processo == StatusProcesso.REJEITADA.value)\
                    .count()
                
                # Valores financeiros
                from sqlalchemy import func
                valor_total_pendente = db.query(func.sum(Processo.valor_fatura))\
                    .filter(Processo.status_processo == StatusProcesso.AGUARDANDO_APROVACAO.value)\
                    .scalar() or 0
                
                valor_total_aprovado = db.query(func.sum(Processo.valor_fatura))\
                    .filter(Processo.status_processo == StatusProcesso.APROVADA.value)\
                    .scalar() or 0
                
                valor_total_rejeitado = db.query(func.sum(Processo.valor_fatura))\
                    .filter(Processo.status_processo == StatusProcesso.REJEITADA.value)\
                    .scalar() or 0
                
                # Estatísticas por operadora
                aprovacoes_por_operadora = db.query(
                    Operadora.nome,
                    func.count(Processo.id).label('total_aprovacoes'),
                    func.sum(Processo.valor_fatura).label('valor_total')
                )\
                .join(Cliente, Operadora.id == Cliente.operadora_id)\
                .join(Processo, Cliente.id == Processo.cliente_id)\
                .filter(Processo.status_processo == StatusProcesso.APROVADA.value)\
                .group_by(Operadora.id, Operadora.nome)\
                .order_by(func.count(Processo.id).desc())\
                .limit(10).all()
                
                operadoras_stats = []
                for item in aprovacoes_por_operadora:
                    operadoras_stats.append({
                        "operadora": item.nome,
                        "total_aprovacoes": item.total_aprovacoes,
                        "valor_total": float(item.valor_total) if item.valor_total else 0
                    })
                
                # Taxa de aprovação
                total_processadas = total_aprovadas + total_rejeitadas
                taxa_aprovacao = (total_aprovadas / total_processadas * 100) if total_processadas > 0 else 0
                
                return {
                    "sucesso": True,
                    "estatisticas": {
                        "contadores": {
                            "total_pendentes": total_pendentes,
                            "total_aprovadas": total_aprovadas,
                            "total_rejeitadas": total_rejeitadas,
                            "total_processadas": total_processadas
                        },
                        "valores_financeiros": {
                            "valor_total_pendente": float(valor_total_pendente),
                            "valor_total_aprovado": float(valor_total_aprovado),
                            "valor_total_rejeitado": float(valor_total_rejeitado)
                        },
                        "metricas": {
                            "taxa_aprovacao_percentual": round(taxa_aprovacao, 2)
                        },
                        "top_operadoras": operadoras_stats
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de aprovação: {str(e)}")
            raise

    @staticmethod
    def aprovar_faturas_em_lote(
        processo_ids: List[str],
        usuario_id: str,
        observacoes_aprovacao: str = None
    ) -> Dict[str, Any]:
        """Aprova múltiplas faturas em lote"""
        try:
            with get_db_session() as db:
                # Buscar usuário
                usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
                if not usuario:
                    raise ValueError(f"Usuário {usuario_id} não encontrado")
                
                aprovadas = []
                erros = []
                
                for processo_id in processo_ids:
                    try:
                        # Buscar processo
                        processo = db.query(Processo).filter(Processo.id == processo_id).first()
                        
                        if not processo:
                            erros.append(f"Processo {processo_id} não encontrado")
                            continue
                        
                        if processo.status_processo != StatusProcesso.AGUARDANDO_APROVACAO.value:
                            erros.append(f"Processo {processo_id} não está aguardando aprovação")
                            continue
                        
                        # Aprovar
                        processo.status_processo = StatusProcesso.APROVADA.value
                        processo.aprovado_por_usuario_id = usuario_id
                        processo.data_aprovacao = datetime.now()
                        processo.data_atualizacao = datetime.now()
                        
                        if observacoes_aprovacao:
                            processo.observacoes = observacoes_aprovacao
                        
                        aprovadas.append({
                            "processo_id": processo_id,
                            "valor_fatura": float(processo.valor_fatura) if processo.valor_fatura else None,
                            "cliente": processo.cliente.nome_sat
                        })
                        
                    except Exception as e:
                        erros.append(f"Processo {processo_id}: {str(e)}")
                        continue
                
                db.commit()
                
                logger.info(f"Aprovação em lote: {len(aprovadas)} aprovadas, {len(erros)} erros")
                
                return {
                    "sucesso": True,
                    "mensagem": f"Aprovação em lote concluída",
                    "aprovadas": aprovadas,
                    "total_aprovadas": len(aprovadas),
                    "erros": erros,
                    "total_erros": len(erros),
                    "aprovado_por": usuario.nome,
                    "data_aprovacao": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro na aprovação em lote: {str(e)}")
            raise

    @staticmethod
    def obter_detalhes_fatura_aprovacao(processo_id: str) -> Dict[str, Any]:
        """Obtém detalhes completos de uma fatura para aprovação"""
        try:
            with get_db_session() as db:
                processo = db.query(Processo)\
                    .join(Cliente)\
                    .join(Operadora)\
                    .filter(Processo.id == processo_id)\
                    .first()
                
                if not processo:
                    raise ValueError(f"Processo {processo_id} não encontrado")
                
                # Buscar execuções relacionadas
                execucoes = db.query(Execucao)\
                    .filter(Execucao.processo_id == processo_id)\
                    .order_by(desc(Execucao.data_inicio))\
                    .all()
                
                execucoes_detalhes = []
                for exec in execucoes:
                    execucoes_detalhes.append({
                        "id": str(exec.id),
                        "tipo_execucao": exec.tipo_execucao,
                        "status_execucao": exec.status_execucao,
                        "data_inicio": exec.data_inicio.isoformat(),
                        "data_fim": exec.data_fim.isoformat() if exec.data_fim else None,
                        "mensagem_log": exec.mensagem_log,
                        "url_arquivo_s3": exec.url_arquivo_s3
                    })
                
                # Buscar dados do usuário que aprovou (se já aprovado)
                usuario_aprovador = None
                if processo.aprovado_por_usuario_id:
                    usuario_aprovador = db.query(Usuario)\
                        .filter(Usuario.id == processo.aprovado_por_usuario_id)\
                        .first()
                
                return {
                    "sucesso": True,
                    "fatura_detalhes": {
                        "processo": {
                            "id": str(processo.id),
                            "mes_ano": processo.mes_ano,
                            "status_processo": processo.status_processo,
                            "valor_fatura": float(processo.valor_fatura) if processo.valor_fatura else None,
                            "data_vencimento": processo.data_vencimento.isoformat() if processo.data_vencimento else None,
                            "caminho_s3_fatura": processo.caminho_s3_fatura,
                            "data_criacao": processo.data_criacao.isoformat(),
                            "data_atualizacao": processo.data_atualizacao.isoformat(),
                            "data_aprovacao": processo.data_aprovacao.isoformat() if processo.data_aprovacao else None,
                            "observacoes": processo.observacoes
                        },
                        "cliente": {
                            "id": str(processo.cliente.id),
                            "hash_unico": processo.cliente.hash_unico,
                            "nome_sat": processo.cliente.nome_sat,
                            "razao_social": processo.cliente.razao_social,
                            "cnpj": processo.cliente.cnpj,
                            "unidade": processo.cliente.unidade,
                            "servico": processo.cliente.servico
                        },
                        "operadora": {
                            "id": str(processo.cliente.operadora.id),
                            "nome": processo.cliente.operadora.nome,
                            "codigo": processo.cliente.operadora.codigo,
                            "possui_rpa": processo.cliente.operadora.possui_rpa
                        },
                        "aprovacao": {
                            "aprovado_por": {
                                "id": str(usuario_aprovador.id) if usuario_aprovador else None,
                                "nome": usuario_aprovador.nome if usuario_aprovador else None
                            } if usuario_aprovador else None,
                            "data_aprovacao": processo.data_aprovacao.isoformat() if processo.data_aprovacao else None
                        },
                        "execucoes": execucoes_detalhes
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter detalhes da fatura: {str(e)}")
            raise