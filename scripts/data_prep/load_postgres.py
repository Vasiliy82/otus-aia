from __future__ import annotations

import json
import logging
from typing import Any

import polars as pl
import psycopg
from psycopg.rows import dict_row

from scripts.data_prep.build_graph import GraphSeed
from scripts.data_prep.config import DATABASE_URL, RISK_COLUMNS
from scripts.data_prep.seed_legal import LegalSeed
from scripts.data_prep.serde import dumps_json, loads_allowed_roles, loads_metadata

logger = logging.getLogger(__name__)

RISK_FACTOR_SEED = [
    ("revenue_drop_gt_30", "Снижение выручки > 30%", "Выручка снизилась на 30% и более", "high"),
    ("negative_profit", "Отрицательная прибыль", "Чистая прибыль отрицательна", "high"),
    ("assets_drop_gt_25", "Падение активов > 25%", "Активы снизились на 25% и более", "medium"),
    ("negative_equity", "Отрицательный капитал", "Собственный капитал отрицательный", "high"),
    ("data_quality_issue", "Проблема качества данных", "Отчёт не подан, имputed или outlier", "medium"),
]

RISK_FLAG_TO_CODE = {
    "risk_revenue_drop_gt_30": "revenue_drop_gt_30",
    "risk_negative_profit": "negative_profit",
    "risk_assets_drop_gt_25": "assets_drop_gt_25",
    "risk_negative_equity": "negative_equity",
    "risk_data_quality_issue": "data_quality_issue",
}


def _parse_date(value: Any) -> Any:
    if value is None or value == "":
        return None
    return str(value)[:10]


def _bool_flag(value: Any) -> bool | None:
    if value is None:
        return None
    return bool(float(value))


