"""
Conexão com PostgreSQL usando dados reais da BGTELECOM
Sistema RPA BGTELECOM - Backend Completo
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class PostgreSQLConnection:
    """Classe para gerenciar conexões PostgreSQL"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise Exception("DATABASE_URL não encontrada nas variáveis de ambiente")
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões PostgreSQL"""
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Executa query SELECT e retorna resultados"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
    
    def execute_insert(self, query: str, params: tuple = None) -> Optional[int]:
        """Executa INSERT e retorna ID"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                if "RETURNING" in query.upper():
                    return cursor.fetchone()[0]
                return cursor.rowcount
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Executa UPDATE e retorna linhas afetadas"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount

# Instância global da conexão
db = PostgreSQLConnection()

# ===== OPERAÇÕES CRUD COM DADOS REAIS =====

class OperadoraService:
    """Serviço para operadoras usando PostgreSQL"""
    
    @staticmethod
    def listar_operadoras(ativo: bool = None, possui_rpa: bool = None):
        """Lista operadoras com filtros"""
        query = "SELECT * FROM operadoras WHERE 1=1"
        params = []
        
        if ativo is not None:
            query += " AND status_ativo = %s"
            params.append(ativo)
        
        if possui_rpa is not None:
            query += " AND possui_rpa = %s"
            params.append(possui_rpa)
        
        query += " ORDER BY nome"
        
        operadoras = db.execute_query(query, tuple(params))
        return {
            "sucesso": True,
            "operadoras": operadoras,
            "total": len(operadoras)
        }
    
    @staticmethod
    def obter_status_rpas():
        """Obtém status de todos os RPAs"""
        query = """
        SELECT 
            o.id,
            o.nome,
            o.codigo,
            o.possui_rpa,
            COUNT(e.id) as execucoes_ativas
        FROM operadoras o
        LEFT JOIN clientes c ON c.operadora_id = o.id
        LEFT JOIN processos p ON p.cliente_id = c.id
        LEFT JOIN execucoes e ON e.processo_id = p.id AND e.status_execucao = 'EXECUTANDO'
        WHERE o.status_ativo = true
        GROUP BY o.id, o.nome, o.codigo, o.possui_rpa
        ORDER BY o.nome
        """
        
        operadoras = db.execute_query(query)
        
        status_por_operadora = {}
        for op in operadoras:
            status_por_operadora[op['codigo']] = {
                "operadora": op['nome'],
                "codigo": op['codigo'],
                "possui_rpa": op['possui_rpa'],
                "execucoes_ativas": op['execucoes_ativas'],
                "disponivel": op['possui_rpa'] and op['execucoes_ativas'] == 0
            }
        
        return {
            "status": "success",
            "operadoras": status_por_operadora,
            "timestamp": datetime.now().isoformat()
        }

class ClienteService:
    """Serviço para clientes usando PostgreSQL"""
    
    @staticmethod
    def listar_clientes(operadora_id: int = None, ativo: bool = None, termo_busca: str = None):
        """Lista clientes com filtros"""
        query = """
        SELECT 
            c.*,
            o.nome as operadora_nome,
            o.codigo as operadora_codigo
        FROM clientes c
        JOIN operadoras o ON c.operadora_id = o.id
        WHERE 1=1
        """
        params = []
        
        if operadora_id:
            query += " AND c.operadora_id = %s"
            params.append(operadora_id)
        
        if ativo is not None:
            query += " AND c.status_ativo = %s"
            params.append(ativo)
        
        if termo_busca:
            query += " AND (c.nome_sat ILIKE %s OR c.razao_social ILIKE %s)"
            params.extend([f"%{termo_busca}%", f"%{termo_busca}%"])
        
        query += " ORDER BY c.nome_sat"
        
        clientes = db.execute_query(query, tuple(params))
        return {
            "sucesso": True,
            "clientes": clientes,
            "total": len(clientes)
        }

class ProcessoService:
    """Serviço para processos usando PostgreSQL"""
    
    @staticmethod
    def listar_processos(mes_ano: str = None, status: str = None, operadora_id: int = None):
        """Lista processos com filtros"""
        query = """
        SELECT 
            p.*,
            c.nome_sat,
            c.razao_social,
            o.nome as operadora_nome,
            o.codigo as operadora_codigo
        FROM processos p
        JOIN clientes c ON p.cliente_id = c.id
        JOIN operadoras o ON c.operadora_id = o.id
        WHERE 1=1
        """
        params = []
        
        if mes_ano:
            query += " AND p.mes_ano = %s"
            params.append(mes_ano)
        
        if status:
            query += " AND p.status_processo = %s"
            params.append(status)
        
        if operadora_id:
            query += " AND o.id = %s"
            params.append(operadora_id)
        
        query += " ORDER BY p.created_at DESC"
        
        processos = db.execute_query(query, tuple(params))
        return {
            "sucesso": True,
            "processos": processos,
            "total": len(processos)
        }
    
    @staticmethod
    def aprovar_processo(processo_id: int, aprovado_por: str, observacoes: str = None):
        """Aprova um processo"""
        query = """
        UPDATE processos 
        SET status_processo = 'APROVADA',
            data_aprovacao = NOW(),
            aprovado_por = %s,
            observacoes = COALESCE(%s, observacoes)
        WHERE id = %s
        RETURNING id
        """
        
        resultado = db.execute_insert(query, (aprovado_por, observacoes, processo_id))
        
        if resultado:
            return {
                "sucesso": True,
                "mensagem": "Processo aprovado com sucesso",
                "processo_id": processo_id
            }
        else:
            return {
                "sucesso": False,
                "mensagem": "Processo não encontrado"
            }
    
    @staticmethod
    def rejeitar_processo(processo_id: int, motivo: str):
        """Rejeita um processo"""
        query = """
        UPDATE processos 
        SET status_processo = 'REJEITADA',
            data_rejeicao = NOW(),
            motivo_rejeicao = %s
        WHERE id = %s
        RETURNING id
        """
        
        resultado = db.execute_insert(query, (motivo, processo_id))
        
        if resultado:
            return {
                "sucesso": True,
                "mensagem": "Processo rejeitado com sucesso",
                "processo_id": processo_id
            }
        else:
            return {
                "sucesso": False,
                "mensagem": "Processo não encontrado"
            }

