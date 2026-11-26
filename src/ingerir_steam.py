import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

import kagglehub

import config

log = logging.getLogger(__name__)


def baixar_steam():
    config.BRONZE_STEAM.mkdir(parents=True, exist_ok=True)

    log.info("baixando dataset da Steam via kagglehub: %s", config.DATASET_STEAM)
    pasta_cache = Path(kagglehub.dataset_download(config.DATASET_STEAM))

    csvs = sorted(pasta_cache.glob("*.csv"))
    if not csvs:
        raise FileNotFoundError(f"nenhum CSV encontrado em {pasta_cache}")

    origem = csvs[0]
    hoje = datetime.now().strftime("%Y%m%d")
    destino = config.BRONZE_STEAM / f"steam_games_{hoje}.csv"

    shutil.copy2(origem, destino)
    log.info("arquivo copiado para: %s", destino)
    return destino


def registrar(arquivo):
    info = {
        "fonte": "kagglehub",
        "dataset": config.DATASET_STEAM,
        "arquivo": arquivo.name,
        "tamanho_bytes": arquivo.stat().st_size,
        "ingerido_em": datetime.now().isoformat(timespec="seconds"),
    }
    caminho = config.BRONZE_STEAM / "proveniencia.jsonl"
    with caminho.open("a", encoding="utf-8") as f:
        f.write(json.dumps(info, ensure_ascii=False) + "\n")
    log.info("proveniencia registrada em: %s", caminho)


def main():
    arquivo = baixar_steam()
    registrar(arquivo)


if __name__ == "__main__":
    config.configurar_log()
    main()