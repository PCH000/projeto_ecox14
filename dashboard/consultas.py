from pathlib import Path

import duckdb
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
BANCO = RAIZ / "dados" / "ouro" / "projeto.duckdb"


def banco_existe():
    return BANCO.exists()


@st.cache_data
def _consultar(sql, parametros=None):
    con = duckdb.connect(str(BANCO), read_only=True)
    try:
        return con.execute(sql, parametros or []).df()
    finally:
        con.close()


def faixas_receita():
    return _consultar("""
        select distinct faixa_receita
        from ouro.vw_adaptacoes_completo
        where faixa_receita is not null
        order by 1
    """)


def adaptacoes_filtradas(faixa, apenas_com_metacritic):
    condicoes = ["1 = 1"]
    parametros = []

    if faixa != "Todas":
        condicoes.append("faixa_receita = ?")
        parametros.append(faixa)

    if apenas_com_metacritic:
        condicoes.append("nota_metacritic > 0")

    where = " and ".join(condicoes)
    return _consultar(
        f"""
        select
            nome_jogo,
            titulo_filme,
            ano_lancamento,
            faixa_receita,
            nota_metacritic,
            nota_imdb,
            diferenca_nota,
            receita_filme
        from ouro.vw_adaptacoes_completo
        where {where}
        order by receita_filme desc nulls last
        """,
        parametros,
    )


def resumo_geral(faixa, apenas_com_metacritic):
    condicoes = ["1 = 1"]
    parametros = []

    if faixa != "Todas":
        condicoes.append("faixa_receita = ?")
        parametros.append(faixa)

    if apenas_com_metacritic:
        condicoes.append("nota_metacritic > 0")

    where = " and ".join(condicoes)
    return _consultar(
        f"""
        select
            count(*)            as total_pares,
            avg(nota_imdb)      as media_imdb,
            avg(diferenca_nota) as media_diferenca
        from ouro.vw_adaptacoes_completo
        where {where}
        """,
        parametros,
    )


def evolucao_por_ano(faixa, apenas_com_metacritic):
    condicoes = ["ano_lancamento is not null"]
    parametros = []

    if faixa != "Todas":
        condicoes.append("faixa_receita = ?")
        parametros.append(faixa)

    if apenas_com_metacritic:
        condicoes.append("nota_metacritic > 0")

    where = " and ".join(condicoes)
    return _consultar(
        f"""
        select
            ano_lancamento,
            avg(nota_imdb) as media_imdb
        from ouro.vw_adaptacoes_completo
        where {where}
        group by ano_lancamento
        order by ano_lancamento
        """,
        parametros,
    )