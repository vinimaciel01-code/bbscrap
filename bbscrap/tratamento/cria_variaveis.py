"""
Modificações na base de dados de extratos
- reformata mes de referenência
- cria a data corrigida (data real da transação
- cria o mês da data corrigida
- cria algumas variáveis sempre fixas
"""

import datetime as dt
from dateutil.relativedelta import relativedelta


def cria_variaveis(dados):
    """
    cria novas variáveis
    @dados: base pd.DataFrame que quero transformar.
    """
    data_base = dados.copy()

    # PARCELA ATUAL E TOTAL
    # procura no memo 2 o número de parcelas

    df1 = data_base[['data', 'memo2', 'mes_ref']].loc[
        data_base['tipo_conta'].isin(['Cartão'])
        & data_base['memo2'].str.contains('^PARC [0-9]{2}/[0-9]{2}$')
    ]
    df1['parc_atual'] = df1['memo2'].str.replace('PARC ', '')
    df1['parc_atual'] = df1['parc_atual'].str.split('/', 1)
    df1['parc_total'] = [int(x[1]) for x in df1['parc_atual']]
    df1['parc_atual'] = [int(x[0]) for x in df1['parc_atual']]

    # DataN
    # data da transação corrigida pelo número de parcelas
    # em trans. parcelada, a data é o momento que a transação foi realizada originalmente

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

    # MES DA DATA DA TRANSAÇÃO
    data_base['mesN'] = [x + relativedelta(day=1) for x in data_base['dataN']]

    # OUTRAS VARIÁVEIS (fixas)
    data_base['moeda'] = 'BRL'
    data_base['tipo_entrada'] = 'OFX'
    data_base['valorN'] = data_base['valor']
    data_base['data_import'] = dt.date.today()

    return data_base
