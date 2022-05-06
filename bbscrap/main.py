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
from bbscrap.tratamento.memo_divisao import memo_divisao
from bbscrap.tratamento.altera_variaveis import altera_variaveis
from bbscrap.tratamento.cria_variaveis import cria_variaveis
from bbscrap.tratamento.chave_unica import chave_unica

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
    # setup
    corpo_base = pd.DataFrame({})
    header_base = pd.DataFrame({})
    
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
    corpo, header = navega_todos_extratos(driver, lista_meses)
    corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
    header_base = pd.concat([header_base, header], ignore_index=True)

    # Outros Titulares
    if isinstance(outros_titulares, list):
        for titular in outros_titulares:
            if dependente.login_dependente(driver, titular):
                nav_cartao.navega_pagina(driver)
                corpo, header = nav_cartao.baixa_extrato(driver, lista_meses)
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


def navega_todos_extratos(driver, lista_meses):

    corpo_base = pd.DataFrame({})
    header_base = pd.DataFrame({})

    nav_corrente.navega_pagina(driver)
    corpo, header = nav_corrente.baixa_extrato(driver, lista_meses)
    corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
    header_base = pd.concat([header_base, header], ignore_index=True)

    nav_poupanca.navega_pagina(driver)
    corpo, header = nav_poupanca.baixa_extrato(driver, lista_meses)
    corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
    header_base = pd.concat([header_base, header], ignore_index=True)

    nav_cartao.navega_pagina(driver)
    corpo, header = nav_cartao.baixa_extrato(driver, lista_meses)
    corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
    header_base = pd.concat([header_base, header], ignore_index=True)

    return corpo_base, header_base


def tratamento_dados(corpo, header):
    """Tratamento dos dados, formando novas variáveis, corrigindo outras.

    @param corpo: pd.Dataframe() dos dados dos extratos consultados.
    @param header: pd.Dataframe() dos cabeçalhos da consulta realizada
    """

    # Copia as bases
    dados = corpo.copy()
    dados_h = header.copy()

    # divide o memo em 2 partes
    memo1, memo2 = memo_divisao(dados)
    dados['memo1'] = memo1
    dados['memo2'] = memo2

    # tira o traço '-' da AGENCIA e CONTA
    dados['agencia'] = [x.replace('-', '') for x in dados['agencia']]
    dados['conta'] = [x.replace('-', '') for x in dados['conta']]
    dados_h['agencia'] = [x.replace('-', '') for x in dados_h['agencia']]
    dados_h['conta'] = [x.replace('-', '') for x in dados_h['conta']]

    # Altera variáveis (mes_ref) - depois de memo_divisao (memo2)
    dados = altera_variaveis(dados)

    # Cria variáveis - depois de altera variáveis
    dados = cria_variaveis(dados)

    # Cria a chave de indentificação única - depois de altera variáveis (mes_ref)
    chave = chave_unica(dados)
    dados['chave'] = chave

    # reordenando
    dados = dados[['data', 'banco', 'agencia', 'conta', 'variacao', 'tipo_conta', 'memo', 'tipo_mov', 'moeda', 'valor',
                'chave', 'tipo_entrada', 'mes_ref', 'dataN', 'mesN', 'memo1', 'memo2', 'valorN', 'data_import']]
    dados_h = dados_h[['banco', 'agencia', 'conta', 'variacao', 'tipo_conta', 'mes_ref', 'dt_inicio', 'dt_fim', 'saldo']]

    return dados, dados_h