from __future__ import annotations

import json
from typing import Any

import polars as pl


def dumps_json(value: Any) -> str | None:
    """Serialize a value for CSV / JSON text boundaries."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, pl.Series):
        value = value.to_list()
    if hasattr(value, "to_dict") and not isinstance(value, dict):
        value = value.to_dict()
    return json.dumps(value, ensure_ascii=False)


def loads_json(value: Any, default: Any = None) -> Any:
    """Parse a value coming from CSV / JSON text boundaries into Python objects."""
    if value is None:
        return default
    if isinstance(value, pl.Series):
        value = value.to_list()
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return default
        return json.loads(stripped)
    if hasattr(value, "to_dict") and not isinstance(value, dict):
        return value.to_dict()
    return value


def loads_metadata(value: Any) -> dict[str, Any]:
    parsed = loads_json(value, default={})
    if not isinstance(parsed, dict):
        raise TypeError(f"metadata must be a dict, got {type(parsed)!r}")
    return parsed


def loads_allowed_roles(value: Any) -> list[str]:
    parsed = loads_json(value, default=[])
    if not isinstance(parsed, list):
        raise TypeError(f"allowed_roles must be a list, got {type(parsed)!r}")
    return parsed


def _is_nested_dtype(dtype: pl.DataType) -> bool:
    if dtype == pl.Struct:
        return True
    if isinstance(dtype, pl.List):
        return True
    base = getattr(dtype, "base_type", None)
    if callable(base):
        return base() == pl.List
    return False


def dataframe_for_csv_export(df: pl.DataFrame) -> pl.DataFrame:
    """Flatten Struct/List columns to JSON strings so Polars can write CSV."""
    exprs: list[pl.Expr] = []
    for col, dtype in df.schema.items():
        if _is_nested_dtype(dtype):
            exprs.append(
                pl.col(col)
                .map_elements(dumps_json, return_dtype=pl.Utf8)
                .alias(col)
            )
    if not exprs:
        return df
    return df.with_columns(exprs)
