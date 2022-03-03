"""
Funções de união de duas bases de dados pandas.dataFrame
"""

import pandas as pd


def append_nao_duplicatas(base_a, base_b, col=None):
    """
    Une dois pandas.DataFrames, mantendo toda a tabela A e
    adicionando os registros não duplicados da tabela B.
    base_a: tabela base.
    base_b: tabela a dar o append.
    col: Lista. nome das colunas a considerar.
    Return: pandas.DataFrame
    """

    # inputs pd.dataFrames
    if (
        isinstance(base_a, pd.DataFrame) is False
        or isinstance(base_b, pd.DataFrame) is False
    ):
        raise ValueError('Os inputs precisam ser do tipo "pd.DataFrame"')

    # B subset de A
    if set(base_b.columns).issubset(set(base_a.columns)) is False:
        print('A:', base_a.columns)
        print('B:', base_b.columns)
        raise ValueError('Dataframe B precisa ter todas colunas do A')

    # A ou B não vazias
    if base_a is None and base_b is not None:
        return base_b
    if base_a is not None and base_b is None:
        return base_a

    # Une as duas bases, usando todas as colunas de A como chave
    if col is None:
        base_a['count'] = base_a.groupby(list(base_a.columns)).cumcount()
        base_b['count'] = base_b.groupby(list(base_b.columns)).cumcount()
        base_nova = pd.concat(
            [base_a, base_b], ignore_index=False
        ).drop_duplicates()
        base_nova = base_nova.drop(['count'], axis=1)
        return base_nova

    # Une as duas bases, usando a coluna especificada como chave
    if col == 0:
        base_nova = pd.concat(
            [base_a, base_b], ignore_index=True
        ).drop_duplicates()

    elif isinstance(col, list):
        base_a['count'] = base_a.groupby(col).cumcount()
        base_b['count'] = base_b.groupby(col).cumcount()
        base_nova = pd.concat(
            [base_a, base_b], ignore_index=False
        ).drop_duplicates()
        base_nova = base_nova.drop(['count'], axis=1)

    else:
        raise ValueError('col não é uma lista')

    return base_nova
