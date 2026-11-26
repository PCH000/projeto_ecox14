select
    AppID              as jogo_id,
    id                 as filme_id,
    "Metacritic score" as nota_metacritic,
    imdb_rating        as nota_imdb,
    revenue            as receita_filme,
    diferenca_nota
from {{ source('prata', 'steam_filmes_enriquecido') }}
where id is not null