import logging
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

DADOS = RAIZ / "dados"
BRONZE = DADOS / "bronze"
PRATA = DADOS / "prata"
OURO = DADOS / "ouro"
RELATORIOS = RAIZ / "relatorios"

BRONZE_STEAM = BRONZE / "steam"
BRONZE_FILMES = BRONZE / "filmes"

PADRAO_STEAM = "steam_games_*.csv"
PADRAO_FILMES = "filmes_*.csv"
PALAVRAS_PROIBIDAS_STEAM = ["playtest", "hentai", "demo", "sex"]

ARQUIVO_LOG = RAIZ / "pipeline.log"

DATASET_STEAM = "fronkongames/steam-games-dataset"
DATASET_FILMES = "alanvourch/tmdb-movies-daily-updates"


def configurar_log(nivel=logging.INFO):
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.FileHandler(ARQUIVO_LOG, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def criar_pastas():
    for pasta in (BRONZE_STEAM, BRONZE_FILMES, PRATA, OURO, RELATORIOS):
        pasta.mkdir(parents=True, exist_ok=True)