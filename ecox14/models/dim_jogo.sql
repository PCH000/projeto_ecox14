select
    AppID          as jogo_id,
    Name           as nome_jogo,
    "Release date" as data_lancamento,
    Price          as preco
from {{ source('prata', 'steam') }}