class ExecucaoService:
    """Serviço para execuções usando PostgreSQL"""
    
    @staticmethod
    def listar_execucoes(status: str = None, operadora_codigo: str = None):
        """Lista execuções com filtros"""
        query = """
        SELECT 
            e.*,
            p.mes_ano,
            c.nome_sat,
            o.nome as operadora_nome,
            o.codigo as operadora_codigo
        FROM execucoes e
        JOIN processos p ON e.processo_id = p.id
        JOIN clientes c ON p.cliente_id = c.id
        JOIN operadoras o ON c.operadora_id = o.id
        WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND e.status_execucao = %s"
            params.append(status)
        
        if operadora_codigo:
            query += " AND o.codigo = %s"
            params.append(operadora_codigo)
        
        query += " ORDER BY e.created_at DESC"
        
        execucoes = db.execute_query(query, tuple(params))
        return {
            "sucesso": True,
            "execucoes": execucoes,
            "total": len(execucoes)
        }
    
    @staticmethod
    def obter_execucoes_ativas():
        """Obtém execuções ativas"""
        return ExecucaoService.listar_execucoes(status="EXECUTANDO")
    
    @staticmethod
    def cancelar_execucao(execucao_id: int, motivo: str):
        """Cancela uma execução"""
        query = """
        UPDATE execucoes 
        SET status_execucao = 'CANCELADO',
            data_fim = NOW(),
            erro_detalhes = %s
        WHERE id = %s AND status_execucao = 'EXECUTANDO'
        RETURNING id
        """
        
        resultado = db.execute_insert(query, (motivo, execucao_id))
        
        if resultado:
            return {
                "sucesso": True,
                "mensagem": "Execução cancelada com sucesso",
                "execucao_id": execucao_id
            }
        else:
            return {
                "sucesso": False,
                "mensagem": "Execução não encontrada ou não está em execução"
            }

class DashboardService:
    """Serviço para dashboard usando PostgreSQL"""
    
    @staticmethod
    def obter_metricas_dashboard():
        """Obtém métricas principais do dashboard"""
        
        # Total de operadoras ativas
        operadoras = db.execute_query("SELECT COUNT(*) as total FROM operadoras WHERE status_ativo = true")
        total_operadoras = operadoras[0]['total']
        
        # Total de clientes ativos
        clientes = db.execute_query("SELECT COUNT(*) as total FROM clientes WHERE status_ativo = true")
        total_clientes = clientes[0]['total']
        
        # Processos pendentes de aprovação
        processos_pendentes = db.execute_query(
            "SELECT COUNT(*) as total FROM processos WHERE status_processo = 'PENDENTE_APROVACAO'"
        )
        total_pendentes = processos_pendentes[0]['total']
        
        # Execuções ativas
        execucoes_ativas = db.execute_query(
            "SELECT COUNT(*) as total FROM execucoes WHERE status_execucao = 'EXECUTANDO'"
        )
        total_execucoes_ativas = execucoes_ativas[0]['total']
        
        # Processos por operadora
        processos_por_operadora = db.execute_query("""
        SELECT 
            o.nome as operadora,
            COUNT(p.id) as total_processos,
            SUM(CASE WHEN p.status_processo = 'PENDENTE_APROVACAO' THEN 1 ELSE 0 END) as pendentes,
            SUM(CASE WHEN p.status_processo = 'APROVADA' THEN 1 ELSE 0 END) as aprovadas
        FROM operadoras o
        LEFT JOIN clientes c ON c.operadora_id = o.id
        LEFT JOIN processos p ON p.cliente_id = c.id
        GROUP BY o.id, o.nome
        ORDER BY o.nome
        """)
        
        return {
            "sucesso": True,
            "timestamp": datetime.now().isoformat(),
            "metricas": {
                "total_operadoras": total_operadoras,
                "total_clientes": total_clientes,
                "processos_pendentes": total_pendentes,
                "execucoes_ativas": total_execucoes_ativas
            },
            "processos_por_operadora": processos_por_operadora,
            "alertas": [
                {
                    "tipo": "info",
                    "titulo": "Sistema Operacional",
                    "descricao": f"{total_execucoes_ativas} execuções RPA ativas"
                },
                {
                    "tipo": "warning" if total_pendentes > 5 else "info",
                    "titulo": "Aprovações Pendentes",
                    "descricao": f"{total_pendentes} faturas aguardando aprovação"
                }
            ]
        }

# Instâncias dos serviços
operadora_service = OperadoraService()
cliente_service = ClienteService()
processo_service = ProcessoService()
execucao_service = ExecucaoService()
dashboard_service = DashboardService()