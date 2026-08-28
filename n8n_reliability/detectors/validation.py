"""Tier C (semantic) — input validation before processing.

Same status as idempotency.py: ANNOTATOR 1 (candidate) only. Whether an
IF/Switch node is actually validating input *structure* (e.g. checking a
required field exists / has the right type) versus just implementing
ordinary business-logic branching is a judgment call that needs the
dual-annotator pipeline (candidate detector + Claude-API second annotator +
human adjudication of disagreements + Cohen's kappa) before it is
reportable. See idempotency.py docstring for the full rationale — it
applies identically here.

ADDITIONAL, CORPUS-SPECIFIC CAVEAT: this detector needs real `connections`
topology to check whether a conditional node sits immediately downstream of
an entry node. `detectors.connections_integrity` establishes that on this
corpus, connection targets essentially never resolve to a real node
(99.93% follow an `error-handler-<uuid>` pattern that matches nothing in
the file). As a direct consequence, this detector returns 0/2061 on the
pinned corpus — that is the corpus's broken topology data being correctly
reported as absent, not a claim that no workflow in the corpus validates
its input. Do not read the 0.0% as a finding about input validation
practice; read it as a finding about this export's connections field (see
connections_integrity.py), which is itself worth stating plainly in the
article rather than silently working around.
"""

from __future__ import annotations

from ..sticky_notes import executable_nodes
from .base import Detector, Tier, register

_CONDITIONAL_TYPES = {"n8n-nodes-base.if", "n8n-nodes-base.switch", "n8n-nodes-base.filter"}

# Trigger-adjacent node types: a conditional immediately downstream of one
# of these is positionally plausible as "validate the incoming payload
# before doing anything with it" — a CANDIDATE signal only.
_ENTRY_TYPES = {
    "n8n-nodes-base.webhook",
    "n8n-nodes-base.formTrigger",
    "n8n-nodes-base.httpRequest",
}


def _entry_node_names(workflow: dict) -> set[str]:
    return {n.get("name") for n in executable_nodes(workflow) if n.get("type") in _ENTRY_TYPES}


def validation_candidate(workflow: dict) -> bool:
    """CANDIDATE only: workflow has a conditional node whose incoming
    connection traces back (one hop) from an entry-point node. Does not
    inspect the condition's expression, so it cannot tell a structural
    validation check apart from an unrelated business-logic branch on the
    same position in the graph — that is exactly what needs a second
    annotator. Do not report this function's raw rate as a fact.
    """
    entry_names = _entry_node_names(workflow)
    if not entry_names:
        return False
    conditional_names = {
        n.get("name") for n in executable_nodes(workflow) if n.get("type") in _CONDITIONAL_TYPES
    }
    if not conditional_names:
        return False
    connections = workflow.get("connections") or {}
    for entry_name in entry_names:
        outputs = connections.get(entry_name, {})
        for branches in outputs.values():
            for branch in branches or []:
                for target in branch or []:
                    if target.get("node") in conditional_names:
                        return True
    return False


DETECTOR_VERSION = "0.1.0-candidate"

register(
    Detector(
        key="validation_candidate",
        tier=Tier.C_SEMANTIC,
        version=DETECTOR_VERSION,
        summary="KANDYDAT (annotator 1/2) — walidacja wejścia bezpośrednio po punkcie wejścia",
        denominator_definition=(
            "wszystkie pliki workflow w korpusie — UWAGA: to nie jest zwalidowana "
            "metryka, patrz docstring modułu."
        ),
        fn=validation_candidate,
        notes=(
            "Wymaga drugiego anotatora (LLM) + Cohen's kappa przed publikacją liczby. "
            "Na tym korpusie zwraca ~0 z powodu nierozwiązywalnej topologii connections "
            "(patrz connections_integrity.py) — to nie jest wynik o praktyce walidacji, "
            "to konsekwencja jakości eksportu."
        ),
    )
)
