import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import limpeza

BRONZE = Path("dados/bronze/steam")
PRATA = Path("dados/prata")
PADRAO = "steam_games_*.csv"

def carregar():
    arquivos = sorted(BRONZE.glob(PADRAO))
    if not arquivos:
        raise FileNotFoundError(f"nada em {BRONZE}")
    caminho = arquivos[-1]

    # Corrige o defeito do cabeçalho do CSV da Steam (falta vírgula em DiscountDLC count)
    with caminho.open("r", encoding="utf-8") as f:
        cabecalho = (
            f.readline()
            .strip()
            .replace("DiscountDLC count", "Discount,DLC count")
            .split(",")
        )

    df = pd.read_csv(caminho, names=cabecalho, skiprows=1, index_col=False)
    print("lido:", caminho.name, df.shape)
    return df, caminho

def conferir_chave(df, chave="AppID"):
    repetidas = df[chave].duplicated().sum()
    print("chaves repetidas:", repetidas)
    if repetidas:
        print(df[df[chave].duplicated(keep=False)])
    return df.drop_duplicates(subset=chave)

def tratar_plataforma(df):
    e_windows = df["Windows"] == True
    print("jogos compativeis com Windows:", e_windows.sum())
    print("jogos nao compativeis removidos:", (~e_windows).sum())
    return df[e_windows].copy()

def tratar_metacritic(df):
    coluna = "Metacritic score"
    print(f"valores nulos ou zero em {coluna}:", (df[coluna] == 0).sum() + df[coluna].isna().sum())
    return df

def criar_chave_juncao(df):
    df["chave_nome_jogo"] = limpeza.chave_texto(df["Name"])
    return df

def salvar(df):
    PRATA.mkdir(parents=True, exist_ok=True)
    destino = PRATA / "steam.parquet"
    df.to_parquet(destino, index=False)
    print("salvo em:", destino, df.shape)
    return destino

def registrar(origem, destino, antes, depois, decisoes):
    info = {
        "origem": origem.name,
        "arquivo_prata": destino.name,
        "linhas_antes": antes,
        "linhas_depois": depois,
        "decisoes": decisoes,
        "transformado_em": datetime.now().isoformat(timespec="seconds")
    }
    caminho = PRATA / "proveniencia.jsonl"
    with caminho.open("a", encoding="utf-8") as f:
        f.write(json.dumps(info, ensure_ascii=False) + "\n")

def filtrar_palavras_proibidas(df):
    
    palavras_proibidas = ["playtest", "hentai", "demo","sex"]
    
    padrao = '|'.join(palavras_proibidas)
    
    condicao = df["Name"].str.contains(padrao, case=False, na=False)
    print(f"Jogos removidos por conterem termos indesejados ({palavras_proibidas}):", condicao.sum())
    
    return df[~condicao].copy()

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
        "espacos removidos usando modulo generico",
        "chave AppID conferida",
        "jogos nao-Windows removidos",
        "jogos com termos indesejados (playtest, hentai, etc.) filtrados"
    ])

if __name__ == '__main__':
    main()