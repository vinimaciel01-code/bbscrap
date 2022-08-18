"""Login na página do Banco do Brasil."""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def login_banco(driver, agencia=None, conta=None, senha=None):
    """Login na página do Banco do Brasil.

    A página já deve estar na página de acesso à conta.
    @param driver: driver da página Selenium
    @param agencia: número da agencia (com DV, sem traço)
    @param conta: número da conta (com DV, sem traço)
    @param senha: senha da conta. Caso vazia, a senha será inserida manualmente
    """
    wdw = WebDriverWait(driver, 20)

    # agencia e conta
    if agencia is None or conta is None:
        print('Insira a agência e conta.')
        locator = (By.ID, 'senhaConta')
        WebDriverWait(driver, 120).until(
              ec.presence_of_element_located(locator),
              message='Encerrado: ag/conta não add.')

    else:

        # Navega para a página de login
        locator = (By.XPATH, '//*[@title="Acesse sua conta PF"]')
        tag = wdw.until(ec.presence_of_element_located(locator))
        driver.execute_script('arguments[0].click();', tag)

        # insere agencia e conta
        locator = (By.ID, 'dependenciaOrigem')
        dob = wdw.until(ec.presence_of_element_located(locator))
        for _ in range(0, 10):
            dob.send_keys(Keys.BACKSPACE)
        dob.send_keys(f'{agencia}')

        locator = (By.ID, 'numeroContratoOrigem')
        dob = driver.find_element(*locator)
        for _ in range(0, 10):
            dob.send_keys(Keys.BACKSPACE)
        dob.send_keys(f'{conta}')

        # envia os dados e vai para pagina de senha
        locator = (By.ID, 'botaoEnviar')
        driver.find_element(*locator).click()

        time.sleep(2)  # troca de tela

    # senha
    if senha is None:
        print('Insira a senha da conta.')

    else:
        locator = (By.ID, 'senhaConta')
        dob = wdw.until(ec.presence_of_element_located(locator))
        for _ in range(0, 10):
            dob.send_keys(Keys.BACKSPACE)
        dob.send_keys(f'{senha}')

        locator = (By.ID, 'botaoEnviar')
        driver.find_element(*locator).click()

    # Tenta encontrar os titulares
    try:
        locator = (By.ID, 'dialogContent_0')
        wdw.until(
            ec.presence_of_element_located(locator))

        box = driver.find_element(*locator)
        box_tags = box.find_elements(By.TAG_NAME, 'a')
        box_tags[0].click()

    except:
        pass

    # espera a página carregar
    locator = (By.XPATH, '//a[@title="Minha página"]')
    wdw.until(
        ec.presence_of_element_located(locator),
        message='Encerrado: página inicial não foi carregada.')

    time.sleep(2)  # troca de tela
