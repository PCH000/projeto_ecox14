import pandas as pd
from data_profiling import ProfileReport
from pathlib import Path

RELATORIOS = Path("relatorios")

def mais_recente(pasta_bronze):
    arquivos = sorted(pasta_bronze.glob("*.csv"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {pasta_bronze}")
    return arquivos[-1]

def gerar(caminho):
    print(f"Lendo {caminho.name}...")
    df = pd.read_csv(caminho)
    
    if len(df) > 100000:
        print("Dataset muito pesado. Extraindo amostra aleatória de 100.000 linhas...")
        df = df.sample(n=100000, random_state=42)
        
    colunas_para_ignorar = ['About the game', 'Reviews', 'Notes', 'Header image', 'Website', 'Support url', 'Support email','Movies','Screenshots']
    colunas_existentes = [c for c in colunas_para_ignorar if c in df.columns]
    df = df.drop(columns=colunas_existentes)
        
    perfil = ProfileReport(df, title=caminho.name, minimal=True)
    RELATORIOS.mkdir(exist_ok=True)
    saida = RELATORIOS / f"{caminho.stem}.html"
    perfil.to_file(saida)
    print(f"Relatório salvo em: {saida}\n")
    return saida

def main():
    fontes = [Path("dados/bronze/steam"), Path("dados/bronze/filmes")]
    for pasta in fontes:
        try:
            caminho = mais_recente(pasta)
            gerar(caminho)
        except Exception as e:
            print(f"Erro na pasta {pasta}: {e}")

if __name__ == '__main__':
    main()