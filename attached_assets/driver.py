from contextlib import contextmanager
from difflib import get_close_matches
from time import sleep
from typing import Callable, Iterator, List

import chromedriver_autoinstaller
from configs.config import getenv
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    InvalidElementStateException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from platformdirs import user_downloads_dir


class WindowNotFound(Exception):
    """Browser window not found."""


ENV = getenv("ENV")
MODE = getenv("MODE")


class Browser:
    """Classe com alguns incrementos."""

    _driver: webdriver.Firefox = None
    _driver_wait: WebDriverWait = None

    def __init__(self, eager_load: bool = False):

        self._original_timeout = 30
        self.actions = ActionChains(self._driver)

        self.options = Options()
        if MODE == "prod":
            self.options.add_argument("--headless")

        if eager_load:
            self.options.page_load_strategy = "eager"
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--no-sandbox")
        self.options.set_preference(
            "browser.download.folderList", 2
        )  # Use custom download directory
        self.options.set_preference(
            "browser.download.dir", f"{user_downloads_dir()}/TIRUS_DOWNLOADS"
        )
        self.options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/pdf,application/octet-stream",
        )
        self.options.set_preference("browser.download.useDownloadDir", True)
        self.options.set_preference(
            "pdfjs.disabled", True
        )  # Disable built-in PDF viewer
        # Usa a versão em cache se já tiver sido baixada
        gecko_driver_path = "/usr/local/bin/geckodriver"

        self._driver = webdriver.Firefox(
            service=Service(gecko_driver_path), options=self.options
        )

        self._driver.delete_all_cookies()
        self._driver_wait = WebDriverWait(self._driver, self._original_timeout)
        self._driver.maximize_window()

    def set_timeout(self, timeout):
        self._driver_wait._timeout = timeout

    def reset_timeout(self):
        self._driver_wait._timeout = self._original_timeout

    def close(self):
        self._driver.quit()

    @contextmanager
    def on_new_window(self, url: str) -> Iterator[None]:
        """Open a new window with a given url. and handles the context"""
        last_handle = self._driver.current_window_handle
        self._driver.execute_script(f"window.open('{url}')")
        new_handle = None
        while not new_handle:
            for handle in self._driver.window_handles:
                if handle is not last_handle:
                    self._driver.switch_to.window(handle)
                    if self._driver.current_url == url:
                        if (
                            self._driver.execute_script(
                                "return document.readyState")
                            == "complete"
                        ):
                            new_handle = handle
                            break
            sleep(1)
        yield
        self._driver.close()
        self._driver.switch_to.window(last_handle)

    @contextmanager
    def on_window(self, has_element: str, retry: int = 10) -> Iterator[None]:
        """Switch to a window that has the given element."""
        default_handler = self._driver.current_window_handle
        found_handle = None
        while not found_handle:
            for handle in self._driver.window_handles:
                if handle is default_handler:
                    continue
                self._driver.switch_to.window(handle)
                if self._driver.find_elements(By.XPATH, has_element):
                    found_handle = handle
                    break
                sleep(1)
                retry -= 1
                if retry < 1:
                    raise WindowNotFound(
                        f"Window with xpath {has_element} not found.")

        yield
        self._driver.switch_to.window(default_handler)

    @contextmanager
    def on_iframe(self, xpath: str) -> Iterator[None]:
        """Troca para iframe"""
        iframe = self._driver_wait.until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        self._driver.switch_to.frame(iframe)
        yield
        self._driver.switch_to.default_content()

    @staticmethod
    def __get_condition(condition: str) -> Callable:
        """Returns the expected condition function based on the condition name."""
        conditions = {
            "visible": EC.visibility_of_element_located,
            "visible_any": EC.visibility_of_any_elements_located,
            "visible_all": EC.visibility_of_all_elements_located,
            "clickable": EC.element_to_be_clickable,
            "selected": EC.element_to_be_selected,
            "located_all": EC.presence_of_all_elements_located,
        }
        return conditions.get(condition, EC.presence_of_element_located)

    def __get_element(self, xpath: str, ec: str, retry: int = 1) -> WebElement:

        try:
            condition = self.__get_condition(ec)
            return WebDriverWait(self._driver, self._driver_wait._timeout).until(
                condition((By.XPATH, xpath))
            )

            return element
        except (TimeoutException, NoSuchElementException) as exc:
            retry -= 1
            if retry < 1:
                raise NoSuchElementException(
                    f"Element with xpath {xpath} not found. {exc}"
                )

    def find_elements(
        self, xpath: str, condition: str = "located_all"
    ) -> List[WebElement]:
        """Waits for any elements to be located and returns a list of elements."""
        try:
            condition_func = self.__get_condition(condition)
            return self._driver_wait.until(condition_func((By.XPATH, xpath)))
        except TimeoutException as exc:
            raise NoSuchElementException(
                f"Elements with xpath {xpath} not found. {exc}"
            )

    def find_element(self, xpath: str, condition: str = None) -> WebElement:  # type: ignore
        """Waits for a single element and returns it."""
        return self.__get_element(xpath, ec=condition or "presence")

    def click(self, xpath: str) -> None:
        """Aguarda elemento ser clicavel e envia evento click."""
        element = self.find_element(xpath, condition="clickable")
        self._driver.execute_script(
            "arguments[0].scrollIntoView(true);", element)
        try:
            element.click()
        except ElementClickInterceptedException:
            self._driver.execute_script("arguments[0].click();", element)
        except ElementNotInteractableException:
            self._driver.execute_script("arguments[0].click();", element)
        except StaleElementReferenceException:
            self._driver.execute_script("arguments[0].click();", element)

    def get_text(self, xpath: str, timeout: int = 10) -> str:
        """Get the text from the element."""
        while timeout > 0:
            try:
                return self.find_element(xpath).text
            except NoSuchElementException:
                sleep(1)
                timeout -= 1
        raise NoSuchElementException(f"Element with xpath {xpath} not found.")

    def send_text(
        self,
        xpath: str,
        text: str | int,
        clear: bool = False,
        timeout: int = 15,
        verify=False,
    ) -> None:
        """Envia texto para o elemento.

        Args:
            xpath (str): xpath campo para ser digitado
            text (str): texto a ser digitado
            clear (bool, optional): Limpar campo antes de digitar. Defaults to False.
            timeout (int, optional): tempo para aguardar valor caso `verify=True`.
            verify (bool, optional): Aguarda campo ter o texto passado.
        """
        while timeout > 0:
            try:
                element = self.find_element(xpath, "clikable")
                if clear:
                    element.clear()
                element.send_keys(text)  # type: ignore
            except InvalidElementStateException as exc:
                if "Element is read-only" in str(exc):
                    self._driver.execute_script(
                        "arguments[0].removeAttribute('readonly')", element
                    )
                    continue
            if not verify or element.get_attribute("value") == text:
                return
            sleep(2)
            timeout -= 1
        raise TimeoutException(
            f"Timeout sending text to element with xpath {xpath}")

    def __select_option(self, xpath: str, option: str) -> None:
        """Select an option from a select element."""
        element = self.find_element(xpath, condition="clickable")
        select = Select(element)
        select.select_by_visible_text(option)

    def select_option(
        self, xpath: str, option: str, timeout: int = 10, verify: bool = False
    ) -> None:
        """Seleciona option em elemento select

        Args:
            xpath (str): xpath to elemento select
            option (str): string da option
        """
        while timeout > 0:
            self.__select_option(xpath, option)
            if not verify:
                return

            current_value = self.find_element(xpath).get_attribute("value")
            for opt in self.find_elements(f'//option[@value="{current_value}"]'):
                text = opt.get_attribute("innerText")
                if text == option:
                    return
            sleep(2)
            timeout -= 1
        raise NoSuchElementException(
            f"Option {option} not found in select element with xpath {xpath}."
        )

    def get_texts_from_select(self, xpath: str) -> List[str]:
        element = self._driver_wait.until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        select_element = Select(element)
        return [opt.text for opt in select_element.options]

    def select_option_by_similarity(
        self,
        xpath: str,
        option: str,
        similarity_threshold: float = 0.6,
        timeout: int = 10,
        verify: bool = False,
    ) -> None:
        """
        Select an option from a select element by similarity, ignoring case sensitivity.

        Args:
            xpath (str): XPath to the select element.
            option (str): Option text to select.
            similarity_threshold (float): Minimum similarity ratio (0 to 1) for selecting an option.
            timeout (int): Time to retry selecting the option.
            verify (bool): Whether to verify the selection after clicking.
        """
        available_options = self.get_texts_from_select(xpath)

        # Convert to uppercase for case-insensitive comparison
        option_upper = option.upper()
        available_options_upper = [opt.upper() for opt in available_options]

        # Find the closest match
        closest_matches = get_close_matches(
            option_upper,
            available_options_upper,
            n=1,
            cutoff=similarity_threshold,
        )

        if not closest_matches:
            raise NoSuchElementException(
                f"No similar option found for '{option}' in select element with xpath '{xpath}'."
            )

        # Retrieve the original case-sensitive option
        closest_option = available_options[
            available_options_upper.index(closest_matches[0])
        ]

        while timeout > 0:
            self.__select_option(xpath, closest_option)
            if not verify:
                return

            current_value = self.find_element(xpath).get_attribute("value")
            for opt in self.find_elements(f'//option[@value="{current_value}"]'):
                text = opt.get_attribute("innerText")
                if text.upper() == closest_option.upper():
                    return

            sleep(2)
            timeout -= 1

        raise NoSuchElementException(
            f"Failed to select option '{closest_option}' in select element with xpath '{xpath}'."
        )

    def get(self, url: str):
        self._driver.get(url)

    def check_for_error(
        self, xpath: str, condition: str = None, retry: int = 1
    ) -> WebElement:
        """Check if the download error message is present."""
        try:
            self.set_timeout(5)
            self.__get_element(xpath, ec=condition, retry=retry)
            self.reset_timeout()
            return True
        except NoSuchElementException:
            return False


