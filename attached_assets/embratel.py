import base64
import os
from datetime import datetime
from time import sleep

import pdfkit
import PyPDF2
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from services.controle_execucao_processo_service import ProcessManager
from util.dataclass import StatusExecucao
from util.driver import BrowserChrome
from util.utilities import sanitize_filename, upload_file_to_s3


# Adiciona informações do cliente e processo aos logs
class Embratel:
    def __init__(self, parameters, logger):
        # Informações de configuração
        self.__dict__.update(parameters.__dict__)
        self.logger = logger
        self.pm = ProcessManager()
        # Inicia o logger com metadados para o Loki

        self.browser = BrowserChrome(self.is_dev, self.logger)
        self.execution()

    def realizar_login(self):
        self.logger.info("Abrindo URL de login")
        self.browser.driver.get(self.url)

        self.logger.info("Inserindo credenciais")
        username_field = self.browser.wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='login']"))
        )
        password_field = self.browser.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@id='MainContent_password']")
            )
        )

        username_field.send_keys(self.login)
        password_field.send_keys(self.senha)

        login_button = self.browser.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
        )
        login_button.click()

    def merge_pdfs(self, pdf_list):

        self.vencimento_formatado = self.vencimento.replace("/", "-")
        self.logger.info(f"Data de vencimento da fatura: {self.vencimento_formatado}")

        new_name_file = f"{self.hash_cron_cad}_{self.vencimento_formatado}.pdf"
        new_name_file = sanitize_filename(new_name_file)
        self.logger.info(f"Salvando fatura como: {new_name_file}")

        pdf_writer = PyPDF2.PdfWriter()

        for pdf in pdf_list:
            pdf_reader = PyPDF2.PdfReader(pdf)
            for page in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page])

        with open(new_name_file, "wb") as output_pdf:
            pdf_writer.write(output_pdf)

        # Verifica se o PDF de saída foi criado com sucesso
        if os.path.exists(new_name_file):
            self.logger.info(f"PDFs merged successfully into {new_name_file}")

            # Exclui os PDFs originais
            for pdf in pdf_list:
                try:
                    os.remove(pdf)
                    self.logger.info(f"Removed original PDF: {pdf}")
                    return new_name_file
                except Exception as e:
                    self.logger.error(f"Error removing {pdf}: {e}")
            return True
        else:
            self.logger.error("Failed to create the merged PDF.")

    def extrair_data_vencimento(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        # Encontrar a div que contém a Data de Vencimento
        data_vencimento_div = soup.find("div", string="Data de Vencimento")

        if data_vencimento_div:
            # Navegar para a próxima div que contém a data
            data_vencimento = data_vencimento_div.find_next(
                "div", class_="txtPretoBold12"
            )
            if data_vencimento:
                return data_vencimento.get_text(strip=True)

        self.logger.error("Data de vencimento não encontrada.")
        return None

    def html_para_pdf(self, html_content, file_name, css=False):

        if "<meta charset=" not in html_content:
            html_content = f'<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>{html_content}</body></html>'

        if css:
            css_response = requests.get(
                "https://www2.embratel.com.br:9442/EbppCorporativo/scriptcss/styles.css",
                verify=False,
            )
            css_content = css_response.text

            logo_response = requests.get(
                "https://www2.embratel.com.br:9442/EbppCorporativo/imagens/RH-logo-verde-amarelo-transparente.gif",
                verify=False,
            )
            encoded_logo = base64.b64encode(logo_response.content).decode("utf-8")

            html_content = html_content.replace(
                "/EbppCorporativo/imagens/RH-logo-verde-amarelo-transparente.gif",
                f"data:image/gif;base64,{encoded_logo}",
            )

            if "<meta charset=" not in html_content:
                html_content = f'<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>{html_content}</body></html>'

            # Montando o HTML final com o conteúdo, o CSS e a logo
            html_content = f"<style>{css_content}</style>{html_content}"

        options = {
            "page-size": "A4",
            "margin-top": "10mm",
            "margin-right": "10mm",
            "margin-bottom": "10mm",
            "margin-left": "10mm",
            "orientation": "Portrait",
            "background": True,
            "enable-local-file-access": True,
        }
        try:
            # Usar o pdfkit para gerar o PDF a partir do HTML
            pdfkit.from_string(html_content, file_name, options=options)
            self.logger.info(f"PDF salvo com sucesso: {file_name}.pdf")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao gerar PDF: {e}")
            return False

    def acessar_area_download(self):

        self.clicar_elemento_por_xpath(
            "//a[contains(normalize-space(.), 'Fatura On Line')]",
            "logon da fatura",
        )

        data = self.obter_data_atual()

        self.clicar_elemento_por_xpath(f"//option[@value={data}]", "mês da fatura")

        self.clicar_elemento_por_xpath("//input[@id='submit']", "Ok")

        try:
            self.browser.driver.find_element(
                By.XPATH, "//table[contains(@class, 'txtCinzaHand')]/tbody"
            )
        except Exception:
            self.pm.update_status_execucao(
                self.hash_processo, self.session_id, StatusExecucao.FAILED
            )
            self.browser.driver.close()

    def escolha_da_fatura(self):
        try:
            fatura_table = self.browser.driver.find_element(
                By.XPATH, "//table[contains(@class, 'txtCinzaHand')]/tbody"
            )
        except Exception as e:
            self.logger.error(f"Erro ao localizar a tabela de faturas: {e}")
            return

        linhas = fatura_table.find_elements(By.XPATH, ".//tr")
        encontrou = False

        # Tenta extrair conta e dia, se possível
        try:
            conta_alvo, dia_alvo = self.filtro.split("_")
            self.logger.info(
                f"Filtro completo detectado: Conta '{conta_alvo}' com dia '{dia_alvo}'."
            )
        except ValueError:
            conta_alvo = self.filtro.strip()
            dia_alvo = None
            self.logger.info(
                f"Filtro simples detectado: Conta '{conta_alvo}' (sem data)."
            )

        for linha in linhas:
            colunas = linha.find_elements(By.TAG_NAME, "td")

            if len(colunas) < 5:
                continue  # Linha incompleta, ignora

            conta_texto = colunas[1].text.strip()
            data_texto = colunas[4].text.strip()

            # Proteção contra formatos inválidos de data
            if not data_texto or len(data_texto) < 2:
                continue

            if conta_texto == conta_alvo:
                if dia_alvo is None or data_texto[:2] == dia_alvo:
                    try:
                        linha.click()
                        self.logger.info(
                            f"Selecionando a fatura - Conta: {conta_texto} | Data: {data_texto}"
                        )
                        encontrou = True
                        break
                    except Exception as e:
                        self.logger.error(
                            f"Erro ao tentar clicar na linha correspondente: {e}"
                        )
                        return

        if not encontrou:
            msg = f"Nenhuma fatura encontrada para Conta '{conta_alvo}'"
            if dia_alvo:
                msg += f" com data iniciando em '{dia_alvo}'"
            self.logger.warning(msg)

        self.window_id = self.browser.driver.current_window_handle

    def mudar_para_ultima_aba(self):
        todas_as_janelas = self.browser.driver.window_handles
        if len(todas_as_janelas) > 1:
            self.browser.driver.switch_to.window(todas_as_janelas[-1])
        else:
            raise Exception("Não há janelas suficientes abertas para mudar.")

    def fechar_aba_atual_e_voltar(self):
        todas_as_janelas = self.browser.driver.window_handles
        for indice, janela in enumerate(todas_as_janelas):
            if self.window_id in janela:
                self.browser.driver.switch_to.window(todas_as_janelas[indice])
                break

    def baixar_documento(self, xpath, documento, css):

        self.clicar_elemento_por_xpath(
            xpath,
            documento,
        )
        self.mudar_para_ultima_aba()
        sleep(5)
        html_pagina = self.browser.driver.page_source
        if documento == "Boleto.pdf":
            self.vencimento = self.extrair_data_vencimento(html_pagina)
        self.html_para_pdf(html_pagina, documento, css)
        self.fechar_aba_atual_e_voltar()
        return documento

    def acessar_area_nf(self, recorrente: bool = False):
        if recorrente:
            self.fechar_aba_atual_e_voltar()
        self.clicar_elemento_por_xpath(
            "//tr[@onclick=\"return chamaFatura('notaFiscal')\"]",
            "Nota Fiscal",
        )
        self.mudar_para_ultima_aba()

    def baixando_all_docs(self):

        self.lista_docs = []

        fatura = self.baixar_documento(
            "//tr[@onclick=\"return chamaFatura('imprimirFatura')\"]",
            "Fatura.pdf",
            True,
        )
        if fatura:
            self.lista_docs.append(fatura)
        boleto = self.baixar_documento(
            "//tr[@onclick=\"return chamaFatura('imprimirBoleto')\"]",
            "Boleto.pdf",
            False,
        )
        if boleto:
            self.lista_docs.append(boleto)

        icms_xpath = "//td[contains(text(), 'ICMS') and @align='left']"
        iss_xpath = "//td[contains(text(), 'ISS') and @align='left']"
        self.acessar_area_nf()
        try:
            if self.browser.driver.find_element(By.XPATH, icms_xpath):
                icms = self.baixar_documento(icms_xpath, "NF_ICMS.pdf", False)
                self.lista_docs.append(icms)
        except Exception:
            self.logger.info("Não há NF do tipo ICMS")
        self.acessar_area_nf(True)
        try:
            if self.browser.driver.find_element(By.XPATH, iss_xpath):
                iss = self.baixar_documento(iss_xpath, "NF_ISS.pdf", False)
                self.lista_docs.append(iss)
        except Exception:
            self.logger.info("Não há NF do tipo ISS")

        return self.lista_docs

    def obter_data_atual(self):
        return datetime.now().strftime("%Y%m")

    def clicar_elemento_por_xpath(self, xpath, info):
        try:
            elemento = self.browser.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        xpath,
                    )
                )
            )
            self.logger.info(f"Clicando no elemento: {info}")
            elemento.click()
        except Exception as e:
            self.logger.error(f"Erro ao clicar no elemento: {info}: {e}")

    def execution(self):
        try:
            self.pm.update_status_execucao(
                self.hash_processo, self.session_id, StatusExecucao.RUNNING
            )
            self.realizar_login()
            self.acessar_area_download()
            self.escolha_da_fatura()
            self.baixando_all_docs()
            arquivo_fatura = self.merge_pdfs(self.lista_docs)
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
                    self.vencimento,
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
            else:
                self.pm.update_status_all(
                    self.hash_processo,
                    self.session_id,
                    StatusExecucao.FAILED,
                    StatusExecucao.FAILED,
                    "Processo de download da fatura falhou",
                )
                self.logger.info("Erro ao realizar o download da fatura")

        except Exception as e:
            self.logger.error(f"Erro na execução: {str(e)}")
            self.pm.update_status_execucao(
                self.hash_processo,
                self.session_id,
                StatusExecucao.FAILED,
                f"Erro: {str(e)}",
            )
        finally:
            self.browser.driver.close()
