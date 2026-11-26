import json
import logging
from datetime import datetime

import pandas as pd

import config
import juncao

log = logging.getLogger(__name__)

STEAM = config.PRATA / "steam.parquet"
FILMES = config.PRATA / "filmes.parquet"
DESTINO = config.PRATA / "steam_filmes_enriquecido.parquet"

CHAVE_STEAM = "chave_nome_jogo"
CHAVE_FILMES = "chave_nome_filme"


def carregar():
    steam = pd.read_parquet(STEAM)
    filmes = pd.read_parquet(FILMES)
    log.info("steam : %s", steam.shape)
    log.info("filmes: %s", filmes.shape)
    return steam, filmes


def preparar_filmes(filmes):
    colunas = [
        "id",
        "title",
        "imdb_rating",
        "revenue",
        "ano_lancamento",
        "faixa_receita",
        CHAVE_FILMES,
    ]
    colunas_existentes = [c for c in colunas if c in filmes.columns]
    df = filmes[colunas_existentes].copy()

    antes = len(df)
    df = df.sort_values(by=["revenue", "imdb_rating"], ascending=False)
    df = df.drop_duplicates(subset=CHAVE_FILMES, keep="first")
    log.info("filmes deduplicados por titulo: %d -> %d", antes, len(df))
    return df


def calcular_diferenca_nota(df):
    tem_ambos = (df["Metacritic score"] > 0) & df["imdb_rating"].notna()
    df["diferenca_nota"] = pd.NA
    df.loc[tem_ambos, "diferenca_nota"] = (
        df.loc[tem_ambos, "Metacritic score"]
        - (df.loc[tem_ambos, "imdb_rating"] * 10)
    )
    log.info("jogos com nota no Metacritic e par no IMDb: %d", int(tem_ambos.sum()))
    return df


def registrar(resultado, sem_par, antes, casados):
    info = {
        "origem_esquerda": STEAM.name,
        "origem_direita": FILMES.name,
        "arquivo_prata": DESTINO.name,
        "chave": f"{CHAVE_STEAM} = {CHAVE_FILMES}",
        "tipo_de_juncao": "left",
        "linhas_esquerda": antes,
        "linhas_resultado": len(resultado),
        "linhas_com_par": int(casados),
        "linhas_sem_par": len(sem_par),
        "atributos_derivados": ["diferenca_nota"],
        "transformado_em": datetime.now().isoformat(timespec="seconds"),
    }
    caminho = config.PRATA / "proveniencia.jsonl"
    with caminho.open("a", encoding="utf-8") as f:
        f.write(json.dumps(info, ensure_ascii=False) + "\n")
    log.info("proveniencia: %s", caminho)
    return info


def main():
    steam, filmes = carregar()
    filmes = preparar_filmes(filmes)

    juncao.conferir_chaves(steam, filmes, CHAVE_STEAM, CHAVE_FILMES)

    antes = len(steam)
    resultado = juncao.juntar(
        steam, filmes, CHAVE_STEAM, CHAVE_FILMES, relacao="many_to_one"
    )

    sem_par = juncao.validar(steam, resultado, CHAVE_FILMES)
    casados = len(resultado) - len(sem_par)
    log.info("com par: %d", casados)

    resultado = calcular_diferenca_nota(resultado)

    resultado.to_parquet(DESTINO, index=False)
    log.info("salvo em: %s %s", DESTINO, resultado.shape)

    registrar(resultado, sem_par, antes, casados)


if __name__ == "__main__":
    config.configurar_log()
    main()