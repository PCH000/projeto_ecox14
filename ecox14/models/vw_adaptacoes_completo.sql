{{ config(materialized='view') }}

select
    f.*,
    j.nome_jogo,
    j.data_lancamento,
    j.preco,
    m.titulo_filme,
    m.ano_lancamento,
    m.faixa_receita
from {{ ref('fato_adaptacao') }} f
join {{ ref('dim_jogo') }} j using (jogo_id)
join {{ ref('dim_filme') }} m using (filme_id)