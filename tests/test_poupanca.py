from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import bbscrap.navegacao.nav_poupanca as nav_poupanca
import tests.config as config


def test_navega_pagina_poupanca(driver):
    wdw = WebDriverWait(driver, 20)
    
    nav_poupanca.navega_pagina(driver)
    locator = (By.XPATH,  '//li[contains(@class, "extrato-selecionado")]')
    tag = wdw.until(ec.presence_of_element_located(locator))
    assert tag.text == 'Poupança'


def test_poupanca_baixa_mes_janeiro_22_minuscula_ofx_existe(driver):
    nav_poupanca.navega_pagina(driver)
    corpo, header = nav_poupanca.baixa_extrato(driver, ['jan/22'], config.path_download)
    assert not corpo.empty


def test_poupanca_baixa_mes_janeiro_22_maiuscula_ofx_existe(driver):
    nav_poupanca.navega_pagina(driver)
    corpo, header = nav_poupanca.baixa_extrato(driver, ['JAN/22'], config.path_download)
    assert not corpo.empty


def test_poupanca_baixa_nome_errado_ofx_vazio(driver):
    nav_poupanca.navega_pagina(driver)
    corpo, header = nav_poupanca.baixa_extrato(driver, ['batata'], config.path_download)
    assert corpo.empty


def test_poupanca_baixa_mes_existe_path_download_errado_ofx_vazio(driver):
    path = r'C:\Users\vinim\Downloads\Nova pasta'
    nav_poupanca.navega_pagina(driver)
    corpo, header = nav_poupanca.baixa_extrato(driver, ['jan/22'], path)
    assert corpo.empty

# def test_poupanca_baixa_extrato_mais_atual():
#     pass
#
#
