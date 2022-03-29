"""Função auxiliar: ler o ofx salvado na pasta de downloads."""

import os
import pandas as pd
from ofxparse import OfxParser

from bbscrap.utils.arquivo import download_concluido


def abre_le_arquivo_ofx(path_download):
    """Junta os dois procedimentos abaixo."""
    dados = abre_arquivo_ofx(path_download)

    ofx_header, ofx_dados = ler_ofx(dados)

    return ofx_header, ofx_dados


def abre_arquivo_ofx(path_download):
    """Seleciona o arquivo que iremos que iremos ler."""
    
    download_concluido(path_download)

    # lista todos arquivos com extensão OFX
    pasta_baixados = os.listdir(path_download)
    pasta_baixados = [d for d in pasta_baixados if '.ofx' in d]
    if pasta_baixados == []:
        return None
    
    # seleciona o OFX mais novo
    pasta_baixados = [os.path.join(path_download, d) for d in pasta_baixados]
    arquivo_novato = max(pasta_baixados, key=os.path.getctime)
    
    dados = open(arquivo_novato)
    
    return dados


def ler_ofx(dados):
    """Lê o arquivo ofx recebido."""

    if not dados:
        return None, None

    # le o arquivo recebido
    try:
        ofx = OfxParser.parse(dados)
    except:
        print('Arquivo vazio.')
        return None

    # le os dados de cabeçalho
    account = ofx.account
    statement = account.statement
    lista_header = pd.DataFrame({})
    lista_header['banco'] = [account.institution.fid]
    lista_header['agencia'] = [account.branch_id]
    lista_header['conta'] = [account.account_id]
    lista_header['dt_inicio'] = [statement.start_date]
    lista_header['dt_fim'] = [statement.end_date]
    lista_header['saldo'] = [statement.balance]

    # le os dados das transações
    cols = ['data', 'valor', 'memo', 'tipo_mov']
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
        lista_header['saldo'] = pd.to_numeric(
            lista_header['saldo'], errors='ignore'
        )

    # add variacao e a tira da conta (se houver)
    lista_header['variacao'] = [
        x[x.find('/') + 1:] if x.find('/') > 0 else ''
        for x in lista_header['conta']
    ]
    lista_header['conta'] = [
        x[: x.find('/')] if x.find('/') > 0 else x
        for x in lista_header['conta']
    ]

    # novas variáveis das transacoes
    lista['banco'] = lista_header['banco'][0]
    lista['agencia'] = lista_header['agencia'][0]
    lista['conta'] = lista_header['conta'][0]
    lista['variacao'] = lista_header['variacao'][0]

    return lista, lista_header


if __name__ == '__main__':

    path_download = r'C:\Users\vinim\Downloads'
    ler_ofx(path_download)
