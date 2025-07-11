# Projeto Estágio Curricular ARMIS

Implementação de sistema RAG com Graph Database.

## Modelo de Domínio
![Modelo de Domimio](./docs/dm/domain_model.svg)

**TODO:** rever/melhorar o modelo com mais pormenores

## Extração de Entidades e Relações
### Abordagem 1
Nesta abordagem é pedido ao LLM que consiga extrair as entidades e relações num único passo, seguindo as mesmas instruções.

Cada ficheiro é dividido em chunks de tamanho X e processados separadamente.

No processamento de um chunk, todas as entidades e relações já extraídas anteriormente são fornecidas ao LLM para contexto.

O resultado final é um JSON com uma lista de entidades e uma lista de relações. O schema desta resposta é definido num JSON.

![Abordagem 1](docs/sd/entity_relationship_extraction/abordagem1.svg)

### Abordagem 2
Nesta abordagem é pedido ao LLM que extraia as entidades e as relações separadamente.

Inicialmente é feita a extração de entidades. É também pedido ao LLM para as categorizar nas seguintes categorias:

- Seres Vivos 
- Objetos 
- Lugares e Espaços 
- Eventos e Processos 
- Organizações e Instituições 
- Conceitos e Ideias 
- Propriedades e Qualidades 
- Tempo e Quantidades

Após a estração de entidades estar concluída, é pedido ao LLM para extrair as relações existentes entre essas mesmas entidades. 

É ainda feita uma terceira passagem do LLM para garantir que não existem entidades e relações repetidas ou entidades com nomes diferentes que se referem à mesma coisa.

Cada ficheiro é dividido em chunks de tamanho X e processados separadamente.

No processamento de um chunk - todas as entidades e relações já extraídas anteriormente são fornecidas ao LLM para contexto, respeitando as fases acima explicadas.

O resultado final é um JSON com uma lista de entidades e uma lista de relações. O schema desta resposta é definido através da biblioteca pydantic.

![Abordagem 2](./docs/sd/entity_relationship_extraction/abordagem2.svg)

## Pesquisa na Base de Dados

### Abordagem 1
Nesta abordagem, o LLM sabe qual é o conteúdo da base de dados "de uma forma declarativa", isto é, ele não tem acesso diretamente à base de dados, apenas tem acesso ao schema.

O schema pode ser caracterizado como uma "blueprint" da base de dados, indicando apenas quais são as relações e o tipo da entidade.

O objetivo do LLM é analisar o schema e formar uma query em chyper válido que responda à pergunta em linguagem natural.

No final, os resultados da query são interpretados e é formatada uma resposta em linguagem natural.

![Abordagem 1](./docs/sd/graph_query/abordagem1.png)

### Abordagem 2
Esta abordagem usa a biblioteca Langchain e a sua implementação.

Na teoria e prática é igual, mas está mais otimizada a nível de utilização de tokens.

Uma melhoria seria permitir ao LLM fazer várias chamadas à base de dados, com diferentes queries e não apenas uma.

## ENDPOINTS

### GET /chat/make-question
Faz uma pergunta e devolve a resposta.
#### Exemplo:
    /chat/make-question?question=Onde é que a Sofia mora?

### GET /chat/import-file
Importa um ficheiro (já presente no sistema de ficheiros) para as diferentes bases de dados.
#### Exemplo:
    /chat/import-file?filename=meuarquivo.txt

### GET /azure/extract-entities-and-relations
Extrai todas as entidades e relações usando um LLM.
#### Exemplo:
    /azure/extract-entities-and-relations?filename=meuarquivo.txt

### GET /neo4j/import-file
Importa nós e relações de um ficheiro para a base de dados Neo4j.
#### Exemplo:
    /neo4j/import-file?filename=meuarquivo.txt

### GET /neo4j/import-nodes
Importa todos os nós para o Neo4j.
#### Exemplo:
    /neo4j/import-nodes?filename=meuarquivo.txt

### GET /neo4j/import-relationships
Importa todas as relações para o Neo4j.
#### Exemplo:
    /neo4j/import-relationships?filename=meuarquivo.txt

### GET /neo4j/get-all-nodes
Retorna todos os nós do Neo4j.

### GET /neo4j/clean-db
Limpa a base de dados toda.

### POST /files/import-file
Guarda um ficheiro no sistema de ficheiros.

### GET /favicon.ico
Fornece o ícone do site.

## Exemplos input e output correspondente
### 1.
[Ficheiro input1](./docs/exemplos/exemplo1/input.txt)

[Ficheiro output1](./docs/exemplos/exemplo1/output.txt)

### 2.
[Ficheiro input2](./docs/exemplos/exemplo2/input.txt)

[Ficheiro output1](./docs/exemplos/exemplo2/output.txt)

