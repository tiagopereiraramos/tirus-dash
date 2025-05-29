"""
RPA Base - Classe abstrata para todos os RPAs
Desenvolvido por: Tiago Pereira Ramos
"""

import os
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from config.database import SessionLocal
from models.cliente import Cliente
from models.processo import Processo
from models.execucao import Execucao
from utils.selenium_driver import SeleniumDriver
from utils.file_manager import FileManager
from utils.logger import RPALogger


class RPABase(ABC):
    """Classe base abstrata para todos os RPAs"""
    
    def __init__(self, operadora: str):
        self.operadora = operadora
        self.driver = None
        self.db: Session = SessionLocal()
        self.logger = RPALogger(operadora)
        self.file_manager = FileManager()
        self.status = "PARADO"
        self.processo_atual = None
        self.execucao_atual = None
    
    @abstractmethod
    def fazer_login(self, login: str, senha: str) -> bool:
        """Método abstrato para fazer login no portal da operadora"""
        pass
    
    @abstractmethod
    def buscar_faturas(self, cliente: Cliente, mes_ano: str) -> List[Dict[str, Any]]:
        """Método abstrato para buscar faturas"""
        pass
    
    @abstractmethod
    def baixar_fatura(self, cliente: Cliente, dados_fatura: Dict[str, Any]) -> str:
        """Método abstrato para baixar fatura"""
        pass
    
    def inicializar_driver(self, headless: bool = True) -> bool:
        """Inicializa o driver Selenium"""
        try:
            self.driver = SeleniumDriver(headless=headless)
            self.driver.inicializar()
            self.logger.info(f"Driver inicializado para {self.operadora}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao inicializar driver: {e}")
            return False
    
    def finalizar_driver(self):
        """Finaliza o driver Selenium"""
        try:
            if self.driver:
                self.driver.finalizar()
                self.driver = None
                self.logger.info(f"Driver finalizado para {self.operadora}")
        except Exception as e:
            self.logger.error(f"Erro ao finalizar driver: {e}")
    
    def executar_processo(self, cliente_id: str, mes_ano: str, hash_execucao: str = None) -> Dict[str, Any]:
        """Executa o processo completo de download de fatura"""
        self.status = "EXECUTANDO"
        resultado = {
            "sucesso": False,
            "mensagem": "",
            "arquivo_baixado": None,
            "hash_execucao": hash_execucao or str(uuid.uuid4()),
            "detalhes": {}
        }
        
        try:
            # Buscar cliente
            cliente = self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
            if not cliente:
                raise Exception(f"Cliente não encontrado: {cliente_id}")
            
            # Criar ou buscar processo
            self.processo_atual = self._criar_ou_buscar_processo(cliente, mes_ano)
            
            # Criar execução
            self.execucao_atual = self._criar_execucao(resultado["hash_execucao"])
            
            self.logger.info(f"Iniciando execução para {cliente.razao_social} - {mes_ano}")
            
            # Inicializar driver
            if not self.inicializar_driver():
                raise Exception("Falha ao inicializar driver")
            
            # Fazer login
            if not self.fazer_login(cliente.login_portal, cliente.senha_portal):
                raise Exception("Falha no login")
            
            # Buscar faturas
            faturas = self.buscar_faturas(cliente, mes_ano)
            if not faturas:
                raise Exception("Nenhuma fatura encontrada")
            
            # Baixar primeira fatura encontrada
            dados_fatura = faturas[0]
            arquivo_baixado = self.baixar_fatura(cliente, dados_fatura)
            
            if arquivo_baixado:
                # Upload para S3
                url_s3 = self.file_manager.upload_to_s3(arquivo_baixado, cliente.hash_unico, mes_ano)
                
                # Atualizar processo
                self._atualizar_processo_sucesso(url_s3, dados_fatura)
                
                resultado.update({
                    "sucesso": True,
                    "mensagem": "Fatura baixada com sucesso",
                    "arquivo_baixado": arquivo_baixado,
                    "url_s3": url_s3,
                    "detalhes": dados_fatura
                })
                
                self.logger.info(f"Execução concluída com sucesso: {arquivo_baixado}")
            else:
                raise Exception("Falha ao baixar fatura")
                
        except Exception as e:
            erro_msg = f"Erro na execução: {str(e)}"
            self.logger.error(erro_msg)
            resultado["mensagem"] = erro_msg
            
            if self.processo_atual:
                self._atualizar_processo_erro(erro_msg)
            
        finally:
            self.finalizar_driver()
            self._finalizar_execucao(resultado)
            self.status = "PARADO"
            self.db.close()
        
        return resultado
    
    def _criar_ou_buscar_processo(self, cliente: Cliente, mes_ano: str) -> Processo:
        """Cria ou busca processo existente"""
        processo = self.db.query(Processo).filter(
            Processo.cliente_id == cliente.id,
            Processo.mes_ano == mes_ano
        ).first()
        
        if not processo:
            processo = Processo(
                cliente_id=cliente.id,
                mes_ano=mes_ano,
                status_processo="AGUARDANDO_DOWNLOAD",
                criado_automaticamente=True
            )
            self.db.add(processo)
            self.db.commit()
            self.db.refresh(processo)
        
        return processo
    
    def _criar_execucao(self, hash_execucao: str) -> Execucao:
        """Cria nova execução"""
        execucao = Execucao(
            processo_id=self.processo_atual.id,
            tipo_execucao="DOWNLOAD_FATURA",
            status_execucao="EXECUTANDO",
            parametros_entrada={
                "operadora": self.operadora,
                "hash_execucao": hash_execucao
            },
            data_inicio=datetime.now(),
            numero_tentativa=1
        )
        self.db.add(execucao)
        self.db.commit()
        self.db.refresh(execucao)
        return execucao
    
    def _atualizar_processo_sucesso(self, url_s3: str, dados_fatura: Dict[str, Any]):
        """Atualiza processo com sucesso"""
        self.processo_atual.status_processo = "FATURA_BAIXADA"
        self.processo_atual.caminho_s3_fatura = url_s3
        self.processo_atual.url_fatura = dados_fatura.get("url_download")
        
        if dados_fatura.get("valor"):
            self.processo_atual.valor_fatura = dados_fatura["valor"]
        if dados_fatura.get("vencimento"):
            self.processo_atual.data_vencimento = dados_fatura["vencimento"]
            
        self.db.commit()
    
    def _atualizar_processo_erro(self, erro_msg: str):
        """Atualiza processo com erro"""
        self.processo_atual.status_processo = "ERRO"
        self.processo_atual.observacoes = erro_msg
        self.db.commit()
    
    def _finalizar_execucao(self, resultado: Dict[str, Any]):
        """Finaliza execução"""
        if self.execucao_atual:
            self.execucao_atual.status_execucao = "CONCLUIDO" if resultado["sucesso"] else "FALHOU"
            self.execucao_atual.data_fim = datetime.now()
            self.execucao_atual.resultado_saida = resultado
            self.execucao_atual.mensagem_log = resultado["mensagem"]
            
            if not resultado["sucesso"]:
                self.execucao_atual.detalhes_erro = {"erro": resultado["mensagem"]}
            
            self.db.commit()
    
    def obter_status(self) -> Dict[str, Any]:
        """Retorna status atual do RPA"""
        return {
            "operadora": self.operadora,
            "status": self.status,
            "processo_atual": self.processo_atual.id if self.processo_atual else None,
            "execucao_atual": self.execucao_atual.id if self.execucao_atual else None,
            "driver_ativo": self.driver is not None
        }
    
    def parar_execucao(self):
        """Para a execução atual"""
        self.status = "PARANDO"
        if self.driver:
            self.finalizar_driver()
        self.status = "PARADO"
        self.logger.info(f"Execução parada para {self.operadora}")
    
    def validar_cliente(self, cliente: Cliente) -> bool:
        """Valida se o cliente possui dados necessários"""
        if not cliente.login_portal or not cliente.senha_portal:
            self.logger.error(f"Cliente {cliente.razao_social} sem credenciais de portal")
            return False
        return True
    
    def aguardar(self, segundos: int):
        """Aguarda um tempo determinado"""
        time.sleep(segundos)
    
    def __del__(self):
        """Destrutor da classe"""
        if self.db:
            self.db.close()