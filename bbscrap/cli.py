import pandas as pd
import click

from bbscrap.main import acesso_bb


@click.command()
@click.argument('path', type=click.Path(exists=True), required=True)
@click.option('-a', '--agencia', type=click.STRING, required=False)
@click.option('-c', '--conta', type=click.STRING)
@click.option('-s', '--senha', type=click.STRING)
@click.option('-d', '--data_inicial', type=click.DateTime(formats=['%d/%m/%Y']))
@click.option('-o', '--segundo_titular', type=click.STRING)
@click.option('-e', '--export', type=click.Choice(['csv', 'xlsx']), default='xlsx')
def cli(path, agencia, conta, senha, data_inicial, segundo_titular, export):

    dados, dados_h = acesso_bb(path, agencia, conta, senha, data_inicial, segundo_titular, export)

    if export == 'xlsx':

        with pd.ExcelWriter('saida.xlsx', mode='w') as writer:
            dados.to_excel(writer, index=False, float_format='%.2f', sheet_name='corpo')
            dados_h.to_excel(writer, index=False, float_format='%.2f', sheet_name='header')

    if export == 'csv':

        dados.to_csv('bb_dados_corpo.csv')
        dados_h.to_csv('bb_dados_header.csv')
