import pandas as pd
import bbscrap.main as main
corpo, header = main.acesso_bb(agencia='51977', conta='9991425', senha='02092812', data_inicial='01/03/2022')

"""Exporta para o Excel"""

with pd.ExcelWriter('test_corpo.xlsx', mode='w') as writer:
    corpo.to_excel(writer, index=False, float_format='%.2f', sheet_name='corpo')
    header.to_excel(writer, index=False, float_format='%.2f', sheet_name='header')

# para rodar manualmente

agencia='51977' 
conta='9991425' 
senha='02092812'
data_inicial='01/05/2022'
outros_titulares=None
tratamento=False
block_print=False

import os
from pathlib import Path
path_download = str(os.path.join(Path.home(), "Downloads"))
nome_arquivos_list = os.listdir(path_download)
nome_arquivos_list = [os.path.join(path_download, d) for d in nome_arquivos_list if '.ofx' in d]
nome_arquivo = nome_arquivos_list[1]