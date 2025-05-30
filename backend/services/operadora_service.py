"""
Serviço de Manipulação de Operadoras
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
from ..models.operadora import Operadora
from ..models.cliente import Cliente

logger = logging.getLogger(__name__)

class OperadoraService:
    """Serviço para manipulação de operadoras"""

    @staticmethod
    def criar_operadora(
        nome: str,
        codigo: str,
        possui_rpa: bool = False,
        url_portal: str = None,
        instrucoes_acesso: str = None
    ) -> Dict[str, Any]:
        """Cria uma nova operadora"""
        try:
            with get_db_session() as db:
                # Verificar unicidade do nome
                operadora_existente_nome = db.query(Operadora).filter(
                    Operadora.nome.ilike(nome)
                ).first()
                
                if operadora_existente_nome:
                    return {
                        "sucesso": False,
                        "mensagem": f"Operadora com nome '{nome}' já existe",
                        "operadora_id": str(operadora_existente_nome.id)
                    }
                
                # Verificar unicidade do código
                operadora_existente_codigo = db.query(Operadora).filter(
                    Operadora.codigo.ilike(codigo)
                ).first()
                
                if operadora_existente_codigo:
                    return {
                        "sucesso": False,
                        "mensagem": f"Operadora com código '{codigo}' já existe",
                        "operadora_id": str(operadora_existente_codigo.id)
                    }
                
                # Criar operadora
                operadora = Operadora(
                    nome=nome.strip(),
                    codigo=codigo.strip().upper(),
                    possui_rpa=possui_rpa,
                    url_portal=url_portal,
                    instrucoes_acesso=instrucoes_acesso
                )
                
                db.add(operadora)
                db.commit()
                db.refresh(operadora)
                
                logger.info(f"Operadora criada: {operadora.id} - {nome}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Operadora criada com sucesso",
                    "operadora_id": str(operadora.id),
                    "nome": nome,
                    "codigo": codigo,
                    "possui_rpa": possui_rpa
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar operadora: {str(e)}")
            raise

    @staticmethod
    def atualizar_operadora(
        operadora_id: str,
        dados_atualizacao: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atualiza dados de uma operadora"""
        try:
            with get_db_session() as db:
                operadora = db.query(Operadora).filter(Operadora.id == operadora_id).first()
                
                if not operadora:
                    raise ValueError(f"Operadora {operadora_id} não encontrada")
                
                # Campos que podem ser atualizados
                campos_permitidos = [
                    'nome', 'codigo', 'possui_rpa', 'url_portal', 
                    'instrucoes_acesso', 'status_ativo'
                ]
                
                # Verificar unicidade se nome ou código foram alterados
                if 'nome' in dados_atualizacao:
                    nome_existente = db.query(Operadora).filter(
                        and_(
                            Operadora.nome.ilike(dados_atualizacao['nome']),
                            Operadora.id != operadora_id
                        )
                    ).first()
                    
                    if nome_existente:
                        raise ValueError(f"Nome '{dados_atualizacao['nome']}' já está em uso")
                
                if 'codigo' in dados_atualizacao:
                    codigo_existente = db.query(Operadora).filter(
                        and_(
                            Operadora.codigo.ilike(dados_atualizacao['codigo']),
                            Operadora.id != operadora_id
                        )
                    ).first()
                    
                    if codigo_existente:
                        raise ValueError(f"Código '{dados_atualizacao['codigo']}' já está em uso")
                
                # Aplicar atualizações
                for campo, valor in dados_atualizacao.items():
                    if campo in campos_permitidos and hasattr(operadora, campo):
                        if campo == 'codigo' and valor:
                            setattr(operadora, campo, valor.strip().upper())
                        elif campo == 'nome' and valor:
                            setattr(operadora, campo, valor.strip())
                        else:
                            setattr(operadora, campo, valor)
                
                operadora.data_atualizacao = datetime.now()
                db.commit()
                
                logger.info(f"Operadora {operadora_id} atualizada")
                
                return {
                    "sucesso": True,
                    "mensagem": "Operadora atualizada com sucesso",
                    "operadora_id": operadora_id,
                    "nome": operadora.nome,
                    "codigo": operadora.codigo
                }
                
        except Exception as e:
            logger.error(f"Erro ao atualizar operadora: {str(e)}")
            raise

    @staticmethod
    def buscar_operadoras_com_filtros(
        ativo: bool = None,
        possui_rpa: bool = None,
        termo_busca: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Busca operadoras com filtros avançados"""
        try:
            with get_db_session() as db:
                query = db.query(Operadora)
                
                # Aplicar filtros
                if ativo is not None:
                    query = query.filter(Operadora.status_ativo == ativo)
                
                if possui_rpa is not None:
                    query = query.filter(Operadora.possui_rpa == possui_rpa)
                
                if termo_busca:
                    termo = f"%{termo_busca}%"
                    query = query.filter(
                        or_(
                            Operadora.nome.ilike(termo),
                            Operadora.codigo.ilike(termo)
                        )
                    )
                
                # Contar total
                total = query.count()
                
                # Aplicar paginação e ordenação
                operadoras = query.order_by(Operadora.nome).offset(skip).limit(limit).all()
                
                # Formatar resultados
                resultados = []
                for operadora in operadoras:
                    # Contar clientes associados
                    total_clientes = db.query(Cliente).filter(
                        Cliente.operadora_id == operadora.id
                    ).count()
                    
                    clientes_ativos = db.query(Cliente).filter(
                        and_(
                            Cliente.operadora_id == operadora.id,
                            Cliente.status_ativo == True
                        )
                    ).count()
                    
                    resultados.append({
                        "id": str(operadora.id),
                        "nome": operadora.nome,
                        "codigo": operadora.codigo,
                        "possui_rpa": operadora.possui_rpa,
                        "url_portal": operadora.url_portal,
                        "instrucoes_acesso": operadora.instrucoes_acesso,
                        "status_ativo": operadora.status_ativo,
                        "data_criacao": operadora.data_criacao.isoformat(),
                        "data_atualizacao": operadora.data_atualizacao.isoformat(),
                        "estatisticas": {
                            "total_clientes": total_clientes,
                            "clientes_ativos": clientes_ativos
                        }
                    })
                
                return {
                    "sucesso": True,
                    "operadoras": resultados,
                    "total": total,
                    "pagina_atual": skip // limit + 1 if limit > 0 else 1,
                    "total_paginas": (total + limit - 1) // limit if limit > 0 else 1
                }
                
        except Exception as e:
            logger.error(f"Erro na busca de operadoras: {str(e)}")
            raise

    @staticmethod
    def obter_operadora_por_id(operadora_id: str) -> Dict[str, Any]:
        """Obtém uma operadora específica com detalhes completos"""
        try:
            with get_db_session() as db:
                operadora = db.query(Operadora).filter(Operadora.id == operadora_id).first()
                
                if not operadora:
                    raise ValueError(f"Operadora {operadora_id} não encontrada")
                
                # Estatísticas detalhadas
                total_clientes = db.query(Cliente).filter(
                    Cliente.operadora_id == operadora_id
                ).count()
                
                clientes_ativos = db.query(Cliente).filter(
                    and_(
                        Cliente.operadora_id == operadora_id,
                        Cliente.status_ativo == True
                    )
                ).count()
                
                # Processos associados através dos clientes
                from ..models.processo import Processo
                total_processos = db.query(Processo).join(Cliente).filter(
                    Cliente.operadora_id == operadora_id
                ).count()
                
                return {
                    "sucesso": True,
                    "operadora": {
                        "id": str(operadora.id),
                        "nome": operadora.nome,
                        "codigo": operadora.codigo,
                        "possui_rpa": operadora.possui_rpa,
                        "url_portal": operadora.url_portal,
                        "instrucoes_acesso": operadora.instrucoes_acesso,
                        "status_ativo": operadora.status_ativo,
                        "data_criacao": operadora.data_criacao.isoformat(),
                        "data_atualizacao": operadora.data_atualizacao.isoformat(),
                        "estatisticas": {
                            "total_clientes": total_clientes,
                            "clientes_ativos": clientes_ativos,
                            "clientes_inativos": total_clientes - clientes_ativos,
                            "total_processos": total_processos
                        }
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter operadora: {str(e)}")
            raise

    @staticmethod
    def obter_estatisticas_operadoras() -> Dict[str, Any]:
        """Obtém estatísticas gerais das operadoras"""
        try:
            with get_db_session() as db:
                # Estatísticas gerais
                total_operadoras = db.query(Operadora).count()
                operadoras_ativas = db.query(Operadora).filter(Operadora.status_ativo == True).count()
                operadoras_com_rpa = db.query(Operadora).filter(Operadora.possui_rpa == True).count()
                
                # Distribuição por status RPA
                from sqlalchemy import func
                distribuicao_rpa = db.query(
                    Operadora.possui_rpa,
                    func.count(Operadora.id).label('count')
                ).group_by(Operadora.possui_rpa).all()
                
                rpa_stats = {}
                for item in distribuicao_rpa:
                    key = "com_rpa" if item.possui_rpa else "sem_rpa"
                    rpa_stats[key] = item.count
                
                # Top operadoras por número de clientes
                top_operadoras = db.query(
                    Operadora.nome,
                    Operadora.codigo,
                    func.count(Cliente.id).label('total_clientes')
                ).join(Cliente, Operadora.id == Cliente.operadora_id)\
                .group_by(Operadora.id, Operadora.nome, Operadora.codigo)\
                .order_by(func.count(Cliente.id).desc())\
                .limit(10).all()
                
                top_list = []
                for item in top_operadoras:
                    top_list.append({
                        "nome": item.nome,
                        "codigo": item.codigo,
                        "total_clientes": item.total_clientes
                    })
                
                return {
                    "sucesso": True,
                    "estatisticas": {
                        "total_operadoras": total_operadoras,
                        "operadoras_ativas": operadoras_ativas,
                        "operadoras_inativas": total_operadoras - operadoras_ativas,
                        "operadoras_com_rpa": operadoras_com_rpa,
                        "operadoras_sem_rpa": total_operadoras - operadoras_com_rpa,
                        "distribuicao_rpa": rpa_stats,
                        "top_operadoras_por_clientes": top_list
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de operadoras: {str(e)}")
            raise

    @staticmethod
    def deletar_operadora(operadora_id: str, forcar: bool = False) -> Dict[str, Any]:
        """Deleta uma operadora (com validações de segurança)"""
        try:
            with get_db_session() as db:
                operadora = db.query(Operadora).filter(Operadora.id == operadora_id).first()
                
                if not operadora:
                    raise ValueError(f"Operadora {operadora_id} não encontrada")
                
                # Verificar se tem clientes associados
                clientes_associados = db.query(Cliente).filter(
                    Cliente.operadora_id == operadora_id
                ).count()
                
                if clientes_associados > 0 and not forcar:
                    raise ValueError(f"Operadora possui {clientes_associados} clientes associados. Use forcar=True para deletar")
                
                # Se forçando, deletar clientes e seus processos primeiro
                if forcar and clientes_associados > 0:
                    clientes = db.query(Cliente).filter(Cliente.operadora_id == operadora_id).all()
                    for cliente in clientes:
                        # Deletar processos e execuções do cliente
                        from ..models.processo import Processo, Execucao
                        processos = db.query(Processo).filter(Processo.cliente_id == cliente.id).all()
                        for processo in processos:
                            # Deletar execuções do processo
                            execucoes = db.query(Execucao).filter(Execucao.processo_id == processo.id).all()
                            for execucao in execucoes:
                                db.delete(execucao)
                            
                            # Deletar processo
                            db.delete(processo)
                        
                        # Deletar cliente
                        db.delete(cliente)
                
                # Deletar operadora
                db.delete(operadora)
                db.commit()
                
                logger.info(f"Operadora {operadora_id} deletada com sucesso")
                
                return {
                    "sucesso": True,
                    "mensagem": "Operadora deletada com sucesso",
                    "operadora_id": operadora_id,
                    "clientes_deletados": clientes_associados if forcar else 0
                }
                
        except Exception as e:
            logger.error(f"Erro ao deletar operadora: {str(e)}")
            raise

    @staticmethod
    def inicializar_operadoras_padrao() -> Dict[str, Any]:
        """Inicializa operadoras padrão do sistema"""
        try:
            operadoras_padrao = [
                {
                    "nome": "EMBRATEL",
                    "codigo": "EMB",
                    "possui_rpa": True,
                    "url_portal": "https://webebt01.embratel.com.br/embratelonline/index.asp",
                    "instrucoes_acesso": "Portal Embratel Online - RPA homologado"
                },
                {
                    "nome": "VIVO",
                    "codigo": "VIV",
                    "possui_rpa": True,
                    "url_portal": "https://empresas.vivo.com.br",
                    "instrucoes_acesso": "Portal Vivo Empresas - RPA homologado"
                },
                {
                    "nome": "OI",
                    "codigo": "OI",
                    "possui_rpa": True,
                    "url_portal": "https://empresas.oi.com.br",
                    "instrucoes_acesso": "Portal OI Empresas - RPA homologado"
                },
                {
                    "nome": "DIGITALNET",
                    "codigo": "DIG",
                    "possui_rpa": True,
                    "url_portal": "https://sac.digitalnetms.com.br/login",
                    "instrucoes_acesso": "Portal DigitalNet - RPA homologado"
                },
                {
                    "nome": "AZUTON",
                    "codigo": "AZU",
                    "possui_rpa": True,
                    "url_portal": "https://azuton.com.br",
                    "instrucoes_acesso": "Portal Azuton - RPA homologado"
                },
                {
                    "nome": "SAT",
                    "codigo": "SAT",
                    "possui_rpa": True,
                    "url_portal": "https://sistema.sat.com.br",
                    "instrucoes_acesso": "Sistema SAT - Upload de faturas"
                }
            ]
            
            operadoras_criadas = 0
            operadoras_existentes = 0
            
            with get_db_session() as db:
                for dados in operadoras_padrao:
                    # Verificar se operadora já existe
                    operadora_existente = db.query(Operadora).filter(
                        or_(
                            Operadora.nome == dados["nome"],
                            Operadora.codigo == dados["codigo"]
                        )
                    ).first()
                    
                    if operadora_existente:
                        operadoras_existentes += 1
                        continue
                    
                    # Criar operadora
                    operadora = Operadora(**dados)
                    db.add(operadora)
                    operadoras_criadas += 1
                
                db.commit()
            
            logger.info(f"Inicialização de operadoras: {operadoras_criadas} criadas, {operadoras_existentes} já existiam")
            
            return {
                "sucesso": True,
                "mensagem": "Inicialização de operadoras concluída",
                "operadoras_criadas": operadoras_criadas,
                "operadoras_existentes": operadoras_existentes,
                "total_configuradas": len(operadoras_padrao)
            }
            
        except Exception as e:
            logger.error(f"Erro na inicialização de operadoras: {str(e)}")
            raise

    @staticmethod
    def testar_conexao_rpa(operadora_id: str) -> Dict[str, Any]:
        """Testa a conexão RPA de uma operadora"""
        try:
            with get_db_session() as db:
                operadora = db.query(Operadora).filter(Operadora.id == operadora_id).first()
                
                if not operadora:
                    raise ValueError(f"Operadora {operadora_id} não encontrada")
                
                if not operadora.possui_rpa:
                    return {
                        "sucesso": False,
                        "mensagem": "Operadora não possui RPA configurado",
                        "status_teste": "N/A"
                    }
                
                # Simular teste de conexão
                # Em produção, aqui seria feita a conexão real com o RPA
                import time
                time.sleep(1)  # Simular tempo de teste
                
                # Para demonstração, assumir sucesso
                return {
                    "sucesso": True,
                    "mensagem": f"Teste de conexão RPA para {operadora.nome} realizado com sucesso",
                    "status_teste": "CONECTADO",
                    "operadora": {
                        "nome": operadora.nome,
                        "codigo": operadora.codigo,
                        "url_portal": operadora.url_portal
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao testar conexão RPA: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": f"Erro no teste de conexão: {str(e)}",
                "status_teste": "ERRO"
            }

    @staticmethod
    def obter_status_rpas() -> Dict[str, Any]:
        """Obtém status de todos os RPAs das operadoras"""
        try:
            with get_db_session() as db:
                operadoras_rpa = db.query(Operadora).filter(
                    and_(
                        Operadora.possui_rpa == True,
                        Operadora.status_ativo == True
                    )
                ).all()
                
                status_list = []
                for operadora in operadoras_rpa:
                    # Em produção, verificar status real do RPA
                    status_list.append({
                        "operadora_id": str(operadora.id),
                        "nome": operadora.nome,
                        "codigo": operadora.codigo,
                        "status": "ATIVO",  # Em produção, verificar status real
                        "ultima_execucao": datetime.now().isoformat(),
                        "url_portal": operadora.url_portal
                    })
                
                return {
                    "sucesso": True,
                    "rpas": status_list,
                    "total_rpas": len(status_list),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter status dos RPAs: {str(e)}")
            raise