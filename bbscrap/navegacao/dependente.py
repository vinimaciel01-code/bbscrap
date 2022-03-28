"""Login na página do Banco do Brasil."""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def login_dependente(driver, nome_titular):
    """Troca de titular.

    @param driver: drive do navegador
    @param nome: nome do titular para o qual desejo trocar
    returns: Boolean, indicando se encontrou o titular
    """
    wait = 20
    wdw = WebDriverWait(driver, wait)

    locator = (By.XPATH, '//div[@class="dados-conta"]')
    driver.find_element(*locator).click()

    locator = (By.ID, 'listaOutrasContas')
    tab = driver.find_element(*locator)

    time.sleep(1)
    tab_a = tab.find_elements(By.TAG_NAME, 'a')

    for tag in tab_a:
        if nome_titular.lower() in tag.text.lower():

            # Encontrou a conta: clica e espera a página carregar
            tag.click()
            locator = (By.XPATH, '//a[@title="Minha página"]')
            wdw.until(
                ec.presence_of_element_located(locator),
                message='Pagina inicial não foi carregada a tempo.',
            )
            time.sleep(2)
            return True

    # Não encontrou outra conta
    locator = (By.XPATH, '//li[@class="minha-pagina"]')
    driver.find_element(*locator).click()
    return False
