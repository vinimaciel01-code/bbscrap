import pandas as pd

from bbscrap.tratamento.memo_divisao import memo_divisao
from bbscrap.tratamento.altera_variaveis import altera_variaveis
from bbscrap.tratamento.cria_variaveis import cria_variaveis
from bbscrap.tratamento.chave_unica import chave_unica


def tratamento_dados(corpo_base, header_base):

    # Copia as bases
    dados = corpo_base.copy()
    dados_h = header_base.copy()
    
    # divide o memo em 2 partes
    memo1, memo2 = memo_divisao(dados)
    dados['memo1'] = memo1
    dados['memo2'] = memo2

    # tira o traço '-' da AGENCIA e CONTA
    dados['agencia'] = [x.replace('-', '') for x in dados['agencia']]
    dados['conta'] = [x.replace('-', '') for x in dados['conta']]
    dados_h['agencia'] = [x.replace('-', '') for x in dados_h['agencia']]
    dados_h['conta'] = [x.replace('-', '') for x in dados_h['conta']]

    # Altera variáveis (mes_ref) - depois de memo_divisao (memo2)
    dados = altera_variaveis(dados)

    # Cria variáveis - depois de altera variáveis
    dados = cria_variaveis(dados)

    # Cria a chave de indentificação única - depois de altera variáveis (mes_ref)
    chave = chave_unica(dados)
    dados['chave'] = chave

    # reordenando
    dados = dados[['data', 'banco', 'agencia', 'conta', 'variacao', 'tipo_conta', 'memo', 'tipo_mov', 'moeda', 'valor',
                'chave', 'tipo_entrada', 'mes_ref', 'dataN', 'mesN', 'memo1', 'memo2', 'valorN', 'data_import']]
    dados_h = dados_h[['banco', 'agencia', 'conta', 'variacao', 'tipo_conta', 'mes_ref', 'dt_inicio', 'dt_fim', 'saldo']]

    return dados, dados_h