class BrowserChrome:
    def __init__(self, is_dev, logger):
        self.is_dev = is_dev
        self.logger = logger
        self._original_timeout = 30
        # Instala automaticamente o ChromeDriver na versão correta
        chromedriver_autoinstaller.install()

        chrome_options = ChromeOptions()

        if ENV == "prod":
            self.logger.info("Iniciando processo em ambiente de produção")
            # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            # Define um tempo de espera implícito
            self.driver.implicitly_wait(10)
        except Exception as e:
            self.logger.error(f"Erro ao iniciar o ChromeDriver: {e}")
            raise
        self.wait = WebDriverWait(self.driver, self._original_timeout)

    def clicar_elemento_por_xpath(self, xpath, info):
        try:
            elemento = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            self.logger.info(f"Clicando no elemento: {info}")
            elemento.click()
        except Exception as e:
            self.logger.error(f"Erro ao clicar no elemento: {info}: {e}")

    def verificar_elemento_por_xpath(self, xpath, info):
        elemento = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.logger.info(f"Verificando elemento: {info}")
        return True, elemento

    def set_timeout(self, timeout):
        self.wait = WebDriverWait(self.driver, timeout)

    def reset_timeout(self):
        self.wait = WebDriverWait(self.driver, self._original_timeout)

    def check_for_error(
            self, xpath: str, info: str = "") -> WebElement:
        """Check if the download error message is present."""
        try:
            self.set_timeout(5)
            elemento = self.verificar_elemento_por_xpath(xpath, info)
            self.reset_timeout()
            return True, elemento
        except NoSuchElementException:
            return False
