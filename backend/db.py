from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

import psycopg
from psycopg.rows import dict_row

from backend.config import DATABASE_URL


@contextmanager
def get_connection(database_url: str | None = None) -> Generator[psycopg.Connection, None, None]:
    with psycopg.connect(database_url or DATABASE_URL, row_factory=dict_row) as conn:
        yield conn
