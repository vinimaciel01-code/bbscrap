"""Função auxiliar: ler o ofx salvado na pasta de downloads."""

import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

import os
from pathlib import Path
import pandas as pd
from ofxparse import OfxParser


def ler_ofx(nome_arquivo, mes_ref=None):
    """Lê o arquivo ofx recebido."""

    try:
        dados = open(nome_arquivo)
    except:
        print('Arquivo', nome_arquivo)
        raise ValueError('Arquivo não encontrado.')

    if not dados:
        return None, None

    # le o arquivo recebido
    try:
        ofx = OfxParser.parse(dados)
    except:
        print('Arquivo vazio.')
        return None, None

    # HEADER

    # le os dados de cabeçalho
    account = ofx.account
    statement = account.statement
    lista_header = pd.DataFrame({})
    lista_header['banco'] = [account.institution.fid]
    lista_header['agencia'] = [account.branch_id]
    lista_header['conta'] = [account.account_id]
    lista_header['tipo'] = [account.type]
    lista_header['dt_inicio'] = [statement.start_date]
    lista_header['dt_fim'] = [statement.end_date]
    lista_header['saldo'] = pd.to_numeric([statement.balance], errors='ignore')

    # add extras
    lista_header['variacao'] = [x[x.find('/') + 1:] if x.find('/') > 0 else '' for x in lista_header['conta']]
    lista_header['conta'] = [x[: x.find('/')] if x.find('/') > 0 else x for x in lista_header['conta']]
    
    if lista_header['tipo'][0] == 1:
        if lista_header['variacao'][0]:
            lista_header['tipo_conta'] = 'Poupança'    
        else:
            lista_header['tipo_conta'] = 'Conta Corrente'
    else:
        lista_header['tipo_conta'] ='Cartão'
    
    lista_header['mes_ref'] = mes_ref

    # TRANSACAO

    # lê os dados das transações
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

    # add extras
    lista['banco'] = lista_header['banco'][0]
    lista['agencia'] = lista_header['agencia'][0]
    lista['conta'] = lista_header['conta'][0]
    lista['variacao'] = lista_header['variacao'][0]
    lista['tipo_conta'] = lista_header['tipo_conta'][0]
    lista['mes_ref'] = mes_ref
    
    return lista, lista_header
