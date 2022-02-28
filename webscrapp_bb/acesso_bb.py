"""
Acesso à conta do Banco do brasil
Download e leitura dos extratos de conta corrente, poupança e cartões de crédito.
Exporta a base em excel.
"""

import time
import os
import locale
import datetime as dt
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from lib import login
from lib import nav_contas
from lib import nav_cartao
from lib import funcoes
from helpers.data_functions import data_converte

# import config # COMENTAR DEPOIS DOS TESTES

def acesso_bb(PATH_DOWNLOAD, AGENCIA, CONTA, SENHA=None):

    #####################
    ##### PARAMETROS ####
    #####################

    dt1 = dt.datetime(2021, 12, 1).date()
    dt2 = dt.datetime.today().date()
    
    # # para teste
    # PATH_DOWNLOAD = config.path_download
    # AGENCIA = config.agencia1
    # CONTA = config.conta1
    # SENHA = config.senha1
    
    ###############
    ##### MAIN ####
    ###############

    WAIT = 20
    base = pd.DataFrame({})
    baseh = pd.DataFrame({})
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    # valida datas
    dt1 = data_converte(dt1)
    dt2 = data_converte(dt2)

    # Lista de meses desejados
    lista_meses = pd.date_range(dt1, dt2, freq='MS').tolist()
    lista_meses = [x.strftime("%b/%y") for x in lista_meses]
    lista_meses = [x.lower() for x in lista_meses]

    if dt2.date() == dt.datetime.today().date():
        prox = dt.datetime.strptime(lista_meses[-1], '%b/%y')
        if prox.month == 12:
            PROX_MONTH = 1
            prox_year = prox.year + 1
        else:
            PROX_MONTH = prox.month + 1
            prox_year = prox.year
        prox = dt.date(prox_year, PROX_MONTH, 1).strftime("%b/%y")
        lista_meses.append(prox)

    # Abre o navegador na página
    URL = 'https://www.bb.com.br/pbb/pagina-inicial#/'
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.set_page_load_timeout(20000)  # milisegundos

    WAIT = 20
    wdw = WebDriverWait(driver, WAIT)

    while True:
        try:
            driver.get(URL)
        except TimeoutException:
            print('Timeout, reloading...')
            driver.refresh()
            continue
        else:
            break

    # Navega para a página de login
    locator = (By.XPATH, '//*[@id="acesseSuaConta"]')
    AcesseSuaConta = wdw.until(ec.presence_of_element_located(locator)) 
    driver.execute_script("arguments[0].click();", AcesseSuaConta)

    #####################
    ### LOGIN TITULAR ###
    #####################

    print('Primeiro Titular')
    login.login(driver, AGENCIA, CONTA, SENHA)

    #######################
    #### CONTA CORRENTE ###
    #######################

    nav_contas.nav_corrente(driver)
    agregados, agregados_header = nav_contas.nav_extrato_baixar(driver, lista_meses, PATH_DOWNLOAD)

    base = base.append(agregados, ignore_index=True)
    baseh = baseh.append(agregados_header, ignore_index=True)

    ########################
    #### CONTA  POUPANÇA ###
    ########################

    nav_contas.nav_poupanca(driver)
    agregados, agregados_header = nav_contas.nav_extrato_baixar(driver, lista_meses, PATH_DOWNLOAD)

    base = base.append(agregados, ignore_index=True)
    baseh = baseh.append(agregados_header, ignore_index=True)

    ###############
    #### CARTÃO ###
    ###############

    nav_cartao.nav_cartao(driver)
    agregados, agregados_header = nav_cartao.nav_cartao_baixar(driver, lista_meses, PATH_DOWNLOAD)

    base = base.append(agregados, ignore_index=True)
    baseh = baseh.append(agregados_header, ignore_index=True)

    ##########################
    #### TROCA DE TITULAR ####
    ##########################

    print('Troca de titular')
    nome_titular = '2º'
    existe_titular = login.login_dependente(driver, nome_titular)
    
    ###############
    #### CARTÃO ###
    ###############

    if existe_titular == True:
        nav_cartao.nav_cartao(driver)
        agregados, agregados_header = nav_cartao.nav_cartao_baixar(driver, lista_meses, PATH_DOWNLOAD)

        base = base.append(agregados, ignore_index=True)
        baseh = baseh.append(agregados_header, ignore_index=True)

    ############
    #### FIM ###
    ############

    driver.close()
    return base, baseh