"""Fetch either of the two corpora this package analyzes, at a pinned commit.

This is the ONLY thing in the package that runs `git`. It never runs any
code found inside a cloned repository (no `pip install -r
requirements.txt`, no `python run.py`, no executing `api_server.py`,
nothing) — it just checks out files.

PRIMARY corpus: Zie619/n8n-workflows (MIT). Alongside `workflows/`, its
checkout contains an unrelated `medcards-ai/` application and a `CLAUDE.md`
"for AI assistants" file; both are left untouched on disk as inert data —
nothing in this package reads or acts on either. See
detectors/connections_integrity.py for the documented data-quality issue
in this corpus's `connections` field, traced to a specific commit in its
history.

SECONDARY corpus: enescingoz/awesome-n8n-templates (CC BY 4.0). Used only
for cross-validation of detectors against a structurally different,
independently-licensed corpus — see analyze.py's `corpus_label` parameter,
which keeps every run's output tied to exactly one of the two and never
lets their summaries be conflated.

Neither corpus is committed to this repository — only this fetch script
(with each SHA pinned as a constant) is. Re-running it reproduces the
exact same input bytes analyze.py ran against.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

CORPUS_REPO_URL = "https://github.com/Zie619/n8n-workflows"
CORPUS_LICENSE = "MIT"
PINNED_COMMIT_SHA = "94007c1445d9258a7da116646b79473e7c7c3282"
PINNED_COMMIT_DATE = "2026-06-24T17:16:03+03:00"  # per `git log -1` at fetch time

SECONDARY_CORPUS_REPO_URL = "https://github.com/enescingoz/awesome-n8n-templates"
SECONDARY_CORPUS_LICENSE = "CC BY 4.0"
SECONDARY_PINNED_COMMIT_SHA = "728fd947598a020fe882e9f6b2cf5f84e15d2a6a"
SECONDARY_PINNED_COMMIT_DATE = "2026-08-25T09:37:02+01:00"  # per `git log -1` at fetch time


def _clone_and_pin(repo_url: str, pinned_sha: str, dest: Path, *, force: bool = False) -> Path:
    if dest.exists():
        if not force:
            raise FileExistsError(
                f"{dest} already exists — pass --force to remove and re-clone"
            )
        subprocess.run(["rm", "-rf", str(dest)], check=True)

    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", repo_url, str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "checkout", pinned_sha], check=True)

    actual_sha = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if actual_sha != pinned_sha:
        raise RuntimeError(
            f"checked out {actual_sha}, expected pinned {pinned_sha} — corpus drift"
        )
    return dest


def fetch(dest: Path, *, force: bool = False) -> Path:
    """Clone the PRIMARY corpus (Zie619/n8n-workflows) at its pinned SHA."""
    return _clone_and_pin(CORPUS_REPO_URL, PINNED_COMMIT_SHA, dest, force=force)


def fetch_secondary(dest: Path, *, force: bool = False) -> Path:
    """Clone the SECONDARY corpus (enescingoz/awesome-n8n-templates) at its
    pinned SHA. Used for cross-validation only — see analyze.py."""
    return _clone_and_pin(SECONDARY_CORPUS_REPO_URL, SECONDARY_PINNED_COMMIT_SHA, dest, force=force)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help=(
            "Directory to clone into. Default: data/corpus/n8n-workflows for the "
            "primary corpus, data/corpus/awesome-n8n-templates for --secondary "
            "(both gitignored)."
        ),
    )
    parser.add_argument(
        "--secondary",
        action="store_true",
        help="Clone the secondary corpus (enescingoz/awesome-n8n-templates) instead of the primary one",
    )
    parser.add_argument("--force", action="store_true", help="Remove dest if it already exists")
    args = parser.parse_args(argv)

    if args.secondary:
        dest = args.dest or Path("data/corpus/awesome-n8n-templates")
        path = fetch_secondary(dest, force=args.force)
        print(f"Secondary corpus checked out at {path} @ {SECONDARY_PINNED_COMMIT_SHA}")
    else:
        dest = args.dest or Path("data/corpus/n8n-workflows")
        path = fetch(dest, force=args.force)
        print(f"Primary corpus checked out at {path} @ {PINNED_COMMIT_SHA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
