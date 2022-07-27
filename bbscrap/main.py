"""Acesso à conta do Banco do Brasil.

Acessa a conta pessoal do Banco do Brasil do usuário.
O login pode ser feito totalmente pelo app ou manualmente pelo usuário.
Download dos extratos de conta corrente, poupança e cartões de crédito do titular principal.
Para os outros titulares, baixa apenas o cartão de crédito (pois os extratos são os mesmos).
"""

import datetime as dt
import locale
import pandas as pd
from dateutil.relativedelta import relativedelta

from bbscrap.navegacao import drivers, nav_pagina, login, dependente
from bbscrap.navegacao import nav_corrente, nav_poupanca, nav_cartao

from bbscrap.tratamento.main_tratamento import tratamento_dados
from bbscrap.tratamento.lerofx import ler_ofx

from bbscrap.utils.data_functions import converte_datetime
from bbscrap.utils.sistema import blockPrint, enablePrint


def acesso_bb(agencia=None, conta=None, senha=None,
              data_inicial=None, outros_titulares=None, 
              tratamento=False,
              block_print=True):
    """Acessa o Banco do Brasil e baixa as informações requisitadas.

    @param agencia: número da agência (com DV, sem traço)
    @param conta: numero da conta (com DV, sem traço)
    @param senha: senha da cota
    @param data_inicial: data de início da procura de dados
    @param outros_titulares: lista com o nome Bancário dos outros titulares da conta.
    Nome parcial é permitido. Apenas extratos de cartões de crédito são baixados.
    """
    
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    if block_print is True:
        blockPrint()

    # datas
    data_inicial = converte_datetime(data_inicial)
    data_final = dt.datetime.today()
    if data_inicial is None or data_inicial > data_final:
        data_inicial = converte_datetime(data_final - relativedelta(years=1))
    else:
        data_inicial = converte_datetime(data_inicial)

    lista_meses = pd.date_range(data_inicial, data_final, freq='MS').tolist()
    lista_meses = [x.strftime('%b/%y') for x in lista_meses]
    lista_meses = [x.lower() for x in lista_meses]

    # Inicializa pagina
    driver = drivers.chrome_driver_init()
    nav_pagina.navega_pagina(driver)
    login.login_banco(driver, agencia, conta, senha)

    # Títular Principal
    
    corpo_base = pd.DataFrame({})
    header_base = pd.DataFrame({})

    nome_arquivos_list = nav_corrente.central(driver, lista_meses)
    if nome_arquivos_list:
        for key in nome_arquivos_list:
            for elem in nome_arquivos_list[key]:
                corpo, header = ler_ofx(elem, key)
                corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
                header_base = pd.concat([header_base, header], ignore_index=True)

    nome_arquivos_list = nav_poupanca.central(driver, lista_meses)
    if nome_arquivos_list:
        for key in nome_arquivos_list:
            for elem in nome_arquivos_list[key]:
                corpo, header = ler_ofx(elem, key)
                corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
                header_base = pd.concat([header_base, header], ignore_index=True)
    
    nome_arquivos_list = nav_cartao.central(driver, lista_meses)
    if nome_arquivos_list:
        for key in nome_arquivos_list:
            for elem in nome_arquivos_list[key]:
                corpo, header = ler_ofx(elem, key)
                corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
                header_base = pd.concat([header_base, header], ignore_index=True)
 
    # Outros Titulares
    if isinstance(outros_titulares, list):
        for titular in outros_titulares:
            if dependente.login_dependente(driver, titular):
                nome_arquivos_list = nav_cartao.central(driver, lista_meses)
                if nome_arquivos_list:
                    for key in nome_arquivos_list:
                        for elem in nome_arquivos_list[key]:
                            corpo, header = ler_ofx(elem, key)
                            corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
                            header_base = pd.concat([header_base, header], ignore_index=True)

    # Encerra driver
    driver.close()
    if block_print is True:
        enablePrint()

    #Tratamento de dados
    if tratamento is True:
        corpo_base, header_base = tratamento_dados(corpo_base, header_base)

    # Fim
    return corpo_base, header_base