"""
Serviço de Manipulação de Usuários
Sistema RPA BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
"""

import uuid
import logging
import bcrypt
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.database import get_db_session
from ..models.usuario import Usuario, TipoUsuario

logger = logging.getLogger(__name__)

class UsuarioService:
    """Serviço para manipulação de usuários"""

    @staticmethod
    def criar_usuario(
        nome: str,
        email: str,
        senha: str,
        tipo_usuario: TipoUsuario = TipoUsuario.OPERADOR,
        telefone: str = None,
        departamento: str = None
    ) -> Dict[str, Any]:
        """Cria um novo usuário"""
        try:
            with get_db_session() as db:
                # Verificar se email já existe
                usuario_existente = db.query(Usuario).filter(
                    Usuario.email.ilike(email)
                ).first()
                
                if usuario_existente:
                    return {
                        "sucesso": False,
                        "mensagem": f"Email '{email}' já está em uso",
                        "usuario_id": str(usuario_existente.id)
                    }
                
                # Criptografar senha
                senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Criar usuário
                usuario = Usuario(
                    nome=nome.strip(),
                    email=email.strip().lower(),
                    senha_hash=senha_hash,
                    tipo_usuario=tipo_usuario.value,
                    telefone=telefone,
                    departamento=departamento
                )
                
                db.add(usuario)
                db.commit()
                db.refresh(usuario)
                
                logger.info(f"Usuário criado: {usuario.id} - {nome}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Usuário criado com sucesso",
                    "usuario_id": str(usuario.id),
                    "nome": nome,
                    "email": email,
                    "tipo_usuario": tipo_usuario.value
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            raise

    @staticmethod
    def autenticar_usuario(email: str, senha: str) -> Dict[str, Any]:
        """Autentica um usuário"""
        try:
            with get_db_session() as db:
                usuario = db.query(Usuario).filter(
                    and_(
                        Usuario.email.ilike(email),
                        Usuario.status_ativo == True
                    )
                ).first()
                
                if not usuario:
                    return {
                        "sucesso": False,
                        "mensagem": "Email não encontrado ou usuário inativo",
                        "usuario": None
                    }
                
                # Verificar senha
                if not bcrypt.checkpw(senha.encode('utf-8'), usuario.senha_hash.encode('utf-8')):
                    return {
                        "sucesso": False,
                        "mensagem": "Senha incorreta",
                        "usuario": None
                    }
                
                # Atualizar último login
                usuario.ultimo_login = datetime.now()
                db.commit()
                
                return {
                    "sucesso": True,
                    "mensagem": "Autenticação realizada com sucesso",
                    "usuario": {
                        "id": str(usuario.id),
                        "nome": usuario.nome,
                        "email": usuario.email,
                        "tipo_usuario": usuario.tipo_usuario,
                        "telefone": usuario.telefone,
                        "departamento": usuario.departamento,
                        "ultimo_login": usuario.ultimo_login.isoformat() if usuario.ultimo_login else None
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro na autenticação: {str(e)}")
            raise

    @staticmethod
    def buscar_usuarios_com_filtros(
        tipo_usuario: TipoUsuario = None,
        ativo: bool = None,
        termo_busca: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Busca usuários com filtros avançados"""
        try:
            with get_db_session() as db:
                query = db.query(Usuario)
                
                # Aplicar filtros
                if tipo_usuario:
                    query = query.filter(Usuario.tipo_usuario == tipo_usuario.value)
                
                if ativo is not None:
                    query = query.filter(Usuario.status_ativo == ativo)
                
                if termo_busca:
                    termo = f"%{termo_busca}%"
                    query = query.filter(
                        or_(
                            Usuario.nome.ilike(termo),
                            Usuario.email.ilike(termo),
                            Usuario.departamento.ilike(termo)
                        )
                    )
                
                # Contar total
                total = query.count()
                
                # Aplicar paginação
                usuarios = query.order_by(Usuario.nome).offset(skip).limit(limit).all()
                
                # Formatar resultados (sem senha)
                resultados = []
                for usuario in usuarios:
                    resultados.append({
                        "id": str(usuario.id),
                        "nome": usuario.nome,
                        "email": usuario.email,
                        "tipo_usuario": usuario.tipo_usuario,
                        "telefone": usuario.telefone,
                        "departamento": usuario.departamento,
                        "status_ativo": usuario.status_ativo,
                        "data_criacao": usuario.data_criacao.isoformat(),
                        "ultimo_login": usuario.ultimo_login.isoformat() if usuario.ultimo_login else None
                    })
                
                return {
                    "sucesso": True,
                    "usuarios": resultados,
                    "total": total,
                    "pagina_atual": skip // limit + 1 if limit > 0 else 1,
                    "total_paginas": (total + limit - 1) // limit if limit > 0 else 1
                }
                
        except Exception as e:
            logger.error(f"Erro na busca de usuários: {str(e)}")
            raise

    @staticmethod
    def atualizar_usuario(
        usuario_id: str,
        dados_atualizacao: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atualiza dados de um usuário"""
        try:
            with get_db_session() as db:
                usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
                
                if not usuario:
                    raise ValueError(f"Usuário {usuario_id} não encontrado")
                
                # Campos que podem ser atualizados
                campos_permitidos = [
                    'nome', 'telefone', 'departamento', 'tipo_usuario', 'status_ativo'
                ]
                
                # Verificar unicidade do email se foi alterado
                if 'email' in dados_atualizacao:
                    email_existente = db.query(Usuario).filter(
                        and_(
                            Usuario.email.ilike(dados_atualizacao['email']),
                            Usuario.id != usuario_id
                        )
                    ).first()
                    
                    if email_existente:
                        raise ValueError(f"Email '{dados_atualizacao['email']}' já está em uso")
                    
                    usuario.email = dados_atualizacao['email'].strip().lower()
                
                # Atualizar senha se fornecida
                if 'senha' in dados_atualizacao and dados_atualizacao['senha']:
                    nova_senha_hash = bcrypt.hashpw(
                        dados_atualizacao['senha'].encode('utf-8'), 
                        bcrypt.gensalt()
                    ).decode('utf-8')
                    usuario.senha_hash = nova_senha_hash
                
                # Aplicar outras atualizações
                for campo, valor in dados_atualizacao.items():
                    if campo in campos_permitidos and hasattr(usuario, campo):
                        if campo == 'nome' and valor:
                            setattr(usuario, campo, valor.strip())
                        elif campo == 'tipo_usuario' and valor:
                            # Validar tipo de usuário
                            if isinstance(valor, str):
                                try:
                                    tipo_enum = TipoUsuario(valor)
                                    setattr(usuario, campo, tipo_enum.value)
                                except ValueError:
                                    raise ValueError(f"Tipo de usuário inválido: {valor}")
                            else:
                                setattr(usuario, campo, valor)
                        else:
                            setattr(usuario, campo, valor)
                
                usuario.data_atualizacao = datetime.now()
                db.commit()
                
                logger.info(f"Usuário {usuario_id} atualizado")
                
                return {
                    "sucesso": True,
                    "mensagem": "Usuário atualizado com sucesso",
                    "usuario_id": usuario_id,
                    "nome": usuario.nome,
                    "email": usuario.email
                }
                
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {str(e)}")
            raise

    @staticmethod
    def obter_usuario_por_id(usuario_id: str) -> Dict[str, Any]:
        """Obtém um usuário específico por ID"""
        try:
            with get_db_session() as db:
                usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
                
                if not usuario:
                    raise ValueError(f"Usuário {usuario_id} não encontrado")
                
                return {
                    "sucesso": True,
                    "usuario": {
                        "id": str(usuario.id),
                        "nome": usuario.nome,
                        "email": usuario.email,
                        "tipo_usuario": usuario.tipo_usuario,
                        "telefone": usuario.telefone,
                        "departamento": usuario.departamento,
                        "status_ativo": usuario.status_ativo,
                        "data_criacao": usuario.data_criacao.isoformat(),
                        "data_atualizacao": usuario.data_atualizacao.isoformat(),
                        "ultimo_login": usuario.ultimo_login.isoformat() if usuario.ultimo_login else None
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter usuário: {str(e)}")
            raise

    @staticmethod
    def alterar_senha(
        usuario_id: str,
        senha_atual: str,
        nova_senha: str
    ) -> Dict[str, Any]:
        """Altera a senha de um usuário"""
        try:
            with get_db_session() as db:
                usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
                
                if not usuario:
                    raise ValueError(f"Usuário {usuario_id} não encontrado")
                
                # Verificar senha atual
                if not bcrypt.checkpw(senha_atual.encode('utf-8'), usuario.senha_hash.encode('utf-8')):
                    return {
                        "sucesso": False,
                        "mensagem": "Senha atual incorreta"
                    }
                
                # Criptografar nova senha
                nova_senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                usuario.senha_hash = nova_senha_hash
                usuario.data_atualizacao = datetime.now()
                
                db.commit()
                
                logger.info(f"Senha alterada para usuário {usuario_id}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Senha alterada com sucesso"
                }
                
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {str(e)}")
            raise

    @staticmethod
    def obter_estatisticas_usuarios() -> Dict[str, Any]:
        """Obtém estatísticas de usuários"""
        try:
            with get_db_session() as db:
                # Estatísticas gerais
                total_usuarios = db.query(Usuario).count()
                usuarios_ativos = db.query(Usuario).filter(Usuario.status_ativo == True).count()
                
                # Distribuição por tipo
                from sqlalchemy import func
                distribuicao_tipo = db.query(
                    Usuario.tipo_usuario,
                    func.count(Usuario.id).label('count')
                ).group_by(Usuario.tipo_usuario).all()
                
                tipos_stats = {}
                for item in distribuicao_tipo:
                    tipos_stats[item.tipo_usuario] = item.count
                
                # Últimos logins (30 dias)
                from datetime import timedelta
                data_limite = datetime.now() - timedelta(days=30)
                usuarios_ativos_30d = db.query(Usuario).filter(
                    Usuario.ultimo_login >= data_limite
                ).count()
                
                return {
                    "sucesso": True,
                    "estatisticas": {
                        "total_usuarios": total_usuarios,
                        "usuarios_ativos": usuarios_ativos,
                        "usuarios_inativos": total_usuarios - usuarios_ativos,
                        "usuarios_ativos_30_dias": usuarios_ativos_30d,
                        "distribuicao_por_tipo": tipos_stats
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de usuários: {str(e)}")
            raise

    @staticmethod
    def deletar_usuario(usuario_id: str, forcar: bool = False) -> Dict[str, Any]:
        """Deleta um usuário (com validações de segurança)"""
        try:
            with get_db_session() as db:
                usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
                
                if not usuario:
                    raise ValueError(f"Usuário {usuario_id} não encontrado")
                
                # Verificar se é o único administrador
                if usuario.tipo_usuario == TipoUsuario.ADMINISTRADOR.value:
                    outros_admins = db.query(Usuario).filter(
                        and_(
                            Usuario.tipo_usuario == TipoUsuario.ADMINISTRADOR.value,
                            Usuario.id != usuario_id,
                            Usuario.status_ativo == True
                        )
                    ).count()
                    
                    if outros_admins == 0 and not forcar:
                        raise ValueError("Não é possível deletar o último administrador ativo")
                
                # Verificar atividades associadas (execuções, aprovações, etc.)
                from ..models.processo import Execucao, Processo
                execucoes_usuario = db.query(Execucao).filter(
                    Execucao.executado_por_usuario_id == usuario_id
                ).count()
                
                processos_aprovados = db.query(Processo).filter(
                    Processo.aprovado_por_usuario_id == usuario_id
                ).count()
                
                if (execucoes_usuario > 0 or processos_aprovados > 0) and not forcar:
                    return {
                        "sucesso": False,
                        "mensagem": f"Usuário possui {execucoes_usuario + processos_aprovados} atividades associadas. Use forcar=True para deletar"
                    }
                
                # Deletar usuário
                db.delete(usuario)
                db.commit()
                
                logger.info(f"Usuário {usuario_id} deletado")
                
                return {
                    "sucesso": True,
                    "mensagem": "Usuário deletado com sucesso",
                    "usuario_id": usuario_id
                }
                
        except Exception as e:
            logger.error(f"Erro ao deletar usuário: {str(e)}")
            raise

    @staticmethod
    def criar_usuario_admin_inicial() -> Dict[str, Any]:
        """Cria o usuário administrador inicial do sistema"""
        try:
            with get_db_session() as db:
                # Verificar se já existe um administrador
                admin_existente = db.query(Usuario).filter(
                    Usuario.tipo_usuario == TipoUsuario.ADMINISTRADOR.value
                ).first()
                
                if admin_existente:
                    return {
                        "sucesso": False,
                        "mensagem": "Já existe um administrador no sistema",
                        "usuario_id": str(admin_existente.id)
                    }
                
                # Criar administrador padrão
                senha_padrao = "admin123"
                senha_hash = bcrypt.hashpw(senha_padrao.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                admin = Usuario(
                    nome="Administrador",
                    email="admin@bgtelecom.com.br",
                    senha_hash=senha_hash,
                    tipo_usuario=TipoUsuario.ADMINISTRADOR.value,
                    departamento="TI"
                )
                
                db.add(admin)
                db.commit()
                db.refresh(admin)
                
                logger.info(f"Administrador inicial criado: {admin.id}")
                
                return {
                    "sucesso": True,
                    "mensagem": "Administrador inicial criado com sucesso",
                    "usuario_id": str(admin.id),
                    "email": admin.email,
                    "senha_temporaria": senha_padrao,
                    "importante": "ALTERE A SENHA IMEDIATAMENTE APÓS O PRIMEIRO LOGIN"
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar administrador inicial: {str(e)}")
            raise