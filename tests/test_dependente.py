import bbscrap.navegacao.login as login
import bbscrap.navegacao.dependente as dependente

import tests.config as config


def test_troca_dependente_numero_do_nome_existe(driver):
    Indicador = dependente.login_dependente(driver, '2')
    assert Indicador is True


def test_troca_dependente_nome_existe(driver):
    Indicador = dependente.login_dependente(driver, 'Thais')
    assert Indicador is True


def test_troca_dependente_nome_nao_existe(driver):
    Indicador = dependente.login_dependente(driver, 'Costa')
    assert Indicador is False
