"""Função auxiliar: ler o ofx salvado na pasta de downloads."""

import os
from pathlib import Path

from bbscrap.utils.arquivo import download_concluido


def ultimo_arquivo_baixado():
    """Seleciona o arquivo que iremos que iremos ler."""
    
    path_download = str(os.path.join(Path.home(), "Downloads"))
    download_concluido(path_download)

    # lista todos arquivos com extensão OFX
    pasta_baixados = os.listdir(path_download)
    pasta_baixados = [d for d in pasta_baixados if '.ofx' in d]
    if pasta_baixados == []:
        return None

    # seleciona o OFX mais novo
    pasta_baixados = [os.path.join(path_download, d) for d in pasta_baixados]
    arquivo_novato = max(pasta_baixados, key=os.path.getctime)

    return arquivo_novato

