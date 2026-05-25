from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import polars as pl

from scripts.data_prep.build_graph import GraphSeed, build_graph_seed
from scripts.data_prep.config import POC_DIR, PROCESSED_DIR, RAW_RFSD_DIR, YearPaths, ensure_data_dirs
from scripts.data_prep.download_rfsd import download_all_years
from scripts.data_prep.seed_legal import LegalSeed, build_legal_seed
from scripts.data_prep.transform_rfsd import transform_rfsd

logger = logging.getLogger(__name__)


@dataclass
class PreparedDataset:
    poc_company: pl.DataFrame
    poc_financial_report: pl.DataFrame
    poc_company_features: pl.DataFrame
    legal: LegalSeed
    graph: GraphSeed
    demo_inn: str


def _resolve_year_paths() -> YearPaths:
    paths: dict[int, Path] = {}
    for year_dir in sorted(RAW_RFSD_DIR.glob("RFSD/year=*")):
        year = int(year_dir.name.split("=")[1])
        parquet_files = list(year_dir.glob("*.parquet"))
        if parquet_files:
            paths[year] = parquet_files[0]

    if not paths:
        for parquet in RAW_RFSD_DIR.rglob("*.parquet"):
            if "year=" in str(parquet):
                part = parquet.parent.name
                year = int(part.split("=")[1])
                paths[year] = parquet

    if not paths:
        raise FileNotFoundError(
            f"No RFSD parquet files in {RAW_RFSD_DIR}. Run data-download first."
        )
    return YearPaths(paths=paths)


def export_artifacts(dataset: PreparedDataset, output_dir: Path | None = None) -> Path:
    output_dir = output_dir or POC_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset.poc_company.write_csv(output_dir / "poc_company.csv")
    dataset.poc_financial_report.write_csv(output_dir / "poc_financial_report.csv")
    dataset.poc_company_features.write_csv(output_dir / "poc_company_features.csv")
    dataset.legal.documents.write_csv(output_dir / "documents.csv")
    dataset.legal.chunks.write_csv(output_dir / "chunks.csv")
    dataset.graph.nodes.write_csv(output_dir / "graph_nodes.csv")
    dataset.graph.edges.write_csv(output_dir / "graph_edges.csv")

    manifest = {
        "demo_inn": dataset.demo_inn,
        "companies": dataset.poc_company.height,
        "reports": dataset.poc_financial_report.height,
        "documents": dataset.legal.documents.height,
        "chunks": dataset.legal.chunks.height,
        "graph_nodes": dataset.graph.nodes.height,
        "graph_edges": dataset.graph.edges.height,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Exported PoC artifacts to %s", output_dir)
    return output_dir


def run_prepare_pipeline(
    *,
    skip_download: bool = False,
    export: bool = True,
) -> PreparedDataset:
    ensure_data_dirs()

    if not skip_download:
        download_all_years()

    year_paths = _resolve_year_paths()
    poc_company, poc_financial_report, poc_company_features = transform_rfsd(year_paths)

    demo_row = poc_company.sort("inn").row(0, named=True)
    demo_inn = demo_row["inn"]
    demo_name = "ООО Ромашка" if poc_company.height else "Demo Company"

    legal = build_legal_seed(demo_inn=demo_inn, demo_company_name=demo_name)
    graph = build_graph_seed(legal=legal, demo_inn=demo_inn, demo_company_name=demo_name)

    dataset = PreparedDataset(
        poc_company=poc_company,
        poc_financial_report=poc_financial_report,
        poc_company_features=poc_company_features,
        legal=legal,
        graph=graph,
        demo_inn=demo_inn,
    )

    if export:
        export_artifacts(dataset, PROCESSED_DIR)
        export_artifacts(dataset, POC_DIR)

    return dataset
