
# Análise do Sucesso de Mudanças de Mídia de Franquias de Entretenimento

## Fontes de Dados

| Fonte | Formato | Acesso | Extraído em | Link |
|---|---|---|---|---|
| Steam Games Dataset | CSV | API Kaggle | 01/10/2026 | [kaggle.com/datasets/fronkongames/steam-games-dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset) |
| TMDB+IMDb Movies | CSV | API Kaggle | 01/10/2026 | [kaggle.com/datasets/alanvourch/tmdb-movies-daily-updates](https://www.kaggle.com/datasets/alanvourch/tmdb-movies-daily-updates) |

## Estrutura do Projeto

O pipeline de dados segue a arquitetura em três camadas:
* **Camada Bronze:** Ingestão automatizada do dado no seu formato original via API do Kaggle, organizada por data de extração, mantendo o histórico intacto e com registo contínuo de proveniência (`proveniencia.jsonl`).
* **Camada Prata:** Limpeza, padronização de tipologias, tratamento de valores nulos e cruzamento das duas bases utilizando *string matching*.
* **Camada Ouro:** Modelação final contendo os agregados estatísticos e o pareamento numérico de sucesso crítico (`Metacritic score` vs `vote_average`), pronta para visualização num *dashboard* analítico.

## Defeitos Conhecidos das Fontes

### Steam Games Dataset (Kaggle)
* A coluna `Metacritic score` (variável de negócio principal) apresenta 96.6% de valores a zero.
* A coluna `Price` possui 67.5% de valores a zero.
* As colunas `Categories`, `Publishers` e `Genres` apresentam cerca de 7% de valores em falta (*missing*).
* A variável de plataforma `Windows` está altamente desequilibrada (*highly imbalanced*), dominando 99.6% dos registos.

### TMDB+IMDb Movies Dataset (Kaggle)
* A coluna `imdb_rating` possui 62.0% de valores em falta (*missing*).
* A coluna `release_date` apresenta 10.8% de valores em falta (*missing*).
* As colunas financeiras estão comprometidas na origem: `revenue` tem 97.7% de zeros e `budget` tem 93.3% de zeros.
* A métrica `vote_count` apresenta 66.7% de valores a zero.

## Decisões de Tratamento (Camada Prata)
**Steam Games:**
* Espaços em branco removidos dos nomes das colunas e campos de texto.
* Jogos não compatíveis com Windows removidos por irrelevância estatística (apenas 44 linhas mantidas).

**TMDB+IMDb Movies:**
* Espaços em branco limpos de todos os textos.
* 771723 linhas removidas por ausência da métrica crítica `imdb_rating`.

## Atributos Derivados (Camada Prata)
### ano_lancamento
Extração do ano a partir da data de lançamento (`release_date`) na base de filmes. Serve para permitir a análise cronológica de sucesso e a organização por décadas.

### faixa_receita
Quartil gerado a partir do orçamento financeiro (`revenue`) na base de filmes, categorizado em "Baixa", "Média", "Alta" e "Blockbuster". Serve para agrupar os filmes comparáveis e permitir análises estatísticas em bloco, ignorando os valores ausentes de receitas.

### chave_nome_jogo / chave_nome_filme
Nomes dos jogos e filmes padronizados, com os acentos retirados e com todas as letras convertidas em minúsculas (ex: "Spider-Man" -> "spider-man"). Este campo oculto não é para ser exibido graficamente, servindo exclusivamente como âncora de cruzamento de dados (*string matching*) para unir as duas tabelas na futura Camada Ouro.