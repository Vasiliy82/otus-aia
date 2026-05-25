from __future__ import annotations

import json
from dataclasses import dataclass

import polars as pl

from scripts.data_prep.seed_legal import LegalSeed


@dataclass(frozen=True)
class GraphSeed:
    nodes: pl.DataFrame
    edges: pl.DataFrame


def build_graph_seed(
    legal: LegalSeed,
    demo_inn: str,
    demo_company_name: str = "ООО Ромашка",
) -> GraphSeed:
    nodes_rows = [
        {
            "node_id": f"company:{demo_inn}",
            "node_type": "Company",
            "label": demo_company_name,
            "ref_table": "company",
            "ref_id": demo_inn,
            "metadata": {},
        },
        {
            "node_id": "legal_act:banking_law",
            "node_type": "LegalAct",
            "label": "Закон о банковской деятельности",
            "ref_table": "document",
            "ref_id": "law_001",
            "metadata": {},
        },
    ]

    for doc in legal.documents.iter_rows(named=True):
        nodes_rows.append(
            {
                "node_id": f"document:{doc['external_id']}",
                "node_type": "Document",
                "label": doc["title"],
                "ref_table": "document",
                "ref_id": doc["external_id"],
                "metadata": {"security_level": doc["security_level"]},
            }
        )

    for chunk in legal.chunks.iter_rows(named=True):
        nodes_rows.append(
            {
                "node_id": f"chunk:{chunk['external_id']}",
                "node_type": "Chunk",
                "label": chunk["external_id"],
                "ref_table": "chunk",
                "ref_id": chunk["external_id"],
                "metadata": chunk["metadata"],
            }
        )

    nodes_rows.append(
        {
            "node_id": "risk_factor:revenue_drop",
            "node_type": "RiskFactor",
            "label": "Снижение выручки > 30%",
            "ref_table": "risk_factor",
            "ref_id": "revenue_drop_gt_30",
            "metadata": {},
        }
    )

    for row in nodes_rows:
        row["metadata"] = json.dumps(row["metadata"], ensure_ascii=False)

    nodes = pl.DataFrame(nodes_rows)

    edges_rows = [
        {
            "source_node_id": f"chunk:ch_002",
            "target_node_id": f"document:policy_001",
            "edge_type": "BELONGS_TO",
            "weight": 1.0,
            "confidence": 1.0,
            "source_chunk_external_id": "ch_002",
            "metadata": {},
        },
        {
            "source_node_id": f"chunk:ch_002",
            "target_node_id": "risk_factor:revenue_drop",
            "edge_type": "MENTIONS",
            "weight": 1.0,
            "confidence": 1.0,
            "source_chunk_external_id": "ch_002",
            "metadata": {},
        },
        {
            "source_node_id": f"chunk:ch_002",
            "target_node_id": f"company:{demo_inn}",
            "edge_type": "MENTIONS",
            "weight": 1.0,
            "confidence": 1.0,
            "source_chunk_external_id": "ch_002",
            "metadata": {},
        },
        {
            "source_node_id": f"chunk:ch_001",
            "target_node_id": "legal_act:banking_law",
            "edge_type": "LINKED_TO",
            "weight": 1.0,
            "confidence": 1.0,
            "source_chunk_external_id": "ch_001",
            "metadata": {},
        },
        {
            "source_node_id": f"document:policy_001",
            "target_node_id": f"document:law_001",
            "edge_type": "LINKED_TO",
            "weight": 0.8,
            "confidence": 0.9,
            "source_chunk_external_id": None,
            "metadata": {},
        },
        {
            "source_node_id": f"chunk:ch_003",
            "target_node_id": f"document:risk_001",
            "edge_type": "BELONGS_TO",
            "weight": 1.0,
            "confidence": 1.0,
            "source_chunk_external_id": "ch_003",
            "metadata": {},
        },
    ]

    for row in edges_rows:
        row["metadata"] = json.dumps(row["metadata"], ensure_ascii=False)

    edges = pl.DataFrame(edges_rows)

    return GraphSeed(nodes=nodes, edges=edges)
