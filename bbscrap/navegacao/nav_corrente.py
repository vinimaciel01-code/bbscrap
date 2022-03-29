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
    """Navega para a página de extrato da conta corrente.

    @param driver: driver da página Selenium
    """
    wdw = WebDriverWait(driver, 20)

    # navegacao
    locator = (By.XPATH, '//a[@codigo="32454"]')
    element = wdw.until(ec.element_to_be_clickable(locator))
    tentativas = 0
    while tentativas <= 2:
        tentativas = tentativas + 1
        try:
            parent = element.find_element(By.XPATH, '..')
            parent.click()
            parent2 = parent.find_element(By.XPATH, '..')
            parent2.click()
            element.click()
            break
        except:
            time.sleep(1)
            continue

    # subelemento
    locator = (By.XPATH, '//a[@codigo="32456"]')
    wdw.until(ec.element_to_be_clickable(locator)).click()

    # Espera a página carregar (até aparecer o header dos meses)
    locator = (By.XPATH, '//*[@id="tabs"]/ul')
    try:
        wdw.until(ec.element_to_be_clickable(locator))
    except:
        pass


def baixa_extrato(driver, lista_meses, path_download):
    """Baixa o extratos da conta corrente ou poupança.

    @param driver: driver da página Selenium
    @param lista_meses: Lista com os meses desejados (formato mmm/yy)
    @param path_download: caminho da pasta de download.
    """
    wdw = WebDriverWait(driver, 20)
    corpo = pd.DataFrame({})
    header = pd.DataFrame({})

    # tratamento inicial
    lista_meses = [x.lower() for x in lista_meses]

    # testa se existe uma conta cadastrada
    locator = (By.XPATH, '//*[@id="cxErro"]')
    element = driver.find_elements(*locator)
    if element:
        print('conta extrato inexistente')
        return pd.DataFrame(), pd.DataFrame()

    # mes atual
    xpath = '//*[@id="dia"]/option'
    locator = (By.XPATH, xpath)
    header_ult_mes = driver.find_element(*locator)
    header_ult_mes = header_ult_mes.get_attribute('innerHTML')

    # todos links
    xpath = '//li[@aria-controls="divResultadoExtrato"]'
    locator = (By.XPATH, xpath)
    header_lis = driver.find_elements(*locator)
    header_nomes = meses_links(header_lis)

    # Navega para o mes e download
    for index, nome in enumerate(header_nomes):

        if nome not in lista_meses:
            continue

        print(f'\n{nome}')
        tag = header_lis[index]

        # coloca o mes desejado em display
        meses_navega_ate_display(driver, tag, nome)

        # Seleciona o extrato do mes desejados
        # Para mes corrente: combobox >> abrir seleção >> clica na primeira opção (mes inteiro)
        if index == len(header_lis) - 2:
            xpath = '//span[@class="custom-combobox"]//a[@tabindex="-1"]'
            locator = (By.XPATH, xpath)
            element = tag.find_element(*locator)
            element.click()

            xpath = '//li[@class="ui-menu-item"]'
            locator = (By.XPATH, xpath)
            tag = driver.find_element(*locator)   # atualizando o Tag!

        tag.click()

        # wait: tabela de valores aparecer
        locator = (By.XPATH, '//div[@id="divResultadoExtrato"]')
        wdw.until(ec.element_to_be_clickable(locator))

        # baixa e le arquivo
        locator = (By.XPATH, '//a[@title="Salvar documento"]')
        element = wdw.until(ec.element_to_be_clickable(locator))
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        driver.find_element(*locator).click()

        locator = (By.XPATH, '//div[@class="caixa-dialogo-conteudo"]')
        element = wdw.until(ec.element_to_be_clickable(locator))
        element = element.find_elements(By.TAG_NAME, 'a')
        element = [x for x in element if x.text == 'Money 2000+ (ofx)'][0]
        element.click()

        lista, lista_header = abre_le_arquivo_ofx(path_download)

        # validacao
        if lista is None or lista.empty:
            print('lista vazia')
            continue

        # validacao
        if dt.datetime.strftime(lista.iloc[0, 0], '%b/%y').lower() != nome:
            raise Exception('Erro: data do extrato diferente do mês de referência')

        # grava o mes
        lista_header['mes_ref'] = nome.lower()
        lista['mes_ref'] = nome.lower()

        # grava a variacao
        lista_header['tipo_conta'] = ['Poupança' if x != '' else 'Conta Corrente'
                                      for x in lista_header['variacao']]
        lista['tipo_conta'] = ['Poupança' if x != '' else 'Conta Corrente'
                               for x in lista['variacao']]

        # grava no acumulado
        corpo = pd.concat([corpo, lista], ignore_index=True)
        header = pd.concat([header, lista_header], ignore_index=True)

        print(lista.iloc[0, 0])

    return corpo, header


def meses_links(header_lis):
    """Pega o html dos links dos meses e retorna lista de meses."""
    # meses de todos links
    header_nomes = ['' for x in header_lis]
    for index, nome in enumerate(header_nomes):
        temp_mes = ''
        # especial: pula o ext dos ultimos 30 dias
        if index == len(header_nomes) - 1:
            pass
        # especial: nome do mes atual (anterior + 1month)
        elif index == len(header_nomes) - 2:
            nome = header_lis[index - 1]
            temp_atr = nome.get_attribute('mes')
            temp_mes = temp_atr
            if len(temp_mes) > 6:   # corrente
                temp_mes = temp_mes[-4:] + temp_mes[-6:-4]
            temp_mes = dt.datetime.strptime(temp_mes, '%Y%m').date()
            temp_mes = temp_mes + relativedelta(months=1)
            temp_mes = dt.datetime.strftime(temp_mes, '%b/%y')
        # normal
        else:
            nome = header_lis[index]
            temp_atr = nome.get_attribute('mes')
            temp_mes = temp_atr
            if len(temp_mes) > 6:   # corrente
                temp_mes = temp_mes[-4:] + temp_mes[-6:-4]
            temp_mes = dt.datetime.strptime(temp_mes, '%Y%m').date()
            temp_mes = dt.datetime.strftime(temp_mes, '%b/%y')
        # salva
        header_nomes[index] = temp_mes.lower()

    return header_nomes


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
