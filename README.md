# Webscrapp-BancodoBrasil
Acessa a a conta bancária do Banco do Brasil do usuários e baixa os extratos da conta corrente, poupança e conta corrente.

## Motivação
O site do banco do brasil tem uma API para acesso de algumas informações, mas não permite baixar todo os extratos bancários. A solução foi acessar o banco via Web scrapping. Optei por usar o Selenium, porque o site bancário tem um nível de segurança alto e este pacote de navegação simula o acesso real. 

## Navegação e limitações
A navegação ocorre por meio de tags da estrutura HTML da página, utilizando marcadores para identificar onde clicar. Isto gera facilidades de acesso, porque tudo que o usuário faz, o programa consegue fazer. Porém existem duas limitações: 
1. Se a estrutura do site mudar, o programa deve ser adaptado
2. O navegador especial deve estar aberto e não pode ser mexido durante o tempo de execução.

## Preparação
1. Instalar configuração de browser do Selenium, para permitir que seu browser seja aja automatizado. https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/
4. Instalar pacotes necessários, mostrados em pyproject.toml. 
`poetry install` 

## Como usar
O programa abre o navegador, acessa a conta bancária e baixa os extratos. A senha pedida é a senha de 8 digitos de acesso à conta (possui apenas permissão de visaulização, portanto, é impossível fazer modificações na conta). 

A função então retorna duas base de dados, a primeira com os dados dos extratos e o segundo dados de cabeçalho (totais, datas, etc.).

Em app.main, rode função acesso_bb:
`dados, dados_header = acesso_bb(path_download='c:downloads', agencia='123456', conta='1212123', senha='batata123'):`
