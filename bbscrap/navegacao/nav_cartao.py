"""Navegação e download dos extratos de conta corrente e poupança."""

import datetime as dt
import time

import pandas as pd
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from bbscrap.navegacao.lerofx import abre_le_arquivo_ofx


def navega_pagina(driver):
    """Navega para a página dos extratos dos cartões.

    @param driver: driver da página Selenium
    """
    wdw = WebDriverWait(driver, 20)

    # navegacao
    locator = (By.XPATH, '//a[@codigo="32578"]')
    barra_menu = wdw.until(ec.element_to_be_clickable(locator))
    tentativas = 0  # para corrigir uma falha no click
    while tentativas <= 2:
        tentativas = tentativas + 1
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


def baixa_extrato(driver, lista_meses, path_download):
    """Baixa os extratos dos cartões de crédito.

    @param driver: driver da página Selenium
    @param lista_meses: list. Lista com os meses desejados (formato mmm/yy)
    @param path_download: caminho da pasta de download
    """
    wdw = WebDriverWait(driver, 20)
    header = pd.DataFrame({})
    corpo = pd.DataFrame({})

    # testa se existe uma conta cadastrada (se nao existir, retorna dataframes vazios)
    locator = (By.XPATH, '//*[@id="cxErro"]')
    element = driver.find_elements(*locator)
    if element:
        print('Não há cartoes para este cliente')
        return pd.DataFrame(), pd.DataFrame()

    # loop nas imagens de cartoes (que se mantém no topo e n some)
    locator = (By.ID, 'carousel-cartoes')
    cartoes = driver.find_element(*locator)
    cartoes = cartoes.find_elements(By.TAG_NAME, 'img')

    for cartao in cartoes:

        print('\n- Cartão', cartao.get_attribute('funcao')[-3:-2])

        # espera a img dos cartoes estar carregada
        locator = (By.XPATH, '//*[@id="carousel-cartoes"]/img[1]')
        while True:
            try:
                wdw.until(ec.element_to_be_clickable(locator))
                break
            except:
                locator = (By.ID, 'carousel-cartoes')
                driver.find_element(*locator)

        # clica no cartão
        cartao.click()
        time.sleep(3)

        # meses de todos os links das abas
        locator = (By.ID, 'tabs-cartao')
        headers_mes_tags = driver.find_element(*locator)
        headers_mes_tags = headers_mes_tags.find_elements(By.TAG_NAME, 'a')
        headers_mes_nomes = [x.text for x in headers_mes_tags]

        # add proximo mes como mmm/aa
        prox_mes = dt.datetime.strptime(headers_mes_nomes[-2], '%b/%y')
        prox_mes = prox_mes + relativedelta(months=1)
        prox_mes = prox_mes.strftime('%b/%y').capitalize()
        headers_mes_nomes[headers_mes_nomes.index('Próxima Fatura')] = prox_mes

        # loop em todos os meses (se na lista)
        for index, nome in enumerate(headers_mes_tags):

            tag = headers_mes_tags[index]

            # apenas meses desejados
            if headers_mes_nomes[index].lower() not in lista_meses:
                continue
            print(f'{headers_mes_nomes[index].lower()}')

            # muda para o mes
            meses_navega_ate_display(driver, tag, nome)
            tag.click()

            # espera o mes carregar (por algum motivo n funciona, logo, sleep)
            locator = (By.XPATH, '//div[@id="tab-conteudo"]//table')
            wdw.until(ec.presence_of_element_located(locator))
            time.sleep(3)

            # baixa e le o arquivo
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
            lista, lista_header = abre_le_arquivo_ofx(path_download)

            # validacao
            if lista is None or lista.empty:
                continue

            # grava o mes de referencia da fatura
            lista['mes_ref'] = headers_mes_nomes[index].lower()
            lista_header['mes_ref'] = headers_mes_nomes[index].lower()

            # grava o tipo de conta
            lista['tipo_conta'] = 'Cartão'
            lista_header['tipo_conta'] = 'Cartão'

            #  grava número da conta
            lista['conta'] = [x[-4:] for x in lista['conta']]
            lista_header['conta'] = [x[-4:] for x in lista_header['conta']]

            # grava no acumulado
            corpo = pd.concat([corpo, lista], ignore_index=True)
            header = pd.concat([header, lista_header], ignore_index=True)

            print(lista.iloc[0, 0])

    return corpo, header


def meses_navega_ate_display(driver, tag, nome):
    """
    Coloca em Display o mês do extrato desejado.

    Move a partir das setas laterais
    @param driver: driver do navegador
    @param tag link selenium do extrato
    @param nome: nome do mês do extrato (mmm/aa)
    """
    if tag.get_attribute('style') == 'display: none;':

        # Primeiro mes em display
        xpath = '//li[@aria-controls="divResultadoExtrato" and @style="display: list-item;"]'
        locator = (By.XPATH, xpath)
        display = driver.find_element(*locator)
        display_esq = display.get_attribute('mes')
        display_esq = display_esq[-4:] + display_esq[-6:-4]
        display_esq = dt.datetime.strptime(display_esq, '%Y%m').date()
        temp_desejo = dt.datetime.strptime(nome, '%b/%y').date()

        # caminha esquerda
        if temp_desejo < display_esq:
            xpath = '//li[contains(@class, "ui-tabs-paging-prev")]/a'
            locator = (By.XPATH, xpath)
            seta_esq = driver.find_element(*locator)
            while True:
                seta_esq.click()
                if tag.get_attribute('style') != 'display: none;':
                    break

        # caminha direita
        else:
            xpath = '//li[contains(@class, "ui-tabs-paging-next")]/a'
            locator = (By.XPATH, xpath)
            seta_dir = driver.find_element(*locator)
            while True:
                seta_dir.click()
                if tag.get_attribute('style') != 'display: none;':
                    break
