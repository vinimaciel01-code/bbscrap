"""
Acesso à conta do Banco do brasil
Download e leitura dos extratos de conta corrente, poupança e cartões de crédito.
Exporta a base em excel.
"""

import sys
import locale
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

import utils.append as app
print(sys.path)

# from utils import append

# from lib import nav_contas
# from lib import nav_cartao

# from navegacao.funcoes import base_export
# from library.funcoes import base_export

# from helpers.data_functions import data_converte

# import config # COMENTAR DEPOIS DOS TESTES

# def acesso_bb(path_download, agencia, conta, senha=None):

#     dt1 = data_converte(
#         dt.datetime(2021, 12, 1).date())
#     dt2 = data_converte(
#         dt.datetime.today().date())
    
#     ###############
#     ##### MAIN ####
#     ###############
    
#     base = pd.DataFrame({})
#     baseh = pd.DataFrame({})
#     locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

#     # Lista de meses desejados
#     lista_meses = pd.date_range(dt1, dt2, freq='MS').tolist()
#     lista_meses = [x.strftime("%b/%y") for x in lista_meses]
#     lista_meses = [x.lower() for x in lista_meses]

#     if dt2.date() == dt.datetime.today().date():
#         prox = dt.datetime.strptime(lista_meses[-1], '%b/%y')
#         if prox.month == 12:
#             prox_month = 1
#             prox_year = prox.year + 1
#         else:
#             prox_month = prox.month + 1
#             prox_year = prox.year
#         prox = dt.date(prox_year, prox_month, 1).strftime("%b/%y")
#         lista_meses.append(prox)

#     # Abre o navegador na página
#     URL = 'https://www.bb.com.br/pbb/pagina-inicial#/'
#     driver = webdriver.Chrome()
#     driver.maximize_window()
#     driver.set_page_load_timeout(20000)  # milisegundos
#     wdw = WebDriverWait(driver, 20)

#     while True:
#         try:
#             driver.get(URL)
#         except TimeoutException:
#             print('Timeout, reloading...')
#             driver.refresh()
#             continue
#         else:
#             break

#     # Navega para a página de login
#     locator = (By.XPATH, '//*[@id="acesseSuaconta"]')
#     tag = wdw.until(ec.presence_of_element_located(locator)) 
#     driver.execute_script("arguments[0].click();", tag)

#     #####################
#     ### LOGIN TITULAR ###
#     #####################

#     print('Primeiro Titular')
#     login.login(driver, agencia, conta, senha)

#     # #######################
#     # #### conta CORRENTE ###
#     # #######################

#     # nav_contas.nav_corrente(driver)
#     # agregados, agregados_header = nav_contas.nav_extrato_baixar(driver, lista_meses, path_download)

#     # base = base.append(agregados, ignore_index=True)
#     # baseh = baseh.append(agregados_header, ignore_index=True)

#     # ########################
#     # #### conta  POUPANÇA ###
#     # ########################

#     # nav_contas.nav_poupanca(driver)
#     # agregados, agregados_header = nav_contas.nav_extrato_baixar(driver, lista_meses, path_download)

#     # base = base.append(agregados, ignore_index=True)
#     # baseh = baseh.append(agregados_header, ignore_index=True)

#     # ###############
#     # #### CARTÃO ###
#     # ###############

#     # nav_cartao.nav_cartao(driver)
#     # agregados, agregados_header = nav_cartao.nav_cartao_baixar(driver, lista_meses, path_download)

#     # base = base.append(agregados, ignore_index=True)
#     # baseh = baseh.append(agregados_header, ignore_index=True)

#     # ##########################
#     # #### TROCA DE TITULAR ####
#     # ##########################

#     # if login.login_dependente(driver, '2º'):

#     #     print('Troca de titular')
#     #     #### CARTÃO ###
#     #     nav_cartao.nav_cartao(driver)
#     #     agregados, agregados_header = nav_cartao.nav_cartao_baixar(driver, lista_meses, path_download)

#     #     base = base.append(agregados, ignore_index=True)
#     #     baseh = baseh.append(agregados_header, ignore_index=True)

#     ############
#     #### FIM ###
#     ############

#     driver.close()
#     return base, baseh