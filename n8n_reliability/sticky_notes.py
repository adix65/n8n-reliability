"""Central sticky-note exclusion.

Sticky notes (`n8n-nodes-base.stickyNote`) are canvas annotations, not
executable nodes — they carry free-text `parameters.content` written by the
workflow author. Naively substring-searching the full parameter blob of a
workflow (a mistake made by an earlier prototype of this tool) matches words
that appear inside sticky-note comments, not inside real node configuration.
Every detector in this package must read nodes through `executable_nodes()`
(or `EXECUTABLE_NODE_TYPES` be Excluded explicitly) rather than iterating
`workflow["nodes"]` directly.
"""

from __future__ import annotations

STICKY_NOTE_TYPE = "n8n-nodes-base.stickyNote"


def is_executable(node: dict) -> bool:
    """True for any node that is not a canvas annotation."""
    return node.get("type") != STICKY_NOTE_TYPE


def executable_nodes(workflow: dict) -> list[dict]:
    """All nodes in `workflow` except sticky notes.

    Accepts a raw workflow dict (as loaded from a `.json` export) so it can
    be used identically in unit-test fixtures and in corpus-wide analysis.
    """
    return [n for n in workflow.get("nodes", []) if is_executable(n)]


def sticky_note_count(workflow: dict) -> int:
    return sum(1 for n in workflow.get("nodes", []) if not is_executable(n))
