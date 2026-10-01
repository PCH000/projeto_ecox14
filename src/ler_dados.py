import pandas as pd

CAMINHO = "dados/bronze/games.csv"

def carregar():
    return pd.read_csv(CAMINHO)

def conferir_estrutura(df):
    print("Formato (linhas, colunas):", df.shape)

    print("\nColunas encontradas no arquivo:")
    for coluna in df.columns:
        print(f'"{coluna}"')
        
    esperadas = ["Name", "Metacritic score", "Release date"]
    
    faltando = [c for c in esperadas if c not in df.columns]
    
    if faltando:
        print("\nAviso! Colunas não encontradas:", faltando)
    else:
        print("\nSucesso!")

if __name__ == "__main__":
    conferir_estrutura(carregar())