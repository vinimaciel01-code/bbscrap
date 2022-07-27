import os
from pathlib import Path

import bbscrap.tratamento.lerofx as lerofx

nome_arquivo = 'OUROCARD_PLATINUM_ESTILO_VISA-Jun_22.ofx'


def test_abre_arquivo_existente():
    dados_corpo, dados_header = lerofx.ler_ofx(nome_arquivo)
    assert dados_corpo is not None


def test_abre_arquivo_nao_existente():
    dados = lerofx.ler_ofx('')
    assert dados is None


def test_abre_lerofx_existe_ofx_no_path():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    ofx_path = os.path.join(dir_path, 'auxiliar')

    dados = lerofx.ler_ofx(ofx_path)
    ofx_table = lerofx.ler_ofx(dados)
    assert ofx_table is not None


def test_abre_lerofx_nao_existe_ofx_no_path():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    ofx_path = os.path.join(dir_path, '')

    dados = lerofx.abre_arquivo_ofx(ofx_path)
    ofx_table = lerofx.ler_ofx(dados)
    assert ofx_table == (None, None)
