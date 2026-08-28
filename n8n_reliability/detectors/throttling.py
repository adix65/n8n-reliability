"""Tier B: explicit throttling / rate limiting.

Structural anchor: node.type in {n8n-nodes-base.wait, n8n-nodes-base.splitInBatches}.
For Wait nodes, also reads `parameters.resume` — a Wait node configured
`resume: "webhook"` is waiting for an external callback, not throttling a
loop, so it is reported as a separate breakdown bucket rather than folded
silently into "has throttling".
"""

from __future__ import annotations

from ..sticky_notes import executable_nodes
from .base import Detector, Tier, register

WAIT_TYPE = "n8n-nodes-base.wait"
SPLIT_IN_BATCHES_TYPE = "n8n-nodes-base.splitInBatches"


def throttling_node_present(workflow: dict) -> bool:
    return any(
        n.get("type") in (WAIT_TYPE, SPLIT_IN_BATCHES_TYPE) for n in executable_nodes(workflow)
    )


def wait_node_resume_modes(workflow: dict) -> list[str]:
    """One entry per Wait node: its `parameters.resume` value (default
    'timeInterval' when unset, i.e. a genuine timed delay)."""
    return [
        n.get("parameters", {}).get("resume", "timeInterval")
        for n in executable_nodes(workflow)
        if n.get("type") == WAIT_TYPE
    ]


def has_time_delay_wait(workflow: dict) -> bool:
    """A Wait node that is a genuine timed delay (resume != 'webhook'),
    i.e. plausibly used for throttling rather than for pausing until an
    external callback arrives."""
    return any(mode != "webhook" for mode in wait_node_resume_modes(workflow))


DETECTOR_VERSION = "1.0.0"

register(
    Detector(
        key="throttling_node_present",
        tier=Tier.B_STRUCTURAL,
        version=DETECTOR_VERSION,
        summary="Node typu Wait lub Split In Batches obecny w workflow",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=throttling_node_present,
        notes=(
            "Obecność strukturalna, nie ocena czy throttling jest 'poprawnie' "
            "skonfigurowany — patrz has_time_delay_wait dla dokładniejszego podziału Wait."
        ),
    )
)

register(
    Detector(
        key="has_time_delay_wait",
        tier=Tier.B_STRUCTURAL,
        version=DETECTOR_VERSION,
        summary="Wait node z resume != 'webhook' (rzeczywiste opóźnienie czasowe)",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=has_time_delay_wait,
    )
)
