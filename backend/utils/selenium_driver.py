"""
Driver Selenium adaptado da classe Browser legada
Integração com a estrutura de RPAs do sistema
"""

import os
import time
from contextlib import contextmanager
from typing import List, Iterator, Optional
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException
)


class SeleniumDriver:
    """
    Driver Selenium adaptado da classe Browser legada
    Compatível com a estrutura de RPAs do orquestrador
    """
    
    def __init__(self, headless: bool = True, browser: str = "firefox"):
        self.browser_type = browser
        self.headless = headless
        self._driver = None
        self._driver_wait = None
        self._original_timeout = 30
        self.download_dir = self._get_download_directory()
        
    def _get_download_directory(self) -> str:
        """Obtém diretório de download"""
        downloads_dir = Path.home() / "Downloads" / "RPA_DOWNLOADS"
        downloads_dir.mkdir(exist_ok=True)
        return str(downloads_dir)
    
    def inicializar(self):
        """Inicializa o driver baseado na classe Browser legada"""
        if self.browser_type.lower() == "firefox":
            self._inicializar_firefox()
        else:
            self._inicializar_chrome()
            
        self._driver_wait = WebDriverWait(self._driver, self._original_timeout)
        self._driver.maximize_window()
        
    def _inicializar_firefox(self):
        """Inicializa Firefox com configurações da classe Browser legada"""
        options = Options()
        
        if self.headless:
            options.add_argument("--headless")
            
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        # Configurações de download adaptadas
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", self.download_dir)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/pdf,application/octet-stream,application/zip"
        )
        options.set_preference("browser.download.useDownloadDir", True)
        options.set_preference("pdfjs.disabled", True)
        
        # Tentar usar geckodriver do sistema ou instalar
        try:
            self._driver = webdriver.Firefox(options=options)
        except Exception:
            # Fallback para geckodriver padrão
            gecko_driver_path = "/usr/local/bin/geckodriver"
            if os.path.exists(gecko_driver_path):
                from selenium.webdriver.firefox.service import Service
                service = Service(gecko_driver_path)
                self._driver = webdriver.Firefox(service=service, options=options)
            else:
                raise Exception("Geckodriver não encontrado")
        
        self._driver.delete_all_cookies()
    
    def _inicializar_chrome(self):
        """Inicializa Chrome como alternativa"""
        options = ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless")
            
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        
        # Configurações de download
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        }
        options.add_experimental_option("prefs", prefs)
        
        self._driver = webdriver.Chrome(options=options)
    
    def finalizar(self):
        """Finaliza o driver"""
        if self._driver:
            self._driver.quit()
            self._driver = None
    
    def get(self, url: str):
        """Navega para URL"""
        self._driver.get(url)
        
    def current_url(self) -> str:
        """URL atual"""
        return self._driver.current_url
    
    def find_element(self, xpath: str, condition: str = "presence") -> WebElement:
        """Encontra elemento adaptado da classe Browser legada"""
        conditions = {
            "presence": EC.presence_of_element_located,
            "visible": EC.visibility_of_element_located,
            "clickable": EC.element_to_be_clickable,
        }
        
        condition_func = conditions.get(condition, EC.presence_of_element_located)
        
        try:
            return self._driver_wait.until(condition_func((By.XPATH, xpath)))
        except TimeoutException:
            raise NoSuchElementException(f"Element with xpath {xpath} not found")
    
    def find_elements(self, xpath: str) -> List[WebElement]:
        """Encontra elementos"""
        try:
            return self._driver_wait.until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
        except TimeoutException:
            return []
    
    def click(self, xpath: str):
        """Clica em elemento adaptado da classe Browser legada"""
        element = self.find_element(xpath, condition="clickable")
        self._driver.execute_script("arguments[0].scrollIntoView(true);", element)
        
        try:
            element.click()
        except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException):
            self._driver.execute_script("arguments[0].click();", element)
    
    def send_text(self, xpath: str, text: str, clear: bool = True):
        """Envia texto para elemento"""
        element = self.find_element(xpath, "clickable")
        
        if clear:
            element.clear()
            
        element.send_keys(str(text))
    
    def get_text(self, xpath: str) -> str:
        """Obtém texto do elemento"""
        element = self.find_element(xpath)
        return element.text
    
    def get_attribute(self, xpath: str, attribute: str) -> str:
        """Obtém atributo do elemento"""
        element = self.find_element(xpath)
        return element.get_attribute(attribute) or ""
    
    def select_option(self, xpath: str, option: str):
        """Seleciona opção em select"""
        element = self.find_element(xpath, "clickable")
        select = Select(element)
        select.select_by_visible_text(option)
    
    def wait_for_download(self, filename_pattern: str, timeout: int = 30) -> Optional[str]:
        """Aguarda download de arquivo"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            for file in os.listdir(self.download_dir):
                if filename_pattern in file and not file.endswith('.tmp'):
                    return os.path.join(self.download_dir, file)
            time.sleep(1)
        
        return None
    
    def execute_script(self, script: str, *args):
        """Executa JavaScript"""
        return self._driver.execute_script(script, *args)
    
    def switch_to_window(self, window_handle: str):
        """Muda para janela"""
        self._driver.switch_to.window(window_handle)
    
    def get_window_handles(self) -> List[str]:
        """Obtém handles das janelas"""
        return self._driver.window_handles
    
    def set_timeout(self, timeout: int):
        """Define timeout personalizado"""
        self._driver_wait._timeout = timeout
    
    def reset_timeout(self):
        """Reseta timeout para padrão"""
        self._driver_wait._timeout = self._original_timeout
    
    @contextmanager
    def on_iframe(self, xpath: str) -> Iterator[None]:
        """Context manager para iframe"""
        iframe = self._driver_wait.until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        self._driver.switch_to.frame(iframe)
        try:
            yield
        finally:
            self._driver.switch_to.default_content()
    
    def aguardar(self, segundos: int):
        """Aguarda tempo especificado"""
        time.sleep(segundos)