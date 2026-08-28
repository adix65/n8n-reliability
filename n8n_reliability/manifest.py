"""Build versioned_manifest.json — what corpus, at what commit, analyzed by
what code, when. Exists so any number in summary.json can be traced back to
an exact, reproducible input + detector version pair.
"""

from __future__ import annotations

import json
import platform
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import __version__ as PACKAGE_VERSION
from . import fetch_corpus
from .detectors import REGISTRY
from .detectors.connections_integrity import corruption_commit_citation

_PINNED_BY_LABEL = {
    "primary": {
        "repo_url": fetch_corpus.CORPUS_REPO_URL,
        "license": fetch_corpus.CORPUS_LICENSE,
        "sha": fetch_corpus.PINNED_COMMIT_SHA,
        "date": fetch_corpus.PINNED_COMMIT_DATE,
    },
    "secondary": {
        "repo_url": fetch_corpus.SECONDARY_CORPUS_REPO_URL,
        "license": fetch_corpus.SECONDARY_CORPUS_LICENSE,
        "sha": fetch_corpus.SECONDARY_PINNED_COMMIT_SHA,
        "date": fetch_corpus.SECONDARY_PINNED_COMMIT_DATE,
    },
}


def _corpus_commit_sha(corpus_dir: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(corpus_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


@dataclass
class Manifest:
    generated_at_utc: str
    package_version: str
    python_version: str
    corpus_label: str
    corpus_repo_url: str
    corpus_license: str
    corpus_pinned_commit_sha: str
    corpus_pinned_commit_date: str
    corpus_actual_commit_sha: str | None
    corpus_commit_matches_pinned: bool
    detector_versions: dict = field(default_factory=dict)
    corpus_corruption_provenance: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def build_manifest(corpus_dir: Path, corpus_label: str) -> Manifest:
    if corpus_label not in _PINNED_BY_LABEL:
        raise ValueError(f"corpus_label must be one of {sorted(_PINNED_BY_LABEL)!r}, got {corpus_label!r}")
    pinned = _PINNED_BY_LABEL[corpus_label]
    actual = _corpus_commit_sha(corpus_dir)

    # The connections-corruption provenance (commit 5ffee225, see
    # connections_integrity.py) was established specifically for the
    # PRIMARY corpus. It is not attached to a secondary-corpus manifest —
    # doing so would misrepresent an unrelated, independently-licensed
    # repository as sharing a defect that was never established for it.
    corruption = corruption_commit_citation() if corpus_label == "primary" else {}

    return Manifest(
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        package_version=PACKAGE_VERSION,
        python_version=platform.python_version(),
        corpus_label=corpus_label,
        corpus_repo_url=pinned["repo_url"],
        corpus_license=pinned["license"],
        corpus_pinned_commit_sha=pinned["sha"],
        corpus_pinned_commit_date=pinned["date"],
        corpus_actual_commit_sha=actual,
        corpus_commit_matches_pinned=(actual == pinned["sha"]),
        detector_versions={
            key: {"tier": d.tier.value, "version": d.version} for key, d in sorted(REGISTRY.items())
        },
        corpus_corruption_provenance=corruption,
    )


def write_manifest(corpus_dir: Path, out_path: Path, corpus_label: str) -> Manifest:
    manifest = build_manifest(corpus_dir, corpus_label)
    out_path.write_text(json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False) + "\n")
    return manifest
