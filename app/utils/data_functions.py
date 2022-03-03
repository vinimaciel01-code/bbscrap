"""
Funções de manipulação e testes em Datas
"""

import datetime as dt


def valida(data):
    """
    Valida se a data é válida (Date ou Datetime)
    @param data: string ou datetime
    return: boolean
    """

    if isinstance(data, dt.datetime):
        return True

    if isinstance(data, dt.date):
        return True

    return False


def converte_datetime(data):
    """
    Retorna a data convertida para 'datetime.datetime'
    @param data: string ou datetime formatada
    return: data datetime.datetime ou msg de 'Erro'
    """

    if isinstance(data, dt.datetime):
        # print('instancia de datetime.datetime: OK')
        return data

    if isinstance(data, dt.date):
        # print('instancia de datetime.date: converter para datetime')
        return dt.datetime.combine(data, dt.datetime.min.time())

    if isinstance(data, str):
        try:
            # print('instancia de string: convertendo para datetime.datetime')
            return dt.datetime.strptime(data, '%d/%m/%Y')
        except Exception as erro:
            raise ValueError(
                f'Data "{data}" invalida. Erro ({erro.__class__})'
            ) from erro
    else:
        raise ValueError('Erro: nao se encaixou nos casos especificados.')


if __name__ == '__main__':

    data_teste = dt.datetime.today().date()
    isinstance(data_teste, dt.date)
    print(valida(data_teste))
    print(converte_datetime(data_teste))
