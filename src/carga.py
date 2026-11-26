import logging
import duckdb
from config import OURO, PRATA

log = logging.getLogger(__name__)

BANCO = OURO / "projeto.duckdb"

TABELAS_PRATA = {
    "steam": "steam.parquet",
    "filmes": "filmes.parquet",
    "steam_filmes_enriquecido": "steam_filmes_enriquecido.parquet",
}


def um_valor(con, sql):
    return con.execute(sql).fetchone()[0]


def conectar():
    BANCO.parent.mkdir(parents=True, exist_ok=True)
    log.info("banco: %s", BANCO)
    return duckdb.connect(str(BANCO))


def criar_esquemas(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS prata")
    con.execute("CREATE SCHEMA IF NOT EXISTS ouro")
    log.info("esquemas prata e ouro prontos")


def carregar_prata(con):
    for tabela, arquivo in TABELAS_PRATA.items():
        caminho = PRATA / arquivo
        if not caminho.exists():
            log.warning("prata.%s: arquivo nao encontrado, pulando", tabela)
            continue
        con.execute(f"""
            CREATE OR REPLACE TABLE prata.{tabela} AS
            SELECT * FROM read_parquet('{caminho.as_posix()}')
        """)
        linhas = um_valor(con, f"SELECT COUNT(*) FROM prata.{tabela}")
        log.info("prata.%s: %s linhas", tabela, linhas)


def construir_ouro(con):
    con.execute("""
        CREATE OR REPLACE TABLE ouro.dim_jogo AS
        SELECT
            AppID          AS jogo_id,
            Name           AS nome_jogo,
            "Release date" AS data_lancamento,
            Price          AS preco
        FROM prata.steam
    """)
    log.info(
        "ouro.dim_jogo: %s linhas",
        um_valor(con, "SELECT COUNT(*) FROM ouro.dim_jogo"),
    )

    con.execute("""
        CREATE OR REPLACE TABLE ouro.dim_filme AS
        SELECT
            id             AS filme_id,
            title          AS titulo_filme,
            ano_lancamento,
            faixa_receita
        FROM prata.filmes
    """)
    log.info(
        "ouro.dim_filme: %s linhas",
        um_valor(con, "SELECT COUNT(*) FROM ouro.dim_filme"),
    )

    con.execute("""
        CREATE OR REPLACE TABLE ouro.fato_adaptacao AS
        SELECT
            AppID              AS jogo_id,
            id                 AS filme_id,
            "Metacritic score" AS nota_metacritic,
            imdb_rating        AS nota_imdb,
            revenue            AS receita_filme,
            diferenca_nota
        FROM prata.steam_filmes_enriquecido
        WHERE id IS NOT NULL
    """)
    log.info(
        "ouro.fato_adaptacao: %s linhas",
        um_valor(con, "SELECT COUNT(*) FROM ouro.fato_adaptacao"),
    )

    descartados = um_valor(
        con,
        """
        SELECT COUNT(*) FROM prata.steam_filmes_enriquecido
        WHERE id IS NULL
        """,
    )
    if descartados:
        log.warning(
            "%s jogos ficaram fora da fato: sem filme correspondente",
            descartados,
        )

    con.execute("""
        CREATE OR REPLACE VIEW ouro.vw_adaptacoes_completo AS
        SELECT
            f.*,
            j.nome_jogo,
            j.data_lancamento,
            j.preco,
            m.titulo_filme,
            m.ano_lancamento,
            m.faixa_receita
        FROM ouro.fato_adaptacao f
        JOIN ouro.dim_jogo j USING (jogo_id)
        JOIN ouro.dim_filme m USING (filme_id)
    """)
    log.info("ouro.vw_adaptacoes_completo: criada")


def conferir(con):
    grao_repetido = um_valor(
        con,
        """
        SELECT COUNT(*) FROM (
            SELECT jogo_id
            FROM ouro.fato_adaptacao
            GROUP BY jogo_id
            HAVING COUNT(*) > 1
        )
        """,
    )

    orfaos_jogo = um_valor(
        con,
        """
        SELECT COUNT(*)
        FROM ouro.fato_adaptacao f
        LEFT JOIN ouro.dim_jogo j USING (jogo_id)
        WHERE j.jogo_id IS NULL
        """,
    )

    orfaos_filme = um_valor(
        con,
        """
        SELECT COUNT(*)
        FROM ouro.fato_adaptacao f
        LEFT JOIN ouro.dim_filme m USING (filme_id)
        WHERE m.filme_id IS NULL
        """,
    )

    log.info("jogos repetidos na fato : %s (esperado 0)", grao_repetido)
    log.info("fatos sem dim_jogo      : %s (esperado 0)", orfaos_jogo)
    log.info("fatos sem dim_filme     : %s (esperado 0)", orfaos_filme)

    if grao_repetido or orfaos_jogo or orfaos_filme:
        raise ValueError(
            f"modelo inconsistente: {grao_repetido} repetidos, "
            f"{orfaos_jogo} sem jogo, {orfaos_filme} sem filme"
        )


def main():
    con = conectar()
    try:
        criar_esquemas(con)
        carregar_prata(con)
        # construir_ouro(con)
        conferir(con)
    finally:
        con.close()
    log.info("carga concluida")


if __name__ == "__main__":
    import config

    config.configurar_log()
    main()