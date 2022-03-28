import pytest
from selenium.webdriver.common.by import By

import bbscrap.navegacao.nav_corrente as nav_corrente
import tests.config as config


@pytest.mark.skip
def test_navega_pagina_conta_corrente(driver):
    nav_corrente.navega_pagina(driver)
    locator = (By.XPATH,  '//li[contains(@class, "extrato-selecionado")]')
    tag = driver.find_element(*locator)
    assert tag.text == 'Conta corrente'


def test_corrente_baixa_mes_janeiro_22_minuscula(driver):
    nav_corrente.navega_pagina(driver)
    header, corpo = nav_corrente.baixa_extrato(driver, ['jan/22'], config.path_download)
    assert not corpo.empty


def test_corrente_baixa_mes_janeiro_22_maiuscula(driver):
    nav_corrente.navega_pagina(driver)
    header, corpo = nav_corrente.baixa_extrato(driver, ['JAN/22'], config.path_download)
    assert not corpo.empty


def test_corrente_baixa_nome_errado(driver):
    nav_corrente.navega_pagina(driver)
    header, corpo = nav_corrente.baixa_extrato(driver, ['batata'], config.path_download)
    assert corpo.empty


def test_corrente_baixa_mes_existe_path_download_errado(driver):
    path = r'C:\Users\vinim\Downloads\Nova pasta'
    nav_corrente.navega_pagina(driver)
    header, corpo = nav_corrente.baixa_extrato(driver, ['jan/22'], path)
    assert not corpo.empty

# def test_corrente_baixa_extrato_mais_atual():
#     pass
#
#
