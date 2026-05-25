from __future__ import annotations

import logging
from pathlib import Path

from huggingface_hub import hf_hub_download

from scripts.data_prep.config import HF_DATASET_REPO, HF_TOKEN, RAW_RFSD_DIR, YEARS, YearPaths, ensure_data_dirs

logger = logging.getLogger(__name__)


def download_rfsd_year(year: int, local_dir: Path | None = None) -> Path:
    local_dir = local_dir or RAW_RFSD_DIR
    local_dir.mkdir(parents=True, exist_ok=True)
    filename = f"RFSD/year={year}/part-0.parquet"
    downloaded = hf_hub_download(
        repo_id=HF_DATASET_REPO,
        repo_type="dataset",
        filename=filename,
        token=HF_TOKEN,
        local_dir=local_dir,
    )
    return Path(downloaded)


def download_all_years(years: list[int] | None = None) -> YearPaths:
    ensure_data_dirs()
    years = years or YEARS
    paths: dict[int, Path] = {}
    for year in years:
        logger.info("Downloading RFSD year=%s", year)
        paths[year] = download_rfsd_year(year)
        logger.info("Saved %s", paths[year])
    return YearPaths(paths=paths)
