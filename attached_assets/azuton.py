from time import sleep
from util.utilities import get_latest_file, upload_file_to_s3, get_current_month_year
from bs4 import BeautifulSoup
from configs.config import getenv
from util.driver import Browser
from util.dataclass import FaturaEmail, EmailConfig, StatusExecucao
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from services.gmail_service import GmailService
from selenium.common.exceptions import WebDriverException
from db.mongo import Database
from services.controle_execucao_processo_service import ProcessManager
from util.log import Logs, log_process
from services.pdf_service import PDFService
import os
from pathlib import Path


class Azuton:
    """
    Classe responsável por executar o fluxo de extração e processamento de faturas
    enviadas por e-mail e acessadas via navegador.
    """

    def __init__(self):
        """
        Inicializa a classe Azuton, configurando banco de dados, logger e gerenciador de processos.
        """
        self.faturas_email = [FaturaEmail]
        self.db = Database()
        self.logger = Logs.return_log(__name__)
        self.pm = ProcessManager()
        self.logger.debug("Iniciando Azuton")
        self.execution()

    def found_proc_create_execution(
        self, cnpj_mascara: str, path_fatura: str, vencimento: str
    ):
        """
        Verifica se o CNPJ pertence a um cadastro existente e cria uma nova execução de fatura.
        """
        self.logger.debug(f"Verificando CNPJ: {cnpj_mascara}")
        cnpj_mascara = cnpj_mascara.replace("-", "").replace(".", "").replace("/", "")
        cad = self.db.cadastro.read({"cnpj": cnpj_mascara, "operadora": "AZUTON"})  # type: ignore
        if cad:
            self.logger.debug("Cadastro encontrado, verificando status do Processo")
            if (
                isinstance(cad, list) and cad
            ):  # Verifica se é uma lista e não está vazia
                hash_cron_cad = cad[0].hash_cron_cad  # Ou outro valor padrão desejado
            else:
                hash_cron_cad = cad.hash_cron_cad  # Ou outro valor padrão desejado
            proc = self.db.processo.read(
                {
                    "hash_execucao": hash_cron_cad,
                    "mes_ano": get_current_month_year(),
                }
            )
            if proc:
                if (
                    proc.status_final != StatusExecucao.UPLOADED_SAT.value
                    and proc.status_final != StatusExecucao.COMPLETED.value
                ):
                    self.pm.update_status_processo(
                        processo_id=proc.processo_id,
                        novo_status=StatusExecucao.COMPLETED,
                    )
                    self.pm.create_fatura(
                        processo_id=proc.processo_id,
                        nome_arquivo=path_fatura,
                        vencimento=vencimento,
                    )
                    self.pm.create_execucao(
                        processo_id=proc.processo_id,
                        hash_execucao=hash_cron_cad,
                        nao_cria_sat=True,
                    )
                    self.logger.debug("Fatura processada com sucesso")
                else:
                    self.logger.warning(
                        "Para esse Cadastro encontrado, o Processo já encontra-se com a fatura baixada"
                    )

    def fetch_pdf_page_content(
        self,
        pdf_boleto,
        pdf_fatura,
        baixar_boleto: bool = True,
        baixar_fatura: bool = True,
    ):
        """
        Abre um navegador, acessa a URL fornecida e tenta baixar um PDF, se necessário.
        """
        self.logger.debug(f"Acessando URL: {pdf_boleto}")
        arquivo_baixado = ""
        try:
            driver = Browser()
            driver._driver.get(pdf_boleto)
            sleep(10)
        except WebDriverException:
            self.logger.warning("Erro ao acessar a URL fornecida")
            driver._driver.refresh()
            sleep(10)
        if baixar_boleto:
            try:
                driver.find_element("//button[@id='download' ]").click()
                arquivo_baixado_boleto = get_latest_file(".pdf", "Boleto")
                self.logger.debug("Arquivo baixado com sucesso")
                response_boleto = driver._driver.page_source
                driver._driver.close()
            except:
                self.logger.error(
                    "Tempo de espera esgotado. A página não carregou completamente."
                )
                driver._driver.close()
                return None
        if baixar_fatura:
            try:
                self.logger.debug(f"Acessando URL: {pdf_fatura}")
                driver = Browser(True)
                driver._driver.get(pdf_fatura)
                sleep(8)
                driver._driver.close()
            except:
                self.logger.error(
                    "Tempo de espera esgotado. A página não carregou completamente."
                )
                driver._driver.refresh()

            arquivo_baixado_fatura = get_latest_file(".pdf", "Fatura")

        if arquivo_baixado_fatura and arquivo_baixado_boleto:
            nome_arquivo = Path(arquivo_baixado_fatura).name
            nome_arquivo = "Boleto_" + nome_arquivo
            pdf = PDFService()
            arquivo_baixado = pdf.merge_pdfs(
                [arquivo_baixado_boleto, arquivo_baixado_fatura], nome_arquivo
            )
            arquivo_baixado = upload_file_to_s3(arquivo_baixado)
            os.remove(arquivo_baixado_fatura)
            os.remove(arquivo_baixado_boleto)

        return (
            (response_boleto, arquivo_baixado)
            if response_boleto and arquivo_baixado
            else None
        )

    def extract_client_details(self, html_content):
        """
        Extrai nome e CNPJ do cliente a partir do HTML da página.
        """
        self.logger.debug("Extraindo detalhes do cliente")
        soup = BeautifulSoup(html_content, "html.parser")
        pagador = soup.find("span", class_="value name")
        nome_cliente = (
            pagador.get_text(strip=True)
            if pagador
            else "Nome do cliente não encontrado"
        )
        cnpj_info = soup.find("li", class_="dadosPagador")
        cnpj_cliente = (
            cnpj_info.get_text(strip=True).split("CNPJ: ")[-1]
            if cnpj_info and "CNPJ:" in cnpj_info.get_text()
            else "CNPJ não encontrado"
        )
        return nome_cliente, cnpj_cliente

    def extract_email_info(self, html_content: str) -> FaturaEmail:
        """
        Extrai informações relevantes do e-mail, como cliente, vencimento e valor total.
        """
        self.logger.debug("Extraindo informações do e-mail")
        soup = BeautifulSoup(html_content, "html.parser")
        cliente_tag = soup.find(string=lambda text: text and "Olá" in text)
        cliente = (
            cliente_tag.find_next("b").get_text(strip=True)
            if cliente_tag
            else "Cliente não encontrado"
        )
        data_vencimento_tag = soup.find(
            string=lambda text: "Data de vencimento:" in text
        )
        data_vencimento = (
            data_vencimento_tag.find_next("b").get_text(strip=True)
            if data_vencimento_tag
            else "Data não encontrada"
        )
        valor_total_tag = soup.find(string=lambda text: "Valor devido:" in text)
        valor_total = (
            valor_total_tag.find_next("b").get_text(strip=True)
            if valor_total_tag
            else "Valor não encontrado"
        )
        numero_fatura_tag = soup.find(string=lambda text: "Fatura:" in text)
        numero_fatura = (
            numero_fatura_tag.find_next("b").get_text(strip=True)
            if numero_fatura_tag
            else "Fatura não encontrada"
        )
        boleto_link = next(
            (
                botao["href"]
                for botao in soup.find_all("a", href=True)
                if "BAIXAR BOLETO" in botao.get_text()
            ),
            "",
        )
        fatura_link = next(
            (
                botao["href"]
                for botao in soup.find_all("a", href=True)
                if "BAIXAR FATURA" in botao.get_text()
            ),
            "",
        )
        return FaturaEmail(
            cliente,
            data_vencimento,
            valor_total,
            numero_fatura,
            boleto_link,
            fatura_link,
        )

    @log_process
    def execution(self):
        """
        Executa o processo de recuperação de e-mails e processamento de faturas.
        """
        self.logger.info("Iniciando execução do processo")
        email_config = EmailConfig(
            user_email="administrativo@bgtele.com.br",
            query="mailsender@clickdigital.com.br",
            credentials_file=getenv("CREDENTIALS_GOOGLE"),
        )
        gmail_service = GmailService(email_config)
        emails_info = gmail_service.fetch_and_move_emails()

        for info in emails_info:
            self.logger.info("Iniciando a extração de emails da conta")
            fatura_email = self.extract_email_info(info)
            html_content, arquivo_baixado = self.fetch_pdf_page_content(
                fatura_email.baixar_boleto, fatura_email.baixar_fatura
            )
            fatura_email.caminho_boleto = arquivo_baixado
            razao_social, cnpj = self.extract_client_details(html_content)
            fatura_email.razao_social = razao_social
            fatura_email.cnpj = cnpj
            self.found_proc_create_execution(
                fatura_email.cnpj,
                fatura_email.caminho_boleto,
                fatura_email.data_vencimento,
            )
            self.faturas_email.append(fatura_email)
        self.logger.info("Execução concluída")
