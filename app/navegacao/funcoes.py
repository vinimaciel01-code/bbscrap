"""
Funçoes auxiliares não ligadas à navegação na página
- ler_ofx: le o ofx baixado
- base_export: cria novas variáveis e transforma existentes
- chave_unica: cria a chave única da transação
- memo_divisao: divide o memo em 2 partes
"""

import codecs
import datetime as dt
import os
import re

import pandas as pd
from dateutil.relativedelta import relativedelta
from ofxparse import OfxParser

from app.utils.arquivo import download_concluido

####################
##### FUNCOES ######
####################


def ler_ofx(path_download):
    """
    Le o último arquivo baixado com extensão '.ofx'
    @path_download: caminho da pasta de downloads
    @return: pd.DataFrame
    """

    # Escolhe o arquivo
    download_concluido(path_download)

    pasta_baixados = os.listdir(path_download)
    pasta_baixados = [d for d in pasta_baixados if '.ofx' in d]
    pasta_baixados = [os.path.join(path_download, d) for d in pasta_baixados]
    pasta_novato = max(pasta_baixados, key=os.path.getctime)
    arquivo_novato = os.path.basename(pasta_novato)

    try:
        with codecs.open(pasta_novato) as fileobj:
            ofx = OfxParser.parse(fileobj)
    except ValueError as erro:
        print(
            f"""Erro de importação {erro}.
            \n Arquivo a seguir está VAZIO e portanto n foi importado: \n {arquivo_novato}"""
        )
        return None, None

    print('Lendo:', arquivo_novato)

    # le os dados do OFX
    account = ofx.account
    statement = account.statement

    lista_header = {}
    lista_header['conta'] = account.account_id  # numero da conta
    lista_header['agencia'] = account.branch_id  # agencia
    lista_header['banco'] = account.institution.fid  # nome do Banco
    lista_header[
        'dt_inicio'
    ] = statement.start_date  # The start date of the transactions
    lista_header[
        'dt_fim'
    ] = statement.end_date  # The end date of the transactions
    lista_header['saldo'] = statement.balance

    lista = pd.DataFrame({})
    for transaction in statement.transactions:
        lst = []
        lst.append(transaction.date.date())
        lst.append(transaction.amount)
        lst.append(transaction.memo)
        lst.append(transaction.type)
        # lst.append(transaction.id)
        # lst.append(transaction.checknum)
        lst = pd.Series(data=lst)
        lista = lista.append(lst, ignore_index=True)

    # Ajustes no dados finais
    lista.rename(
        columns={0: 'data', 1: 'valor', 2: 'memo', 3: 'tipo_mov'}, inplace=True
    )
    if len(lista) > 0:
        lista['valor'] = pd.to_numeric(lista['valor'], errors='ignore')
        lista_header['saldo'] = pd.to_numeric(
            lista_header['saldo'], errors='ignore'
        )

    # add variacao e a tira da conta (se houver)
    posicao = lista_header['conta'].find('/')
    lista_header['variacao'] = [
        lista_header['conta'][posicao + 1 :] if posicao >= 0 else ''
    ][0]
    lista_header['conta'] = [
        lista_header['conta'][:posicao] if posicao >= 0 else lista_header['conta']
    ][0]

    # novas variáveis das transacoes
    lista['banco'] = lista_header['banco']
    lista['agencia'] = lista_header['agencia']
    lista['conta'] = lista_header['conta']
    lista['variacao'] = lista_header['variacao']

    return lista, lista_header
