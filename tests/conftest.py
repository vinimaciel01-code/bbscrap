import pytest

import bbscrap.navegacao.chrome_driver as chrome_driver
import bbscrap.navegacao.nav_pagina as navega_pagina
import bbscrap.navegacao.login as login

import bbscrap.config as config


@pytest.fixture
def driver():
    driver = chrome_driver.chrome_driver_init()
    navega_pagina.navega_pagina(driver)
    yield driver
    driver.close()


@pytest.fixture
def driver_login():
    driver = chrome_driver.chrome_driver_init()
    navega_pagina.navega_pagina(driver)
    login.login_banco(driver, config.agencia, config.conta, config.senha)
    yield driver
    driver.close()
