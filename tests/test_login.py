from selenium.webdriver.common.by import By

import bbscrap.navegacao.login as login
import tests.config as config


def test_login_com_senha(driver_sem_login):

    login.login_banco(driver_sem_login, config.agencia, config.conta, config.senha)
    locator = (By.XPATH, '//a[@title="Minha página"]')
    tags = driver_sem_login.find_elements(*locator)

    assert tags != []


def test_login_sem_senha(driver_sem_login):

    login.login_banco(driver_sem_login, config.agencia, config.conta)
    locator = (By.XPATH, '//a[@title="Minha página"]')
    tags = driver_sem_login.find_elements(*locator)

    assert tags != []


def test_login_sem_agencia_conta_senha(driver_sem_login):

    login.login_banco(driver_sem_login)
    locator = (By.XPATH, '//a[@title="Minha página"]')
    tags = driver_sem_login.find_elements(*locator)

    assert tags != []
