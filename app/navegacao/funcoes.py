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


def base_export(dados):
    """
    cria novas variáveis e transforma existentes
    @dados: base pd.DataFrame que quero transformar.
    """
    data_base = dados.copy()

    # reformatando
    data_base['mes_ref'] = [
        dt.datetime.strptime(x, '%b/%y').date() for x in data_base['mes_ref']
    ]

    # data corrigida
    df1 = data_base[['data', 'memo2', 'mes_ref']].loc[
        data_base['tipo_conta'].isin(['Cartão'])
        & data_base['memo2'].str.contains('^PARC [0-9]{2}/[0-9]{2}$')
    ]
    df1['parc_atual'] = df1['memo2'].str.replace('PARC ', '')
    df1['parc_atual'] = df1['parc_atual'].str.split('/', 1)
    df1['parc_total'] = [int(x[1]) for x in df1['parc_atual']]
    df1['parc_atual'] = [int(x[0]) for x in df1['parc_atual']]

    temp = []
    for index, value in enumerate(df1['data']):
        desloca = value + relativedelta(months=+df1['parc_atual'].iloc[index] - 1)
        if desloca > df1['mes_ref'].iloc[index]:
            temp.append(value)
        else:
            temp.append(desloca)

    df1['dataN'] = temp
    data_base['dataN'] = data_base['data']
    data_base['dataN'].update(df1['dataN'])

    # mes da data
    data_base['mesN'] = [x + relativedelta(day=1) for x in data_base['dataN']]

    # variáveis fixas
    data_base['moeda'] = 'BRL'
    data_base['tipo_entrada'] = 'OFX'
    data_base['valorN'] = data_base['valor']
    data_base['id_import'] = ''  # considerado no excel?
    data_base['data_import'] = dt.date.today()

    return data_base


def chave_unica(dados):

    """
    Chave única composta de estáveis 46 dígitos:

        - 33 digitos
        pt1 (6) mes do extrato/fatura -> AAAAMM
        pt2 (8) data Transação -> DDMMAAAA
        pt3 (1) origem 1:Cc/2:Pp/3:Ct
        pt4 (8) Agência com dv
        pt5 (10) Conta com dv
            cartao: pt4 e pt5 -> ultimos 4 digitos do cartao.
        - 16 digitos
        pt6 (15) Valor (até 1 trilhao de reais)
        pt7 (1) Déb/Créd -> 1/0

        - 4 digitos
        pt8 (2) Ind de repetição (começa no zero)
        pt9 (2) Ind entrada manual

    :param dados: base de dados pandas.Dataframe
    :return: pandas Series
    """

    data_base = dados.copy()

    # calculos iniciais
    lst1 = data_base['mes_ref'].apply(lambda x: x.strftime('%Y%m'))  # AAAAMM
    lst2 = data_base['data'].apply(lambda x: x.strftime('%Y%m%d'))  # data
    lst3 = [
        '1' if x == 'Conta Corrente' else '2' if x == 'Poupança' else '3'
        for x in data_base['tipo_conta']
    ]  # tipo
    lst4 = [
        x.replace('-', '').zfill(8) for x in data_base['agencia']
    ]  # agencia
    lst5 = [
        x.replace('-', '').zfill(10)[-10:] for x in data_base['conta']
    ]  # conta
    lst6 = [
        str(int(abs(round(x * 100, 0)))).zfill(15) for x in data_base['valor']
    ]  # valor
    lst7 = ['1' if x < 0 else '0' for x in data_base['valor']]  # sinal

    # chave inicial
    lst_chave = lst1 + lst2 + lst3 + lst4 + lst5 + lst6 + lst7

    # calculo de repetição
    rep = lst_chave.value_counts()
    temp = []
    for posicao in lst_chave:
        temp.append(str(rep.loc[posicao] - 1).zfill(2))
        rep[posicao] = rep[posicao] - 1
    lst8 = temp

    # chave final
    lst9 = '00'  # import/manual
    lst_chave = lst1 + lst2 + lst3 + lst4 + lst5 + lst6 + lst7 + lst8 + lst9

    return lst_chave


def memo_divisao(dados):
    """
    divide o memo em 2 partes
    """
    memo = dados['memo'].copy()

    # Substituições
    substituida = {
        'PIX - Enviado': 'PIX Enviado',
        'PIX - Recebido': 'PIX Recebido',
        'PIX - Rejeitado': 'PIX Rejeitado',
    }
    memo.replace(substituida, regex=True, inplace=True)

    # retiradas
    retirada = {
        r' +': ' ',
        r'^..\*': '',
        r'^PAG\*': '',
        r'^PG \*': '',
        r'BRASILIA': '',
        r'\sBR$': '',
    }
    memo.replace(retirada, regex=True, inplace=True)

    # Separando em duas partes
    memo_split = [x.split(sep='-', maxsplit=1) for x in memo]
    memo1 = [x[0].strip() for x in memo_split]
    memo2 = [x[1].strip() if len(x) > 1 else '' for x in memo_split]

    # envia a parcela para o memo2
    for index, value in enumerate(memo1):
        procura = re.search('PARC [0-9]{2}/[0-9]{2}', value)
        if procura is not None:
            memo1[index] = value.split(procura.group())[0]
            memo2[index] = procura.group()

    # retira datas e valores antes da primeira letra
    for index, value in enumerate(memo2):
        for posicao, letra in enumerate(value):
            if value[letra].isalpha():
                memo2[posicao] = value[letra:]
                break

    return memo1, memo2
