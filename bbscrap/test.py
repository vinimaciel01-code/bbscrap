import bbscrap.navegacao.drivers as chrome_driver
import bbscrap.navegacao.nav_pagina as navega_pagina
import bbscrap.navegacao.login as login
import bbscrap.navegacao.nav_corrente as nav_corrente
import bbscrap.navegacao.nav_poupanca as nav_poupanca
import bbscrap.navegacao.nav_cartao as nav_cartao
import bbscrap.config as config

driver = chrome_driver.chrome_driver_init()
navega_pagina.navega_pagina(driver)
login.login_banco(driver, config.agencia, config.conta, config.senha)

lista_meses = ['jan/22']
path_download = r'C:\Users\vinim\Downloads\Nova pasta'

nav_cartao.navega_pagina(driver)
dados = nav_cartao.baixa_extrato(driver, lista_meses, path_download)

nav_corrente.navega_pagina(driver)
dados = nav_corrente.baixa_extrato(driver, lista_meses, config.path_download)

nav_poupanca.navega_pagina(driver)
dados = nav_poupanca.baixa_extrato(driver, lista_meses, config.path_download)
