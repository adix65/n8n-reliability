"""Tier B: database upsert operation — the worked bug-fix example.

The known bug this replaces: an earlier prototype searched for the
substring "upsert" across the *entire* serialized parameter blob of every
node, including sticky notes. Sticky-note authors write things like
"TODO: switch this to an upsert later" in a comment, which is not a
configured upsert operation on any real node — the earlier detector counted
21 such sticky-note matches as if they were.

The fix: read exactly one field, `parameters.operation`, on nodes that
carry it, and route every node lookup through `executable_nodes()` so
sticky notes are excluded before any detector ever sees them, not filtered
out after the fact. `naive_upsert_text_match` is kept ONLY for a regression
test asserting the fixed detector counts strictly fewer / different hits
than the naive one on a fixture reproducing the bug — it must never be used
to report a metric.
"""

from __future__ import annotations

import json as _json

from ..sticky_notes import executable_nodes
from .base import Detector, Tier, register

DETECTOR_VERSION = "1.0.0"


def db_upsert_operation(workflow: dict) -> bool:
    """Anchored: node.parameters.operation (exact field), value 'upsert'
    (case-insensitive), on executable nodes only."""
    for n in executable_nodes(workflow):
        op = n.get("parameters", {}).get("operation")
        if isinstance(op, str) and op.strip().lower() == "upsert":
            return True
    return False


def naive_upsert_text_match(workflow: dict) -> bool:
    """DO NOT USE FOR METRICS — reproduces the known bug (whole-blob text
    search over ALL nodes including sticky notes) for regression testing
    only, so a test can prove the real detector no longer does this."""
    for n in workflow.get("nodes", []):
        blob = _json.dumps(n.get("parameters", {})).lower()
        if "upsert" in blob:
            return True
    return False


register(
    Detector(
        key="db_upsert_operation",
        tier=Tier.B_STRUCTURAL,
        version=DETECTOR_VERSION,
        summary="Node z parameters.operation == 'upsert' (sygnał wzorca idempotencji)",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=db_upsert_operation,
        notes=(
            "Kotwica: pole parameters.operation dokładnie, sticky notes wykluczone. "
            "Naprawia błąd prototypu: naiwne przeszukanie całego blobu parametrów "
            "łapało słowo 'upsert' w treści sticky notes (21/130 trafień w "
            "poprzedniej wersji) — patrz naive_upsert_text_match i test regresyjny."
        ),
    )
)
