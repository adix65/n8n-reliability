"""Tier A: integrity of the `connections` graph itself.

Discovered while building dedupe.py's structural signature and while
debugging why `detectors.validation.validation_candidate` returned 0/2061:
on this corpus (Zie619/n8n-workflows @ 94007c1445d92), the `connections`
object's edge targets (`connections[X]["main"][i][j]["node"]`) essentially
never resolve to a real node `name` or `id` in the same file.

Measured directly against the pinned corpus:
  - 1367/2061 files have a non-empty `connections` object at all.
  - Across those, out of ~27,544 individual connection-target references,
    only 19 resolve to a real node name, 0 resolve to a real node id, and
    27,502 (99.85% of all targets, in 1363/2061 files) follow the exact
    pattern `error-handler-<uuid>[-<8 hex chars>]` — a string that matches
    no node in the file.

This package does not know why (curation-tool artifact when this corpus was
assembled, an n8n export quirk around per-node error-output branches, or
something else) — that is an open question, not something to guess at.
What is established is the fact itself: for the overwhelming majority of
files with any connections, **the graph topology in this export cannot be
trusted to describe how nodes actually connect.**

Consequence for this package: dedupe.py's family signature is node-type
MULTISET only (see its docstring) — an edge-based component would have
added no real signal, since it could not have resolved above 4/1367 files.
`detectors.validation.validation_candidate`, which needs real topology to
judge "does this conditional sit right after the entry point", is reliably
unusable on this corpus for that reason and its 0/2061 result should be
read as "this signal is absent from the export", not "no workflow does
this".
"""

from __future__ import annotations

import re

from .base import NOT_APPLICABLE, Detector, Tier, register

ERROR_HANDLER_TARGET_RE = re.compile(r"^error-handler-")

DETECTOR_VERSION = "1.0.0"


def _all_targets(workflow: dict) -> list[str]:
    out = []
    for outputs in (workflow.get("connections") or {}).values():
        for branches in (outputs or {}).values():
            for branch in branches or []:
                for target in branch or []:
                    node_ref = target.get("node")
                    if node_ref is not None:
                        out.append(node_ref)
    return out


def connections_present(workflow: dict) -> bool:
    return bool(workflow.get("connections"))


def connections_have_unresolvable_targets(workflow: dict):
    """NOT_APPLICABLE if there are no connections at all. Otherwise True if
    at least one connection target does not resolve to any node's `name`
    or `id` in this file."""
    targets = _all_targets(workflow)
    if not targets:
        return NOT_APPLICABLE
    node_names = {n.get("name") for n in workflow.get("nodes", [])}
    node_ids = {n.get("id") for n in workflow.get("nodes", [])}
    return any(t not in node_names and t not in node_ids for t in targets)


def unresolvable_targets_match_error_handler_pattern(workflow: dict):
    """NOT_APPLICABLE if there are no connections. Otherwise True if every
    unresolvable target follows the `error-handler-<uuid>` pattern observed
    corpus-wide (as opposed to some other, unexplained form of breakage)."""
    targets = _all_targets(workflow)
    if not targets:
        return NOT_APPLICABLE
    node_names = {n.get("name") for n in workflow.get("nodes", [])}
    node_ids = {n.get("id") for n in workflow.get("nodes", [])}
    unresolved = [t for t in targets if t not in node_names and t not in node_ids]
    if not unresolved:
        return NOT_APPLICABLE
    return all(ERROR_HANDLER_TARGET_RE.match(t) for t in unresolved)


register(
    Detector(
        key="connections_present",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="Workflow ma niepusty obiekt connections",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=connections_present,
    )
)

register(
    Detector(
        key="connections_have_unresolvable_targets",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="connections zawiera referencję do node'a, który nie istnieje w pliku",
        denominator_definition=(
            "TYLKO pliki z niepustym connections (pozostałe NOT_APPLICABLE)"
        ),
        fn=connections_have_unresolvable_targets,
        notes=(
            "Kluczowe znalezisko o jakości korpusu — patrz docstring modułu. "
            "99,85% referencji celu w connections tego korpusu nie rozwiązuje się "
            "do żadnego realnego node'a."
        ),
    )
)

register(
    Detector(
        key="unresolvable_targets_match_error_handler_pattern",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="Nierozwiązywalne cele connections pasują do wzorca 'error-handler-<uuid>'",
        denominator_definition=(
            "TYLKO pliki z co najmniej jedną nierozwiązywalną referencją w connections "
            "(pozostałe NOT_APPLICABLE)"
        ),
        fn=unresolvable_targets_match_error_handler_pattern,
    )
)
