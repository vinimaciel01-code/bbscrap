"""
Divide o memo em duas partes
A primeira parte contém a informaçào geral da transação
A segunda contém alguma especifidade, se houver.
"""

import re

def memo_divisao(dados):
    """
    divide o memo em 2 partes
    """
    memo = dados['memo'].copy()

    # Substituições
    substituida = {
        'PIX - Enviado': 'PIX Enviado',
        'Pix - Enviado': 'Pix Enviado',
        'PIX - Recebido': 'PIX Recebido',
        'Pix - Recebido': 'Pix Recebido',
        'PIX - Rejeitado': 'PIX Rejeitado',
        'Pix - Rejeitado': 'Pix Rejeitado',
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
    for index, frase in enumerate(memo2):
        for index_letra in range(0, len(frase)):
            if frase[index_letra].isalpha():
                memo2[index] = frase[index_letra:]
                break

    return memo1, memo2
