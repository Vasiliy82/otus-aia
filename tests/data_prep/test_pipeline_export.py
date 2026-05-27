import json
from pathlib import Path

import polars as pl

from scripts.data_prep.build_graph import build_graph_seed
from scripts.data_prep.pipeline import PreparedDataset, export_artifacts
from scripts.data_prep.seed_legal import build_legal_seed
from scripts.data_prep.validate import validate_all


def test_export_artifacts_and_validate(tmp_path: Path):
    legal = build_legal_seed("7700000001", "ООО Ромашка")
    graph = build_graph_seed(legal, "7700000001", "ООО Ромашка")

    poc_company = pl.DataFrame(
        {
            "inn": ["7700000001"],
            "ogrn": ["123"],
            "company_label": ["Компания"],
            "sample_bucket": ["normal"],
        }
    )
    poc_financial_report = pl.DataFrame(
        {
            "inn": ["7700000001", "7700000001"],
            "year": [2023, 2024],
            "revenue": [100.0, 80.0],
            "net_profit": [10.0, -1.0],
            "assets": [50.0, 40.0],
        }
    )
    poc_company_features = pl.DataFrame({"inn": ["7700000001"], "sample_bucket": ["normal"]})

    dataset = PreparedDataset(
        poc_company=poc_company,
        poc_financial_report=poc_financial_report,
        poc_company_features=poc_company_features,
        legal=legal,
        graph=graph,
        demo_inn="7700000001",
    )

    validate_all(
        dataset.poc_company,
        dataset.poc_financial_report,
        dataset.legal,
        dataset.graph,
    )
    export_artifacts(dataset, tmp_path)

    chunks = pl.read_csv(tmp_path / "chunks.csv")
    roles = json.loads(chunks.filter(pl.col("external_id") == "ch_003")["allowed_roles"][0])
    assert roles == ["risk_manager"]
