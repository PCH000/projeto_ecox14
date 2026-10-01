import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import limpeza

BRONZE = Path("dados/bronze/filmes")
PRATA = Path("dados/prata")
PADRAO = "filmes_*.csv"

def carregar():
    arquivos = sorted(BRONZE.glob(PADRAO))
    if not arquivos:
        raise FileNotFoundError(f"nada em {BRONZE}")
    caminho = arquivos[-1]
    df = pd.read_csv(caminho)
    print("lido:", caminho.name, df.shape)
    return df, caminho

def conferir_chave(df, chave="id"):
    repetidas = df[chave].duplicated().sum()
    print("chaves repetidas:", repetidas)
    if repetidas:
        print(df[df[chave].duplicated(keep=False)])
    return df.drop_duplicates(subset=chave)

def tratar_nulos(df):
    valido = df["imdb_rating"].notna()
    print("linhas sem imdb_rating removidas:", (~valido).sum())
    return df[valido].copy()

def marcar_extremos(df, coluna):
    zeros = (df[coluna] == 0).sum()
    print(coluna, "valores zero mantidos:", zeros)
    return df

def criar_chave_juncao(df):
    df["chave_nome_filme"] = limpeza.chave_texto(df["title"])
    return df

def tratar_datas_e_atributos(df):
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    print("datas invalidas/nulas após conversao:", df["release_date"].isna().sum())
    
    df["ano_lancamento"] = df["release_date"].dt.year
    
    df_com_receita = df[df["revenue"] > 0].copy()
    faixas = pd.qcut(df_com_receita["revenue"], q=4, labels=["Baixa", "Media", "Alta", "Blockbuster"])
    df["faixa_receita"] = faixas
    
    return df

def salvar(df):
    PRATA.mkdir(parents=True, exist_ok=True)
    destino = PRATA / "filmes.parquet"
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

def main():
    df, origem = carregar()
    antes = len(df)
    
    df = limpeza.tirar_espacos(df)
    df = conferir_chave(df, "id")
    df = tratar_nulos(df)
    df = marcar_extremos(df, "revenue")
    
    df = criar_chave_juncao(df)
    df = tratar_datas_e_atributos(df)
    
    destino = salvar(df)
    registrar(origem, destino, antes, len(df), [
        "espacos removidos via modulo limpeza",
        "chave id conferida e nulos do imdb_rating removidos",
        "coluna 'chave_nome_filme' criada para string matching",
        "coluna release_date convertida para datetime",
        "atributo derivado 'ano_lancamento' criado",
        "atributo derivado 'faixa_receita' criado por quartis"
    ])

if __name__ == '__main__':
    main()