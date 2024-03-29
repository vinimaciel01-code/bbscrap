
"""Acesso à conta do Banco do Brasil.

Acessa a conta pessoal do Banco do Brasil do usuário.
O login pode ser feito totalmente pelo app ou manualmente pelo usuário.
Download dos extratos de conta corrente, poupança e cartões de crédito do titular principal.
Para os outros titulares, baixa apenas o cartão de crédito (pois os extratos são os mesmos).
"""

import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

import os
import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
from tkinter import *
from tkinter import filedialog

from bbscrap.navegacao import drivers, nav_pagina, login, dependente
from bbscrap.navegacao import nav_corrente, nav_poupanca, nav_cartao

from bbscrap.tratamento.main_tratamento import tratamento_dados
from bbscrap.tratamento.lerofx import ler_ofx

from bbscrap.utils.data_functions import converte_datetime
from bbscrap.utils.sistema import blockPrint, enablePrint


def acesso_bb(agencia=None, conta=None, senha=None, data_inicial=None, outros_titulares=True, 
              tratamento=True, export_file=True, import_file=False, block_print=False):

    """Acessa o Banco do Brasil e baixa as informações requisitadas.

    @param agencia: número da agência (com DV, sem traço)
    @param conta: numero da conta (com DV, sem traço)
    @param senha: senha da cota
    @param data_inicial: data de início da procura de dados
    @param outros_titulares: lista com o nome Bancário dos outros titulares da conta.
    Nome parcial é permitido. Apenas extratos de cartões de crédito são baixados.
    """
    
    # bloqueia prints na tela
    if block_print is True:
        blockPrint()

    # import o ofx, em vez de baixar
    if import_file is True:
        
        root = Tk()
        root.update()
        file_list = filedialog.askopenfilenames()
        root.destroy()

        for fl in file_list:
            corpo_base, header_base = ler_ofx(fl)

    elif import_file is False: 

        # datas
        data_final = dt.datetime.today()
        if data_inicial is None:
            data_inicial = data_final - relativedelta(months=1)
        else:
            data_inicial = converte_datetime(data_inicial)

        if data_inicial > data_final:
            data_inicial = data_final - relativedelta(months=1)

        # data final corrigida (tb queremos as faturas, com data_ref do mes seguinte.)
        data_final = data_final + relativedelta(months=1)

        lista_meses = pd.date_range(data_inicial, data_final, freq='MS').tolist()
        lista_meses = [x.strftime('%b/%y') for x in lista_meses]
        lista_meses = [x.lower() for x in lista_meses]

        # Inicializa pagina
        driver = drivers.chrome_driver_init()
        nav_pagina.navega_pagina(driver)
        login.login_banco(driver, agencia, conta, senha)

        # Títular Principal
        
        corpo_base = pd.DataFrame({})
        header_base = pd.DataFrame({})

        nome_arquivos_list = nav_corrente.central(driver, lista_meses)
        if nome_arquivos_list:
            for key in nome_arquivos_list:
                for elem in nome_arquivos_list[key]:
                    corpo, header = ler_ofx(elem, key)
                    corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
                    header_base = pd.concat([header_base, header], ignore_index=True)

        nome_arquivos_list = nav_poupanca.central(driver, lista_meses)
        if nome_arquivos_list:
            for key in nome_arquivos_list:
                for elem in nome_arquivos_list[key]:
                    corpo, header = ler_ofx(elem, key)
                    corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
                    header_base = pd.concat([header_base, header], ignore_index=True)
        
        nome_arquivos_list = nav_cartao.central(driver, lista_meses)
        if nome_arquivos_list:
            for key in nome_arquivos_list:
                for elem in nome_arquivos_list[key]:
                    corpo, header = ler_ofx(elem, key)
                    corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
                    header_base = pd.concat([header_base, header], ignore_index=True)
    
        # Outros Titulares
        for i in range(2, 5):
            login_dependente = dependente.login_dependente(driver, str(i)+"º")
            if login_dependente is True:
                nome_arquivos_list = nav_cartao.central(driver, lista_meses)
                if nome_arquivos_list:
                    for key in nome_arquivos_list:
                        for elem in nome_arquivos_list[key]:
                            corpo, header = ler_ofx(elem, key)
                            corpo_base = pd.concat([corpo_base, corpo], ignore_index=True)
                            header_base = pd.concat([header_base, header], ignore_index=True)
            else:
                break

        # Encerra driver
        driver.close()
        if block_print is True:
            enablePrint()

    #Tratamento de dados
    if tratamento is True:
        corpo_base, header_base = tratamento_dados(corpo_base, header_base)

    # export
    if export_file is True:
        
        # caminho
        root = Tk()
        # root.withdraw()
        root.update()
        file_path = filedialog.askdirectory()
        root.destroy()
        # nome
        file_date = dt.datetime.now().strftime("%Y_%m_%d_%Hh%Mm%Ss")
        # juntos
        file_name = os.path.join(file_path,f"acessobb_{file_date}.xlsx")

        with pd.ExcelWriter(file_name, mode='w') as writer:
            corpo_base.to_excel(writer, index=False, float_format='%.2f', sheet_name='corpo')
            header_base.to_excel(writer, index=False, float_format='%.2f', sheet_name='header')
        
        print("Arquivo exportado com sucesso.")

        return
    
    # Fim
    return corpo_base, header_base