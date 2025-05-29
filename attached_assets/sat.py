import os
from time import sleep

from configs.config import getenv
from selenium.webdriver.common.keys import Keys

from services.controle_execucao_processo_service import ProcessManager
from util.dataclass import StatusExecucao
from util.driver import Browser
from util.utilities import get_files_from_s3


class Sat:
    def __init__(self, db=None, logger=None, atualiza_coda=False):

        if db is not None:
            self.db = db
            self.logger = logger
            self.session_id = db.session_id
            self.coda_row_id = db.coda_row_id
            self.atualiza_coda = atualiza_coda
            self.hash_processo = db.hash_processo
            self.hash_cron_cad = db.hash_cron_cad

            self.url = getenv("URLSAT")
            self.login = getenv("LOGIN")
            self.senha = getenv("SENHA")

            self.cnpj = db.cnpj
            self.razao = db.razao
            self.operadora = db.operadora
            self.nome_filtro = db.nome_filtro
            self.unidade = db.unidade
            self.servico = db.servico
            self.dados_sat = db.dados_sat
            self.is_dev = db.is_dev
            self.nome_arquivo = db.nome_arquivo
            self.vencimento = db.data_vencimento
            self.logger.info(
                "Inicializando a classe Sat com os dados do banco de dados."
            )
            self.pm = ProcessManager()
            self.execution()

    def execution(self) -> bool:
        try:
            locators: SatSiteLocators = SatSiteLocators()
            driver = Browser()
            self.logger.info(
                f"Atualizando o Status para: {StatusExecucao.RUNNING.value}"
            )
            self.pm.update_status_execucao(
                self.hash_processo, self.session_id, StatusExecucao.RUNNING
            )
            self.logger.info("Executando o processo de login.")
            self.logger.info(f"Acessando a URL:{self.url}")
            driver.get(self.url)

            self.logger.info("Preenchendo o campo de login.")
            driver.send_text(xpath=locators.login_page.login, text=self.login)

            self.logger.info("Preenchendo o campo de senha.")
            driver.send_text(xpath=locators.login_page.senha, text=self.senha)

            self.logger.info("Clicando no botão de entrar.")
            driver.click(xpath=locators.login_page.entrar)

            self.logger.info("Acessando o menu de clientes.")
            driver.click(xpath=locators.menu_link.menu_clientes)

            self.logger.info(
                f"Pesquisando cliente com filtro: {self.nome_filtro}")
            driver.send_text(
                xpath=locators.cliente_page.pesquisa_cliente,
                text=self.nome_filtro,
            )
            driver.find_element(xpath=locators.cliente_page.pesquisa_cliente).send_keys(
                Keys.ENTER
            )

            # Verificar se a grid filtrou apenas 1 cliente
            grid_sem_registros = driver.check_for_error(
                xpath=locators.cliente_page.grid_sem_registros,
                condition="visible",
            )
            if grid_sem_registros:
                sleep(5)
                self.logger.error(
                    "GRID SEM REGISTROS. Nenhum cliente encontrado.")
                self.logger.info("Finalizando a execução e fechando o driver.")
                self.pm.update_status_all(
                    self.hash_processo,
                    self.session_id,
                )
                driver._driver.quit()
                return None
            else:
                self.logger.info("Não houve erros de filtro para o cliente.")

                self.logger.info("Clicando no botão de fatura.")
                driver.click(xpath=locators.cliente_page.botao_fatura)

                self.logger.info(
                    "Aguardando o botão 'Adicionar Fatura' ficar clicável."
                )
                botao_adicionar_fatura = driver.find_element(
                    xpath=locators.fatura_page.botao_adicionar,
                    condition="clickable",
                )
                if botao_adicionar_fatura:
                    self.logger.info("Clicando no botão 'Adicionar Fatura'.")
                    driver.click(xpath=locators.fatura_page.botao_adicionar)
                # Recuperando o arquivo do bucket
                file_path, file = get_files_from_s3(self.nome_arquivo)
                if file_path and file:
                    self.logger.info("Preenchendo o campo da operadora.")
                    campo_operadora = driver.find_element(
                        xpath=locators.fatura_page.operadora,
                        condition="visible",
                    )
                    if campo_operadora:
                        driver.send_text(
                            xpath=locators.fatura_page.operadora,
                            text=self.operadora,
                        )

                        self.logger.info(
                            "Preenchendo o campo de serviço do sat.")
                        driver.send_text(
                            xpath=locators.fatura_page.linha, text=self.dados_sat
                        )

                    self.logger.info(f"Enviando o arquivo: {file}")
                    driver.find_element(
                        xpath=locators.fatura_page.campo_arquivo
                    ).send_keys(file_path)
                    driver.find_element(
                        xpath=locators.fatura_page.campo_input
                    ).send_keys(file_path)

                    self.logger.info("Preenchendo a data de vencimento")
                    driver.send_text(
                        xpath=locators.fatura_page.data,
                        text=self.vencimento,
                        clear=True,
                    )

                    self.logger.info("Selecionando a categoria 'PAGAR'.")
                    driver.select_option(
                        xpath=locators.fatura_page.combo_categorias,
                        option="PAGAR",
                    )
                    try:
                        self.logger.info(
                            f"Selecionando a filial: {self.unidade}")
                        driver.select_option_by_similarity(
                            xpath=locators.fatura_page.combo_filial,
                            option=self.unidade,
                        )
                    except:
                        self.logger.error(
                            "Não encontrou unidade por similaridade")
                    self.logger.info("Clicando no botão 'Cadastrar'.")
                    driver.click(xpath=locators.fatura_page.botao_cadastrar)
                    sleep(3)
                else:
                    self.logger.error("Erro ao resgatar arquivo no s3")
                    self.pm.update_status_all(
                        self.hash_processo,
                        self.session_id,
                    )
                    driver._driver.quit()
                    return False

            self.logger.info(
                f"Atualizando o Status para: {StatusExecucao.UPLOADED_SAT.value}"
            )
            self.pm.update_status_all(
                self.hash_processo,
                self.session_id,
                status_execucao=StatusExecucao.UPLOADED_SAT,
                status_processo=StatusExecucao.UPLOADED_SAT,
            )

            self.logger.info("Finalizando a execução e fechando o driver.")
            driver._driver.quit()
            return True
        except Exception as error:
            self.logger.error(f"Erro:{error}")
            self.pm.update_status_all(
                self.hash_processo,
                self.session_id,
            )
            driver._driver.quit()
            return False


class LoginPage:
    login = "//input[@name='login']"
    senha = "//input[@name='senha']"
    entrar = "//input[@value='Entrar']"


class ClientePage:
    pesquisa_cliente = "//input[@placeholder='Buscando algo ?']"
    botao_fatura = "//a[contains(@href, 'fatura')][img[contains(@src, 'ref.png')]]"
    grid_sem_registros = "//td[contains(normalize-space(text()), 'Sua busca não trouxe nenhum resultado')]"


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
    combo_filial = "//select[@id='categorias' and @name='input[id_filial]']"
    botao_cadastrar = "//input[@class='envia' and @name='cadastar']"


class MenuLink:
    menu_clientes = "//a[normalize-space(text())='Clientes']"


class SatSiteLocators:
    login_page = LoginPage
    menu_link = MenuLink
    cliente_page = ClientePage
    fatura_page = FaturaPage
