"""Login na página do Banco do Brasil."""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def login(driver, agencia, conta, senha=None):
    """
    Login na página do Banco do Brasil.
    A página já deve estar na página de acesso à conta.

    @param driver: driver da página Selenium
    @param agencia: número da agencia (com DV, sem traço)
    @param conta: número da conta (com DV, sem traço)
    @param senha: senha da conta. Caso vazia, a senha será inserida manualmente.
    """
    wait = 20
    wdw = WebDriverWait(driver, wait)

    print(f'Login em {agencia}/{conta}')

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

    locator = (By.ID, 'botaoEnviar')
    driver.find_element(*locator).click()

    time.sleep(2)  # troca de tela

    # SENHA
    if senha is None:
        locator = (By.ID, 'botaoEnviar')
        WebDriverWait(driver, 30).until_not(
            ec.presence_of_element_located(locator),
            message='A SENHA não foi colocada no limite de tempo estipulado.',
        )
    else:
        locator = (By.ID, 'senhaConta')
        dob = wdw.until(ec.presence_of_element_located(locator))
        for _ in range(0, 10):
            dob.send_keys(Keys.BACKSPACE)
        dob.send_keys(f'{senha}')

        locator = (By.ID, 'botaoEnviar')
        driver.find_element(*locator).click()

    # titulares
    locator = (By.ID, 'dialogContent_0')
    try:
        wdw.until(ec.presence_of_element_located(locator))
        box = driver.find_element(*locator)
        box_tags = box.find_elements(By.TAG_NAME, 'a')
        box_tags[0].click()
    except:
        pass

    # espera a página carregar
    locator = (By.XPATH, '//a[@title="Minha página"]')
    wdw.until(
        ec.presence_of_element_located(locator),
        message='A pagina inicial da CONTA não foi carregada no tempo determinado',
    )

    time.sleep(2)  # troca de tela


def login_dependente(driver, nome_titular):
    """
    A partir do login já feito, troca de titular
    @param nome: titular par ao qual desejo trocar
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
                message='A pagina inicial da conta não foi carregada no tempo determinado',
            )
            time.sleep(2)
            return True

    # Não encontrou outra conta
    locator = (By.XPATH, '//li[@class="minha-pagina"]')
    driver.find_element(*locator).click()
    return False
