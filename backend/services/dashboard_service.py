"""
Serviço de Dashboard
Sistema RPA BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from ..models.database import get_db_session
from ..models.processo import (
    Processo, Execucao, Cliente, Operadora,
    StatusProcesso, StatusExecucao, TipoExecucao
)
from ..models.usuario import Usuario

logger = logging.getLogger(__name__)

class DashboardService:
    """Serviço para dados do dashboard"""

    @staticmethod
    def obter_dados_dashboard_principal() -> Dict[str, Any]:
        """Obtém dados principais do dashboard"""
        try:
            with get_db_session() as db:
                # Estatísticas gerais
                total_operadoras = db.query(Operadora).filter(Operadora.status_ativo == True).count()
                total_clientes = db.query(Cliente).filter(Cliente.status_ativo == True).count()
                
                # Processos do mês atual
                mes_atual = datetime.now().strftime("%Y-%m")
                processos_mes_atual = db.query(Processo).filter(
                    Processo.mes_ano == mes_atual
                ).count()
                
                # Execuções ativas
                execucoes_ativas = db.query(Execucao).filter(
                    Execucao.status_execucao == StatusExecucao.EXECUTANDO.value
                ).count()
                
                # Processos por status (últimos 30 dias)
                data_limite = datetime.now() - timedelta(days=30)
                processos_recentes = db.query(
                    Processo.status_processo,
                    func.count(Processo.id).label('count')
                ).filter(
                    Processo.data_criacao >= data_limite
                ).group_by(Processo.status_processo).all()
                
                status_distribution = {}
                for item in processos_recentes:
                    status_distribution[item.status_processo] = item.count
                
                # Execuções por operadora (últimos 7 dias)
                data_limite_7d = datetime.now() - timedelta(days=7)
                execucoes_por_operadora = db.query(
                    Operadora.nome,
                    func.count(Execucao.id).label('count')
                ).join(Cliente, Operadora.id == Cliente.operadora_id)\
                .join(Processo, Cliente.id == Processo.cliente_id)\
                .join(Execucao, Processo.id == Execucao.processo_id)\
                .filter(Execucao.data_inicio >= data_limite_7d)\
                .group_by(Operadora.id, Operadora.nome)\
                .order_by(func.count(Execucao.id).desc())\
                .limit(5).all()
                
                operadoras_ativas = []
                for item in execucoes_por_operadora:
                    operadoras_ativas.append({
                        "nome": item.nome,
                        "execucoes": item.count
                    })
                
                # Taxa de sucesso geral
                total_execucoes_finalizadas = db.query(Execucao).filter(
                    Execucao.status_execucao.in_([StatusExecucao.CONCLUIDO.value, StatusExecucao.FALHOU.value])
                ).count()
                
                execucoes_sucesso = db.query(Execucao).filter(
                    Execucao.status_execucao == StatusExecucao.CONCLUIDO.value
                ).count()
                
                taxa_sucesso = (execucoes_sucesso / total_execucoes_finalizadas * 100) if total_execucoes_finalizadas > 0 else 0
                
                return {
                    "sucesso": True,
                    "dashboard": {
                        "resumo_geral": {
                            "total_operadoras": total_operadoras,
                            "total_clientes": total_clientes,
                            "processos_mes_atual": processos_mes_atual,
                            "execucoes_ativas": execucoes_ativas,
                            "taxa_sucesso_percentual": round(taxa_sucesso, 2)
                        },
                        "distribuicao_status_processos": status_distribution,
                        "top_operadoras_ativas": operadoras_ativas,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter dados do dashboard: {str(e)}")
            raise

    @staticmethod
    def obter_metricas_tempo_real() -> Dict[str, Any]:
        """Obtém métricas em tempo real"""
        try:
            with get_db_session() as db:
                # Execuções ativas com detalhes
                execucoes_ativas = db.query(Execucao)\
                    .join(Processo)\
                    .join(Cliente)\
                    .join(Operadora)\
                    .filter(Execucao.status_execucao == StatusExecucao.EXECUTANDO.value)\
                    .all()
                
                execucoes_detalhes = []
                for exec in execucoes_ativas:
                    tempo_execucao = (datetime.now() - exec.data_inicio).total_seconds()
                    execucoes_detalhes.append({
                        "id": str(exec.id),
                        "operadora": exec.processo.cliente.operadora.nome,
                        "cliente": exec.processo.cliente.nome_sat,
                        "tipo": exec.tipo_execucao,
                        "tempo_execucao_segundos": round(tempo_execucao),
                        "data_inicio": exec.data_inicio.isoformat()
                    })
                
                # Últimas execuções concluídas (últimas 10)
                ultimas_execucoes = db.query(Execucao)\
                    .join(Processo)\
                    .join(Cliente)\
                    .join(Operadora)\
                    .filter(Execucao.status_execucao.in_([
                        StatusExecucao.CONCLUIDO.value,
                        StatusExecucao.FALHOU.value
                    ]))\
                    .order_by(desc(Execucao.data_fim))\
                    .limit(10).all()
                
                historico_recente = []
                for exec in ultimas_execucoes:
                    tempo_total = None
                    if exec.data_fim and exec.data_inicio:
                        tempo_total = (exec.data_fim - exec.data_inicio).total_seconds()
                    
                    historico_recente.append({
                        "id": str(exec.id),
                        "operadora": exec.processo.cliente.operadora.nome,
                        "cliente": exec.processo.cliente.nome_sat,
                        "tipo": exec.tipo_execucao,
                        "status": exec.status_execucao,
                        "tempo_total_segundos": round(tempo_total) if tempo_total else None,
                        "data_fim": exec.data_fim.isoformat() if exec.data_fim else None
                    })
                
                # Status do sistema
                sistema_stats = {
                    "execucoes_ativas": len(execucoes_ativas),
                    "operadoras_em_uso": len(set([e["operadora"] for e in execucoes_detalhes])),
                    "tempo_medio_execucao_ativa": round(
                        sum([e["tempo_execucao_segundos"] for e in execucoes_detalhes]) / len(execucoes_detalhes)
                    ) if execucoes_detalhes else 0
                }
                
                return {
                    "sucesso": True,
                    "tempo_real": {
                        "execucoes_ativas": execucoes_detalhes,
                        "historico_recente": historico_recente,
                        "sistema_stats": sistema_stats,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter métricas tempo real: {str(e)}")
            raise

    @staticmethod
    def obter_relatorio_operadoras() -> Dict[str, Any]:
        """Obtém relatório detalhado por operadora"""
        try:
            with get_db_session() as db:
                operadoras = db.query(Operadora).filter(Operadora.status_ativo == True).all()
                
                relatorio = []
                for operadora in operadoras:
                    # Estatísticas da operadora
                    total_clientes = db.query(Cliente).filter(
                        and_(
                            Cliente.operadora_id == operadora.id,
                            Cliente.status_ativo == True
                        )
                    ).count()
                    
                    # Processos dos últimos 30 dias
                    data_limite = datetime.now() - timedelta(days=30)
                    processos_30d = db.query(Processo)\
                        .join(Cliente)\
                        .filter(
                            and_(
                                Cliente.operadora_id == operadora.id,
                                Processo.data_criacao >= data_limite
                            )
                        ).count()
                    
                    # Execuções dos últimos 30 dias
                    execucoes_30d = db.query(Execucao)\
                        .join(Processo)\
                        .join(Cliente)\
                        .filter(
                            and_(
                                Cliente.operadora_id == operadora.id,
                                Execucao.data_inicio >= data_limite
                            )
                        ).count()
                    
                    # Taxa de sucesso
                    execucoes_sucesso = db.query(Execucao)\
                        .join(Processo)\
                        .join(Cliente)\
                        .filter(
                            and_(
                                Cliente.operadora_id == operadora.id,
                                Execucao.status_execucao == StatusExecucao.CONCLUIDO.value,
                                Execucao.data_inicio >= data_limite
                            )
                        ).count()
                    
                    taxa_sucesso = (execucoes_sucesso / execucoes_30d * 100) if execucoes_30d > 0 else 0
                    
                    # Valor total das faturas processadas
                    valor_total = db.query(func.sum(Processo.valor_fatura))\
                        .join(Cliente)\
                        .filter(
                            and_(
                                Cliente.operadora_id == operadora.id,
                                Processo.valor_fatura.isnot(None),
                                Processo.data_criacao >= data_limite
                            )
                        ).scalar() or 0
                    
                    relatorio.append({
                        "operadora": {
                            "id": str(operadora.id),
                            "nome": operadora.nome,
                            "codigo": operadora.codigo,
                            "possui_rpa": operadora.possui_rpa
                        },
                        "estatisticas": {
                            "total_clientes": total_clientes,
                            "processos_30_dias": processos_30d,
                            "execucoes_30_dias": execucoes_30d,
                            "taxa_sucesso_percentual": round(taxa_sucesso, 2),
                            "valor_total_faturas": float(valor_total)
                        }
                    })
                
                # Ordenar por número de execuções
                relatorio.sort(key=lambda x: x["estatisticas"]["execucoes_30_dias"], reverse=True)
                
                return {
                    "sucesso": True,
                    "relatorio_operadoras": relatorio,
                    "periodo": "últimos 30 dias",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de operadoras: {str(e)}")
            raise

    @staticmethod
    def obter_grafico_execucoes_tempo(dias: int = 7) -> Dict[str, Any]:
        """Obtém dados para gráfico de execuções por tempo"""
        try:
            with get_db_session() as db:
                data_limite = datetime.now() - timedelta(days=dias)
                
                # Execuções por dia
                execucoes_por_dia = db.query(
                    func.date(Execucao.data_inicio).label('data'),
                    Execucao.status_execucao,
                    func.count(Execucao.id).label('count')
                ).filter(
                    Execucao.data_inicio >= data_limite
                ).group_by(
                    func.date(Execucao.data_inicio),
                    Execucao.status_execucao
                ).order_by(func.date(Execucao.data_inicio)).all()
                
                # Organizar dados por data
                dados_grafico = {}
                for item in execucoes_por_dia:
                    data_str = item.data.isoformat()
                    if data_str not in dados_grafico:
                        dados_grafico[data_str] = {
                            "data": data_str,
                            "total": 0,
                            "sucesso": 0,
                            "falha": 0,
                            "executando": 0
                        }
                    
                    dados_grafico[data_str]["total"] += item.count
                    
                    if item.status_execucao == StatusExecucao.CONCLUIDO.value:
                        dados_grafico[data_str]["sucesso"] += item.count
                    elif item.status_execucao == StatusExecucao.FALHOU.value:
                        dados_grafico[data_str]["falha"] += item.count
                    elif item.status_execucao == StatusExecucao.EXECUTANDO.value:
                        dados_grafico[data_str]["executando"] += item.count
                
                # Converter para lista ordenada
                grafico_dados = list(dados_grafico.values())
                grafico_dados.sort(key=lambda x: x["data"])
                
                return {
                    "sucesso": True,
                    "grafico_execucoes": {
                        "dados": grafico_dados,
                        "periodo_dias": dias,
                        "data_inicio": data_limite.isoformat(),
                        "data_fim": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de execuções: {str(e)}")
            raise

    @staticmethod
    def obter_alertas_sistema() -> Dict[str, Any]:
        """Obtém alertas e notificações do sistema"""
        try:
            with get_db_session() as db:
                alertas = []
                
                # Execuções há muito tempo em execução (> 2 horas)
                limite_tempo = datetime.now() - timedelta(hours=2)
                execucoes_lentas = db.query(Execucao)\
                    .join(Processo)\
                    .join(Cliente)\
                    .join(Operadora)\
                    .filter(
                        and_(
                            Execucao.status_execucao == StatusExecucao.EXECUTANDO.value,
                            Execucao.data_inicio <= limite_tempo
                        )
                    ).all()
                
                for exec in execucoes_lentas:
                    tempo_execucao = (datetime.now() - exec.data_inicio).total_seconds() / 3600
                    alertas.append({
                        "tipo": "EXECUCAO_LENTA",
                        "severidade": "ALTA",
                        "titulo": "Execução em andamento há muito tempo",
                        "descricao": f"Execução {exec.id} da operadora {exec.processo.cliente.operadora.nome} está em andamento há {tempo_execucao:.1f} horas",
                        "data": exec.data_inicio.isoformat(),
                        "dados": {
                            "execucao_id": str(exec.id),
                            "operadora": exec.processo.cliente.operadora.nome,
                            "tempo_horas": round(tempo_execucao, 1)
                        }
                    })
                
                # Falhas recentes (últimas 24 horas)
                limite_24h = datetime.now() - timedelta(hours=24)
                falhas_recentes = db.query(Execucao).filter(
                    and_(
                        Execucao.status_execucao == StatusExecucao.FALHOU.value,
                        Execucao.data_fim >= limite_24h
                    )
                ).count()
                
                if falhas_recentes > 5:  # Mais de 5 falhas em 24h
                    alertas.append({
                        "tipo": "MUITAS_FALHAS",
                        "severidade": "MEDIA",
                        "titulo": "Muitas falhas nas últimas 24 horas",
                        "descricao": f"{falhas_recentes} execuções falharam nas últimas 24 horas",
                        "data": datetime.now().isoformat(),
                        "dados": {
                            "total_falhas": falhas_recentes
                        }
                    })
                
                # Operadoras sem execuções recentes (últimos 7 dias)
                limite_7d = datetime.now() - timedelta(days=7)
                operadoras_inativas = db.query(Operadora)\
                    .filter(
                        and_(
                            Operadora.status_ativo == True,
                            Operadora.possui_rpa == True
                        )
                    ).all()
                
                for operadora in operadoras_inativas:
                    execucoes_recentes = db.query(Execucao)\
                        .join(Processo)\
                        .join(Cliente)\
                        .filter(
                            and_(
                                Cliente.operadora_id == operadora.id,
                                Execucao.data_inicio >= limite_7d
                            )
                        ).count()
                    
                    if execucoes_recentes == 0:
                        alertas.append({
                            "tipo": "OPERADORA_INATIVA",
                            "severidade": "BAIXA",
                            "titulo": "Operadora sem execuções recentes",
                            "descricao": f"Operadora {operadora.nome} não teve execuções nos últimos 7 dias",
                            "data": datetime.now().isoformat(),
                            "dados": {
                                "operadora_id": str(operadora.id),
                                "operadora_nome": operadora.nome
                            }
                        })
                
                # Ordenar alertas por severidade
                ordem_severidade = {"ALTA": 3, "MEDIA": 2, "BAIXA": 1}
                alertas.sort(key=lambda x: ordem_severidade.get(x["severidade"], 0), reverse=True)
                
                return {
                    "sucesso": True,
                    "alertas": alertas,
                    "total_alertas": len(alertas),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter alertas do sistema: {str(e)}")
            raise

    @staticmethod
    def obter_dados_completos_dashboard() -> Dict[str, Any]:
        """Obtém todos os dados do dashboard em uma única chamada"""
        try:
            # Combinar todos os métodos
            dados_principais = DashboardService.obter_dados_dashboard_principal()
            metricas_tempo_real = DashboardService.obter_metricas_tempo_real()
            relatorio_operadoras = DashboardService.obter_relatorio_operadoras()
            grafico_execucoes = DashboardService.obter_grafico_execucoes_tempo()
            alertas_sistema = DashboardService.obter_alertas_sistema()
            
            return {
                "sucesso": True,
                "dashboard_completo": {
                    "principal": dados_principais["dashboard"],
                    "tempo_real": metricas_tempo_real["tempo_real"],
                    "operadoras": relatorio_operadoras["relatorio_operadoras"],
                    "grafico_execucoes": grafico_execucoes["grafico_execucoes"],
                    "alertas": alertas_sistema["alertas"],
                    "timestamp_atualizacao": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter dados completos do dashboard: {str(e)}")
            raise