"""Tier C (semantic) — idempotency patterns.

This module implements ANNOTATOR 1 only: a regex/structural candidate
detector. It is not a validated metric. Per the project brief, a Tier-C
detector becomes reportable only after:

  1. This candidate detector runs over the corpus (rating 1 per workflow).
  2. A second annotator — Claude via the API — independently rates the same
     workflows from a trimmed JSON view + a closed question (rating 2).
  3. Disagreements + 15 random agreements are exported to CSV for human
     adjudication.
  4. Inter-annotator agreement (Cohen's kappa) between annotators 1 and 2 is
     computed and reported in summary.json — that kappa, not this
     detector's raw rate, is the number fit for the article.

Steps 2-4 are deferred to the gold-set phase (llm_annotator.py, kappa.py —
not yet built) and must not be inferred from this module alone. Calling
`idempotency_candidate` and reporting its True/False rate as "the
idempotency rate" would misrepresent a Tier-C signal as if it were Tier A/B.
"""

from __future__ import annotations

from ..sticky_notes import executable_nodes
from .base import Detector, Tier, register
from .db_upsert import db_upsert_operation

# Node types where "read-then-branch-then-write" commonly implements a
# duplicate/existence check ahead of a create — a plausible idempotency
# pattern when combined with a conditional. This is a heuristic allow-list
# for the CANDIDATE detector only, not a claim about what the node does.
_CONDITIONAL_TYPES = {"n8n-nodes-base.if", "n8n-nodes-base.switch", "n8n-nodes-base.filter"}
_WRITE_TYPES = {
    "n8n-nodes-base.postgres",
    "n8n-nodes-base.mySql",
    "n8n-nodes-base.mongoDb",
    "n8n-nodes-base.airtable",
    "n8n-nodes-base.googleSheets",
    "n8n-nodes-base.supabase",
    "n8n-nodes-base.notion",
}


def _has_conditional_before_write(workflow: dict) -> bool:
    """CANDIDATE structural heuristic: workflow contains both a conditional
    node and a known write-capable node type. Does not verify the
    conditional actually gates the write, or that it checks for existence
    rather than something unrelated — that judgment is exactly what the
    Tier-C dual-annotator step exists to make. Do not treat this function's
    output as a validated fact.
    """
    types = {n.get("type") for n in executable_nodes(workflow)}
    return bool(types & _CONDITIONAL_TYPES) and bool(types & _WRITE_TYPES)


def idempotency_candidate(workflow: dict) -> bool:
    """Annotator 1 (candidate only — see module docstring)."""
    return db_upsert_operation(workflow) or _has_conditional_before_write(workflow)


DETECTOR_VERSION = "0.1.0-candidate"

register(
    Detector(
        key="idempotency_candidate",
        tier=Tier.C_SEMANTIC,
        version=DETECTOR_VERSION,
        summary="KANDYDAT (annotator 1/2) — sygnał wzorca idempotencji",
        denominator_definition=(
            "wszystkie pliki workflow w korpusie — UWAGA: to nie jest zwalidowana "
            "metryka, patrz docstring modułu. Nie raportować surowego odsetka jako faktu."
        ),
        fn=idempotency_candidate,
        notes="Wymaga drugiego anotatora (LLM) + Cohen's kappa przed publikacją liczby.",
    )
)
