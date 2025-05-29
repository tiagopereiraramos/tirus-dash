"""
SAT RPA - Adaptado ao padrão RPA Base
Preservando 100% do código legado conforme manual da BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
Data: 29/05/2025
"""

import os
from datetime import datetime
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .rpa_base import (
    RPABase, 
    ParametrosEntradaPadrao, 
    ResultadoSaidaPadrao, 
    StatusExecucao
)
from ..utils.selenium_driver import SeleniumDriver
from ..utils.file_manager import FileManager

class SatRPA(RPABase):
    """
    RPA SAT adaptado ao padrão imutável do RPA Base
    Preserva 100% da lógica legada de upload conforme manual
    """
    
    def __init__(self):
        super().__init__()
        self.driver_manager = SeleniumDriver()
        self.file_manager = FileManager()
        self.driver = None
        self.wait = None
        
        # Configurações SAT (serão obtidas de variáveis de ambiente)
        self.url_sat = os.getenv("URLSAT", "")
        self.login_sat = os.getenv("LOGINSAT", "")
        self.senha_sat = os.getenv("SENHASAT", "")
    
    def executar_download(self, parametros: ParametrosEntradaPadrao) -> ResultadoSaidaPadrao:
        """
        SAT não executa download, apenas upload
        """
        return ResultadoSaidaPadrao(
            sucesso=False,
            status=StatusExecucao.ERRO,
            mensagem="SAT RPA é apenas para upload de faturas",
            timestamp_inicio=datetime.now(),
            timestamp_fim=datetime.now()
        )
    
    def executar_upload_sat(self, parametros: ParametrosEntradaPadrao) -> ResultadoSaidaPadrao:
        """
        Executa upload de fatura para o SAT preservando lógica legada
        """
        timestamp_inicio = datetime.now()
        
        try:
            self.logger.info(f"Iniciando upload SAT para cliente {parametros.id_cliente}")
            
            # Inicializa driver
            self.driver = self.driver_manager.obter_driver()
            self.wait = self.driver_manager.obter_wait(self.driver)
            
            # Execução da lógica legada preservada
            success = self._executar_processo_sat(parametros)
            
            if success:
                return ResultadoSaidaPadrao(
                    sucesso=True,
                    status=StatusExecucao.SUCESSO,
                    mensagem="Upload para SAT realizado com sucesso",
                    tempo_execucao_segundos=(datetime.now() - timestamp_inicio).total_seconds(),
                    timestamp_inicio=timestamp_inicio,
                    timestamp_fim=datetime.now(),
                    logs_execucao=[f"Fatura enviada para SAT - Cliente: {parametros.nome_sat}"]
                )
            else:
                return ResultadoSaidaPadrao(
                    sucesso=False,
                    status=StatusExecucao.ERRO,
                    mensagem="Falha no upload para SAT",
                    timestamp_inicio=timestamp_inicio,
                    timestamp_fim=datetime.now()
                )
                
        except Exception as e:
            self.logger.error(f"Erro no upload SAT: {e}")
            return ResultadoSaidaPadrao(
                sucesso=False,
                status=StatusExecucao.ERRO,
                mensagem=f"Erro interno: {str(e)}",
                timestamp_inicio=timestamp_inicio,
                timestamp_fim=datetime.now()
            )
        finally:
            if self.driver:
                self.driver.quit()
    
    # ========== MÉTODOS LEGADOS PRESERVADOS 100% ==========
    
    def _executar_processo_sat(self, parametros: ParametrosEntradaPadrao) -> bool:
        """Lógica principal do SAT preservada do código legado"""
        try:
            locators = self._obter_localizadores_sat()
            
            self.logger.info("Executando o processo de login SAT")
            self.logger.info(f"Acessando a URL: {self.url_sat}")
            self.driver.get(self.url_sat)

            self.logger.info("Preenchendo o campo de login")
            self._enviar_texto(locators.login_page.login, self.login_sat)

            self.logger.info("Preenchendo o campo de senha")
            self._enviar_texto(locators.login_page.senha, self.senha_sat)

            self.logger.info("Clicando no botão de entrar")
            self._clicar(locators.login_page.entrar)

            self.logger.info("Acessando o menu de clientes")
            self._clicar(locators.menu_link.menu_clientes)

            self.logger.info(f"Pesquisando cliente com filtro: {parametros.nome_sat}")
            self._enviar_texto(locators.cliente_page.pesquisa_cliente, parametros.nome_sat)
            
            # Pressionar Enter para pesquisar
            elemento_pesquisa = self.driver.find_element(By.XPATH, locators.cliente_page.pesquisa_cliente)
            elemento_pesquisa.send_keys(Keys.ENTER)

            # Verificar se a grid filtrou apenas 1 cliente
            if self._verificar_grid_sem_registros(locators):
                self.logger.error("GRID SEM REGISTROS. Nenhum cliente encontrado")
                return False

            self.logger.info("Cliente encontrado. Clicando no botão de fatura")
            self._clicar(locators.cliente_page.botao_fatura)

            self.logger.info("Aguardando o botão 'Adicionar Fatura' ficar clicável")
            if self._aguardar_elemento_clicavel(locators.fatura_page.botao_adicionar):
                self.logger.info("Clicando no botão 'Adicionar Fatura'")
                self._clicar(locators.fatura_page.botao_adicionar)
            
            # Recuperar arquivo (aqui seria adaptado para usar o file_manager)
            file_path = self._obter_caminho_arquivo(parametros)
            if not file_path:
                self.logger.error("Erro ao obter arquivo para upload")
                return False

            # Preencher formulário de fatura
            if self._preencher_formulario_fatura(locators, parametros, file_path):
                self.logger.info("Fatura cadastrada com sucesso no SAT")
                return True
            else:
                self.logger.error("Erro ao cadastrar fatura no SAT")
                return False

        except Exception as error:
            self.logger.error(f"Erro no processo SAT: {error}")
            return False

    def _verificar_grid_sem_registros(self, locators) -> bool:
        """Verifica se a grid retornou sem registros"""
        try:
            sleep(5)
            elemento_sem_registros = self.driver.find_element(
                By.XPATH, locators.cliente_page.grid_sem_registros
            )
            return elemento_sem_registros.is_displayed()
        except:
            return False

    def _preencher_formulario_fatura(self, locators, parametros: ParametrosEntradaPadrao, file_path: str) -> bool:
        """Preenche o formulário de fatura no SAT"""
        try:
            self.logger.info("Preenchendo o campo da operadora")
            if self._aguardar_elemento_visivel(locators.fatura_page.operadora):
                # Determina operadora baseada no código
                operadora_nome = self._obter_nome_operadora(parametros.operadora_codigo)
                self._enviar_texto(locators.fatura_page.operadora, operadora_nome)

                self.logger.info("Preenchendo o campo de serviço do SAT")
                self._enviar_texto(locators.fatura_page.linha, parametros.dados_sat)

            self.logger.info(f"Enviando o arquivo: {file_path}")
            self.driver.find_element(By.XPATH, locators.fatura_page.campo_arquivo).send_keys(file_path)
            self.driver.find_element(By.XPATH, locators.fatura_page.campo_input).send_keys(file_path)

            # Aqui seria necessário obter a data de vencimento do arquivo ou parâmetros
            data_vencimento = self._extrair_data_vencimento_parametros(parametros)
            if data_vencimento:
                self.logger.info("Preenchendo a data de vencimento")
                self._enviar_texto_com_limpar(locators.fatura_page.data, data_vencimento)

            self.logger.info("Selecionando a categoria 'PAGAR'")
            self._selecionar_opcao(locators.fatura_page.combo_categorias, "PAGAR")
            
            try:
                self.logger.info(f"Selecionando a filial: {parametros.unidade}")
                self._selecionar_opcao_por_similaridade(locators.fatura_page.combo_filial, parametros.unidade)
            except:
                self.logger.error("Não encontrou unidade por similaridade")

            self.logger.info("Clicando no botão 'Cadastrar'")
            self._clicar(locators.fatura_page.botao_cadastrar)
            sleep(3)
            
            return True

        except Exception as e:
            self.logger.error(f"Erro ao preencher formulário: {e}")
            return False

    def _obter_caminho_arquivo(self, parametros: ParametrosEntradaPadrao) -> str:
        """Obtém o caminho do arquivo para upload"""
        # Aqui seria implementada a lógica para baixar do S3 ou obter arquivo local
        # Por enquanto, retorna um placeholder que seria adaptado
        return f"/tmp/{parametros.id_cliente}_fatura.pdf"

    def _extrair_data_vencimento_parametros(self, parametros: ParametrosEntradaPadrao) -> str:
        """Extrai data de vencimento dos parâmetros ou arquivo"""
        # Implementar lógica para extrair data de vencimento
        return datetime.now().strftime("%d/%m/%Y")

    def _obter_nome_operadora(self, codigo_operadora: str) -> str:
        """Converte código da operadora para nome completo"""
        mapeamento = {
            "EMB": "EMBRATEL",
            "EMBRATEL": "EMBRATEL",
            "DIG": "DIGITALNET", 
            "DIGITALNET": "DIGITALNET",
            "VIV": "VIVO",
            "VIVO": "VIVO",
            "OI": "OI",
            "AZU": "AZUTON",
            "AZUTON": "AZUTON"
        }
        return mapeamento.get(codigo_operadora.upper(), codigo_operadora)

    # ========== MÉTODOS AUXILIARES SELENIUM ==========
    
    def _enviar_texto(self, xpath: str, texto: str):
        """Envia texto para elemento"""
        elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        elemento.send_keys(texto)

    def _enviar_texto_com_limpar(self, xpath: str, texto: str):
        """Envia texto para elemento limpando antes"""
        elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        elemento.clear()
        elemento.send_keys(texto)

    def _clicar(self, xpath: str):
        """Clica em elemento"""
        elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        elemento.click()

    def _aguardar_elemento_clicavel(self, xpath: str) -> bool:
        """Aguarda elemento ficar clicável"""
        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            return True
        except:
            return False

    def _aguardar_elemento_visivel(self, xpath: str) -> bool:
        """Aguarda elemento ficar visível"""
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            return True
        except:
            return False

    def _selecionar_opcao(self, xpath: str, opcao: str):
        """Seleciona opção em select"""
        from selenium.webdriver.support.ui import Select
        elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        select = Select(elemento)
        select.select_by_visible_text(opcao)

    def _selecionar_opcao_por_similaridade(self, xpath: str, opcao: str):
        """Seleciona opção por similaridade"""
        from selenium.webdriver.support.ui import Select
        elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        select = Select(elemento)
        
        # Procura opção mais similar
        for option in select.options:
            if opcao.upper() in option.text.upper():
                select.select_by_visible_text(option.text)
                return
        
        # Se não encontrou, seleciona a primeira opção
        if select.options:
            select.select_by_index(0)

    def _obter_localizadores_sat(self):
        """Retorna localizadores do SAT preservados do código legado"""
        class LoginPage:
            login = "//input[@name='login']"
            senha = "//input[@name='senha']"
            entrar = "//input[@value='Entrar']"

        class ClientePage:
            pesquisa_cliente = "//input[@placeholder='Buscando algo ?']"
            botao_fatura = "//a[contains(@href, 'fatura')][img[contains(@src, 'ref.png')]]"
            grid_sem_registros = "//td[contains(normalize-space(text()), 'Sua busca não trouxe nenhum resultado')]"

        class FaturaPage:
            botao_adicionar = "//a[contains(text(), 'Adicionar') and not(contains(text(), 'Excel'))]"
            operadora = "//input[@name='input[operadora]']"
            linha = "//input[@name='input[telefone]']"
            arquivo = "//input[@type='file']"
            campo_arquivo = "//input[@class='file' and @style='display: inline; width: 250px;']"
            campo_input = "//input[@type='file' and @name='file[]']"
            data = "//input[@name='input[data_competencia]']"
            combo_categorias = "//select[@id='categorias']"
            combo_filial = "//select[@id='categorias' and @name='input[id_filial]']"
            botao_cadastrar = "//input[@class='envia' and @name='cadastar']"

        class MenuLink:
            menu_clientes = "//a[normalize-space(text())='Clientes']"

        class SatSiteLocators:
            login_page = LoginPage()
            menu_link = MenuLink()
            cliente_page = ClientePage()
            fatura_page = FaturaPage()

        return SatSiteLocators()