
import bbscrap.navegacao.drivers as chrome_driver
import bbscrap.navegacao.nav_pagina as navega_pagina
import bbscrap.navegacao.login as login
import bbscrap.navegacao.nav_corrente as nav_corrente
import bbscrap.config as config

driver = chrome_driver.chrome_driver_init()
navega_pagina.navega_pagina(driver)
login.login_banco(driver, config.agencia, config.conta, config.senha)
nav_corrente.navega_pagina(driver)

lista_meses = ['jan/22']
path_download = r'C:\Users\vinim\Downloads\Nova pasta'
dados = nav_corrente.baixa_extrato(driver, lista_meses, config.path_download)
