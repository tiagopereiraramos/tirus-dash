"""
Serviço de Manipulação de Processos
Sistema RPA BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.database import get_db_session
from ..models.processo import Processo, StatusProcesso
from ..models.cliente import Cliente
from ..models.operadora import Operadora
from ..models.execucao import Execucao, StatusExecucao, TipoExecucao

logger = logging.getLogger(__name__)

class ProcessoService:
    """Serviço para manipulação de processos"""

    @staticmethod
    def criar_processo_individual(
        cliente_id: str,
        mes_ano: str,
        criado_automaticamente: bool = True,
        observacoes: str = None
    ) -> Dict[str, Any]:
        """Cria um processo individual"""
        try:
            with get_db_session() as db:
                # Verificar se cliente existe
                cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
                if not cliente:
                    raise ValueError(f"Cliente {cliente_id} não encontrado")
                
                # Verificar unicidade
                processo_existente = db.query(Processo).filter(
                    and_(
                        Processo.cliente_id == cliente_id,
                        Processo.mes_ano == mes_ano
                    )
                ).first()
                
                if processo_existente:
                    return {
                        "sucesso": False,
                        "mensagem": f"Processo já existe para cliente {cliente.nome_sat} no período {mes_ano}",
                        "processo_id": str(processo_existente.id)
                    }
                
                # Criar processo
                processo = Processo(
                    cliente_id=cliente_id,
                    mes_ano=mes_ano,
                    status_processo=StatusProcesso.AGUARDANDO_DOWNLOAD.value,
                    criado_automaticamente=criado_automaticamente,
                    observacoes=observacoes
                )
                
                db.add(processo)
                db.commit()
                db.refresh(processo)
                
                logger.info(f"Processo criado: {processo.id} para cliente {cliente.nome_sat}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Processo criado com sucesso",
                    "processo_id": str(processo.id),
                    "cliente_nome": cliente.nome_sat,
                    "operadora": cliente.operadora.nome,
                    "mes_ano": mes_ano
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar processo: {str(e)}")
            raise

    @staticmethod
    def criar_processos_em_massa(
        mes_ano: str,
        operadora_id: str = None,
        apenas_ativos: bool = True
    ) -> Dict[str, Any]:
        """Cria processos em massa para um período específico"""
        try:
            with get_db_session() as db:
                # Filtrar clientes
                query = db.query(Cliente)
                
                if apenas_ativos:
                    query = query.filter(Cliente.status_ativo == True)
                
                if operadora_id:
                    query = query.filter(Cliente.operadora_id == operadora_id)
                
                clientes = query.all()
                
                processos_criados = 0
                processos_existentes = 0
                erros = []
                
                for cliente in clientes:
                    try:
                        # Verificar se processo já existe
                        processo_existente = db.query(Processo).filter(
                            and_(
                                Processo.cliente_id == cliente.id,
                                Processo.mes_ano == mes_ano
                            )
                        ).first()
                        
                        if processo_existente:
                            processos_existentes += 1
                            continue
                        
                        # Criar processo
                        processo = Processo(
                            cliente_id=cliente.id,
                            mes_ano=mes_ano,
                            status_processo=StatusProcesso.AGUARDANDO_DOWNLOAD.value,
                            criado_automaticamente=True
                        )
                        
                        db.add(processo)
                        processos_criados += 1
                        
                    except Exception as e:
                        erros.append(f"Cliente {cliente.nome_sat}: {str(e)}")
                        continue
                
                db.commit()
                
                logger.info(f"Criação em massa concluída: {processos_criados} criados, {processos_existentes} já existiam")
                
                return {
                    "sucesso": True,
                    "mensagem": "Criação em massa concluída",
                    "processos_criados": processos_criados,
                    "processos_existentes": processos_existentes,
                    "total_clientes": len(clientes),
                    "erros": erros,
                    "mes_ano": mes_ano
                }
                
        except Exception as e:
            logger.error(f"Erro na criação em massa: {str(e)}")
            raise

    @staticmethod
    def atualizar_status_processo(
        processo_id: str,
        novo_status: StatusProcesso,
        observacoes: str = None,
        dados_adicionais: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Atualiza status de um processo"""
        try:
            with get_db_session() as db:
                processo = db.query(Processo).filter(Processo.id == processo_id).first()
                
                if not processo:
                    raise ValueError(f"Processo {processo_id} não encontrado")
                
                status_anterior = processo.status_processo
                processo.status_processo = novo_status.value
                processo.data_atualizacao = datetime.now()
                
                if observacoes:
                    processo.observacoes = observacoes
                
                # Dados específicos baseados no status
                if dados_adicionais:
                    if "caminho_s3_fatura" in dados_adicionais:
                        processo.caminho_s3_fatura = dados_adicionais["caminho_s3_fatura"]
                    if "valor_fatura" in dados_adicionais:
                        processo.valor_fatura = dados_adicionais["valor_fatura"]
                    if "data_vencimento" in dados_adicionais:
                        processo.data_vencimento = dados_adicionais["data_vencimento"]
                    if "aprovado_por_usuario_id" in dados_adicionais:
                        processo.aprovado_por_usuario_id = dados_adicionais["aprovado_por_usuario_id"]
                        processo.data_aprovacao = datetime.now()
                    if "enviado_para_sat" in dados_adicionais:
                        processo.enviado_para_sat = dados_adicionais["enviado_para_sat"]
                        if dados_adicionais["enviado_para_sat"]:
                            processo.data_envio_sat = datetime.now()
                
                db.commit()
                
                logger.info(f"Status do processo {processo_id} alterado de {status_anterior} para {novo_status.value}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Status atualizado com sucesso",
                    "processo_id": processo_id,
                    "status_anterior": status_anterior,
                    "status_atual": novo_status.value
                }
                
        except Exception as e:
            logger.error(f"Erro ao atualizar status do processo: {str(e)}")
            raise

    @staticmethod
    def buscar_processos_com_filtros(
        mes_ano: str = None,
        status: StatusProcesso = None,
        operadora_id: str = None,
        cliente_id: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Busca processos com filtros avançados"""
        try:
            with get_db_session() as db:
                query = db.query(Processo).join(Cliente).join(Operadora)
                
                # Aplicar filtros
                if mes_ano:
                    query = query.filter(Processo.mes_ano == mes_ano)
                
                if status:
                    query = query.filter(Processo.status_processo == status.value)
                
                if operadora_id:
                    query = query.filter(Cliente.operadora_id == operadora_id)
                
                if cliente_id:
                    query = query.filter(Processo.cliente_id == cliente_id)
                
                # Contar total
                total = query.count()
                
                # Aplicar paginação
                processos = query.offset(skip).limit(limit).all()
                
                # Formatar resultados
                resultados = []
                for processo in processos:
                    resultados.append({
                        "id": str(processo.id),
                        "mes_ano": processo.mes_ano,
                        "status_processo": processo.status_processo,
                        "data_criacao": processo.data_criacao.isoformat(),
                        "data_atualizacao": processo.data_atualizacao.isoformat(),
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
                        "valor_fatura": float(processo.valor_fatura) if processo.valor_fatura else None,
                        "data_vencimento": processo.data_vencimento.isoformat() if processo.data_vencimento else None,
                        "enviado_para_sat": processo.enviado_para_sat,
                        "data_envio_sat": processo.data_envio_sat.isoformat() if processo.data_envio_sat else None,
                        "observacoes": processo.observacoes
                    })
                
                return {
                    "sucesso": True,
                    "processos": resultados,
                    "total": total,
                    "pagina_atual": skip // limit + 1 if limit > 0 else 1,
                    "total_paginas": (total + limit - 1) // limit if limit > 0 else 1
                }
                
        except Exception as e:
            logger.error(f"Erro na busca de processos: {str(e)}")
            raise

    @staticmethod
    def obter_estatisticas_processos(
        mes_ano: str = None,
        operadora_id: str = None
    ) -> Dict[str, Any]:
        """Obtém estatísticas de processos"""
        try:
            with get_db_session() as db:
                query = db.query(Processo).join(Cliente)
                
                if mes_ano:
                    query = query.filter(Processo.mes_ano == mes_ano)
                
                if operadora_id:
                    query = query.filter(Cliente.operadora_id == operadora_id)
                
                # Contar por status
                estatisticas_status = {}
                for status in StatusProcesso:
                    count = query.filter(Processo.status_processo == status.value).count()
                    estatisticas_status[status.value] = count
                
                # Estatísticas gerais
                total_processos = query.count()
                processos_com_fatura = query.filter(Processo.caminho_s3_fatura.isnot(None)).count()
                processos_enviados_sat = query.filter(Processo.enviado_para_sat == True).count()
                
                # Valor total das faturas
                from sqlalchemy import func
                valor_total = db.query(func.sum(Processo.valor_fatura)).scalar() or 0
                
                return {
                    "sucesso": True,
                    "estatisticas": {
                        "total_processos": total_processos,
                        "processos_com_fatura": processos_com_fatura,
                        "processos_enviados_sat": processos_enviados_sat,
                        "valor_total_faturas": float(valor_total),
                        "distribuicao_status": estatisticas_status
                    },
                    "periodo": mes_ano or "todos",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            raise

    @staticmethod
    def deletar_processo(processo_id: str, forcar: bool = False) -> Dict[str, Any]:
        """Deleta um processo (com validações de segurança)"""
        try:
            with get_db_session() as db:
                processo = db.query(Processo).filter(Processo.id == processo_id).first()
                
                if not processo:
                    raise ValueError(f"Processo {processo_id} não encontrado")
                
                # Validações de segurança
                if not forcar:
                    if processo.status_processo in [StatusProcesso.ENVIADA_SAT.value, StatusProcesso.APROVADA.value]:
                        raise ValueError("Não é possível deletar processo aprovado ou enviado para SAT")
                    
                    if processo.enviado_para_sat:
                        raise ValueError("Não é possível deletar processo já enviado para SAT")
                
                # Deletar execuções relacionadas primeiro
                execucoes = db.query(Execucao).filter(Execucao.processo_id == processo_id).all()
                for execucao in execucoes:
                    db.delete(execucao)
                
                # Deletar processo
                db.delete(processo)
                db.commit()
                
                logger.info(f"Processo {processo_id} deletado com sucesso")
                
                return {
                    "sucesso": True,
                    "mensagem": "Processo deletado com sucesso",
                    "processo_id": processo_id,
                    "execucoes_deletadas": len(execucoes)
                }
                
        except Exception as e:
            logger.error(f"Erro ao deletar processo: {str(e)}")
            raise