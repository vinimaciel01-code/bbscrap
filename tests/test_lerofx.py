import os

import bbscrap.navegacao.lerofx as lerofx

dir_path = os.path.dirname(os.path.realpath(__file__))
ofx_path = os.path.join(dir_path, 'auxiliar')
path_parent = os.path.abspath(os.path.join(ofx_path, ".."))


def test_abre_arquivo_existente():
    dados = lerofx.abre_arquivo_ofx(ofx_path)
    assert dados is not None


def test_abre_arquivo_nao_existente():
    dados = lerofx.abre_arquivo_ofx(path_parent)
    assert dados is None


def test_abre_lerofx():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    ofx_path = os.path.join(dir_path, 'auxiliar')
    dados = lerofx.abre_arquivo_ofx(ofx_path)

    ofx_table = lerofx.ler_ofx(dados)
    assert ofx_table is not None
