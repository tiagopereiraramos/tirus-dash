"""
Serviço de Manipulação de Clientes
Sistema RPA BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
"""

import uuid
import logging
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.database import get_db_session
from ..models.cliente import Cliente
from ..models.operadora import Operadora
from .hash_service import generate_hash_cad

logger = logging.getLogger(__name__)

class ClienteService:
    """Serviço para manipulação de clientes"""

    @staticmethod
    def criar_cliente(
        razao_social: str,
        nome_sat: str,
        cnpj: str,
        operadora_id: str,
        unidade: str,
        filtro: str = None,
        servico: str = None,
        dados_sat: str = None,
        site_emissao: str = None,
        login_portal: str = None,
        senha_portal: str = None,
        cpf: str = None
    ) -> Dict[str, Any]:
        """Cria um novo cliente"""
        try:
            with get_db_session() as db:
                # Verificar se operadora existe
                operadora = db.query(Operadora).filter(
                    and_(
                        Operadora.id == operadora_id,
                        Operadora.status_ativo == True
                    )
                ).first()
                
                if not operadora:
                    raise ValueError(f"Operadora {operadora_id} não encontrada ou inativa")
                
                # Gerar hash único
                hash_unico = generate_hash_cad(
                    nome_filtro=nome_sat,
                    operadora=operadora.nome,
                    servico=servico or "",
                    dados_sat=dados_sat or "",
                    filtro=filtro or "",
                    unidade=unidade
                )
                
                # Verificar unicidade
                cliente_existente = db.query(Cliente).filter(Cliente.hash_unico == hash_unico).first()
                if cliente_existente:
                    return {
                        "sucesso": False,
                        "mensagem": f"Cliente já existe com os mesmos parâmetros",
                        "cliente_id": str(cliente_existente.id),
                        "hash_existente": hash_unico
                    }
                
                # Criar cliente
                cliente = Cliente(
                    hash_unico=hash_unico,
                    razao_social=razao_social,
                    nome_sat=nome_sat,
                    cnpj=cnpj,
                    operadora_id=operadora_id,
                    filtro=filtro,
                    servico=servico,
                    dados_sat=dados_sat,
                    unidade=unidade,
                    site_emissao=site_emissao,
                    login_portal=login_portal,
                    senha_portal=senha_portal,
                    cpf=cpf
                )
                
                db.add(cliente)
                db.commit()
                db.refresh(cliente)
                
                logger.info(f"Cliente criado: {cliente.id} - {nome_sat}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Cliente criado com sucesso",
                    "cliente_id": str(cliente.id),
                    "hash_unico": hash_unico,
                    "nome_sat": nome_sat,
                    "operadora": operadora.nome
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {str(e)}")
            raise

    @staticmethod
    def atualizar_cliente(
        cliente_id: str,
        dados_atualizacao: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atualiza dados de um cliente"""
        try:
            with get_db_session() as db:
                cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
                
                if not cliente:
                    raise ValueError(f"Cliente {cliente_id} não encontrado")
                
                # Campos que podem ser atualizados
                campos_permitidos = [
                    'razao_social', 'filtro', 'servico', 'dados_sat',
                    'site_emissao', 'login_portal', 'senha_portal', 'cpf', 'status_ativo'
                ]
                
                # Aplicar atualizações
                for campo, valor in dados_atualizacao.items():
                    if campo in campos_permitidos and hasattr(cliente, campo):
                        setattr(cliente, campo, valor)
                
                # Se houve mudança em campos que afetam a hash, recalcular
                campos_hash = ['nome_sat', 'operadora_id', 'servico', 'dados_sat', 'filtro', 'unidade']
                if any(campo in dados_atualizacao for campo in campos_hash):
                    operadora = db.query(Operadora).filter(Operadora.id == cliente.operadora_id).first()
                    novo_hash = generate_hash_cad(
                        nome_filtro=cliente.nome_sat,
                        operadora=operadora.nome,
                        servico=cliente.servico or "",
                        dados_sat=cliente.dados_sat or "",
                        filtro=cliente.filtro or "",
                        unidade=cliente.unidade
                    )
                    
                    # Verificar se novo hash já existe em outro cliente
                    hash_existente = db.query(Cliente).filter(
                        and_(
                            Cliente.hash_unico == novo_hash,
                            Cliente.id != cliente_id
                        )
                    ).first()
                    
                    if hash_existente:
                        raise ValueError(f"Já existe outro cliente com esses parâmetros")
                    
                    cliente.hash_unico = novo_hash
                
                cliente.data_atualizacao = datetime.now()
                db.commit()
                
                logger.info(f"Cliente {cliente_id} atualizado")
                
                return {
                    "sucesso": True,
                    "mensagem": "Cliente atualizado com sucesso",
                    "cliente_id": cliente_id,
                    "hash_unico": cliente.hash_unico
                }
                
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {str(e)}")
            raise

    @staticmethod
    def buscar_clientes_com_filtros(
        operadora_id: str = None,
        ativo: bool = None,
        termo_busca: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Busca clientes com filtros avançados"""
        try:
            with get_db_session() as db:
                query = db.query(Cliente).join(Operadora)
                
                # Aplicar filtros
                if operadora_id:
                    query = query.filter(Cliente.operadora_id == operadora_id)
                
                if ativo is not None:
                    query = query.filter(Cliente.status_ativo == ativo)
                
                if termo_busca:
                    termo = f"%{termo_busca}%"
                    query = query.filter(
                        or_(
                            Cliente.razao_social.ilike(termo),
                            Cliente.nome_sat.ilike(termo),
                            Cliente.cnpj.ilike(termo),
                            Cliente.hash_unico.ilike(termo)
                        )
                    )
                
                # Contar total
                total = query.count()
                
                # Aplicar paginação
                clientes = query.offset(skip).limit(limit).all()
                
                # Formatar resultados
                resultados = []
                for cliente in clientes:
                    resultados.append({
                        "id": str(cliente.id),
                        "hash_unico": cliente.hash_unico,
                        "razao_social": cliente.razao_social,
                        "nome_sat": cliente.nome_sat,
                        "cnpj": cliente.cnpj,
                        "unidade": cliente.unidade,
                        "filtro": cliente.filtro,
                        "servico": cliente.servico,
                        "dados_sat": cliente.dados_sat,
                        "site_emissao": cliente.site_emissao,
                        "login_portal": cliente.login_portal,
                        "cpf": cliente.cpf,
                        "status_ativo": cliente.status_ativo,
                        "data_criacao": cliente.data_criacao.isoformat(),
                        "data_atualizacao": cliente.data_atualizacao.isoformat(),
                        "operadora": {
                            "id": str(cliente.operadora.id),
                            "nome": cliente.operadora.nome,
                            "codigo": cliente.operadora.codigo,
                            "possui_rpa": cliente.operadora.possui_rpa
                        }
                    })
                
                return {
                    "sucesso": True,
                    "clientes": resultados,
                    "total": total,
                    "pagina_atual": skip // limit + 1 if limit > 0 else 1,
                    "total_paginas": (total + limit - 1) // limit if limit > 0 else 1
                }
                
        except Exception as e:
            logger.error(f"Erro na busca de clientes: {str(e)}")
            raise

    @staticmethod
    def inicializar_clientes_bgtelecom() -> Dict[str, Any]:
        """Inicializa clientes padrão da BGTELECOM"""
        try:
            logger.info("Inicializando clientes BGTELECOM...")
            
            # Clientes já estão criados no banco, apenas retornamos sucesso
            with get_db_session() as db:
                total_clientes = db.query(Cliente).count()
                logger.info(f"Total de clientes no banco: {total_clientes}")
                
                return {
                    "sucesso": True,
                    "mensagem": f"Clientes BGTELECOM inicializados: {total_clientes} encontrados",
                    "total": total_clientes
                }
                
        except Exception as e:
            logger.error(f"Erro ao inicializar clientes BGTELECOM: {str(e)}")
            return {
                "sucesso": False,
                "erro": str(e)
            }

    @staticmethod
    def importar_clientes_csv(
        arquivo_csv: str,
        operadora_padrao_id: str = None,
        sobrescrever: bool = False
    ) -> Dict[str, Any]:
        """Importa clientes a partir de arquivo CSV"""
        try:
            # Ler CSV
            df = pd.read_csv(arquivo_csv)
            
            clientes_criados = 0
            clientes_existentes = 0
            clientes_atualizados = 0
            erros = []
            
            with get_db_session() as db:
                for _, row in df.iterrows():
                    try:
                        # Extrair dados do CSV
                        nome_sat = str(row.get('NOME SAT', '')).strip()
                        razao_social = str(row.get('RAZÃO SOCIAL', nome_sat)).strip()
                        cnpj = str(row.get('CNPJ', '')).strip()
                        operadora_nome = str(row.get('OPERADORA', '')).strip()
                        unidade = str(row.get('UNIDADE / FILTRO SAT', 'Principal')).strip()
                        
                        # Validar dados obrigatórios
                        if not nome_sat or not cnpj:
                            erros.append(f"Linha {_}: Nome SAT ou CNPJ em branco")
                            continue
                        
                        # Buscar operadora
                        operadora = None
                        if operadora_nome:
                            operadora = db.query(Operadora).filter(
                                Operadora.nome.ilike(f"%{operadora_nome}%")
                            ).first()
                        
                        if not operadora and operadora_padrao_id:
                            operadora = db.query(Operadora).filter(
                                Operadora.id == operadora_padrao_id
                            ).first()
                        
                        if not operadora:
                            erros.append(f"Linha {_}: Operadora '{operadora_nome}' não encontrada")
                            continue
                        
                        # Dados adicionais
                        filtro = str(row.get('FILTRO', '')).strip() or None
                        servico = str(row.get('SERVIÇO', 'Não especificado')).strip()
                        dados_sat = str(row.get('DADOS SAT', '')).strip() or None
                        site_emissao = str(row.get('SITE PARA EMISSÃO', '')).strip() or None
                        login_portal = str(row.get('LOGIN', '')).strip() or None
                        senha_portal = str(row.get('SENHA', '')).strip() or None
                        cpf = str(row.get('CPF', '')).strip() or None
                        
                        # Gerar hash
                        hash_unico = generate_hash_cad(
                            nome_filtro=nome_sat,
                            operadora=operadora.nome,
                            servico=servico,
                            dados_sat=dados_sat or "",
                            filtro=filtro or "",
                            unidade=unidade
                        )
                        
                        # Verificar se cliente já existe
                        cliente_existente = db.query(Cliente).filter(
                            Cliente.hash_unico == hash_unico
                        ).first()
                        
                        if cliente_existente:
                            if sobrescrever:
                                # Atualizar cliente existente
                                cliente_existente.razao_social = razao_social
                                cliente_existente.filtro = filtro
                                cliente_existente.servico = servico
                                cliente_existente.dados_sat = dados_sat
                                cliente_existente.site_emissao = site_emissao
                                cliente_existente.login_portal = login_portal
                                cliente_existente.senha_portal = senha_portal
                                cliente_existente.cpf = cpf
                                cliente_existente.data_atualizacao = datetime.now()
                                
                                clientes_atualizados += 1
                            else:
                                clientes_existentes += 1
                            continue
                        
                        # Criar novo cliente
                        cliente = Cliente(
                            hash_unico=hash_unico,
                            razao_social=razao_social,
                            nome_sat=nome_sat,
                            cnpj=cnpj,
                            operadora_id=operadora.id,
                            filtro=filtro,
                            servico=servico,
                            dados_sat=dados_sat,
                            unidade=unidade,
                            site_emissao=site_emissao,
                            login_portal=login_portal,
                            senha_portal=senha_portal,
                            cpf=cpf
                        )
                        
                        db.add(cliente)
                        clientes_criados += 1
                        
                    except Exception as e:
                        erros.append(f"Linha {_}: {str(e)}")
                        continue
                
                db.commit()
            
            logger.info(f"Importação CSV concluída: {clientes_criados} criados, {clientes_atualizados} atualizados")
            
            return {
                "sucesso": True,
                "mensagem": "Importação concluída",
                "clientes_criados": clientes_criados,
                "clientes_existentes": clientes_existentes,
                "clientes_atualizados": clientes_atualizados,
                "total_linhas": len(df),
                "erros": erros
            }
            
        except Exception as e:
            logger.error(f"Erro na importação CSV: {str(e)}")
            raise

    @staticmethod
    def obter_estatisticas_clientes() -> Dict[str, Any]:
        """Obtém estatísticas de clientes"""
        try:
            with get_db_session() as db:
                # Estatísticas gerais
                total_clientes = db.query(Cliente).count()
                clientes_ativos = db.query(Cliente).filter(Cliente.status_ativo == True).count()
                clientes_inativos = total_clientes - clientes_ativos
                
                # Estatísticas por operadora
                from sqlalchemy import func
                clientes_por_operadora = db.query(
                    Operadora.nome,
                    Operadora.codigo,
                    func.count(Cliente.id).label('total_clientes')
                ).join(Cliente).group_by(Operadora.id, Operadora.nome, Operadora.codigo).all()
                
                estatisticas_operadora = []
                for item in clientes_por_operadora:
                    estatisticas_operadora.append({
                        "operadora": item.nome,
                        "codigo": item.codigo,
                        "total_clientes": item.total_clientes
                    })
                
                return {
                    "sucesso": True,
                    "estatisticas": {
                        "total_clientes": total_clientes,
                        "clientes_ativos": clientes_ativos,
                        "clientes_inativos": clientes_inativos,
                        "distribuicao_operadoras": estatisticas_operadora
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de clientes: {str(e)}")
            raise

    @staticmethod
    def deletar_cliente(cliente_id: str, forcar: bool = False) -> Dict[str, Any]:
        """Deleta um cliente (com validações de segurança)"""
        try:
            with get_db_session() as db:
                cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
                
                if not cliente:
                    raise ValueError(f"Cliente {cliente_id} não encontrado")
                
                # Verificar se tem processos associados
                from ..models.processo import Processo
                processos_associados = db.query(Processo).filter(
                    Processo.cliente_id == cliente_id
                ).count()
                
                if processos_associados > 0 and not forcar:
                    raise ValueError(f"Cliente possui {processos_associados} processos associados. Use forcar=True para deletar")
                
                # Se forçando, deletar processos primeiro
                if forcar and processos_associados > 0:
                    processos = db.query(Processo).filter(Processo.cliente_id == cliente_id).all()
                    for processo in processos:
                        # Deletar execuções do processo
                        from ..models.processo import Execucao
                        execucoes = db.query(Execucao).filter(Execucao.processo_id == processo.id).all()
                        for execucao in execucoes:
                            db.delete(execucao)
                        
                        # Deletar processo
                        db.delete(processo)
                
                # Deletar cliente
                db.delete(cliente)
                db.commit()
                
                logger.info(f"Cliente {cliente_id} deletado com sucesso")
                
                return {
                    "sucesso": True,
                    "mensagem": "Cliente deletado com sucesso",
                    "cliente_id": cliente_id,
                    "processos_deletados": processos_associados if forcar else 0
                }
                
        except Exception as e:
            logger.error(f"Erro ao deletar cliente: {str(e)}")
            raise