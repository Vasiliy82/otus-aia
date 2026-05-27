import json

import polars as pl

from scripts.data_prep.seed_legal import build_legal_seed
from scripts.data_prep.serde import (
    dataframe_for_csv_export,
    dumps_json,
    loads_allowed_roles,
    loads_metadata,
)


def test_roundtrip_metadata_and_roles():
    legal = build_legal_seed("7700000001")
    row = legal.chunks.filter(pl.col("external_id") == "ch_003").row(0, named=True)

    assert loads_allowed_roles(row["allowed_roles"]) == ["risk_manager"]
    assert loads_metadata(row["metadata"]) == {"linked_inn": "7700000001"}

    exported = dumps_json(row["allowed_roles"])
    assert json.loads(exported) == ["risk_manager"]


def test_legal_frames_export_to_csv(tmp_path):
    legal = build_legal_seed("7700000001")
    for name, df in [("documents", legal.documents), ("chunks", legal.chunks)]:
        path = tmp_path / f"{name}.csv"
        dataframe_for_csv_export(df).write_csv(path)
        assert path.stat().st_size > 0
