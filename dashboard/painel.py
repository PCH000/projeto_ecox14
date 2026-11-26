"""
Como executar, a partir da raiz do projeto:
    streamlit run dashboard/painel.py
"""

import streamlit as st

import consultas

st.set_page_config(
    page_title="A Maldição das Adaptações",
    page_icon="🎮",
    layout="wide",
)


def br(valor, casas=1):
    if valor is None or valor != valor:
        return "sem dado"
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "@").replace(".", ",").replace("@", ".")


st.title("A Maldição das Adaptações: Steam vs. IMDb")
st.caption("Camada Ouro do projeto, construída pelo pipeline e modelada em dbt.")

if not consultas.banco_existe():
    st.error("Banco não encontrado. Rode antes: python src/pipeline.py")
    st.stop()

with st.sidebar:
    st.header("Filtros")
    opcoes_faixa = ["Todas"] + consultas.faixas_receita()["faixa_receita"].tolist()
    faixa = st.selectbox("Faixa de receita do filme", opcoes_faixa)
    apenas_metacritic = st.checkbox(
        "Apenas jogos com nota no Metacritic",
        value=True,
    )
    st.divider()
    st.caption(
        "Os filtros viram parâmetros na consulta SQL em consultas.py."
    )

dados = consultas.adaptacoes_filtradas(faixa, apenas_metacritic)

if dados.empty:
    st.warning("Nenhum registro encontrado para esse filtro.")
    st.stop()

resumo = consultas.resumo_geral(faixa, apenas_metacritic).iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("Pares jogo-filme", br(resumo["total_pares"], 0))
c2.metric("Nota média no IMDb", br(resumo["media_imdb"], 2) + " / 10")
c3.metric(
    "Diferença média (Jogo - Filme)",
    br(resumo["media_diferenca"], 1) + " pts",
    help="Metacritic (0-100) menos IMDb*10. Negativo indica filme melhor avaliado.",
)

st.divider()

esq, dir_ = st.columns([3, 2])

with esq:
    st.subheader("Top 10 por receita de bilheteria (USD)")
    st.bar_chart(
        dados.head(10),
        x="titulo_filme",
        y="receita_filme",
        color="#1B3A5F",
        height=320,
    )

with dir_:
    st.subheader("Nota média no IMDb por ano de lançamento")
    serie = consultas.evolucao_por_ano(faixa, apenas_metacritic)
    st.line_chart(
        serie,
        x="ano_lancamento",
        y="media_imdb",
        color="#D96F2C",
        height=320,
    )

st.divider()

st.subheader("Detalhe dos pares encontrados")
st.dataframe(
    dados,
    hide_index=True,
    use_container_width=True,
    column_config={
        "nome_jogo": st.column_config.TextColumn("Jogo (Steam)"),
        "titulo_filme": st.column_config.TextColumn("Filme (IMDb)"),
        "ano_lancamento": st.column_config.NumberColumn("Ano", format="%d"),
        "faixa_receita": st.column_config.TextColumn("Faixa de receita"),
        "nota_metacritic": st.column_config.NumberColumn("Metacritic", format="%d"),
        "nota_imdb": st.column_config.NumberColumn("IMDb", format="%.1f"),
        "diferenca_nota": st.column_config.NumberColumn("Dif. Nota", format="%.1f"),
        "receita_filme": st.column_config.NumberColumn("Receita (USD)", format="$%.0f"),
    },
)

st.caption(
    f"Fontes: Steam e IMDb/TMDB (via Kaggle). {len(dados)} registros nesta seleção. "
    "Dado tratado e modelado pelo pipeline da disciplina."
)