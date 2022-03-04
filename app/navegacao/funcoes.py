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

    # le os dados de cabeçalho
    account = ofx.account # QUANDO VAZIO???
    statement = account.statement

    lista_header = pd.DataFrame({})
    lista_header['conta'] = [account.account_id]  # número da conta
    lista_header['agencia'] = [account.branch_id]  # número da agência
    lista_header['banco'] = [account.institution.fid]  # nome do Banco
    lista_header['dt_inicio'] = [statement.start_date]  # data inicial das transações
    lista_header['dt_fim'] = [statement.end_date]  # data final das transações
    lista_header['saldo'] = [statement.balance]

    # le os dados das transações
    cols=['data', 'valor', 'memo', 'tipo_mov']
    lista = pd.DataFrame(columns=cols)
    for transaction in statement.transactions:
        lst = []
        lst.append(transaction.date.date())
        lst.append(transaction.amount)
        lst.append(transaction.memo)
        lst.append(transaction.type)
        lst = pd.DataFrame([lst], columns=cols)
        lista = pd.concat([lista, lst], ignore_index=True)

    # Ajustes no dados finais
    if len(lista) > 0:
        lista['valor'] = pd.to_numeric(lista['valor'], errors='ignore')
        lista_header['saldo'] = pd.to_numeric(lista_header['saldo'], errors='ignore')

    # add variacao e a tira da conta (se houver)
    lista_header['variacao'] = [x[x.find('/') + 1 :] 
        if x.find('/') > 0 else '' for x in lista_header['conta']]
    lista_header['conta'] = [x[:x.find('/')] 
        if x.find('/') > 0 else x for x in lista_header['conta']]
    
    # novas variáveis das transacoes
    lista['banco'] = lista_header['banco'][0]
    lista['agencia'] = lista_header['agencia'][0]
    lista['conta'] = lista_header['conta'][0]
    lista['variacao'] = lista_header['variacao'][0]

    return lista, lista_header


if __name__ == '__main__':

    path_download = r'C:\Users\vinim\Downloads'
    ler_ofx(path_download)
