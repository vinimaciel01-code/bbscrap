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
from bbscrap.utils.data_functions import converte_datetime
from bbscrap.utils.sistema import blockPrint, enablePrint


def acesso_bb(path_download, agencia=None, conta=None, senha=None,
              dt1=None, outros_titulares=None, block_print=True):
    """Acessa o Banco do Brasil e baixa as informações requisitadas.

    @param path_download: caminho completo da pasta de downloads
    @param agencia: número da agência (com DV, sem traço)
    @param conta: numero da conta (com DV, sem traço)
    @param senha: senha da cota
    @param dt1: data de início da procura de dados
    @param outros_titulares: lista com o nome Bancário dos outros titulares da conta.
    Nome parcial é permitido. Apenas extratos de cartões de crédito são baixados.
    """
    # setup
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    corpo_base = pd.DataFrame({})
    header_base = pd.DataFrame({})
    if block_print is True:
        blockPrint()

    # datas
    dt2 = dt.datetime.today()
    dt1 = converte_datetime(dt1)
    if dt1 is None or dt1 > dt2:
        dt1 = converte_datetime(dt2 - relativedelta(years=1))
    lista_meses = transforma_datas_lista(dt1, dt2)

    # Inicializa pagina
    driver = drivers.chrome_driver_init()
    nav_pagina.navega_pagina(driver)
    login.login_banco(driver, agencia, conta, senha)

    # Títular Principal
    corpo, header = navega_todos_extratos(driver, lista_meses, path_download)
    corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
    header_base = pd.concat([header_base, header], ignore_index=True)

    # Outros Titulares
    if isinstance(outros_titulares, list):
        for titular in outros_titulares:
            if dependente.login_dependente(driver, titular):
                nav_cartao.navega_pagina(driver)
                corpo, header = nav_cartao.baixa_extrato(driver, lista_meses, path_download)
                corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
                header_base = pd.concat([header_base, header], ignore_index=True)

    # Encerra
    driver.close()
    if block_print is True:
        enablePrint()
    return corpo_base, header_base


def transforma_datas_lista(dt1, dt2):

    lista_meses = pd.date_range(dt1, dt2, freq='MS').tolist()
    lista_meses = [x.strftime('%b/%y') for x in lista_meses]
    lista_meses = [x.lower() for x in lista_meses]

    if dt2.date() == dt.datetime.today().date():
        prox_mes = dt.datetime.strptime(lista_meses[-1], '%b/%y')
        prox_mes = prox_mes + relativedelta(months=1)
        prox_mes = prox_mes.strftime('%b/%y')
        lista_meses.append(prox_mes)

    return lista_meses


def navega_todos_extratos(driver, lista_meses, path_download):

    corpo_base = pd.DataFrame({})
    header_base = pd.DataFrame({})

    nav_corrente.navega_pagina(driver)
    corpo, header = nav_corrente.baixa_extrato(driver, lista_meses, path_download)
    corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
    header_base = pd.concat([header_base, header], ignore_index=True)

    nav_poupanca.navega_pagina(driver)
    corpo, header = nav_poupanca.baixa_extrato(driver, lista_meses, path_download)
    corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
    header_base = pd.concat([header_base, header], ignore_index=True)

    nav_cartao.navega_pagina(driver)
    corpo, header = nav_cartao.baixa_extrato(driver, lista_meses, path_download)
    corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
    header_base = pd.concat([header_base, header], ignore_index=True)

    return corpo_base, header_base


if __name__ == '__main__':

    import bbscrap.config as config
    corpo, header = acesso_bb(path_download=config.path_download, dt1='01/01/2022',
                              agencia=config.agencia, conta=config.conta, senha=config.senha,
                              outros_titulares=['Thais'], block_print=False)
