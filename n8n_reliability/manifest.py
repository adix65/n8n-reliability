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
from .detectors import REGISTRY
from .detectors.connections_integrity import corruption_commit_citation
from .fetch_corpus import PINNED_COMMIT_DATE, PINNED_COMMIT_SHA


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
    corpus_repo_url: str
    corpus_pinned_commit_sha: str
    corpus_pinned_commit_date: str
    corpus_actual_commit_sha: str | None
    corpus_commit_matches_pinned: bool
    detector_versions: dict = field(default_factory=dict)
    corpus_corruption_provenance: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def build_manifest(corpus_dir: Path) -> Manifest:
    actual = _corpus_commit_sha(corpus_dir)
    return Manifest(
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        package_version=PACKAGE_VERSION,
        python_version=platform.python_version(),
        corpus_repo_url="https://github.com/Zie619/n8n-workflows",
        corpus_pinned_commit_sha=PINNED_COMMIT_SHA,
        corpus_pinned_commit_date=PINNED_COMMIT_DATE,
        corpus_actual_commit_sha=actual,
        corpus_commit_matches_pinned=(actual == PINNED_COMMIT_SHA),
        detector_versions={
            key: {"tier": d.tier.value, "version": d.version} for key, d in sorted(REGISTRY.items())
        },
        corpus_corruption_provenance=corruption_commit_citation(),
    )


def write_manifest(corpus_dir: Path, out_path: Path) -> Manifest:
    manifest = build_manifest(corpus_dir)
    out_path.write_text(json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False) + "\n")
    return manifest
