"""
Serviço de Manipulação de Execuções
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
    Execucao, Processo, Cliente, Operadora,
    StatusExecucao, TipoExecucao
)

logger = logging.getLogger(__name__)

class ExecucaoService:
    """Serviço para manipulação de execuções de RPA"""

    @staticmethod
    def criar_execucao(
        processo_id: str,
        tipo_execucao: TipoExecucao,
        parametros_entrada: Dict[str, Any] = None,
        usuario_id: str = None,
        ip_origem: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """Cria uma nova execução"""
        try:
            with get_db_session() as db:
                # Verificar se processo existe
                processo = db.query(Processo).filter(Processo.id == processo_id).first()
                if not processo:
                    raise ValueError(f"Processo {processo_id} não encontrado")
                
                # Criar execução
                execucao = Execucao(
                    processo_id=processo_id,
                    tipo_execucao=tipo_execucao.value,
                    status_execucao=StatusExecucao.EXECUTANDO.value,
                    parametros_entrada=parametros_entrada or {},
                    executado_por_usuario_id=usuario_id,
                    ip_origem=ip_origem,
                    user_agent=user_agent,
                    numero_tentativa=1
                )
                
                # Verificar tentativas anteriores
                tentativas_anteriores = db.query(Execucao).filter(
                    and_(
                        Execucao.processo_id == processo_id,
                        Execucao.tipo_execucao == tipo_execucao.value
                    )
                ).count()
                
                execucao.numero_tentativa = tentativas_anteriores + 1
                
                db.add(execucao)
                db.commit()
                db.refresh(execucao)
                
                logger.info(f"Execução criada: {execucao.id} para processo {processo_id}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Execução criada com sucesso",
                    "execucao_id": str(execucao.id),
                    "processo_id": processo_id,
                    "tipo_execucao": tipo_execucao.value,
                    "numero_tentativa": execucao.numero_tentativa
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar execução: {str(e)}")
            raise

    @staticmethod
    def atualizar_execucao(
        execucao_id: str,
        status_execucao: StatusExecucao = None,
        resultado_saida: Dict[str, Any] = None,
        mensagem_log: str = None,
        detalhes_erro: Dict[str, Any] = None,
        url_arquivo_s3: str = None,
        finalizar: bool = False
    ) -> Dict[str, Any]:
        """Atualiza uma execução existente"""
        try:
            with get_db_session() as db:
                execucao = db.query(Execucao).filter(Execucao.id == execucao_id).first()
                
                if not execucao:
                    raise ValueError(f"Execução {execucao_id} não encontrada")
                
                # Atualizar campos
                if status_execucao:
                    execucao.status_execucao = status_execucao.value
                
                if resultado_saida:
                    execucao.resultado_saida = resultado_saida
                
                if mensagem_log:
                    execucao.mensagem_log = mensagem_log
                
                if detalhes_erro:
                    execucao.detalhes_erro = detalhes_erro
                
                if url_arquivo_s3:
                    execucao.url_arquivo_s3 = url_arquivo_s3
                
                if finalizar or status_execucao in [StatusExecucao.CONCLUIDO, StatusExecucao.FALHOU]:
                    execucao.data_fim = datetime.now()
                
                db.commit()
                
                logger.info(f"Execução {execucao_id} atualizada com status: {execucao.status_execucao}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Execução atualizada com sucesso",
                    "execucao_id": execucao_id,
                    "status_atual": execucao.status_execucao
                }
                
        except Exception as e:
            logger.error(f"Erro ao atualizar execução: {str(e)}")
            raise

    @staticmethod
    def buscar_execucoes_com_filtros(
        processo_id: str = None,
        tipo_execucao: TipoExecucao = None,
        status_execucao: StatusExecucao = None,
        operadora_id: str = None,
        data_inicio: datetime = None,
        data_fim: datetime = None,
        apenas_ativas: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Busca execuções com filtros avançados"""
        try:
            with get_db_session() as db:
                query = db.query(Execucao).join(Processo).join(Cliente).join(Operadora)
                
                # Aplicar filtros
                if processo_id:
                    query = query.filter(Execucao.processo_id == processo_id)
                
                if tipo_execucao:
                    query = query.filter(Execucao.tipo_execucao == tipo_execucao.value)
                
                if status_execucao:
                    query = query.filter(Execucao.status_execucao == status_execucao.value)
                
                if operadora_id:
                    query = query.filter(Cliente.operadora_id == operadora_id)
                
                if data_inicio:
                    query = query.filter(Execucao.data_inicio >= data_inicio)
                
                if data_fim:
                    query = query.filter(Execucao.data_inicio <= data_fim)
                
                if apenas_ativas:
                    query = query.filter(Execucao.status_execucao == StatusExecucao.EXECUTANDO.value)
                
                # Ordenar por data mais recente
                query = query.order_by(desc(Execucao.data_inicio))
                
                # Contar total
                total = query.count()
                
                # Aplicar paginação
                execucoes = query.offset(skip).limit(limit).all()
                
                # Formatar resultados
                resultados = []
                for execucao in execucoes:
                    tempo_execucao = None
                    if execucao.data_fim and execucao.data_inicio:
                        tempo_execucao = (execucao.data_fim - execucao.data_inicio).total_seconds()
                    
                    resultados.append({
                        "id": str(execucao.id),
                        "processo_id": str(execucao.processo_id),
                        "tipo_execucao": execucao.tipo_execucao,
                        "status_execucao": execucao.status_execucao,
                        "numero_tentativa": execucao.numero_tentativa,
                        "data_inicio": execucao.data_inicio.isoformat(),
                        "data_fim": execucao.data_fim.isoformat() if execucao.data_fim else None,
                        "tempo_execucao_segundos": tempo_execucao,
                        "mensagem_log": execucao.mensagem_log,
                        "url_arquivo_s3": execucao.url_arquivo_s3,
                        "processo": {
                            "mes_ano": execucao.processo.mes_ano,
                            "status_processo": execucao.processo.status_processo
                        },
                        "cliente": {
                            "nome_sat": execucao.processo.cliente.nome_sat,
                            "cnpj": execucao.processo.cliente.cnpj
                        },
                        "operadora": {
                            "nome": execucao.processo.cliente.operadora.nome,
                            "codigo": execucao.processo.cliente.operadora.codigo
                        },
                        "parametros_entrada": execucao.parametros_entrada,
                        "resultado_saida": execucao.resultado_saida,
                        "detalhes_erro": execucao.detalhes_erro
                    })
                
                return {
                    "sucesso": True,
                    "execucoes": resultados,
                    "total": total,
                    "pagina_atual": skip // limit + 1 if limit > 0 else 1,
                    "total_paginas": (total + limit - 1) // limit if limit > 0 else 1
                }
                
        except Exception as e:
            logger.error(f"Erro na busca de execuções: {str(e)}")
            raise

    @staticmethod
    def obter_execucoes_ativas() -> Dict[str, Any]:
        """Obtém todas as execuções atualmente ativas"""
        try:
            with get_db_session() as db:
                execucoes = db.query(Execucao).filter(
                    Execucao.status_execucao == StatusExecucao.EXECUTANDO.value
                ).join(Processo).join(Cliente).join(Operadora).all()
                
                resultados = []
                for execucao in execucoes:
                    tempo_execucao = (datetime.now() - execucao.data_inicio).total_seconds()
                    
                    resultados.append({
                        "id": str(execucao.id),
                        "processo_id": str(execucao.processo_id),
                        "tipo_execucao": execucao.tipo_execucao,
                        "numero_tentativa": execucao.numero_tentativa,
                        "data_inicio": execucao.data_inicio.isoformat(),
                        "tempo_execucao_segundos": tempo_execucao,
                        "operadora": execucao.processo.cliente.operadora.nome,
                        "cliente": execucao.processo.cliente.nome_sat,
                        "mes_ano": execucao.processo.mes_ano
                    })
                
                return {
                    "sucesso": True,
                    "execucoes_ativas": resultados,
                    "total_ativas": len(resultados),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter execuções ativas: {str(e)}")
            raise

    @staticmethod
    def obter_estatisticas_execucoes(
        data_inicio: datetime = None,
        data_fim: datetime = None,
        operadora_id: str = None
    ) -> Dict[str, Any]:
        """Obtém estatísticas de execuções"""
        try:
            with get_db_session() as db:
                query = db.query(Execucao).join(Processo).join(Cliente)
                
                if data_inicio:
                    query = query.filter(Execucao.data_inicio >= data_inicio)
                
                if data_fim:
                    query = query.filter(Execucao.data_inicio <= data_fim)
                
                if operadora_id:
                    query = query.filter(Cliente.operadora_id == operadora_id)
                
                # Estatísticas por status
                estatisticas_status = {}
                for status in StatusExecucao:
                    count = query.filter(Execucao.status_execucao == status.value).count()
                    estatisticas_status[status.value] = count
                
                # Estatísticas por tipo
                estatisticas_tipo = {}
                for tipo in TipoExecucao:
                    count = query.filter(Execucao.tipo_execucao == tipo.value).count()
                    estatisticas_tipo[tipo.value] = count
                
                # Estatísticas de sucesso
                total_execucoes = query.count()
                execucoes_sucesso = query.filter(Execucao.status_execucao == StatusExecucao.CONCLUIDO.value).count()
                execucoes_falha = query.filter(Execucao.status_execucao == StatusExecucao.FALHOU.value).count()
                
                taxa_sucesso = (execucoes_sucesso / total_execucoes * 100) if total_execucoes > 0 else 0
                
                # Tempo médio de execução
                from sqlalchemy import func
                execucoes_finalizadas = query.filter(Execucao.data_fim.isnot(None)).all()
                tempo_medio = 0
                if execucoes_finalizadas:
                    tempos = [(e.data_fim - e.data_inicio).total_seconds() for e in execucoes_finalizadas]
                    tempo_medio = sum(tempos) / len(tempos)
                
                return {
                    "sucesso": True,
                    "estatisticas": {
                        "total_execucoes": total_execucoes,
                        "execucoes_sucesso": execucoes_sucesso,
                        "execucoes_falha": execucoes_falha,
                        "taxa_sucesso_percentual": round(taxa_sucesso, 2),
                        "tempo_medio_execucao_segundos": round(tempo_medio, 2),
                        "distribuicao_status": estatisticas_status,
                        "distribuicao_tipo": estatisticas_tipo
                    },
                    "periodo": {
                        "data_inicio": data_inicio.isoformat() if data_inicio else None,
                        "data_fim": data_fim.isoformat() if data_fim else None
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de execuções: {str(e)}")
            raise

    @staticmethod
    def cancelar_execucao(execucao_id: str, motivo: str = None) -> Dict[str, Any]:
        """Cancela uma execução em andamento"""
        try:
            with get_db_session() as db:
                execucao = db.query(Execucao).filter(Execucao.id == execucao_id).first()
                
                if not execucao:
                    raise ValueError(f"Execução {execucao_id} não encontrada")
                
                if execucao.status_execucao != StatusExecucao.EXECUTANDO.value:
                    raise ValueError(f"Execução não está em andamento (status: {execucao.status_execucao})")
                
                # Cancelar execução
                execucao.status_execucao = StatusExecucao.FALHOU.value
                execucao.data_fim = datetime.now()
                execucao.mensagem_log = f"Execução cancelada pelo usuário. Motivo: {motivo or 'Não informado'}"
                execucao.detalhes_erro = {
                    "cancelado_pelo_usuario": True,
                    "motivo": motivo,
                    "timestamp_cancelamento": datetime.now().isoformat()
                }
                
                db.commit()
                
                logger.info(f"Execução {execucao_id} cancelada. Motivo: {motivo}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Execução cancelada com sucesso",
                    "execucao_id": execucao_id,
                    "motivo": motivo
                }
                
        except Exception as e:
            logger.error(f"Erro ao cancelar execução: {str(e)}")
            raise

    @staticmethod
    def retentar_execucao(execucao_id: str) -> Dict[str, Any]:
        """Cria uma nova tentativa baseada em uma execução anterior"""
        try:
            with get_db_session() as db:
                execucao_original = db.query(Execucao).filter(Execucao.id == execucao_id).first()
                
                if not execucao_original:
                    raise ValueError(f"Execução {execucao_id} não encontrada")
                
                if execucao_original.status_execucao == StatusExecucao.EXECUTANDO.value:
                    raise ValueError("Não é possível retentar execução em andamento")
                
                # Criar nova execução baseada na anterior
                nova_execucao = Execucao(
                    processo_id=execucao_original.processo_id,
                    tipo_execucao=execucao_original.tipo_execucao,
                    status_execucao=StatusExecucao.EXECUTANDO.value,
                    parametros_entrada=execucao_original.parametros_entrada,
                    numero_tentativa=execucao_original.numero_tentativa + 1,
                    executado_por_usuario_id=execucao_original.executado_por_usuario_id
                )
                
                db.add(nova_execucao)
                db.commit()
                db.refresh(nova_execucao)
                
                logger.info(f"Nova tentativa criada: {nova_execucao.id} baseada em {execucao_id}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Nova tentativa criada com sucesso",
                    "nova_execucao_id": str(nova_execucao.id),
                    "execucao_original_id": execucao_id,
                    "numero_tentativa": nova_execucao.numero_tentativa
                }
                
        except Exception as e:
            logger.error(f"Erro ao retentar execução: {str(e)}")
            raise