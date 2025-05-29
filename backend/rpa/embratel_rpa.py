"""
Embratel RPA - Adaptado ao padrão RPA Base
Preservando 100% do código legado conforme manual da BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
Data: 29/05/2025
"""

import base64
import os
from datetime import datetime
from time import sleep
from typing import Optional

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .rpa_base import (
    RPABase, 
    ParametrosEntradaPadrao, 
    ResultadoSaidaPadrao, 
    StatusExecucao, 
    TipoOperacao
)
from ..utils.selenium_driver import SeleniumDriver
from ..utils.file_manager import FileManager

class EmbratelRPA(RPABase):
    """
    RPA Embratel adaptado ao padrão imutável do RPA Base
    Preserva 100% da lógica legada de scraping conforme manual
    """
    
    def __init__(self):
        super().__init__()
        self.driver_manager = SeleniumDriver()
        self.file_manager = FileManager()
        self.driver = None
        self.wait = None
        self.window_id = None
        self.vencimento = None
        self.lista_docs = []
    
    def executar_download(self, parametros: ParametrosEntradaPadrao) -> ResultadoSaidaPadrao:
        """
        Executa download de fatura da Embratel preservando lógica legada
        """
        timestamp_inicio = datetime.now()
        
        try:
            self.logger.info(f"Iniciando download Embratel para cliente {parametros.id_cliente}")
            
            # Inicializa driver
            self.driver = self.driver_manager.obter_driver()
            self.wait = self.driver_manager.obter_wait(self.driver)
            
            # Execução da lógica legada preservada
            self._realizar_login(parametros)
            self._acessar_area_download(parametros)
            self._escolha_da_fatura(parametros)
            lista_docs = self._baixando_all_docs()
            arquivo_fatura = self._merge_pdfs(lista_docs, parametros)
            
            if arquivo_fatura:
                # Upload para S3
                url_s3 = self.file_manager.upload_arquivo(arquivo_fatura)
                
                return ResultadoSaidaPadrao(
                    sucesso=True,
                    status=StatusExecucao.SUCESSO,
                    mensagem="Download da fatura Embratel realizado com sucesso",
                    arquivo_baixado=arquivo_fatura,
                    url_s3=url_s3,
                    dados_extraidos={"vencimento": self.vencimento},
                    tempo_execucao_segundos=(datetime.now() - timestamp_inicio).total_seconds(),
                    timestamp_inicio=timestamp_inicio,
                    timestamp_fim=datetime.now(),
                    logs_execucao=[f"Fatura baixada: {arquivo_fatura}"]
                )
            else:
                return ResultadoSaidaPadrao(
                    sucesso=False,
                    status=StatusExecucao.ERRO,
                    mensagem="Falha no download da fatura Embratel",
                    timestamp_inicio=timestamp_inicio,
                    timestamp_fim=datetime.now()
                )
                
        except Exception as e:
            self.logger.error(f"Erro no download Embratel: {e}")
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
    
    def executar_upload_sat(self, parametros: ParametrosEntradaPadrao) -> ResultadoSaidaPadrao:
        """
        Upload para SAT será implementado no SAT RPA específico
        """
        return ResultadoSaidaPadrao(
            sucesso=False,
            status=StatusExecucao.ERRO,
            mensagem="Upload SAT deve ser executado através do SAT RPA",
            timestamp_inicio=datetime.now(),
            timestamp_fim=datetime.now()
        )
    
    # ========== MÉTODOS LEGADOS PRESERVADOS 100% ==========
    
    def _realizar_login(self, parametros: ParametrosEntradaPadrao):
        """Lógica de login preservada do código legado"""
        self.logger.info("Abrindo URL de login")
        self.driver.get(parametros.url_portal)

        self.logger.info("Inserindo credenciais")
        username_field = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='login']"))
        )
        password_field = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@id='MainContent_password']")
            )
        )

        username_field.send_keys(parametros.usuario)
        password_field.send_keys(parametros.senha)

        login_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
        )
        login_button.click()

    def _merge_pdfs(self, pdf_list, parametros: ParametrosEntradaPadrao):
        """Lógica de merge de PDFs preservada do código legado"""
        try:
            import PyPDF2
            
            vencimento_formatado = self.vencimento.replace("/", "-") if self.vencimento else "sem-data"
            self.logger.info(f"Data de vencimento da fatura: {vencimento_formatado}")

            new_name_file = f"{parametros.id_cliente}_{vencimento_formatado}.pdf"
            new_name_file = self._sanitize_filename(new_name_file)
            self.logger.info(f"Salvando fatura como: {new_name_file}")

            pdf_writer = PyPDF2.PdfWriter()

            for pdf in pdf_list:
                if os.path.exists(pdf):
                    pdf_reader = PyPDF2.PdfReader(pdf)
                    for page in range(len(pdf_reader.pages)):
                        pdf_writer.add_page(pdf_reader.pages[page])

            with open(new_name_file, "wb") as output_pdf:
                pdf_writer.write(output_pdf)

            # Verifica se o PDF foi criado com sucesso
            if os.path.exists(new_name_file):
                self.logger.info(f"PDFs merged successfully into {new_name_file}")

                # Remove PDFs originais
                for pdf in pdf_list:
                    try:
                        if os.path.exists(pdf):
                            os.remove(pdf)
                            self.logger.info(f"Removed original PDF: {pdf}")
                    except Exception as e:
                        self.logger.error(f"Error removing {pdf}: {e}")
                
                return new_name_file
            else:
                self.logger.error("Failed to create the merged PDF.")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro no merge de PDFs: {e}")
            return None

    def _extrair_data_vencimento(self, html_content):
        """Lógica de extração de vencimento preservada do código legado"""
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

    def _html_para_pdf(self, html_content, file_name, css=False):
        """Lógica de conversão HTML para PDF preservada do código legado"""
        try:
            import pdfkit
            
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
            
            # Usar o pdfkit para gerar o PDF a partir do HTML
            pdfkit.from_string(html_content, file_name, options=options)
            self.logger.info(f"PDF salvo com sucesso: {file_name}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao gerar PDF: {e}")
            return False

    def _acessar_area_download(self, parametros: ParametrosEntradaPadrao):
        """Lógica de acesso à área de download preservada do código legado"""
        self._clicar_elemento_por_xpath(
            "//a[contains(normalize-space(.), 'Fatura On Line')]",
            "logon da fatura",
        )

        data = self._obter_data_atual()

        self._clicar_elemento_por_xpath(f"//option[@value={data}]", "mês da fatura")

        self._clicar_elemento_por_xpath("//input[@id='submit']", "Ok")

        try:
            self.driver.find_element(
                By.XPATH, "//table[contains(@class, 'txtCinzaHand')]/tbody"
            )
        except Exception:
            raise Exception("Tabela de faturas não encontrada")

    def _escolha_da_fatura(self, parametros: ParametrosEntradaPadrao):
        """Lógica de escolha da fatura preservada do código legado"""
        try:
            fatura_table = self.driver.find_element(
                By.XPATH, "//table[contains(@class, 'txtCinzaHand')]/tbody"
            )
        except Exception as e:
            self.logger.error(f"Erro ao localizar a tabela de faturas: {e}")
            return

        linhas = fatura_table.find_elements(By.XPATH, ".//tr")
        encontrou = False

        # Tenta extrair conta e dia, se possível
        try:
            conta_alvo, dia_alvo = parametros.filtro.split("_")
            self.logger.info(
                f"Filtro completo detectado: Conta '{conta_alvo}' com dia '{dia_alvo}'."
            )
        except (ValueError, AttributeError):
            conta_alvo = parametros.filtro.strip() if parametros.filtro else ""
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

        self.window_id = self.driver.current_window_handle

    def _mudar_para_ultima_aba(self):
        """Lógica preservada do código legado"""
        todas_as_janelas = self.driver.window_handles
        if len(todas_as_janelas) > 1:
            self.driver.switch_to.window(todas_as_janelas[-1])
        else:
            raise Exception("Não há janelas suficientes abertas para mudar.")

    def _fechar_aba_atual_e_voltar(self):
        """Lógica preservada do código legado"""
        todas_as_janelas = self.driver.window_handles
        for indice, janela in enumerate(todas_as_janelas):
            if self.window_id in janela:
                self.driver.switch_to.window(todas_as_janelas[indice])
                break

    def _baixar_documento(self, xpath, documento, css):
        """Lógica de download de documento preservada do código legado"""
        self._clicar_elemento_por_xpath(xpath, documento)
        self._mudar_para_ultima_aba()
        sleep(5)
        html_pagina = self.driver.page_source
        if documento == "Boleto.pdf":
            self.vencimento = self._extrair_data_vencimento(html_pagina)
        self._html_para_pdf(html_pagina, documento, css)
        self._fechar_aba_atual_e_voltar()
        return documento

    def _acessar_area_nf(self, recorrente: bool = False):
        """Lógica preservada do código legado"""
        if recorrente:
            self._fechar_aba_atual_e_voltar()
        self._clicar_elemento_por_xpath(
            "//tr[@onclick=\"return chamaFatura('notaFiscal')\"]",
            "Nota Fiscal",
        )
        self._mudar_para_ultima_aba()

    def _baixando_all_docs(self):
        """Lógica de download de todos os documentos preservada do código legado"""
        self.lista_docs = []

        fatura = self._baixar_documento(
            "//tr[@onclick=\"return chamaFatura('imprimirFatura')\"]",
            "Fatura.pdf",
            True,
        )
        if fatura:
            self.lista_docs.append(fatura)
            
        boleto = self._baixar_documento(
            "//tr[@onclick=\"return chamaFatura('imprimirBoleto')\"]",
            "Boleto.pdf",
            False,
        )
        if boleto:
            self.lista_docs.append(boleto)

        icms_xpath = "//td[contains(text(), 'ICMS') and @align='left']"
        iss_xpath = "//td[contains(text(), 'ISS') and @align='left']"
        
        self._acessar_area_nf()
        try:
            if self.driver.find_element(By.XPATH, icms_xpath):
                icms = self._baixar_documento(icms_xpath, "NF_ICMS.pdf", False)
                self.lista_docs.append(icms)
        except Exception:
            self.logger.info("Não há NF do tipo ICMS")
            
        self._acessar_area_nf(True)
        try:
            if self.driver.find_element(By.XPATH, iss_xpath):
                iss = self._baixar_documento(iss_xpath, "NF_ISS.pdf", False)
                self.lista_docs.append(iss)
        except Exception:
            self.logger.info("Não há NF do tipo ISS")

        return self.lista_docs

    def _obter_data_atual(self):
        """Lógica preservada do código legado"""
        return datetime.now().strftime("%Y%m")

    def _clicar_elemento_por_xpath(self, xpath, info):
        """Lógica preservada do código legado"""
        try:
            elemento = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            self.logger.info(f"Clicando no elemento: {info}")
            elemento.click()
        except Exception as e:
            self.logger.error(f"Erro ao clicar no elemento: {info}: {e}")

    def _sanitize_filename(self, filename):
        """Função auxiliar para sanitizar nome de arquivo"""
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', filename)