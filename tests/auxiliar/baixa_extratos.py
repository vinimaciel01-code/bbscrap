import pandas as pd

import bbscrap.navegacao.drivers as chrome_driver
import bbscrap.navegacao.nav_pagina as navega_pagina
import bbscrap.navegacao.login as login
import bbscrap.navegacao.nav_corrente as nav_corrente
import bbscrap.navegacao.nav_poupanca as nav_poupanca
import bbscrap.navegacao.nav_cartao as nav_cartao
import tests.config as config


driver = chrome_driver.chrome_driver_init()
navega_pagina.navega_pagina(driver)
login.login_banco(driver, config.agencia1, config.conta1, config.senha1)

lista_meses = ['abr/22', 'mai/22']

nav_corrente.navega_pagina(driver)
dados_corrente, temp = nav_corrente.baixa_extrato(driver, lista_meses)

nav_poupanca.navega_pagina(driver)
dados_poupanca, temp = nav_poupanca.baixa_extrato(driver, lista_meses)

nav_cartao.navega_pagina(driver)
dados_cartao, temp = nav_cartao.baixa_extrato(driver, lista_meses)

driver.close()

"""Exporta para o Excel"""

with pd.ExcelWriter('test_corpo.xlsx', mode='w') as writer:
    dados_corrente.to_excel(writer, index=False, float_format='%.2f', sheet_name='corrente')
    dados_poupanca.to_excel(writer, index=False, float_format='%.2f', sheet_name='poupanca')
    dados_cartao.to_excel(writer, index=False, float_format='%.2f', sheet_name='cartao')
