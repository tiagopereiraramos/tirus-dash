from datetime import datetime
from io import BytesIO
from time import sleep

import requests
from PyPDF2 import PdfReader, PdfWriter
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from util.dataclass import StatusExecucao
from services.controle_execucao_processo_service import ProcessManager
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from util.driver import Browser
from util.log import Logs
from util.utilities import (
    get_download_directory,
    upload_file_to_s3,
    sanitize_filename,
)

logger = Logs.return_log(__name__)


class Digitalnet:

    def __init__(self, parameters, logger):
        # Informações de configuração
        self.__dict__.update(parameters.__dict__)
        self.logger = logger
        self.pm = ProcessManager()
        self.execution()

    def obter_tres_primeiros_digitos_cnpj(self, cnpj):
        return str(cnpj)[:3] if len(str(cnpj)) >= 3 else None

    def salvar_pdf(self, response_content, file_name):
        download_directory = get_download_directory()
        file_path = f"{download_directory}/{file_name}"
        try:
            with open(file_path, "wb") as pdf_file:
                pdf_file.write(response_content)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar PDF: {str(e)}")
            return False

    def realizar_login(self) -> bool:
        try:
            self.logger.info("Abrindo URL de login")
            self.browser.get(self.url)

            self.logger.info("Inserindo credenciais")
            username_field = self.browser.find_element(
                xpath=self.locators.login_page.user)
            username_field.send_keys(self.login)

            if not self.browser.check_for_error(
                    xpath=self.locators.login_page.login_geral):
                botao_entrar = self.browser.find_element(
                    xpath=self.locators.login_page.entrar)
                if botao_entrar:
                    botao_entrar.click()
            else:
                # Se o botão de login geral não estava presente, então clicou no botao entrar, agora teho que procurar o botao de login geral novaamente
                self.logger.info("Clicando no botão de login geral")
                if self.browser.check_for_error(xpath=self.locators.login_page.login_geral):
                    self.logger.info("Botão de login geral encontrado")
                    self.browser.click(
                        xpath=self.locators.login_page.login_geral)

                    self.logger.info(
                        "Aguardando o carregamento da página após o clique no botão de login geral")
                    # Agora si, tenho que digitar login e esenha novamente.
                    username_field = self.browser.find_element(
                        xpath=self.locators.login_page.user)
                    username_field.send_keys(self.login)
                    password_field = self.browser.find_element(
                        xpath=self.locators.login_page.senha)
                    password_field.send_keys(self.senha)
                    self.browser.click(
                        xpath=self.locators.login_page.entrar)
                    # Aguarda o carregamento da página após o login
                    self.logger.info(
                        "Aguardando o carregamento da página após o login")
                    sleep(3)
                    return True
        except Exception as e:
            self.logger.error(f"Erro ao realizar login: {str(e)}")
            return False

    def selecionar_fatura(self):
        sleep(5)
        self.browser.click(
            xpath=self.locators.contrato.invoice_id)
        self.logger.info("Aguardando o carregamento da página de fatura")
        sleep(2)
        self.logger.info("Capturando o código da empresa")
        codigo_empresa = self.browser._driver.title
        return codigo_empresa

    def capturar_dados_fatura(self) -> tuple:
        try:
            # TODO melhorar essa lógica depois
            faturas_pendentes = self.browser.check_for_error(
                xpath=self.locators.dados_fatura.faturas_pendentes
            )
            if faturas_pendentes:
                self.logger.warning(
                    "Não existem faturas pendentes para este contrato.")
                return None
            else:
                self.logger.info("Faturas pendentes encontradas.")
                self.browser.click(
                    xpath=self.locators.dados_fatura.pagar_agora)
                sleep(3)
                self.logger.info("Capturando o Vencimento da Fatura.")
                vencimento_campo = self.browser.find_element(
                    xpath=self.locators.dados_fatura.vencimento_campo)
                if vencimento_campo:
                    self.logger.info("Campo de vencimento encontrado.")
                    vencimento = vencimento_campo.text
                    if vencimento:
                        self.logger.info(
                            f"Vencimento encontrado: {vencimento}")
                        vencimento_formatado = vencimento.replace("/", "-")
                        return vencimento_formatado, vencimento
                    else:
                        self.logger.error("Vencimento não encontrado.")
                        return None
        except Exception as e:
            self.logger.error(f"Erro ao capturar dados da fatura: {str(e)}")
            return None

    def mesclar_pdfs(
        self,
        pdf_binario1,
        pdf_binario2,
    ):

        pdf_file1 = BytesIO(pdf_binario1)
        pdf_file2 = BytesIO(pdf_binario2)

        # Criar leitores para cada PDF a partir dos binários
        pdf1 = PdfReader(pdf_file1)
        pdf1.decrypt(self.obter_tres_primeiros_digitos_cnpj(self.cnpj))
        pdf2 = PdfReader(pdf_file2)

        # Criar um writer para gerar o PDF final
        pdf_writer = PdfWriter()

        # Adicionar todas as páginas do primeiro PDF
        for page in pdf1.pages:
            pdf_writer.add_page(page)

        # Adicionar todas as páginas do segundo PDF
        for page in pdf2.pages:
            pdf_writer.add_page(page)

        # Salvar o PDF mesclado em um objeto BytesIO (em memória)
        pdf_saida = BytesIO()
        pdf_writer.write(pdf_saida)

        # Retornar o binário do PDF mesclado
        return pdf_saida.getvalue()

    def baixar_fatura(self, vencimento, codigo_empresa):
        header_fatura = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjIxNGE2MDRjLTUyNjktNDAxMS1iY2JkLTRmMmRmNTlkOTk1NSIsIm5hbWUiOiJTQU5UQSBJWkFCRUwgVFJBTlNQT1JURSBSRVZFTkRFRE9SIFJFVEFMSElTVEEgTFREQSIsImluaXRpYWxzIjoiU0wiLCJ0eElkIjoiMDA0MTE1NjYwMDAxMDYiLCJjb21wYW55SWQiOiJkMTYxMWU2Ni00MjI0LTQwNzAtYTY5My1jNDkyMWI3ZmI2M2EiLCJlcnBDdXN0b21lcklkIjoiMTQwNzAwIiwiZXJwVG9rZW4iOiIiLCJyb2xlIjpbIlZpZXdJbnZvaWNlcyIsIlBheUludm9pY2VzIiwiU2hvd0ludm9pY2VzIiwiVmlld0ludm9pY2VSZWZlcmVuY2UiLCJTaG93Q29udHJhY3RzIiwiU2hvd1BqRmlzY2FsRG9jdW1lbnRzIiwiVmlld1BkZkludm9pY2VzIiwiVmlld0NvbnRyYWN0IiwiVW5sb2NrQ29udHJhY3QiLCJWaWV3QWxsSW52b2ljZXMiLCJDaGFuZ2VQYXltZW50TWV0aG9kIiwiVmlld0Zpc2NhbERvY3VtZW50cyIsIkNhblJlZ2lzdGVyUGVuZGluZ0JpbGxldCIsIlNob3dDb25uZWN0aW9uIiwiVmlld0F1dGhlbnRpY2F0aW9uQWNjb3VudGluZyIsIkNhbk5lZ290aWF0ZSIsIlZpZXdDb250cmFjdERvY3VtZW50cyIsIlNwZWVkUmVzdHJpY3Rpb25Db250cmFjdCIsIlZpZXdBbGxDb250cmFjdHNJbnZvaWNlcyIsIlZpZXdEb3dubG9hZEZESW5JbnZvaWNlcyJdLCJuYmYiOjE3MjkxMjIyMzAsImV4cCI6MTcyOTEyMjUzMCwiaWF0IjoxNzI5MTIyMjMwLCJpc3MiOiJodHRwczovL2FwaS5wb3J0YWwuN2F6LmNvbS5iciJ9.uvh94jRESWCfRYpKrB7fqySr6CW5TM3LIrtXr-i7PXg",
            "cache-control": "no-cache",
            "origin": "https://sac.digitalnetms.com.br",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://sac.digitalnetms.com.br/",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        }

        header_nf = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjIxNGE2MDRjLTUyNjktNDAxMS1iY2JkLTRmMmRmNTlkOTk1NSIsIm5hbWUiOiJTQU5UQSBJWkFCRUwgVFJBTlNQT1JURSBSRVZFTkRFRE9SIFJFVEFMSElTVEEgTFREQSIsImluaXRpYWxzIjoiU0wiLCJ0eElkIjoiMDA0MTE1NjYwMDAxMDYiLCJjb21wYW55SWQiOiJkMTYxMWU2Ni00MjI0LTQwNzAtYTY5My1jNDkyMWI3ZmI2M2EiLCJlcnBDdXN0b21lcklkIjoiMTQwNzAwIiwiZXJwVG9rZW4iOiIiLCJyb2xlIjpbIlZpZXdJbnZvaWNlcyIsIlBheUludm9pY2VzIiwiU2hvd0ludm9pY2VzIiwiVmlld0ludm9pY2VSZWZlcmVuY2UiLCJTaG93Q29udHJhY3RzIiwiU2hvd1BqRmlzY2FsRG9jdW1lbnRzIiwiVmlld1BkZkludm9pY2VzIiwiVmlld0NvbnRyYWN0IiwiVW5sb2NrQ29udHJhY3QiLCJWaWV3QWxsSW52b2ljZXMiLCJDaGFuZ2VQYXltZW50TWV0aG9kIiwiVmlld0Zpc2NhbERvY3VtZW50cyIsIkNhblJlZ2lzdGVyUGVuZGluZ0JpbGxldCIsIlNob3dDb25uZWN0aW9uIiwiVmlld0F1dGhlbnRpY2F0aW9uQWNjb3VudGluZyIsIkNhbk5lZ290aWF0ZSIsIlZpZXdDb250cmFjdERvY3VtZW50cyIsIlNwZWVkUmVzdHJpY3Rpb25Db250cmFjdCIsIlZpZXdBbGxDb250cmFjdHNJbnZvaWNlcyIsIlZpZXdEb3dubG9hZEZESW5JbnZvaWNlcyJdLCJuYmYiOjE3MjkxNjg1NDEsImV4cCI6MTcyOTE2ODg0MSwiaWF0IjoxNzI5MTY4NTQxLCJpc3MiOiJodHRwczovL2FwaS5wb3J0YWwuN2F6LmNvbS5iciJ9.9UFM5V0s42MJjoTGeLcRDfNse1Tq12EuRMKp_B97jXU",
            "cache-control": "no-cache",
            "origin": "https://sac.digitalnetms.com.br",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://sac.digitalnetms.com.br/",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        }

        response = requests.get(
            f"https://api.portal.cs30.7az.com.br/invoices/{codigo_empresa}/pdf",
            headers=header_fatura,
        )

        response2 = requests.get(
            f"https://api.portal.cs30.7az.com.br/invoices/fiscal-documents/{codigo_empresa}",
            headers=header_nf,
        )

        pdf_mesclado = self.mesclar_pdfs(response.content, response2.content)

        new_name_file = f"{self.hash_cron_cad}_{vencimento}.pdf"
        new_name_file = sanitize_filename(new_name_file)
        self.logger.info(f"Salvando fatura como: {new_name_file}")
        if self.salvar_pdf(pdf_mesclado, new_name_file):
            self.logger.info("Fatura salva com sucesso")
            return new_name_file
        else:
            self.logger.error("Erro ao baixar a fatura.")
            return None

    def selecionar_contrato(self):
        sleep(3)
        if self.browser.check_for_error(
                xpath=self.locators.contrato.todos_os_contratos):
            self.logger.info("Botão de contratos encontrado")
            self.browser.click(
                xpath=self.locators.contrato.todos_os_contratos)
            self.browser.click(xpath=self.locators.contrato.mudar_contrato)
            aguarda_item_tela = self.browser.find_elements(
                xpath=self.locators.contrato.aguarda_item_tela)
            if aguarda_item_tela:
                self.logger.info(
                    "Aguardando o carregamento da tela de contratos")
                contratos = self.browser.find_elements(
                    xpath=self.locators.contrato.contratos)
                if contratos:
                    self.logger.info("Contratos encontrados")
                    for contrato in contratos:
                        if self.filtro in contrato.text:
                            contrato.click()
                            break
        else:
            self.logger.info('Botão de contratos não encontrado')
            self.logger.info("Cliente de contrato único com a operadora")

    def execution(self):
        try:
            self.locators: DigitalnetSiteLocators = DigitalnetSiteLocators()
            self.browser = Browser()
            self.pm.update_status_execucao(
                self.hash_processo, self.session_id, StatusExecucao.RUNNING
            )
            if self.realizar_login():
                self.selecionar_contrato()
                vencimento_formatado, vencimento = self.capturar_dados_fatura()
                if vencimento_formatado is not None:
                    title_page = self.selecionar_fatura().split(" | ")[1]
                    arquivo_fatura = self.baixar_fatura(
                        vencimento_formatado, title_page)
                    arquivo_fatura = upload_file_to_s3(arquivo_fatura)
                    if arquivo_fatura:
                        message = "Fatura baixada com sucesso"
                        self.pm.update_status_execucao(
                            self.hash_processo,
                            self.session_id,
                            StatusExecucao.COMPLETED,
                        )
                        self.logger.info("Execução atualizado para COMPLETED")
                        self.pm.create_fatura(
                            self.hash_processo, arquivo_fatura, vencimento
                        )
                        self.logger.info(
                            "Fatura atualizada no banco de dados com venciemento e nome do arquivo"
                        )
                        self.pm.update_status_processo(
                            self.hash_processo,
                            StatusExecucao.COMPLETED,
                        )
                        self.logger.info("Processo atualizado para COMPLETED")
                    else:
                        message = "Erro ao realizar o download da fatura"
                        self.pm.update_status_execucao(
                            self.hash_processo,
                            self.session_id,
                            StatusExecucao.FAILED,
                            message,
                        )
                else:
                    message = "Erro ao encontrar a fatura. Não existe fatura disponível."
                    self.pm.update_status_execucao(
                        self.hash_processo,
                        self.session_id,
                        StatusExecucao.FAILED,
                        message,
                    )
            else:
                message = "Erro ao realizar o login. Verifique as credenciais."
                self.pm.update_status_execucao(
                    self.hash_processo,
                    self.session_id,
                    StatusExecucao.FAILED,
                    message,
                )

        except Exception as e:
            message = f"Erro na execução: {str(e)}"
            self.pm.update_status_execucao(
                self.hash_processo,
                self.session_id,
                StatusExecucao.FAILED,
                message,
            )
        finally:
            self.browser.close()


class LoginPage:
    user = "//input[@id='cpfcnpj']"
    senha = "//input[@id='passwd']"
    entrar = "//button[@id='loginButton']"
    login_geral = "//button[contains(text(), 'Fazer login')]"


class Contrato:
    todos_os_contratos = "//span[@class='ml-3 text-sm font-medium text-gray-900']/preceding-sibling::div[1]"
    mudar_contrato = "//button[@tabindex='2']"
    aguarda_item_tela = "//div[@class='flex items-center gap-1']"
    contratos = "//div[@class='flex items-center gap-1']"
    invoice_id = "//div[@id='invoiceFirstElement']"


class DadosFatura:
    faturas_pendentes = "(//p[contains(@class, 'text-center') and contains(text(), 'Não existem faturas pendentes para este contrato.')])[1]"
    pagar_agora = "//button[@type='button' and contains(@class, 'btn-base-submit') and contains(text(), 'Pagar agora')]"
    vencimento_campo = "//div[contains(@class, 'card-invoice-text-color') and contains(@class, 'font-bold')]"


class DigitalnetSiteLocators:
    login_page = LoginPage
    contrato = Contrato
    dados_fatura = DadosFatura
