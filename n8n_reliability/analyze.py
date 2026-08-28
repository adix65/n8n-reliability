"""Orchestrates a full corpus run: load -> dedupe into families -> run every
registered detector per-file AND per-family in parallel -> write
summary.json (every percent carries its numerator, denominator, and a
worded denominator definition) and versioned_manifest.json.

Every run analyzes exactly ONE corpus, chosen via `corpus_label`
("primary" | "secondary"). The two corpora (Zie619/n8n-workflows and
enescingoz/awesome-n8n-templates — see fetch_corpus.py) are never mixed in
a single pass, and `corpus_label` is stamped into summary["corpus"]["label"]
so two summary.json files from two runs can never be confused for each
other or silently merged.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from . import fetch_corpus
from .dedupe import Family, group_families
from .detectors.base import NOT_APPLICABLE, NOT_MEASURABLE, REGISTRY, Tier
from .manifest import write_manifest
from .models import LoadedWorkflow, load_corpus
from .sticky_notes import executable_nodes, sticky_note_count

SENTINELS = (NOT_APPLICABLE, NOT_MEASURABLE)

CorpusLabel = Literal["primary", "secondary"]

_CORPUS_INFO = {
    "primary": {
        "source": fetch_corpus.CORPUS_REPO_URL,
        "license": fetch_corpus.CORPUS_LICENSE,
        "pinned_commit_sha": fetch_corpus.PINNED_COMMIT_SHA,
    },
    "secondary": {
        "source": fetch_corpus.SECONDARY_CORPUS_REPO_URL,
        "license": fetch_corpus.SECONDARY_CORPUS_LICENSE,
        "pinned_commit_sha": fetch_corpus.SECONDARY_PINNED_COMMIT_SHA,
    },
}


def _combine_any(values: list[Any]) -> Any:
    """Family-level aggregation: True if any member is True among the
    members for which the detector is applicable/measurable; falls back to
    the (expected-uniform) sentinel if no member is applicable/measurable.
    See dedupe.py docstring for why "any member" is a defensible, checked
    choice rather than an arbitrary one.
    """
    applicable = [v for v in values if v not in SENTINELS]
    if not applicable:
        return values[0] if values else NOT_APPLICABLE
    return any(v is True for v in applicable)


def _aggregate(values: list[Any], denominator_definition: str) -> dict:
    total = len(values)
    not_applicable = sum(1 for v in values if v == NOT_APPLICABLE)
    not_measurable = sum(1 for v in values if v == NOT_MEASURABLE)
    applicable_values = [v for v in values if v not in SENTINELS]
    applicable_denominator = len(applicable_values)
    numerator = sum(1 for v in applicable_values if v is True)
    percent = round(100 * numerator / applicable_denominator, 2) if applicable_denominator else None
    return {
        "numerator": numerator,
        "denominator": applicable_denominator,
        "denominator_definition": denominator_definition,
        "percent": percent,
        "excluded_not_applicable": not_applicable,
        "excluded_not_measurable_from_export": not_measurable,
        "total_units": total,
    }


def _node_level_stats(loaded: list[LoadedWorkflow]) -> dict:
    """Raw, per-node (not per-workflow) counts — supplementary to the
    per-file/per-family detector metrics below, added for parity with the
    original prototype's census.py, which reported node-level totals
    alongside its workflow-level ones (e.g. "291/30774 nodes have
    retryOnFail=true"). Reported with BOTH denominators (including and
    excluding sticky notes) since the prototype's own figure used the
    former and this package's stated policy is the latter — neither is
    hidden.
    """
    total_nodes_incl_sticky = sum(len(wf.data.get("nodes") or []) for wf in loaded)
    total_sticky = sum(sticky_note_count(wf.data) for wf in loaded)
    total_executable = total_nodes_incl_sticky - total_sticky
    retry_nodes = sum(
        1 for wf in loaded for n in executable_nodes(wf.data) if n.get("retryOnFail") is True
    )
    return {
        "total_nodes_including_sticky_notes": total_nodes_incl_sticky,
        "total_sticky_notes": total_sticky,
        "total_executable_nodes": total_executable,
        "nodes_with_retry_on_fail": {
            "count": retry_nodes,
            "percent_of_all_nodes_incl_sticky": (
                round(100 * retry_nodes / total_nodes_incl_sticky, 2) if total_nodes_incl_sticky else None
            ),
            "percent_of_executable_nodes": (
                round(100 * retry_nodes / total_executable, 2) if total_executable else None
            ),
        },
    }


def run_analysis(corpus_dir: Path, corpus_label: CorpusLabel) -> dict:
    if corpus_label not in _CORPUS_INFO:
        raise ValueError(f"corpus_label must be one of {sorted(_CORPUS_INFO)!r}, got {corpus_label!r}")

    loaded, load_errors = load_corpus(corpus_dir)
    families = group_families(loaded)

    total_files = len(loaded)
    total_sticky_notes = sum(sticky_note_count(wf.data) for wf in loaded)

    validated: dict[str, dict] = {}
    candidates: dict[str, dict] = {}

    for key, detector in sorted(REGISTRY.items()):
        per_file_values = [detector.fn(wf.data) for wf in loaded]
        per_family_values = [
            _combine_any([detector.fn(m.data) for m in fam.members]) for fam in families
        ]

        entry = {
            "tier": detector.tier.value,
            "detector_version": detector.version,
            "summary": detector.summary,
            "notes": detector.notes,
            "per_file": _aggregate(
                per_file_values,
                f"pliki workflow: {detector.denominator_definition}",
            ),
            "per_family": _aggregate(
                per_family_values,
                "unikalne rodziny strukturalne (any-member-true, patrz dedupe.py): "
                + detector.denominator_definition.replace(
                    "wszystkie pliki workflow w korpusie", "wszystkie rodziny w korpusie"
                ),
            ),
        }

        if detector.tier is Tier.C_SEMANTIC:
            candidates[key] = entry
        else:
            validated[key] = entry

    return {
        "corpus": {
            "label": corpus_label,
            **_CORPUS_INFO[corpus_label],
            "files_total": total_files,
            "families_total": len(families),
            "families_with_multiple_members": sum(1 for f in families if f.size > 1),
            "sticky_note_instances_excluded_from_all_detectors": total_sticky_notes,
            "load_errors": [{"path": str(e.path), "error": e.error} for e in load_errors],
            "node_level_stats": _node_level_stats(loaded),
        },
        "metrics_tier_a_b_validated": validated,
        "metrics_tier_c_candidates_NOT_VALIDATED": {
            "warning": (
                "Te liczby to wyjście annotatora 1 (regex/strukturalny kandydat) "
                "BEZ drugiego anotatora (LLM) ani rozstrzygnięcia sporów przez człowieka. "
                "NIE cytować jako zmierzoną metrykę w artykule — patrz gold_set.py / "
                "evaluate.py (kolejna faza) i Cohen's kappa, które dopiero czynią ten "
                "wynik wiarygodnym."
            ),
            "detectors": candidates,
        },
    }


def write_summary(corpus_dir: Path, out_dir: Path, corpus_label: CorpusLabel) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = run_analysis(corpus_dir, corpus_label)
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    write_manifest(corpus_dir, out_dir / "versioned_manifest.json", corpus_label)
    return summary_path
