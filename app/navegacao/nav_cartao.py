"""
navega para a conta cartão
- acessa os meses desejados
- baixa o OFX
- lê o OFX
- formata em uma DataFrame
- Retorna o DataFrame
"""
import datetime as dt
import time

import pandas as pd
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from app.navegacao import funcoes


def nav_cartao(driver):
    """
    Navega para a página dos extratos dos cartões
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
    barra_submenu =wdw.until(ec.element_to_be_clickable(locator))
    barra_submenu.click()

    # Espera a página carregar (até aparecer o header dos meses)
    locator = (By.XPATH, '//*[@id="tabs"]/ul')
    try:
        wdw.until(ec.element_to_be_clickable(locator))
    except:
        pass


def nav_cartao_baixar(driver, lista_meses, path_download):
    """
    Navega entre os meses de cada cartão de crédito disponível e faz o download e leitura do OFX
    @param driver: driver da página Selenium
    @param lista_meses: list. Lista com os meses desejados (formato mmm/yy)
    @param path_download: caminho da pasta de download, para recuperar o OFX baixado.
    """
    wdw = WebDriverWait(driver, 20)
    agregados_header = pd.DataFrame({})
    agregados = pd.DataFrame({})

    # testa se existe uma conta cadastrada
    # Se nao existir, retorna dataframes vazios
    locator = (By.XPATH, '//*[@id="cxErro"]')
    tag = driver.find_elements(*locator)
    if tag:
        print('Não há cartoes para este cliente')
        return pd.DataFrame(), pd.DataFrame()

    # loop nas imagens de cartoes (que se mantém no topo e n some)
    locator = (By.ID, 'carousel-cartoes')
    cartoes = driver.find_element(*locator)
    cartoes = cartoes.find_elements(By.TAG_NAME, 'img')

    for cartao in cartoes:
        print('-', cartao.get_attribute('funcao'))

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
        time.sleep(5)

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
        for index, value in enumerate(headers_mes_tags):

            # apenas meses desejados
            if headers_mes_nomes[index].lower() not in lista_meses:
                continue
            print(f'\n{headers_mes_nomes[index].lower()}')

            # muda para o mes
            value.click()

            # espera o mes carregar
            # por algum motivo n funciona. Logo sleep(3)
            locator = (By.XPATH, '//div[@id="tab-conteudo"]//table')
            wdw.until(ec.presence_of_element_located(locator))
            time.sleep(3)

            # baixa e le o arquivo
            locator = (By.XPATH, '//a[@title="Salvar Fatura"]')
            tag = wdw.until(ec.element_to_be_clickable(locator))
            actions = ActionChains(driver)
            actions.move_to_element(tag).perform()
            driver.find_element(*locator).click()

            locator = (By.XPATH, '//div[@class="caixa-dialogo-conteudo"]')
            tag = wdw.until(ec.element_to_be_clickable(locator))
            tag = tag.find_elements(By.TAG_NAME, 'a')
            tag = [x for x in tag if x.text == 'Money 2000+ (ofx)'][0]
            tag.click()

            time.sleep(2)  # espera para o download começar
            lista, lista_header = funcoes.ler_ofx(path_download)

            # validacao
            if lista is None or lista.empty:
                continue

            # validacao
            if lista is not None:
                lista['mes_ref'] = headers_mes_nomes[index].lower()
                lista_header['mes_ref'] = headers_mes_nomes[index].lower()
                agregados = agregados.append(lista)
                agregados_header = agregados_header.append(
                    lista_header, ignore_index=True
                )

            print(lista.iloc[0, 0])

    agregados_header['tipo_conta'] = 'Cartão'
    agregados_header['conta'] = [x[-4:] for x in agregados_header['conta']]

    agregados['tipo_conta'] = 'Cartão'
    agregados['conta'] = [x[-4:] for x in agregados['conta']]

    return agregados, agregados_header
