# IGBD Extractor
Extrai dados de jogos (gêneros, plataformas, modos de jogo, data de lançamento, categoria e nome) da API do site IGBD.
## how to use
+ REST API

É necessário que você mesmo **gere um accessToken** para poder fazer requests com a API. Para isso, siga as instruções contidas [nesse tutorial](https://api-docs.igdb.com/#getting-started). Após conseguir suas credenciais, crie um arquivo _apiAccess.csv_ no diretório raíz desse programa com as colunas ***client_id*** e **client_secret***, com as linhas tendo ambas as informações. 

+ Tratamento de dados

Existe um script tratamento de dados opcional. O motivo de não estar integrado no fluxo do extrator é pelo fato do tratamento ser bem subjetivo e enviesado com minha opinião do que eu considero dados necessários para jogos. O tratamento reduz o número total de gêneros de cada jogo para 3 (pois, em minha opinião, um jogo deve ser capaz de ser descrito em no máximo 3 gêneros ou então ficará abrangente demais para ser único) e o total de plataformas para 5 (pois creio que, em uma geração de consoles, haverão apenas 5 plataformas relevantes, no máximo). 

Rode o tratamento se concordar com os pontos postulados no parágrafo acima.

## to-do
1. tabelas/dataframes relacionais 1-*
2. tratamento das tabelas relacionais
3. (opcional)visualizações com pandas
4. (opcional)ui para auxiliar na navegação do programa e na inserção das credenciais para a API
5. limpeza do código...?

