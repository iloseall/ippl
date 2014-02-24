# Irregular Packing Problem Library

A biblioteca ippl, foi criada para auxiliar no desenvolvimento de aplicações
voltadas para o problema de empacotamento de formas irregulares.

## Execução

Primeiro vá para o diretório raiz do projeto (onde está este README).
Defina o PYTHONPATH para a pasta atual com o comando abaixo.

$ export PYTHONPATH=.

Depois disso, basta executar o script blf_genetic/application.py <profile>

Os profiles estão na pasta data/blf.

Para alterar as configurações, basta chamar o comando help via linha de
comando.

$ python blf_genetic/application.py -h

## Limpeza

Na raiz do projeto há dois scripts de limpeza, uma para limpar a construção do
cython e outro para limpar os logs e as imagens dos testes. O dos testes tem o
nome clean_tests.sh e o do cython tem o nome cython_clean.sh. Caso a raiz esteja
muito bagunçada, simplesmente chame o script respectivo ao que você está
fazendo (testando ou construindo o módulo usando cython).
