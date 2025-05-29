"""
RPA da Vivo - Implementação específica
Baseado no arquivo vivo.py existente
"""

import time
from typing import Dict, List, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .rpa_base import RPABase
from models.cliente import Cliente


class VivoRPA(RPABase):
    """RPA específico para a operadora Vivo"""
    
    def __init__(self):
        super().__init__("VIVO")
        self.portal_url = "https://empresas.vivo.com.br"
        self.login_url = "https://empresas.vivo.com.br/login"
    
    def fazer_login(self, login: str, senha: str) -> bool:
        """Faz login no portal da Vivo"""
        try:
            self.logger.info("Iniciando login no portal Vivo")
            
            # Navegar para página de login
            self.driver.get(self.login_url)
            self.aguardar(3)
            
            # Preencher campos de login
            campo_login = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            campo_login.clear()
            campo_login.send_keys(login)
            
            campo_senha = self.driver.find_element(By.ID, "password")
            campo_senha.clear()
            campo_senha.send_keys(senha)
            
            # Clicar no botão de login
            botao_login = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            botao_login.click()
            
            # Aguardar redirecionamento
            self.aguardar(5)
            
            # Verificar se login foi bem-sucedido
            if "dashboard" in self.driver.current_url.lower() or "home" in self.driver.current_url.lower():
                self.logger.info("Login realizado com sucesso")
                return True
            else:
                self.logger.error("Falha no login - redirecionamento não ocorreu")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro no login Vivo: {e}")
            return False
    
    def buscar_faturas(self, cliente: Cliente, mes_ano: str) -> List[Dict[str, Any]]:
        """Busca faturas na Vivo"""
        try:
            self.logger.info(f"Buscando faturas para {cliente.razao_social} - {mes_ano}")
            
            faturas = []
            
            # Navegar para seção de faturas
            self.driver.get(f"{self.portal_url}/faturas")
            self.aguardar(3)
            
            # Aplicar filtro por período se necessário
            if cliente.filtro:
                campo_filtro = self.driver.find_element(By.NAME, "filtro")
                campo_filtro.clear()
                campo_filtro.send_keys(cliente.filtro)
            
            # Buscar por período específico
            campo_periodo = self.driver.find_element(By.NAME, "periodo")
            campo_periodo.clear()
            campo_periodo.send_keys(mes_ano)
            
            # Clicar em buscar
            botao_buscar = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar')]")
            botao_buscar.click()
            self.aguardar(3)
            
            # Buscar faturas na página
            elementos_faturas = self.driver.find_elements(By.CLASS_NAME, "fatura-item")
            
            for elemento in elementos_faturas:
                try:
                    # Extrair dados da fatura
                    numero = elemento.find_element(By.CLASS_NAME, "numero-fatura").text
                    valor = elemento.find_element(By.CLASS_NAME, "valor-fatura").text
                    vencimento = elemento.find_element(By.CLASS_NAME, "data-vencimento").text
                    link_download = elemento.find_element(By.CLASS_NAME, "link-download").get_attribute("href")
                    
                    fatura = {
                        "numero": numero,
                        "valor": self._extrair_valor(valor),
                        "vencimento": self._extrair_data(vencimento),
                        "url_download": link_download,
                        "mes_ano": mes_ano,
                        "operadora": "VIVO"
                    }
                    
                    faturas.append(fatura)
                    self.logger.info(f"Fatura encontrada: {numero}")
                    
                except Exception as e:
                    self.logger.warning(f"Erro ao processar elemento de fatura: {e}")
                    continue
            
            self.logger.info(f"Total de faturas encontradas: {len(faturas)}")
            return faturas
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar faturas Vivo: {e}")
            return []
    
    def baixar_fatura(self, cliente: Cliente, dados_fatura: Dict[str, Any]) -> str:
        """Baixa fatura específica da Vivo"""
        try:
            self.logger.info(f"Baixando fatura {dados_fatura['numero']}")
            
            # Navegar para URL de download
            self.driver.get(dados_fatura["url_download"])
            self.aguardar(2)
            
            # Aguardar download completar
            download_dir = self.file_manager.get_download_dir()
            arquivo_baixado = None
            
            # Aguardar arquivo aparecer na pasta de download
            for tentativa in range(30):  # 30 segundos de timeout
                arquivos = self.file_manager.listar_arquivos_download()
                for arquivo in arquivos:
                    if arquivo.endswith('.pdf') and dados_fatura['numero'] in arquivo:
                        arquivo_baixado = arquivo
                        break
                
                if arquivo_baixado:
                    break
                    
                self.aguardar(1)
            
            if arquivo_baixado:
                # Renomear arquivo com padrão consistente
                nome_final = f"{cliente.hash_unico}_{dados_fatura['mes_ano']}_VIVO.pdf"
                caminho_final = self.file_manager.renomear_arquivo(arquivo_baixado, nome_final)
                
                self.logger.info(f"Fatura baixada: {caminho_final}")
                return caminho_final
            else:
                raise Exception("Timeout no download da fatura")
                
        except Exception as e:
            self.logger.error(f"Erro ao baixar fatura Vivo: {e}")
            return None
    
    def _extrair_valor(self, texto_valor: str) -> float:
        """Extrai valor monetário do texto"""
        try:
            # Remove caracteres não numéricos exceto vírgula e ponto
            import re
            valor_limpo = re.sub(r'[^\d,.]', '', texto_valor)
            valor_limpo = valor_limpo.replace(',', '.')
            return float(valor_limpo)
        except:
            return 0.0
    
    def _extrair_data(self, texto_data: str) -> str:
        """Extrai data do texto"""
        try:
            import re
            # Busca padrão dd/mm/yyyy
            match = re.search(r'(\d{2}/\d{2}/\d{4})', texto_data)
            if match:
                return match.group(1)
            return texto_data
        except:
            return ""