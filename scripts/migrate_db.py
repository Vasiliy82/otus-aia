"""Apply infra/sql migrations (used by Makefile)."""

from scripts.data_prep.__main__ import cmd_migrate
import argparse

if __name__ == "__main__":
    cmd_migrate(argparse.Namespace())
