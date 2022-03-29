# Webscrapp-BancodoBrasil
Acessa a conta pessoal do Banco do Brasil do usuário. 
O login pode ser feito informando login e senha para o App ou manualmente pelo usuário.
Download dos extratos de conta corrente, poupança e cartões de crédito do titular principal.
Para os outros titulares, baixa apenas o cartão de crédito (pois os extratos são os mesmos).

## Motivação
O site do banco do brasil tem uma API para acesso de algumas informações, mas não permite baixar os extratos bancários completos. A solução foi acessar o banco via Web scrapping. Optei por usar o Selenium, porque o site bancário tem um nível de segurança alto e este pacote de navegação simula o acesso real.

## Navegação e limitações
A navegação ocorre pela estrutura HTML da página, utilizando marcadores para identificar para onde navegar.
Existem duas limitações: 
1. Se a estrutura do site mudar, o programa deve ser adaptado;
2. O navegador especial deve estar aberto e não pode ser manipulado durante o tempo de execução.

## Preparação
1. Instalar configuração de browser do Selenium, para permitir que abra um browser automatizado. https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/
2. Instalar este pacote e suas dependências (no arquivo pyproject.toml)
`poetry install bbscrap` 

## Como usar
O programa abre o navegador, acessa a conta bancária e baixa os extratos. A senha pode ser informada ou o login pode ser manual (o programa continua a funcionar após o login ser realiado). A senha pedida é de 8 digitos, que permite apenas acesso de visualização à conta. 

A função então retorna duas base de dados
- corpo: dados dos extratos baixados. 
- header: dados de cabeçalho de todos extratos (datas de inicio e fim das transações, saldo, entre outros).

`
corpo, header = acesso_bb(path_download, dt1=None, agencia=None, conta=None, senha=None, outros_titulares=None, block_print=True)
`
