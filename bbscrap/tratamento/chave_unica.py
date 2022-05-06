"""
Cria a chave única na base de extratos
"""

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
