"""Detector registry and the A/B/C tier classification.

Tier A — deterministic: reads a boolean/enum/type field straight off the
    JSON. Validated with unit tests on hand-built fixtures. No gold set
    needed — there is no judgment call to disagree about.

Tier B — structural: reads one specific field of one specific node type.
    Must report both `anchored` hits (from the correct field on the correct
    node type) and, where relevant, what a naive whole-blob text search
    would have over-counted — see detectors/db_upsert.py for the worked
    example of the bug this guards against (a naive "upsert" substring
    search matched 21 sticky notes that used the word in a comment).

Tier C — semantic: requires judging what a node graph *means*, not just
    what fields it has. These detectors return a *candidate* label only; the
    reportable metric requires a second annotator (an LLM judge) and human
    adjudication of disagreements — see gold_set.py / evaluate.py, built in
    a later phase. Do not report a Tier-C detector's raw rate as a fact.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class Tier(str, Enum):
    A_DETERMINISTIC = "A"
    B_STRUCTURAL = "B"
    C_SEMANTIC = "C"


# Sentinel returned by a detector when the question is well-defined but the
# export format makes it impossible to answer — e.g. settings.errorWorkflow,
# which references an instance-local workflow ID that does not survive
# template export (see error_handling.py). Never conflate this with False.
NOT_MEASURABLE = "NOT_MEASURABLE_FROM_EXPORT"

# Sentinel returned when the detector's precondition node type is absent
# from the workflow entirely (e.g. asking about webhook auth on a workflow
# with no webhook node). Never conflate this with False either — "no
# webhook, so N/A" is a different fact from "has webhook, but no auth".
NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class Detector:
    key: str
    tier: Tier
    version: str
    summary: str
    denominator_definition: str
    fn: Callable[[dict], Any]
    notes: str = ""


REGISTRY: dict[str, Detector] = {}


def register(detector: Detector) -> Detector:
    if detector.key in REGISTRY:
        raise ValueError(f"duplicate detector key: {detector.key}")
    REGISTRY[detector.key] = detector
    return detector


def detectors_by_tier(tier: Tier) -> list[Detector]:
    return [d for d in REGISTRY.values() if d.tier is tier]
