from selenium.webdriver.common.by import By

import bbscrap.navegacao.drivers as chrome_driver
import bbscrap.navegacao.nav_pagina as navega_pagina


def test_init_driver():

    driver = chrome_driver.chrome_driver_init()
    assert driver is not None


def test_navega_pagina_inicial():

    driver = chrome_driver.chrome_driver_init()
    navega_pagina.navega_pagina(driver)

    locator = (By.XPATH, '//body[@id="bbLogin"]')
    tags = driver.find_elements(*locator)

    assert tags != []
