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
    """All `*.json` workflow-export files in a corpus checkout.

    Two corpus layouts are supported (see fetch_corpus.py):

    - PRIMARY (Zie619/n8n-workflows): workflow exports live under a
      `workflows/` subdirectory. Restricted to it on purpose — the checkout
      also contains an unrelated `medcards-ai/` application and assorted
      tooling/config JSON (package.json, tsconfig.json, .devcontainer files,
      etc.) that are not workflow exports and must not be counted as such.
    - SECONDARY (enescingoz/awesome-n8n-templates): there is no `workflows/`
      subdirectory — exports live directly in topic-named folders at the
      repo root (`Airtable/`, `Discord/`, ...). In that case every `*.json`
      under the checkout is scanned, excluding `.git` internals; anything
      that isn't actually a workflow export (missing a `nodes` key, or not
      valid JSON — both observed in this corpus) is caught by
      `load_corpus()`'s per-file error handling below, not filtered here.
    """
    root = corpus_dir / "workflows"
    if root.is_dir():
        return sorted(root.rglob("*.json"))
    return sorted(p for p in corpus_dir.rglob("*.json") if ".git" not in p.parts)


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
