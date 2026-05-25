import polars as pl
import pytest

from scripts.data_prep.build_graph import build_graph_seed
from scripts.data_prep.seed_legal import build_legal_seed
from scripts.data_prep.validate import (
    DataValidationError,
    validate_graph_seed,
    validate_legal_seed,
    validate_poc_financial,
)


def test_validate_legal_rbac_secret_chunk():
    legal = build_legal_seed("7700000001")
    validate_legal_seed(legal)

    bad_chunks = legal.chunks.with_columns(
        pl.when(pl.col("external_id") == "ch_003")
        .then(pl.lit(["analyst"]))
        .otherwise(pl.col("allowed_roles"))
        .alias("allowed_roles")
    )
    with pytest.raises(DataValidationError):
        validate_legal_seed(
            type(legal)(documents=legal.documents, chunks=bad_chunks)
        )


def test_validate_graph_minimum():
    legal = build_legal_seed("7700000001")
    graph = build_graph_seed(legal, "7700000001")
    validate_graph_seed(graph)


def test_validate_financial_two_years():
    poc_company = pl.DataFrame({"inn": ["1"], "ogrn": ["2"]})
    poc_reports = pl.DataFrame(
        {
            "inn": ["1", "1"],
            "year": [2023, 2024],
            "revenue": [100.0, 80.0],
            "net_profit": [10.0, -1.0],
            "assets": [50.0, 40.0],
        }
    )
    validate_poc_financial(poc_company, poc_reports)

    bad_reports = poc_reports.filter(pl.col("year") != 2024)
    with pytest.raises(DataValidationError):
        validate_poc_financial(poc_company, bad_reports)
