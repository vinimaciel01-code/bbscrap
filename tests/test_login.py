from selenium.webdriver.common.by import By

import bbscrap.navegacao.login as login
import tests.config as config


def test_login_com_senha(driver):

    login.login_banco(driver, config.agencia, config.conta, config.senha)
    locator = (By.XPATH, '//a[@title="Minha página"]')
    tags = driver.find_elements(*locator)

    assert tags != []


def test_login_sem_senha(driver):

    login.login_banco(driver, config.agencia, config.conta)
    locator = (By.XPATH, '//a[@title="Minha página"]')
    tags = driver.find_elements(*locator)

    assert tags != []


def test_login_sem_agencia_conta_senha(driver):

    login.login_banco(driver)
    locator = (By.XPATH, '//a[@title="Minha página"]')
    tags = driver.find_elements(*locator)

    assert tags != []
