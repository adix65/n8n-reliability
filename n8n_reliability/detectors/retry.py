"""Tier A: per-node retry configuration.

IMPORTANT — do not confuse this with `workflow["settings"]["retryOnFail"]`.
That workflow-level settings key was found, on inspection of the real
corpus, to take only 13 distinct value-combinations across all 2061 files,
with one single combination shared by 1871/2061 (~91%) of them, and
`retryOnFail: true` in essentially all of them regardless of what the
workflow actually does. That is the export tool's boilerplate default, not
an authored choice — it is not used as a detector here. The per-NODE
`retryOnFail` boolean (set individually on 108/2061 files' nodes) is the
real, meaningful signal and is what this module reads.
"""

from __future__ import annotations

from ..sticky_notes import executable_nodes
from .base import Detector, Tier, register

DETECTOR_VERSION = "1.0.0"


def node_retry_on_fail(workflow: dict) -> bool:
    """Any node has `retryOnFail: true` set directly on the node (not the
    workflow-level settings boilerplate — see module docstring)."""
    return any(n.get("retryOnFail") is True for n in executable_nodes(workflow))


def nodes_with_retry_config(workflow: dict) -> list[dict]:
    """Detail view: for each node with retryOnFail=true, its maxTries /
    waitBetweenTries if present, to let the gold-set phase judge "quality"
    of the retry config, not just its presence."""
    out = []
    for n in executable_nodes(workflow):
        if n.get("retryOnFail") is True:
            out.append(
                {
                    "node_name": n.get("name"),
                    "node_type": n.get("type"),
                    "max_tries": n.get("maxTries"),
                    "wait_between_tries_ms": n.get("waitBetweenTries"),
                }
            )
    return out


register(
    Detector(
        key="node_retry_on_fail",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="Co najmniej jeden node ma node-level retryOnFail=true",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=node_retry_on_fail,
        notes=(
            "Nie mylić z workflow-level settings.retryOnFail (boilerplate eksportu, "
            "13 unikalnych sygnatur na 2061 plików — patrz manifest)."
        ),
    )
)
