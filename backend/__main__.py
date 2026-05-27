from __future__ import annotations

import argparse
import logging
import sys

from backend.config import API_HOST, API_PORT


def cmd_embed(_: argparse.Namespace) -> int:
    from backend.indexing.embed_chunks import embed_all_chunks

    count = embed_all_chunks()
    return 0 if count >= 0 else 1


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=False)
    return 0


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="GraphRAG PoC backend CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("embed", help="Index chunk embeddings into pgvector").set_defaults(
        func=cmd_embed
    )

    p_serve = sub.add_parser("serve", help="Run FastAPI server")
    p_serve.add_argument("--host", default=API_HOST)
    p_serve.add_argument("--port", type=int, default=API_PORT)
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
