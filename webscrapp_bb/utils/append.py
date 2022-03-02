import os
import pandas as pd

def append_nao_duplicatas(base_a, base_b, col=None):
    """"
    Une dois pandas.DataFrames, mantendo toda a tabela A e adicionando os registros não duplicados da tabela B.
    Return: um pandas.DataFrame
    base_a: tabela base. Retorna todas as observações.
    base_b: tabela a dar o append. Retorna apenas as que não existirem na A.
    col: None. Lista com o nome das colunas a considerar na análise de duplicatas.
    """
    if isinstance(base_a, pd.DataFrame) is False or isinstance(base_b, pd.DataFrame) is False:
        raise ValueError('Os inputs precisam ser do tipo "pd.DataFrame"')
    if set(base_b.columns).issubset(set(base_a.columns)) is False:
        print('A:', base_a.columns)
        print('B:', base_b.columns)
        raise ValueError('Dataframe B precisa ter todas colunas do A')
    if base_a is None:
        return base_b
    if base_b is None:
        return base_a

    if col is None:
        base_a['count'] = base_a.groupby(list(base_a.columns)).cumcount()
        base_b['count'] = base_b.groupby(list(base_b.columns)).cumcount()
        base_c = pd.concat([base_a, base_b], ignore_index=False).drop_duplicates()
        base_c = base_c.drop(['count'], axis=1)
        return base_c

    if col is not None:

        if col == 0:
            pd.concat([base_a, base_b], ignore_index=True).drop_duplicates()

        elif isinstance(col, list):
            base_a['count'] = base_a.groupby(col).cumcount()
            base_b['count'] = base_b.groupby(col).cumcount()
            base_c = pd.concat([base_a, base_b], ignore_index=False).drop_duplicates()
            base_c = base_c.drop(['count'], axis=1)
            return base_c

        else:
            raise ValueError('col não é uma lista')


if __name__ == '__main__':
    
    SALVAR_CAMINHO = r'../data'

    l1 = pd.read_excel(os.path.join(SALVAR_CAMINHO, 'Eventos anterior.xlsx'), engine='openpyxl')
    l2 = pd.read_excel(os.path.join(SALVAR_CAMINHO, 'Eventos.xlsx'), engine='openpyxl')

    lf = append_nao_duplicatas(l1, l2, col=None)
    print(lf.shape)