def truncate_all(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            TRUNCATE TABLE
                graph_edge,
                graph_node,
                chunk,
                document,
                company_risk,
                financial_fact,
                financial_report,
                company,
                risk_factor
            RESTART IDENTITY CASCADE
            """
        )
    conn.commit()


def load_poc_to_postgres(
    poc_company: pl.DataFrame,
    poc_financial_report: pl.DataFrame,
    poc_company_features: pl.DataFrame,
    legal: LegalSeed,
    graph: GraphSeed,
    database_url: str | None = None,
    truncate: bool = True,
) -> None:
    database_url = database_url or DATABASE_URL

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        if truncate:
            truncate_all(conn)

        with conn.cursor() as cur:
            for row in RISK_FACTOR_SEED:
                cur.execute(
                    """
                    INSERT INTO risk_factor (code, title, description, severity)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (code) DO NOTHING
                    """,
                    row,
                )

            inn_to_company_id: dict[str, int] = {}
            for row in poc_company.iter_rows(named=True):
                cur.execute(
                    """
                    INSERT INTO company (
                        inn, ogrn, name, region, okved, okved_section,
                        creation_date, dissolution_date
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING company_id
                    """,
                    (
                        row["inn"],
                        row.get("ogrn"),
                        row.get("company_label") or row.get("name"),
                        row.get("region"),
                        row.get("okved"),
                        row.get("okved_section"),
                        _parse_date(row.get("creation_date")),
                        _parse_date(row.get("dissolution_date")),
                    ),
                )
                company_id = cur.fetchone()["company_id"]
                inn_to_company_id[row["inn"]] = company_id

            for row in poc_financial_report.iter_rows(named=True):
                company_id = inn_to_company_id[row["inn"]]
                cur.execute(
                    """
                    INSERT INTO financial_report (
                        company_id, report_year, revenue, profit, assets,
                        filed, imputed, outlier
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (company_id, report_year) DO UPDATE SET
                        revenue = EXCLUDED.revenue,
                        profit = EXCLUDED.profit,
                        assets = EXCLUDED.assets,
                        filed = EXCLUDED.filed,
                        imputed = EXCLUDED.imputed,
                        outlier = EXCLUDED.outlier
                    """,
                    (
                        company_id,
                        int(row["year"]),
                        row.get("revenue"),
                        row.get("net_profit"),
                        row.get("assets"),
                        _bool_flag(row.get("filed")),
                        _bool_flag(row.get("imputed")),
                        _bool_flag(row.get("outlier")),
                    ),
                )

            cur.execute("SELECT risk_factor_id, code FROM risk_factor")
            risk_ids = {r["code"]: r["risk_factor_id"] for r in cur.fetchall()}

            for row in poc_company_features.iter_rows(named=True):
                company_id = inn_to_company_id[row["inn"]]
                for flag_col in RISK_COLUMNS:
                    if flag_col not in row or not row[flag_col]:
                        continue
                    code = RISK_FLAG_TO_CODE[flag_col]
                    cur.execute(
                        """
                        INSERT INTO company_risk (
                            company_id, risk_factor_id, confidence, explanation
                        )
                        VALUES (%s, %s, %s, %s)
                        """,
                        (company_id, risk_ids[code], 1.0, f"Detected from RFSD features: {flag_col}"),
                    )

            external_doc_to_id: dict[str, int] = {}
            for row in legal.documents.iter_rows(named=True):
                metadata = loads_metadata(row.get("metadata"))
                cur.execute(
                    """
                    INSERT INTO document (source, doc_type, title, security_level, metadata)
                    VALUES (%s, %s, %s, %s, %s::jsonb)
                    RETURNING document_id
                    """,
                    (
                        row["source"],
                        row["doc_type"],
                        row["title"],
                        row["security_level"],
                        json.dumps({**metadata, "external_id": row["external_id"]}),
                    ),
                )
                external_doc_to_id[row["external_id"]] = cur.fetchone()["document_id"]

            external_chunk_to_id: dict[str, int] = {}
            for row in legal.chunks.iter_rows(named=True):
                metadata = loads_metadata(row.get("metadata"))
                doc_id = external_doc_to_id[row["document_external_id"]]
                allowed_roles = loads_allowed_roles(row["allowed_roles"])
                cur.execute(
                    """
                    INSERT INTO chunk (
                        document_id, chunk_text, chunk_order, allowed_roles, metadata
                    )
                    VALUES (%s, %s, %s, %s, %s::jsonb)
                    RETURNING chunk_id
                    """,
                    (
                        doc_id,
                        row["chunk_text"],
                        int(row["chunk_order"]),
                        allowed_roles,
                        json.dumps({**metadata, "external_id": row["external_id"]}),
                    ),
                )
                external_chunk_to_id[row["external_id"]] = cur.fetchone()["chunk_id"]

            for row in graph.nodes.iter_rows(named=True):
                metadata = dumps_json(loads_metadata(row.get("metadata"))) or "{}"
                cur.execute(
                    """
                    INSERT INTO graph_node (node_id, node_type, label, ref_table, ref_id, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (node_id) DO UPDATE SET
                        label = EXCLUDED.label,
                        metadata = EXCLUDED.metadata
                    """,
                    (
                        row["node_id"],
                        row["node_type"],
                        row["label"],
                        row.get("ref_table"),
                        row.get("ref_id"),
                        metadata,
                    ),
                )

            for row in graph.edges.iter_rows(named=True):
                metadata = dumps_json(loads_metadata(row.get("metadata"))) or "{}"
                source_chunk_id = None
                ext = row.get("source_chunk_external_id")
                if ext:
                    source_chunk_id = external_chunk_to_id.get(ext)
                cur.execute(
                    """
                    INSERT INTO graph_edge (
                        source_node_id, target_node_id, edge_type,
                        weight, confidence, source_chunk_id, metadata
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                    """,
                    (
                        row["source_node_id"],
                        row["target_node_id"],
                        row["edge_type"],
                        float(row["weight"]),
                        float(row["confidence"]),
                        source_chunk_id,
                        metadata,
                    ),
                )

        conn.commit()
    logger.info("Loaded PoC dataset into PostgreSQL")
