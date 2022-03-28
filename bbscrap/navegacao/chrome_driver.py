"""Inicializa o Drive do google Chrome."""

from selenium import webdriver


def chrome_driver_init():
    """Inicializa o driver do Chrome."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.set_page_load_timeout(20000)  # milisegundos
    return driver
