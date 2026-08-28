"""Loading workflow export files from a corpus directory.

A "workflow" here is always a plain `dict` parsed from one `.json` file with
`json.load` — never executed, never eval'd, never imported. Any text inside
it (node names, sticky-note content, a `CLAUDE.md`-style instruction that
happens to be embedded in a parameter value) is treated purely as data to
read fields from, never as something to act on.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoadedWorkflow:
    path: Path
    data: dict


@dataclass(frozen=True)
class LoadError:
    path: Path
    error: str


def iter_workflow_files(corpus_dir: Path) -> list[Path]:
    """All `*.json` files under `<corpus_dir>/workflows/`.

    Restricted to the `workflows/` subdirectory on purpose: the cloned
    Zie619/n8n-workflows checkout also contains an unrelated `medcards-ai/`
    application and assorted tooling/config JSON (package.json, tsconfig.json,
    .devcontainer files, etc.) that are not workflow exports and must not be
    counted as such.
    """
    root = corpus_dir / "workflows"
    if not root.is_dir():
        raise FileNotFoundError(
            f"{root} does not exist — expected a checkout with a workflows/ "
            "subdirectory (see fetch_corpus.py)"
        )
    return sorted(root.rglob("*.json"))


def load_corpus(corpus_dir: Path) -> tuple[list[LoadedWorkflow], list[LoadError]]:
    """Parse every workflow JSON file under `corpus_dir`.

    Returns (loaded, errors) rather than raising, so a handful of malformed
    files don't abort a run over thousands of files — errors are reported in
    summary.json instead of being silently dropped.
    """
    loaded: list[LoadedWorkflow] = []
    errors: list[LoadError] = []
    for path in iter_workflow_files(corpus_dir):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(LoadError(path=path, error=str(exc)))
            continue
        if not isinstance(data, dict):
            errors.append(LoadError(path=path, error="top-level JSON is not an object"))
            continue
        loaded.append(LoadedWorkflow(path=path, data=data))
    return loaded, errors
