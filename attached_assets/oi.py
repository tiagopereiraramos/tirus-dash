import os
from datetime import datetime, timedelta
from urllib.parse import urlencode
from platformdirs import user_downloads_dir
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from services.controle_execucao_processo_service import ProcessManager
from util.dataclass import Execucao, Fatura, Processo, StatusExecucao
from util.driver import BrowserChrome
from util.log import Logs, log_process
from util.utilities import (
    contains_similar_substring,
    get_download_directory,
    sanitize_filename,
    upload_file_to_s3,
)


# Adiciona informações do cliente e processo aos logs
class Oi:
    def __init__(self, parameters, logger):
        # Informações de configuração
        self.__dict__.update(parameters.__dict__)
        self.logger = logger
        self.browser = BrowserChrome(self.is_dev, logger)
        self.pm = ProcessManager()
        self.db = parameters.db
        self.execution()

    @staticmethod
    def salvar_pdf(self, response_content, file_name):
        download_directory = f"{user_downloads_dir()}/TIRUS_DOWNLOADS"
        file_path = os.path.join(download_directory, file_name)
        try:
            with open(file_path, "wb") as pdf_file:
                pdf_file.write(response_content)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar PDF: {str(e)}")
            return False

    def realizar_login(self):

        self.logger.info("Abrindo URL de login")
        self.browser.driver.get(self.url)

        # Trocar para o iframe de login
        iframe = self.browser.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//iframe[@src='/api/login/customer']")
            )
        )
        self.browser.driver.switch_to.frame(iframe)

        self.logger.info("Inserindo credenciais")
        username_field = self.browser.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@class='email']"))
        )
        password_field = self.browser.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@class='password']"))
        )
        username_field.send_keys(self.login)
        password_field.send_keys(self.senha)

        login_button = self.browser.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@id='loginButtonApp']"))
        )
        login_button.click()

        # Espera o carregamento da página após o login
        self.logger.info("Login realizado, aguardando carregamento")
        WebDriverWait(self.browser.driver, 10).until(
            EC.invisibility_of_element_located(
                (By.XPATH, '//i[@class="sc-hKwDye fbVeFn sc-jRQBWg iZxZFG"]')
            )
        )
        self.browser.driver.switch_to.default_content()

    def selecionar_cnpj(self):
        self.logger.info(f"Buscando faturas para o CNPJ: {self.cnpj}")
        contas_abertas_button = self.browser.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[@data-context='btn_ver_contas']",
                )
            )
        )
        contas_abertas_button.click()

        cnpj_space = self.browser.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//label[@class='sc-bdvvtL fNKGRl' and text()='CNPJ']/../div/div",
                )
            )
        )
        """ cnpj_space.click()

        cnpj_input = self.browser.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//label[@class='sc-bdvvtL fNKGRl' and text()='CNPJ']/../div/div/div/div/div/input",
                )
            )
        )
        cnpj_input.send_keys(self.cnpj)
        cnpj_input.send_keys(Keys.RETURN) """

    def filtrar_fatura(self):
        try:

            self.acessar_todas_as_contas(self.cnpj)
            btn_filter = self.browser.driver.find_element(
                By.XPATH, "//button[@data-context='btn_filtrar']"
            )
            btn_filter.click()

            tabela_fatura = self.browser.driver.find_element(
                By.XPATH, "//tbody[@class='sc-gsDKAQ sc-dkPtRN erBbkF cwekcn']"
            )
            tabela_fatura_elements = tabela_fatura.find_elements(
                By.TAG_NAME, "tr")

            if tabela_fatura_elements:
                self.logger.info(
                    f"{len(tabela_fatura_elements)} faturas encontradas")
                for fatura in tabela_fatura_elements:
                    servico_text = fatura.find_element(
                        By.XPATH, ".//td[2]").text
                    if self.servico.split(" ")[1].replace("-", "") in servico_text:
                        fatura.click()
                        self.logger.info(
                            f"Fatura encontrada para o serviço: {self.servico}"
                        )
                        return True
                    elif contains_similar_substring(
                        original_site=servico_text,
                        servico_banco=self.servico.split(
                            " ")[1].replace("-", ""),
                    ):
                        fatura.click()
                        self.logger.info(
                            f"Fatura encontrada para o serviço: {self.servico}"
                        )
                        return True
            return False
        except Exception as err:
            return False

    def capturar_dados_fatura(self):
        vencimento = self.browser.driver.find_element(
            By.XPATH,
            "//p[@class='sc-bdvvtL dxOhdO' and text()='Vencimento']/following-sibling::*[1]",
        ).text
        vencimento_formatado = vencimento.replace("/", "-")
        self.logger.info(
            f"Data de vencimento da fatura: {vencimento_formatado}")
        return vencimento_formatado, vencimento

    def baixar_fatura(self, vencimento):
        element_download = self.browser.driver.find_element(
            By.XPATH,
            "//a[@class='sc-eCImPb jxJukv' and @data-context='btn_contestar_conta']",
        )
        link_empresa = element_download.get_attribute("href")
        codigo_empresa = link_empresa.split("/")[-1]
        self.logger.info("Código da empresa capturado com sucesso")

        session = requests.Session()
        for cookie in self.browser.driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"])

        headers = {"accept": "application/json", "user-agent": "Mozilla/5.0"}

        response = session.get(
            f"https://portaloisolucoes.oi.com.br/api/invoices/pdf/{codigo_empresa}",
            headers=headers,
        )

        new_name_file = f"{self.hash_cron_cad}_{vencimento}.pdf"
        new_name_file = sanitize_filename(new_name_file)
        self.logger.info(f"Salvando fatura como: {new_name_file}")
        if self.salvar_pdf(
            self, response_content=response.content, file_name=new_name_file
        ):
            self.logger.info("Fatura salva com sucesso")
            return new_name_file
        else:
            self.logger.error("Erro ao baixar a fatura")
            return None

    def return_period_process(self):
        try:
            p = self.db.processo.read({"processo_id": self.hash_processo})
            if p:
                # Validação do formato do filtro de data
                try:
                    ref_date = datetime.strptime(p.mes_ano, "%Y-%m")
                except ValueError:
                    raise ValueError(
                        "O formato de 'filtro_data' deve ser 'YYYY-MM'.")

                # Gerar datas de início e fim do mês
                ref_date_start = ref_date.strftime("%Y-%m-01T04:00:00.000Z")
                ref_date_end = (ref_date + timedelta(days=32)).replace(
                    day=1
                ) - timedelta(days=1)
                ref_date_end = ref_date_end.strftime("%Y-%m-%dT04:00:00.000Z")
                return ref_date_start, ref_date_end
        except Exception as e:
            self.logger.error(e)

    def acessar_todas_as_contas(self, cnpj):
        """
        Gera a URL com base nos parâmetros fixos e no intervalo de datas obtido pela função `return_period_process`.
        Acessa e clica no link da página no Selenium.

        :param driver: Instância do WebDriver do Selenium.
        :param cnpj: CNPJ a ser usado no filtro.
        """
        # Parâmetros fixos
        limit = 10
        offset = 0
        payment_status = ["em_aberto", "sem_status"]

        # Obter intervalo de datas do método `return_period_process`
        ref_date_start, ref_date_end = self.return_period_process()

        # Gerar a URL dinâmica
        params = {
            "cnpj": cnpj,
            "limit": limit,
            "offset": offset,
            "paymentStatus": payment_status,
            "refDateStart": ref_date_start,
            "refDateEnd": ref_date_end,
        }
        query_string = urlencode(params, doseq=True)
        url = f"https://portaloisolucoes.oi.com.br/todas-as-contas?{query_string}"

        # Acessar a URL no navegador
        self.browser.driver.get(url)

        # Validação de carregamento da página (opcional)
        try:
            assert self.browser.driver.current_url.startswith(
                "https://portaloisolucoes.oi.com.br/todas-as-contas"
            )
            print("Página carregada com sucesso!")
        except AssertionError:
            print("Erro ao carregar a página. Verifique a URL.")

    @log_process
    def execution(self):
        try:
            self.logger.info("Iniciando execução")
            self.pm.update_status_execucao(
                self.hash_processo, self.session_id, StatusExecucao.RUNNING
            )
            self.realizar_login()
            self.selecionar_cnpj()

            if self.filtrar_fatura():
                vencimento_formatado, vencimento = self.capturar_dados_fatura()
                arquivo_fatura = self.baixar_fatura(vencimento_formatado)
                arquivo_fatura = upload_file_to_s3(arquivo_fatura)
                if arquivo_fatura:
                    self.pm.update_status_execucao(
                        self.hash_processo,
                        self.session_id,
                        StatusExecucao.COMPLETED,
                    )
                    self.logger.info("Execução atualizado para COMPLETED")
                    self.pm.create_fatura(
                        self.hash_processo,
                        arquivo_fatura,
                        vencimento_formatado,
                    )
                    self.logger.info(
                        "Fatura atualizada no banco de dados com venciemento e nome do arquivo"
                    )
                    self.pm.update_status_all(
                        self.hash_processo,
                        self.session_id,
                        StatusExecucao.COMPLETED,
                        StatusExecucao.COMPLETED,
                    )
                    self.logger.info("Processo atualizado para COMPLETED")
                    self.browser.driver.quit()
                    self.logger.info("Fechando o navegador")
                else:
                    self.pm.update_status_all(
                        self.hash_processo,
                        self.session_id,
                        StatusExecucao.FAILED,
                        StatusExecucao.FAILED,
                        "Processo de download da fatura falhou",
                    )
                    self.logger.info("Erro ao realizar o download da fatura")
                    self.browser.driver.quit()
                    self.logger.info("Fechando o navegador")
            else:
                self.pm.update_status_all(
                    self.hash_processo,
                    self.session_id,
                    StatusExecucao.FAILED,
                    StatusExecucao.FAILED,
                    "Nenhuma fatura correspondente foi encontrada",
                )
                self.logger.info(
                    "Nenhuma fatura correspondente foi encontrada")
                self.browser.driver.quit()
                self.logger.info("Fechando o navegador")
        except Exception as e:
            self.pm.update_status_all(
                self.hash_processo,
                self.session_id,
                StatusExecucao.FAILED,
                StatusExecucao.FAILED,
                f"Erro na execução: {str(e)}",
            )
            self.logger.error(f"Erro na execução: {str(e)}")
            self.browser.driver.quit()
            self.logger.info("Fechando o navegador")
