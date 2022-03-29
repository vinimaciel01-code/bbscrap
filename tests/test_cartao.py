from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import bbscrap.navegacao.nav_cartao as nav_cartao
import tests.config as config


def test_navega_pagina_cartao(driver):
    wdw = WebDriverWait(driver, 20)

    nav_cartao.navega_pagina(driver)
    locator = (By.XPATH,  '//li[contains(@class, "extrato-selecionado")]')
    tag = wdw.until(ec.presence_of_element_located(locator))
    assert tag.text == 'Cartão de crédito'


def test_cartao_baixa_mes_janeiro_22_minuscula(driver):
    nav_cartao.navega_pagina(driver)
    corpo, header = nav_cartao.baixa_extrato(driver, ['jan/22'], config.path_download)
    assert not corpo.empty


def test_cartao_baixa_mes_janeiro_22_maiuscula(driver):
    nav_cartao.navega_pagina(driver)
    corpo, header = nav_cartao.baixa_extrato(driver, ['JAN/22'], config.path_download)
    assert not corpo.empty


def test_cartao_baixa_nome_errado(driver):
    nav_cartao.navega_pagina(driver)
    corpo, header = nav_cartao.baixa_extrato(driver, ['batata'], config.path_download)
    assert corpo.empty


def test_cartao_baixa_mes_existe_path_download_errado(driver):
    path = r'C:\Users\vinim\Downloads\Nova pasta'
    nav_cartao.navega_pagina(driver)
    corpo, header = nav_cartao.baixa_extrato(driver, ['jan/22'], path)
    assert corpo.empty
