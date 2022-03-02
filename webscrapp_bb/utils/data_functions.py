import datetime as dt

def data_valida(data):
    """
    Valida se a data é válida
    :param data: string ou datetime
    :return: boolean
    """

    if isinstance(data, dt.datetime):
        return True

    if isinstance(data, dt.date):
        return True

    if isinstance(data, str):
        try:
            dt.datetime.strptime(data, '%d/%m/%Y')
            return True
        except:
            return False
            # raise ValueError(f'Data "{data}" invalida. Erro ({erro.__class__})')


def data_converte(data):
    """
    Retorna a data convertida para 'datetime.datetime' ou msg de 'Erro'
    :param data: string ou datetime formatada
    :return: data datetime.datetime
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
            raise ValueError(f'Data "{data}" invalida. Erro ({erro.__class__})')
    else:
        raise ValueError('Erro: nao se encaixou nos casos especificados.')


if __name__ == '__main__':

    dataT = dt.datetime.today().date()
    isinstance(dataT, dt.date)
    print(data_valida(dataT))
    print(data_converte(dataT))
