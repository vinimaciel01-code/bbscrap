import pandas as pd

import bbscrap.navegacao.drivers as chrome_driver
import bbscrap.navegacao.nav_pagina as navega_pagina
import bbscrap.navegacao.login as login
import bbscrap.navegacao.nav_corrente as nav_corrente
import bbscrap.navegacao.nav_poupanca as nav_poupanca
import bbscrap.navegacao.nav_cartao as nav_cartao

from bbscrap.utils.data_functions import converte_datetime
from dateutil.relativedelta import relativedelta
import datetime as dt

from bbscrap.tratamento.memo_divisao import memo_divisao
from bbscrap.tratamento.altera_variaveis import altera_variaveis
from bbscrap.tratamento.cria_variaveis import cria_variaveis
from bbscrap.tratamento.chave_unica import chave_unica

import tests.config as config

# datas
data_inicial = converte_datetime('01/03/2022')
data_final = dt.datetime.today()
if data_inicial is None or data_inicial > data_final:
    data_inicial = converte_datetime(data_final - relativedelta(years=1))
else:
    data_inicial = converte_datetime(data_inicial)

lista_meses = pd.date_range(data_inicial, data_final, freq='MS').tolist()
lista_meses = [x.strftime('%b/%y') for x in lista_meses]
lista_meses = [x.lower() for x in lista_meses]

corpo_base = pd.DataFrame({})
header_base = pd.DataFrame({})

# navega
driver = chrome_driver.chrome_driver_init()
navega_pagina.navega_pagina(driver)
login.login_banco(driver, config.agencia1, config.conta1, config.senha1)

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

driver.close()

"""tratamentos"""

# Copia as bases
dados = corpo_base.copy()
dados_h = header_base.copy()

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

"""Exporta para o Excel"""

with pd.ExcelWriter('test_corpo.xlsx', mode='w') as writer:
    dados.to_excel(writer, index=False, float_format='%.2f', sheet_name='corpo')
    dados_h.to_excel(writer, index=False, float_format='%.2f', sheet_name='header')
