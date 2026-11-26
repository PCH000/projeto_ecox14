select
    id             as filme_id,
    title          as titulo_filme,
    ano_lancamento,
    faixa_receita
from {{ source('prata', 'filmes') }}