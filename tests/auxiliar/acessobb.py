import pandas as pd

import bbscrap.main as main

corpo, header = main.acesso_bb(agencia='51977', conta='9991425', senha='02092812',
                                data_inicial='01/03/2022', outros_titulares=None, 
                                tratamento=True)

"""Exporta para o Excel"""

with pd.ExcelWriter('test_corpo.xlsx', mode='w') as writer:
    corpo.to_excel(writer, index=False, float_format='%.2f', sheet_name='corpo')
    header.to_excel(writer, index=False, float_format='%.2f', sheet_name='header')

