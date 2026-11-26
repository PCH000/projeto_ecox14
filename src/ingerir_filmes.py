import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

import kagglehub

import config

log = logging.getLogger(__name__)


def baixar_filmes():
    config.BRONZE_FILMES.mkdir(parents=True, exist_ok=True)

    log.info("baixando dataset de filmes via kagglehub: %s", config.DATASET_FILMES)
    pasta_cache = Path(kagglehub.dataset_download(config.DATASET_FILMES))

    csvs = sorted(pasta_cache.glob("*.csv"))
    if not csvs:
        raise FileNotFoundError(f"nenhum CSV encontrado em {pasta_cache}")

    origem = csvs[0]
    hoje = datetime.now().strftime("%Y%m%d")
    destino = config.BRONZE_FILMES / f"filmes_{hoje}.csv"

    shutil.copy2(origem, destino)
    log.info("arquivo copiado para: %s", destino)
    return destino


def registrar(arquivo):
    info = {
        "fonte": "kagglehub",
        "dataset": config.DATASET_FILMES,
        "arquivo": arquivo.name,
        "tamanho_bytes": arquivo.stat().st_size,
        "ingerido_em": datetime.now().isoformat(timespec="seconds"),
    }
    caminho = config.BRONZE_FILMES / "proveniencia.jsonl"
    with caminho.open("a", encoding="utf-8") as f:
        f.write(json.dumps(info, ensure_ascii=False) + "\n")
    log.info("proveniencia registrada em: %s", caminho)


def main():
    arquivo = baixar_filmes()
    registrar(arquivo)


if __name__ == "__main__":
    config.configurar_log()
    main()