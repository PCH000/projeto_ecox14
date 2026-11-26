import json
import logging
from datetime import datetime

import pandas as pd

import config
import limpeza

log = logging.getLogger(__name__)


def carregar():
    arquivos = sorted(config.BRONZE_STEAM.glob(config.PADRAO_STEAM))
    if not arquivos:
        raise FileNotFoundError(f"nada em {config.BRONZE_STEAM}")
    caminho = arquivos[-1]

    # Corrige o defeito do cabecalho do CSV da Steam (falta virgula em DiscountDLC count)
    with caminho.open("r", encoding="utf-8") as f:
        cabecalho = (
            f.readline()
            .strip()
            .replace("DiscountDLC count", "Discount,DLC count")
            .split(",")
        )

    df = pd.read_csv(caminho, names=cabecalho, skiprows=1, index_col=False)
    log.info("lido: %s %s", caminho.name, df.shape)
    return df, caminho


def conferir_chave(df, chave="AppID"):
    repetidas = int(df[chave].duplicated().sum())
    if repetidas:
        log.warning("chaves repetidas em %s: %d", chave, repetidas)
    else:
        log.info("chaves repetidas em %s: 0", chave)
    return df.drop_duplicates(subset=chave)


def tratar_plataforma(df):
    e_windows = df["Windows"] == True
    log.info("jogos compativeis com Windows: %d", int(e_windows.sum()))
    log.info("jogos nao compativeis removidos: %d", int((~e_windows).sum()))
    return df[e_windows].copy()


def tratar_metacritic(df):
    coluna = "Metacritic score"
    sem_nota = int((df[coluna] == 0).sum() + df[coluna].isna().sum())
    log.info("valores nulos ou zero em %s: %d", coluna, sem_nota)
    return df


def criar_chave_juncao(df):
    df["chave_nome_jogo"] = limpeza.chave_texto(df["Name"])
    return df


def filtrar_palavras_proibidas(df):
    padrao = "|".join(config.PALAVRAS_PROIBIDAS_STEAM)
    condicao = df["Name"].str.contains(padrao, case=False, na=False)
    log.info(
        "jogos removidos por termos indesejados (%s): %d",
        config.PALAVRAS_PROIBIDAS_STEAM,
        int(condicao.sum()),
    )
    return df[~condicao].copy()


def salvar(df):
    config.PRATA.mkdir(parents=True, exist_ok=True)
    destino = config.PRATA / "steam.parquet"
    df.to_parquet(destino, index=False)
    log.info("salvo em: %s %s", destino, df.shape)
    return destino


def registrar(origem, destino, antes, depois, decisoes):
    info = {
        "origem": origem.name,
        "arquivo_prata": destino.name,
        "linhas_antes": antes,
        "linhas_depois": depois,
        "decisoes": decisoes,
        "transformado_em": datetime.now().isoformat(timespec="seconds"),
    }
    caminho = config.PRATA / "proveniencia.jsonl"
    with caminho.open("a", encoding="utf-8") as f:
        f.write(json.dumps(info, ensure_ascii=False) + "\n")

def main():
    df, origem = carregar()
    antes = len(df)

    df = limpeza.tirar_espacos(df)
    df = conferir_chave(df, "AppID")
    df = tratar_plataforma(df)
    df = tratar_metacritic(df)
    df = criar_chave_juncao(df)
    df = filtrar_palavras_proibidas(df)

    destino = salvar(df)
    registrar(origem, destino, antes, len(df), [
        "cabecalho DiscountDLC count corrigido na leitura",
        "espacos removidos usando modulo generico",
        "chave AppID conferida",
        "jogos nao-Windows removidos por irrelevancia",
        "criada coluna 'chave_nome_jogo' para juncao com IMDb",
        "jogos com termos indesejados filtrados",
    ])


if __name__ == "__main__":
    config.configurar_log()
    main()