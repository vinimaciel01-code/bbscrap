from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import bbscrap.navegacao.nav_corrente as nav_corrente
import tests.config as config


def test_navega_pagina_conta_corrente(driver):
    wdw = WebDriverWait(driver, 20)

    nav_corrente.navega_pagina(driver)
    locator = (By.XPATH,  '//li[contains(@class, "extrato-selecionado")]')
    tag = wdw.until(ec.presence_of_element_located(locator))
    assert tag.text == 'Conta corrente'


def test_corrente_baixa_mes_janeiro_22_minuscula(driver):
    nav_corrente.navega_pagina(driver)
    corpo, header = nav_corrente.baixa_extrato(driver, ['jan/22'], config.path_download)
    assert not corpo.empty


def test_corrente_baixa_mes_janeiro_22_maiuscula(driver):
    nav_corrente.navega_pagina(driver)
    corpo, header = nav_corrente.baixa_extrato(driver, ['JAN/22'], config.path_download)
    assert not corpo.empty


def test_corrente_baixa_nome_errado(driver):
    nav_corrente.navega_pagina(driver)
    corpo, header = nav_corrente.baixa_extrato(driver, ['batata'], config.path_download)
    assert corpo.empty


def test_corrente_baixa_mes_existe_path_download_errado(driver):
    path = r'C:\Users\vinim\Downloads\Nova pasta'
    nav_corrente.navega_pagina(driver)
    corpo, header = nav_corrente.baixa_extrato(driver, ['jan/22'], path)
    assert not corpo.empty

# def test_corrente_baixa_extrato_mais_atual():
#     pass
#
#
