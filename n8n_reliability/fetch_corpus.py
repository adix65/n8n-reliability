"""Fetch the Zie619/n8n-workflows corpus at a pinned commit.

This is the ONLY thing in the package that runs `git`. It never runs any
code found inside the cloned repository (no `pip install -r
requirements.txt`, no `python run.py`, no executing `api_server.py`,
nothing) — it just checks out files. The clone contains, alongside
`workflows/`, an unrelated `medcards-ai/` application and a `CLAUDE.md`
"for AI assistants" file; both are left untouched on disk as inert data.
Nothing in this package reads or acts on either.

The corpus itself is intentionally never committed to this repository —
only this fetch script (with the SHA pinned as a constant) is. Re-running
it reproduces the exact same input bytes analyze.py ran against.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

CORPUS_REPO_URL = "https://github.com/Zie619/n8n-workflows"
PINNED_COMMIT_SHA = "94007c1445d9258a7da116646b79473e7c7c3282"
PINNED_COMMIT_DATE = "2026-06-24T17:16:03+03:00"  # per `git log -1` at fetch time


def fetch(dest: Path, *, force: bool = False) -> Path:
    if dest.exists():
        if not force:
            raise FileExistsError(
                f"{dest} already exists — pass --force to remove and re-clone"
            )
        subprocess.run(["rm", "-rf", str(dest)], check=True)

    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", CORPUS_REPO_URL, str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "checkout", PINNED_COMMIT_SHA], check=True)

    actual_sha = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if actual_sha != PINNED_COMMIT_SHA:
        raise RuntimeError(
            f"checked out {actual_sha}, expected pinned {PINNED_COMMIT_SHA} — corpus drift"
        )
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path("data/corpus/n8n-workflows"),
        help="Directory to clone into (default: data/corpus/n8n-workflows, gitignored)",
    )
    parser.add_argument("--force", action="store_true", help="Remove dest if it already exists")
    args = parser.parse_args(argv)

    path = fetch(args.dest, force=args.force)
    print(f"Corpus checked out at {path} @ {PINNED_COMMIT_SHA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
