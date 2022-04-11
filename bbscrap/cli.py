from argparse import ArgumentParser
# from getpass import getpass

import bbscrap.main as main

parser = ArgumentParser(prog='Scrapper do Banco do Brasil',
                        description='Baixa os extratos bancários do Banco do Brasil.',
                        fromfile_prefix_chars='@')

parser.add_argument('--path', '-p', type=str, required=True,
                    help='Path da pasta de downloads')
parser.add_argument('--agencia', '-a', type=str,
                    help='Número da agência bancária')
parser.add_argument('--conta', '-c', type=str,
                    help='Número da conta bancária')
parser.add_argument('--senha', '-s', type=str,
                    help='Senha da conta')
parser.add_argument('--data_inicial', '-dt', type=str,
                    help='Data inicial para obter os extratos bancários.')
parser.add_argument('--outros_titulares', '-o', type=str,
                    help='Lista dos titulares alternativos da conta. Nome parcial permitido.')

args = parser.parse_args()

if not args.path:
    parser.exit(0, "Indique o path da pasta de downloads")

# senha = args.senha or getpass("Digite sua senha do Banco do Brasil: ")
# if not senha:
    # parser.exit(0, "Você não digitou a senha!\n")

dados = main.acesso_bb(args.path, args.agencia, args.conta, args.senha,
                       args.data_inicial, args.outros_titulares)
