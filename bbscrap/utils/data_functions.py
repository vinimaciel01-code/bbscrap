"""Funções de manipulação e testes em Datas."""

import datetime as dt


def valida(data):
    """Valida se a data é válida (Date ou Datetime).

    @param data: string ou datetime
    @return: boolean
    """
    if isinstance(data, dt.datetime):
        return True

    if isinstance(data, dt.date):
        return True

    return False


def converte_datetime(data):
    """Retorna a data convertida para 'datetime.datetime'.

    @param data: string ou datetime formatada
    @return: dt.datetime
    """
    if isinstance(data, dt.datetime):
        return data

    if isinstance(data, dt.date):
        return dt.datetime.combine(data, dt.datetime.min.time())

    if isinstance(data, str):
        try:
            return dt.datetime.strptime(data, '%d/%m/%Y')
        except Exception as erro:
            raise ValueError(
                f'Data "{data}" invalida. Erro ({erro.__class__})'
            ) from erro
    else:
        raise ValueError('Erro: nao se encaixou nos casos especificados.')


def transforma_data(data):
    """Transforma uma data, para bater a um intervalo.

    A data deve existir e ser maior ou igual a 01/01/2000.
    @param data: datetime
    @return: data
    """
    if data is None:
        data = dt.datetime.today()
        return data

    data = converte_datetime(data)

    if data < dt.datetime(2000, 1, 1):
        data = dt.datetime(2000, 1, 1)

    if data > dt.datetime.today():
        data = dt.datetime.today()

    return data


if __name__ == '__main__':

    dt1 = dt.datetime(2020, 1, 1)
    dt2 = dt.datetime(2022, 1, 1)

    print(valida(dt1))
    print(isinstance(converte_datetime(dt1), dt.datetime))
    print(transforma_data(dt1))
