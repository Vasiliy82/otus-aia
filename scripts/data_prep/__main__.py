from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from scripts.data_prep.config import SQL_DIR
from scripts.data_prep.download_rfsd import download_all_years
from scripts.data_prep.load_postgres import load_poc_to_postgres
from scripts.data_prep.pipeline import run_prepare_pipeline
from scripts.data_prep.validate import validate_all

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def cmd_download(_: argparse.Namespace) -> None:
    download_all_years()


def cmd_prepare(args: argparse.Namespace) -> None:
    dataset = run_prepare_pipeline(skip_download=args.skip_download)
    validate_all(
        dataset.poc_company,
        dataset.poc_financial_report,
        dataset.legal,
        dataset.graph,
    )
    logger.info("Validation passed. demo_inn=%s", dataset.demo_inn)


def cmd_load(_: argparse.Namespace) -> None:
    dataset = run_prepare_pipeline(skip_download=True, export=False)
    validate_all(
        dataset.poc_company,
        dataset.poc_financial_report,
        dataset.legal,
        dataset.graph,
    )
    load_poc_to_postgres(
        dataset.poc_company,
        dataset.poc_financial_report,
        dataset.poc_company_features,
        dataset.legal,
        dataset.graph,
    )


def cmd_migrate(_: argparse.Namespace) -> None:
    import os

    import psycopg

    from scripts.data_prep.config import DATABASE_URL

    sql_files = sorted(SQL_DIR.glob("*.sql"))
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            for sql_file in sql_files:
                logger.info("Applying %s", sql_file.name)
                cur.execute(sql_file.read_text(encoding="utf-8"))
        conn.commit()
    logger.info("Applied %d migration files", len(sql_files))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PoC data preparation CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("download", help="Download RFSD from HuggingFace").set_defaults(
        func=cmd_download
    )

    p_prepare = sub.add_parser("prepare", help="Transform RFSD and build demo legal/graph")
    p_prepare.add_argument(
        "--skip-download",
        action="store_true",
        help="Use existing files in data/raw/rfsd",
    )
    p_prepare.set_defaults(func=cmd_prepare)

    sub.add_parser("load", help="Prepare and load into PostgreSQL").set_defaults(func=cmd_load)
    sub.add_parser("migrate", help="Apply SQL migrations").set_defaults(func=cmd_migrate)

    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except Exception as exc:
        logger.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
