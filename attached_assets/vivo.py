import os
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys

from util.dataclass import StatusExecucao
from util.driver import Browser
from util.log import Logs, log_process
from services.controle_execucao_processo_service import ProcessManager

# Configuração de logging
load_dotenv()


class Vivo:

    def __init__(self, parameters, logger):
        # Informações de configuração
        self.__dict__.update(parameters.__dict__)
        self.logger = logger
        self.locators: VivoSite = VivoSite()
        self.pm = ProcessManager()
        self.execution()

    def realiza_login(self, driver: Browser) -> bool:
        try:
            self.logger.info(f"Acessando a URL: {self.url}")
            driver.get(self.url)

            # tratamento do login vivo:
            email = self.login
            cpf = self.cpf
            self.logger.info("Preenchendo o campo de login - EMAIL.")
            driver.send_text(xpath=self.locators.login_page.login, text=email.strip())
            self.logger.info("Clicando no botão de entrar.")
            driver.click(xpath=self.locators.login_page.entrar)
            self.logger.info("Preenchendo o campo de login - CPF")
            driver.send_text(xpath=self.locators.login_page.cpf, text=cpf.strip())
            self.logger.info("Clicando no botão de entrar.")
            driver.click(xpath=self.locators.login_page.entrar)
            self.logger.info("Preenchendo o campo de senha.")
            driver.send_text(xpath=self.locators.login_page.senha, text=self.senha)
            self.logger.info("Clicando no botão de entrar.")
            driver.click(xpath=self.locators.login_page.entrar)
            self.logger.info("Acessando...")
            return True
        except:
            self.logger.error("Erro encontrado na rotina de login")
            return False

    def execution(self):

        self.pm.update_status_execucao(
            self.hash_processo, self.session_id, StatusExecucao.RUNNING
        )
        self.driver = Browser()
        if self.realiza_login(driver=self.driver):
            self.logger.info("Acessando o menu de clientes.")
            self.driver.click(xpath=self.locators.cliente_page.pesquisa_cliente)
            self.logger.info("Pesquisando os 3 primeiros digitos do CNPJ")
            sleep(1.0)
            self.driver.send_text(
                xpath=self.locators.cliente_page.pesquisa_cnpj_input,
                text=self.cnpj[:3],
            )
            self.logger.info("Selecionando o cliente")
            sleep(2.0)
            tentativa = 0
            while tentativa < 5:
                self.logger.info(f"Selecionando o cliente - tentativa:{tentativa}")
                cnpj_empresa = self.driver.find_element(
                    xpath=self.locators.cliente_page.selecionar_cnpj
                )
                if cnpj_empresa:
                    cnpj_comparacao = cnpj_empresa.text.translate(
                        str.maketrans("", "", ".-/")
                    )

                    if cnpj_comparacao.startswith(self.cnpj[:3]):
                        self.driver.click(
                            xpath=self.locators.cliente_page.selecionar_cnpj
                        )
                        break
                    else:
                        sleep(0.5)
                        tentativa += 1
                        if tentativa >= 5:
                            self.logger.info("Limite de tentativas excedidas")
                            return False

            self.logger.info("Clicando em serviços do cliente")
            self.driver.click(xpath=self.locators.cliente_page.pesquisa_servico)
            self.driver.click(
                xpath=self.locators.cliente_page.selecionar_servico_fixo_corp
            )
            self.logger.info("Pesquisando cliente com filtro: %s", self.nome_filtro)
            self.driver.send_text(
                xpath=self.locators.cliente_page.pesquisa_cliente,
                text=self.nome_filtro,
            )
            self.driver.find_element(
                xpath=self.locators.cliente_page.pesquisa_cliente
            ).send_keys(Keys.ENTER)

            # Verificar se a grid filtrou apenas 1 cliente
            try:
                registros_grid = self.driver.find_element(
                    xpath=self.locators.cliente_page.pesquisa_servico,
                    condition="visible",
                )
                if registros_grid:
                    sleep(5)
                    self.logger.error("GRID SEM REGISTROS. Nenhum cliente encontrado.")
                    return None
            except:
                self.logger.info("Não houve erros de filtro para o cliente.")

                self.logger.info("Clicando no botão de fatura.")
                self.driver.click(xpath=self.locators.cliente_page.combo_servico)

                self.logger.info(
                    "Aguardando o botão 'Adicionar Fatura' ficar clicável."
                )
                botao_adicionar_fatura = self.driver.find_element(
                    xpath=self.locators.fatura_page.botao_adicionar,
                    condition="clickable",
                )
                if botao_adicionar_fatura:
                    self.logger.info("Clicando no botão 'Adicionar Fatura'.")
                    self.driver.click(xpath=self.locators.fatura_page.botao_adicionar)

                self.logger.info("Preenchendo o campo da operadora.")
                campo_operadora = self.driver.find_element(
                    xpath=self.locators.fatura_page.operadora, condition="visible"
                )
                if campo_operadora:
                    self.driver.send_text(
                        xpath=self.locators.fatura_page.operadora,
                        text=self.operadora,
                    )

                    self.logger.info("Preenchendo o campo de serviço.")
                    self.driver.send_text(
                        xpath=self.locators.fatura_page.linha, text=self.servico
                    )

                self.logger.info("Enviando o arquivo: %s", self.caminho_download)
                self.driver.find_element(
                    xpath=self.locators.fatura_page.campo_arquivo
                ).send_keys(self.caminho_download)
                self.driver.find_element(
                    xpath=self.locators.fatura_page.campo_input
                ).send_keys(self.caminho_download)

                self.logger.info("Selecionando a categoria 'PAGAR'.")
                self.driver.select_option(
                    xpath=self.locators.fatura_page.combo_categorias, option="PAGAR"
                )

                self.logger.info("Clicando no botão 'Cadastrar'.")
                self.driver.click(xpath=self.locators.fatura_page.botao_cadastrar)

            self.logger.info("Finalizando a execução e fechando o driver.")
            self.driver._driver.quit()
        else:
            self.pm.update_status_execucao(
                self.hash_processo,
                self.session_id,
                StatusExecucao.FAILED,
                {"Falha no login"},
            )


