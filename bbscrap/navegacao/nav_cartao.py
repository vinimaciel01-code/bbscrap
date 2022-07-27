"""Navegação e download dos extratos de conta corrente e poupança."""

import datetime as dt
import time

import pandas as pd
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from bbscrap.navegacao.nome_arquivo import ultimo_arquivo_baixado


def central(driver, lista_meses):
    navega_pagina(driver)
    nome_arquivo_list = baixa_extrato(driver, lista_meses)
    return nome_arquivo_list


def navega_pagina(driver):
    """Navega para a página dos extratos dos cartões.

    @param driver: driver da página Selenium
    """
    wdw = WebDriverWait(driver, 20)

    # navegacao
    locator = (By.XPATH, '//a[@codigo="32578"]')
    barra_menu = wdw.until(ec.element_to_be_clickable(locator))

    for _ in range(0, 2):
        try:
            parent = barra_menu.find_element(By.XPATH, '..')
            parent.click()
            parent.find_element(By.XPATH, '..').click()
            barra_menu.click()
            break
        except:
            time.sleep(1)
            continue

    # subelemento
    locator = (By.XPATH, '//a[@codigo="32715"]')
    barra_submenu = wdw.until(ec.element_to_be_clickable(locator))
    barra_submenu.click()

    # Espera a página carregar
    locator = (By.XPATH, '//li[@class="containerExtrato"]')
    try:
        wdw.until(ec.element_to_be_clickable(locator))
    except:
        pass


def baixa_extrato(driver, lista_meses):
    """
    Baixa todos extratos dos meses na lista.

    @param driver: driver da página Selenium
    @param mes: lista com os meses desejados (formato mmm/yy)
    """
    wdw = WebDriverWait(driver, 20)

    # testa se existe uma conta cadastrada (se nao existir, retorna dataframes vazios)
    locator = (By.XPATH, '//*[@id="cxErro"]')
    element = driver.find_elements(*locator)
    if element:
        print('Não há cartoes para este cliente.')
        return pd.DataFrame(), pd.DataFrame()

    # tratamento dos meses
    lista_meses = [x.lower() for x in lista_meses]
    
    # add próxima fatura
    lista_meses.append('Próxima Fatura')

    # loop em todos os meses (se na lista)
    print('\nFatura de cartão')

    nome_arquivo_list = dict()
    for mes in lista_meses:
        nome_arquivo_list[mes] = baixa_extrato_de_um_mes(driver, mes)
    
    return nome_arquivo_list
 
def baixa_extrato_de_um_mes(driver, mes):
    """Baixa os extratos dos cartões de crédito.

    @param driver: driver da página Selenium
    @param mes: mes (formato mmm/yy)
    """
    wdw = WebDriverWait(driver, 20)
    nome_arquivo_list = list()
    mes = mes.lower()

    # loop nas imagens de cartoes (que se mantém no topo e n some)
    locator = (By.ID, 'carousel-cartoes')
    cartoes = wdw.until(ec.presence_of_element_located(locator))
    cartoes = cartoes.find_elements(By.TAG_NAME, 'img')

    for cartao in cartoes:

        # espera a imagem dos cartoes aparecer
        locator = (By.XPATH, '//*[@id="carousel-cartoes"]/img[1]')
        tag = wdw.until(ec.element_to_be_clickable(locator))

        # clica no cartão
        cartao.click()
        locator = (By.XPATH, '//*[contains(text(), "Próxima Fatura")]')
        tag = wdw.until(ec.presence_of_element_located(locator))
        time.sleep(2)

        # Navega até o mes
        navega_ate_mes(driver, mes)

        print('\nCartão', cartao.get_attribute('funcao')[-3:-2])
        print('Fatura:', mes)

        # baixa e le o arquivo
        time.sleep(1)
        locator = (By.XPATH, '//a[@title="Salvar Fatura"]')
        element = wdw.until(ec.element_to_be_clickable(locator))
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        driver.find_element(*locator).click()

        locator = (By.XPATH, '//div[@class="caixa-dialogo-conteudo"]')
        element = wdw.until(ec.element_to_be_clickable(locator))
        element = element.find_elements(By.TAG_NAME, 'a')
        element = [x for x in element if x.text == 'Money 2000+ (ofx)'][0]
        element.click()

        time.sleep(2)  # espera para o download começar
        nome_arquivo_list.append(ultimo_arquivo_baixado())

        # validacao
        if len(nome_arquivo_list) == 0:
            raise ValueError('Erro: arquivo n baixado.')

    return nome_arquivo_list


def navega_ate_mes(driver, mes):
    """
    Navega no Header de meses dos extratos.

    Move a partir das setas laterais
    @param driver: driver do navegador
    @param mes: mes do mês do extrato (mmm/aa)
    """
    wdw = WebDriverWait(driver, 20)

    # faturas anteriores
    locator = (By.ID, 'faturasAnt')
    ul_anterior = driver.find_element(*locator)
    li_anterior = ul_anterior.find_elements(By.TAG_NAME, 'li')
    a_anterior = ul_anterior.find_elements(By.TAG_NAME, 'a')

    #faturas atuais
    locator = (By.ID, 'faturasAtual')
    ul_atual = driver.find_element(*locator)
    li_atual = ul_atual.find_elements(By.TAG_NAME, 'li')
    a_atual = ul_atual.find_elements(By.TAG_NAME, 'a')

    # botões (setas)
    bt_anterior = driver.find_element(By.ID, 'laTabs')
    bt_atual = driver.find_element(By.ID, 'raTabs')

    # text`s
    text_atual = [x.text.lower() for x in a_atual]
    
    text_anterior = [x.text.lower() for x in a_anterior]
    for i, k in enumerate(text_anterior):
        k = dt.datetime.strptime(text_atual[0], '%b/%y') + relativedelta(months=-i-1)
        text_anterior[-i-1] = k.strftime('%b/%y')
        
    # Descobre onde o mes desejado está no Header
    try:
        index = text_atual.index(mes)
        a_utilizado = a_atual
    except:
        index = text_anterior.index(mes)
        a_utilizado = a_anterior
        bt_anterior.click()

    tag = a_utilizado[index]
    tag.click()

    # espera o mes carregar
    locator = (By.XPATH, '//*[contains(text(), "Cartão")]')
    tag = wdw.until(ec.presence_of_all_elements_located(locator))

