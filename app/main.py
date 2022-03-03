"""
Acesso à conta do Banco do brasil
Download e leitura dos extratos de conta corrente, poupança e cartões de crédito.
Exporta a base em excel.
"""

import datetime as dt
import locale

import pandas as pd
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from app.navegacao import nav_contas, nav_cartao, login
from app.utils.data_functions import converte_datetime

import config  # COMENTAR DEPOIS DOS TESTES
path_download = config.path_download
agencia = config.agencia1
conta = config.conta1
senha = config.senha1

def acesso_bb(path_download, agencia, conta, senha=None):
    """
    Organiza as etapas de navegação para entrar na conta bancária
    e baixar todas as informações necessárias
    @path-download: caminho completo da pasta de downloads
    @agencia: número da agência (com DV, sem traço)
    @conta: numero da conta (com DV, sem traço)
    @senha: senha da cota
    """
    dt1 = converte_datetime(dt.datetime(2021, 12, 1).date())
    dt2 = converte_datetime(dt.datetime.today().date())

    ###############
    ##### MAIN ####
    ###############

    base = pd.DataFrame({})
    baseh = pd.DataFrame({})
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    # Lista de meses desejados
    lista_meses = pd.date_range(dt1, dt2, freq='MS').tolist()
    lista_meses = [x.strftime('%b/%y') for x in lista_meses]
    lista_meses = [x.lower() for x in lista_meses]

    if dt2.date() == dt.datetime.today().date():
        prox_mes = dt.datetime.strptime(lista_meses[-1], '%b/%y')
        prox_mes = prox_mes + relativedelta(months=1)
        prox_mes = prox_mes.strftime('%b/%y')
        lista_meses.append(prox_mes)

    # Abre o navegador na página
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.set_page_load_timeout(20000)  # milisegundos
    wdw = WebDriverWait(driver, 20)

    while True:
        try:
            driver.get('https://www.bb.com.br/pbb/pagina-inicial#/')
        except TimeoutException:
            print('Timeout, reloading...')
            driver.refresh()
            continue
        else:
            break

    # Navega para a página de login
    locator = (By.XPATH, '//*[@id="acesseSuaConta"]')
    tag = wdw.until(ec.presence_of_element_located(locator))
    driver.execute_script('arguments[0].click();', tag)

    ###############
    ### TITULAR ###
    ###############

    print('Primeiro Titular')
    login.login(driver, agencia, conta, senha)

    nav_contas.nav_corrente(driver)
    dados, dados_header = nav_contas.nav_extrato_baixar(driver, lista_meses, path_download)
    base = base.append(dados, ignore_index=True)
    baseh = baseh.append(dados_header, ignore_index=True)

    nav_contas.nav_poupanca(driver)
    dados, dados_header = nav_contas.nav_extrato_baixar(driver, lista_meses, path_download)
    base = base.append(dados, ignore_index=True)
    baseh = baseh.append(dados_header, ignore_index=True)

    nav_cartao.nav_cartao(driver)
    dados, dados_header = nav_cartao.nav_cartao_baixar(driver, lista_meses, path_download)
    base = base.append(dados, ignore_index=True)
    baseh = baseh.append(dados_header, ignore_index=True)

    ##########################
    #### TROCA DE TITULAR ####
    ##########################

    if login.login_dependente(driver, '2º'):
        print('Troca de titular')

        nav_cartao.nav_cartao(driver)
        dados, dados_header = nav_cartao.nav_cartao_baixar(driver, lista_meses, path_download)
        base = base.append(dados, ignore_index=True)
        baseh = baseh.append(dados_header, ignore_index=True)
        
    ############
    #### FIM ###
    ############

    driver.close()
    return base, baseh
