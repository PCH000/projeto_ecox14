import json
from datetime import datetime
from pathlib import Path

import pandas as pd

import juncao

PRATA = Path("dados/prata")

STEAM = PRATA / "steam.parquet"
FILMES = PRATA / "filmes.parquet"
DESTINO = PRATA / "steam_filmes_enriquecido.parquet"

CHAVE_STEAM = "chave_nome_jogo"
CHAVE_FILMES = "chave_nome_filme"


def carregar():
    steam = pd.read_parquet(STEAM)
    filmes = pd.read_parquet(FILMES)
    print("steam :", steam.shape)
    print("filmes:", filmes.shape)
    print()
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
    df = df[df[CHAVE_FILMES].str.strip() != ""]
    print(f"filmes deduplicados por titulo: {antes} -> {len(df)}")
    return df


def calcular_diferenca_nota(df):
    tem_ambos = (df["Metacritic score"] > 0) & df["imdb_rating"].notna()
    df["diferenca_nota"] = pd.NA
    df.loc[tem_ambos, "diferenca_nota"] = (
        df.loc[tem_ambos, "Metacritic score"]
        - (df.loc[tem_ambos, "imdb_rating"] * 10)
    )
    print("jogos com nota no Metacritic e par no IMDb:", int(tem_ambos.sum()))
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
    caminho = PRATA / "proveniencia.jsonl"
    with caminho.open("a", encoding="utf-8") as f:
        f.write(json.dumps(info, ensure_ascii=False) + "\n")
    print("proveniencia:", caminho)
    return info


def main():
    steam, filmes = carregar()
    filmes = preparar_filmes(filmes)
    print()

    # 1. Conferir as chaves ANTES de juntar.
    juncao.conferir_chaves(steam, filmes, CHAVE_STEAM, CHAVE_FILMES)
    print()

    # 2. Juntar mantendo todos os jogos da Steam (how='left').
    antes = len(steam)
    resultado = juncao.juntar(
        steam, filmes, CHAVE_STEAM, CHAVE_FILMES, relacao="many_to_one"
    )

    # 3. Validar a contagem antes e depois.
    sem_par = juncao.validar(steam, resultado, CHAVE_FILMES)
    casados = len(resultado) - len(sem_par)
    print("com par            :", casados)
    print()

    # 4. Inspecionar exemplos de jogos que casaram e que nao casaram.
    if casados:
        print("exemplos que casaram:")
        print(
            resultado[resultado[CHAVE_FILMES].notna()][
                ["Name", "Metacritic score", "title", "imdb_rating"]
            ].head(5)
        )
        print()

    # 5. Atributo derivado que so existe apos a juncao.
    resultado = calcular_diferenca_nota(resultado)

    resultado.to_parquet(DESTINO, index=False)
    print("salvo em:", DESTINO, resultado.shape)

    registrar(resultado, sem_par, antes, casados)


if __name__ == "__main__":
    main()