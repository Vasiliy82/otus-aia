from __future__ import annotations

import polars as pl

from scripts.data_prep.build_graph import GraphSeed
from scripts.data_prep.config import REQUIRED_YEARS, TARGET_YEAR
from scripts.data_prep.seed_legal import LegalSeed
from scripts.data_prep.serde import loads_allowed_roles


class DataValidationError(Exception):
    pass


def validate_poc_financial(
    poc_company: pl.DataFrame,
    poc_financial_report: pl.DataFrame,
) -> None:
    if poc_company.height == 0:
        raise DataValidationError("poc_company is empty")

    if poc_financial_report.height == 0:
        raise DataValidationError("poc_financial_report is empty")

    years_per_inn = (
        poc_financial_report.group_by("inn")
        .agg(pl.col("year").n_unique().alias("years_count"))
    )
    bad = years_per_inn.filter(pl.col("years_count") != len(REQUIRED_YEARS))
    if bad.height > 0:
        raise DataValidationError(
            f"Expected {len(REQUIRED_YEARS)} years per company, found violations: {bad.height}"
        )

    if poc_financial_report.filter(pl.col("year") == TARGET_YEAR).height == 0:
        raise DataValidationError(f"No reports for target year {TARGET_YEAR}")


def validate_legal_seed(legal: LegalSeed) -> None:
    secret_chunks = legal.chunks.filter(
        pl.col("external_id") == "ch_003"
    )
    if secret_chunks.height != 1:
        raise DataValidationError("Expected exactly one ch_003 chunk")

    roles = loads_allowed_roles(secret_chunks["allowed_roles"].to_list()[0])
    if roles != ["risk_manager"]:
        raise DataValidationError("ch_003 must be accessible only to risk_manager")


def validate_graph_seed(graph: GraphSeed) -> None:
    if graph.nodes.height < 5:
        raise DataValidationError("Graph must contain at least 5 nodes")

    if graph.edges.height < 4:
        raise DataValidationError("Graph must contain at least 4 edges")

    node_ids = set(graph.nodes["node_id"].to_list())
    for row in graph.edges.iter_rows(named=True):
        if row["source_node_id"] not in node_ids or row["target_node_id"] not in node_ids:
            raise DataValidationError("Graph edge references unknown node")


def validate_all(
    poc_company: pl.DataFrame,
    poc_financial_report: pl.DataFrame,
    legal: LegalSeed,
    graph: GraphSeed,
) -> None:
    validate_poc_financial(poc_company, poc_financial_report)
    validate_legal_seed(legal)
    validate_graph_seed(graph)
