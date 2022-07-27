"""
Modificações na base de dados de extratos
- reformata mes de referenência
- cria a data corrigida (data real da transação
- cria o mês da data corrigida
- cria algumas variáveis sempre fixas
"""

import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta


def altera_variaveis(dados):
    """
    cria novas variáveis e transforma existentes
    @dados: base pd.DataFrame que quero transformar.
    """
    data_base = dados.copy()

    # Ajuste no valor
    if len(data_base) > 0:
        data_base['valor'] = pd.to_numeric(data_base['valor'], errors='ignore')
        data_base.loc[data_base['tipo_mov'] == 'credit', 'valor'] = abs(data_base.loc[data_base['tipo_mov'] == 'credit', 'valor'])

    # MES_REF
    
        # calcula o último mes com fatura completa
    temp = data_base.loc[data_base['tipo_conta'].isin(['Cartão']) & ~data_base['mes_ref'].str.contains('Próxima Fatura')]
    temp = temp[['conta', 'mes_ref']]
    temp = temp.drop_duplicates(['conta','mes_ref'])
    temp['mes_ref'] = [dt.datetime.strptime(x, '%b/%y') for x in temp['mes_ref']]
    temp = temp.groupby('conta').max()

        # próxima fatura será igual ao mes seguinte
    temp['mes_ref'] = [x + relativedelta(months=1) for x in temp['mes_ref']]
    temp['mes_ref'] = [dt.datetime.strftime(x, '%b/%y') for x in temp['mes_ref']]
    
        # substitui
    for index, row in temp.iterrows():
        data_base.loc[(data_base.conta == index) & (data_base.mes_ref == 'Próxima Fatura'), 'mes_ref'] = row['mes_ref']

        # converte para data
    data_base['mes_ref'] = [dt.datetime.strptime(x, '%b/%y').date() for x in data_base['mes_ref']]

    return data_base
