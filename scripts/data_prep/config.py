from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT_DIR / "data"))
RAW_RFSD_DIR = DATA_DIR / "raw" / "rfsd"
PROCESSED_DIR = DATA_DIR / "processed"
POC_DIR = DATA_DIR / "poc"

YEARS = [2022, 2023, 2024]
REGION_TAXCODES = ["7700", "7800", "5000"]
OKVED_SECTIONS = ["C", "F", "G", "J", "M"]

BASE_YEAR = 2023
TARGET_YEAR = 2024
REQUIRED_YEARS = [BASE_YEAR, TARGET_YEAR]

SAMPLE_BUCKET_SIZES = {
    "normal": 30,
    "revenue_drop_gt_30": 20,
    "negative_profit": 20,
    "assets_drop_gt_25": 15,
    "data_quality_issue": 15,
}

RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
HF_TOKEN = os.getenv("HF_TOKEN") or None
HF_DATASET_REPO = os.getenv("HF_DATASET_REPO", "irlspbru/RFSD")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://otus:otus@localhost:5432/graphrag_poc",
)

META_COLUMNS = [
    "year",
    "inn",
    "ogrn",
    "region",
    "region_taxcode",
    "creation_date",
    "dissolution_date",
    "age",
    "eligible",
    "filed",
    "imputed",
    "outlier",
    "okved",
    "okved_section",
]

FINANCIAL_COLUMNS = [
    "line_2110",
    "line_2400",
    "line_1600",
    "line_1300",
    "line_1400",
    "line_1500",
    "line_1520",
    "line_1250",
]

COLUMN_RENAME = {
    "line_2110": "revenue",
    "line_2400": "net_profit",
    "line_1600": "assets",
    "line_1300": "equity",
    "line_1400": "longterm_liab",
    "line_1500": "shortterm_liab",
    "line_1520": "payables",
    "line_1250": "cash",
}

ID_COLUMNS = [
    "inn",
    "ogrn",
    "region",
    "region_taxcode",
    "okved",
    "okved_section",
]

FLAG_COLUMNS = ["eligible", "filed", "imputed", "outlier"]

RENAMED_FINANCIAL_COLUMNS = list(COLUMN_RENAME.values())

REPORT_COLUMNS = [
    "inn",
    "ogrn",
    "year",
    "region",
    "region_taxcode",
    "okved",
    "okved_section",
    "creation_date",
    "dissolution_date",
    "age",
    "eligible",
    "filed",
    "imputed",
    "outlier",
    "revenue",
    "net_profit",
    "assets",
    "equity",
    "longterm_liab",
    "shortterm_liab",
    "payables",
    "cash",
]

COMPANY_COLUMNS = [
    "inn",
    "ogrn",
    "region",
    "region_taxcode",
    "okved",
    "okved_section",
    "creation_date",
    "dissolution_date",
    "age",
]

RISK_COLUMNS = [
    "risk_revenue_drop_gt_30",
    "risk_negative_profit",
    "risk_assets_drop_gt_25",
    "risk_negative_equity",
    "risk_data_quality_issue",
]

SQL_DIR = ROOT_DIR / "infra" / "sql"


def ensure_data_dirs() -> None:
    for path in (RAW_RFSD_DIR, PROCESSED_DIR, POC_DIR):
        path.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class YearPaths:
    paths: dict[int, Path]
