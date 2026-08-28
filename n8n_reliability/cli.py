from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import fetch_corpus
from .analyze import write_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="n8n-reliability")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch_p = sub.add_parser("fetch-corpus", help="Clone the pinned Zie619/n8n-workflows commit")
    fetch_p.add_argument("--dest", type=Path, default=Path("data/corpus/n8n-workflows"))
    fetch_p.add_argument("--force", action="store_true")

    analyze_p = sub.add_parser("analyze", help="Run all detectors over a corpus checkout")
    analyze_p.add_argument("--corpus-dir", type=Path, required=True)
    analyze_p.add_argument("--out-dir", type=Path, default=Path("out"))

    args = parser.parse_args(argv)

    if args.command == "fetch-corpus":
        path = fetch_corpus.fetch(args.dest, force=args.force)
        print(f"Corpus checked out at {path} @ {fetch_corpus.PINNED_COMMIT_SHA}")
        return 0

    if args.command == "analyze":
        summary_path = write_summary(args.corpus_dir, args.out_dir)
        print(f"Wrote {summary_path}")
        print(f"Wrote {args.out_dir / 'versioned_manifest.json'}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