class LoginPage:
    login = "//input[@id='login-input']"
    cpf = "//input[@id='input-document-id']"
    senha = "//input[@name='password' and @type='password' and not(@disabled)]"
    entrar = "//button[@data-test-access-button]"


class ClientePage:
    pesquisa_cliente = (
        "//div[@data-e2e-header-customer-box]//p[@data-e2e-header-customer-name]"
    )
    pesquisa_cnpj_input = "//input[@data-customer-search-input]"
    selecionar_cnpj = "//div[@data-customer-select-slider-list]//h1[@class='title']"
    pesquisa_servico = "//li[@id='service-select-desktop']"
    selecionar_servico_fixo_corp = "//li[@data-service-id='ADVANCED_FIXA']"
    selecionar_servico_fixo = "//li[@data-service-id='WIR']"
    selecionar_servico_fixo_movel = "//li[@data-service-id='MOV']"

    combo_servico = "//button[@data-combo-button]//span[@class='combo_value']"
    solucao_de_voz = "//span[@data-value='solucaoDeVoz']"
    internet = "//span[@data-value='internet']"
    dados = "//span[@data-value='dados']"
    internetCorporativa = "//span[@data-value='internetCorporativa']"


class FaturaPage:
    botao_adicionar = (
        "//a[contains(text(), 'Adicionar') and not(contains(text(), 'Excel'))]"
    )
    operadora = "//input[@name='input[operadora]']"
    linha = "//input[@name='input[telefone]']"
    arquivo = "//input[@type='file']"
    campo_arquivo = "//input[@class='file' and @style='display: inline; width: 250px;']"
    campo_input = "//input[@type='file' and @name='file[]']"
    data = "//input[@name='input[data_competencia]']"
    combo_categorias = "//select[@id='categorias']"
    botao_cadastrar = "//input[@class='envia' and @name='cadastar']"


class MenuLink:
    menu_clientes = "//a[normalize-space(text())='Clientes']"


class VivoSite:
    login_page = LoginPage
    menu_link = MenuLink
    cliente_page = ClientePage
    fatura_page = FaturaPage
