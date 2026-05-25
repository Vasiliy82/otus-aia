import polars as pl

from scripts.data_prep.build_graph import build_graph_seed
from scripts.data_prep.seed_legal import build_legal_seed


def test_legal_seed_has_rbac_demo():
    legal = build_legal_seed("7700000001", "ООО Ромашка")
    assert legal.documents.height == 3
    assert legal.chunks.height == 3

    secret = legal.chunks.filter(pl.col("external_id") == "ch_003")
    assert secret.height == 1
    roles = secret["allowed_roles"].to_list()[0]
    assert roles == ["risk_manager"]


def test_graph_links_company_and_chunks():
    legal = build_legal_seed("7700000001")
    graph = build_graph_seed(legal, "7700000001")
    assert graph.nodes.filter(pl.col("node_type") == "Company").height == 1
    assert graph.edges.height >= 4
