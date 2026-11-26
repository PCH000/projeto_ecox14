select jogo_id, count(*)
from {{ ref('fato_adaptacao') }}
group by jogo_id
having count(*) > 1