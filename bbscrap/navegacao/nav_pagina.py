"""Login na página do Banco do Brasil."""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def navega_pagina(driver):
    """Inicia o procedimento até a página de login.

    Inicia o navegador, navega pra página de login.
    @param return: drive
    """
    wdw = WebDriverWait(driver, 20)

    while True:
        try:
            driver.get('https://www.bb.com.br/pbb/pagina-inicial#/')
        except TimeoutException:
            print('Timeout, reloading...')
            driver.refresh()
            continue
        else:
            break
