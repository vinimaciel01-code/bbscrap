import pytest

import bbscrap.navegacao.drivers as chrome_driver
import bbscrap.navegacao.nav_pagina as navega_pagina
import bbscrap.navegacao.login as login

import tests.config as config


@pytest.fixture
def driver_sem_login():
    driver = chrome_driver.chrome_driver_init()
    navega_pagina.navega_pagina(driver)
    yield driver
    driver.close()


@pytest.fixture
def driver():
    driver = chrome_driver.chrome_driver_init()
    navega_pagina.navega_pagina(driver)
    login.login_banco(driver, config.agencia1, config.conta1, config.senha1)
    yield driver
    driver.close()
