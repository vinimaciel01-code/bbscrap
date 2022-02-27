# Webscrapp-BancodoBrasil
Acessa a a conta bancária do Banco do Brasil do usuários e baixa os extratos da conta corrente, poupança e conta corrente.

## Ideia geral
O site do banco do brasil tem uma API para acesso de algumas informações, mas não permite baixar todo os extratos bancários. A solução foi acessar o banco via Web scrapping. Optei por usar o Selenium, porque o site bancário tem um nível de segurança alto e este pacote de navegação simula o acesso real. 

## Navegação e limitações
A navegação ocorre por meio de tags da estrutura HTML da página, utilizando marcadores para identificar onde clicar. Isto gera facilidades de acesso, porque tudo que o usuário faz, o programa consegue fazer. Porém existem duas limitações: 
1. Se a estrutura do site mudar, o programa deve ser adaptado
2. O navegador especial deve estar aberto e não pode ser mexido durante o tempo de execução.

## Preparação

## 
