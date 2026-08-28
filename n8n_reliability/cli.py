from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import fetch_corpus
from .analyze import write_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="n8n-reliability")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch_p = sub.add_parser("fetch-corpus", help="Clone a pinned corpus checkout")
    fetch_p.add_argument("--dest", type=Path, default=None)
    fetch_p.add_argument(
        "--secondary",
        action="store_true",
        help="Clone the secondary corpus (enescingoz/awesome-n8n-templates) instead of the primary one",
    )
    fetch_p.add_argument("--force", action="store_true")

    analyze_p = sub.add_parser("analyze", help="Run all detectors over a corpus checkout")
    analyze_p.add_argument("--corpus-dir", type=Path, required=True)
    analyze_p.add_argument("--out-dir", type=Path, default=Path("out"))
    analyze_p.add_argument(
        "--corpus-label",
        choices=["primary", "secondary"],
        required=True,
        help=(
            "Which corpus --corpus-dir holds. Required (no default) so a run "
            "can never silently mislabel its own output — primary and secondary "
            "results must never be conflated in one summary.json."
        ),
    )

    args = parser.parse_args(argv)

    if args.command == "fetch-corpus":
        if args.secondary:
            dest = args.dest or Path("data/corpus/awesome-n8n-templates")
            path = fetch_corpus.fetch_secondary(dest, force=args.force)
            print(f"Secondary corpus checked out at {path} @ {fetch_corpus.SECONDARY_PINNED_COMMIT_SHA}")
        else:
            dest = args.dest or Path("data/corpus/n8n-workflows")
            path = fetch_corpus.fetch(dest, force=args.force)
            print(f"Primary corpus checked out at {path} @ {fetch_corpus.PINNED_COMMIT_SHA}")
        return 0

    if args.command == "analyze":
        summary_path = write_summary(args.corpus_dir, args.out_dir, args.corpus_label)
        print(f"[{args.corpus_label}] Wrote {summary_path}")
        print(f"[{args.corpus_label}] Wrote {args.out_dir / 'versioned_manifest.json'}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
