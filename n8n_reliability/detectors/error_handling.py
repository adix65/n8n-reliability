"""Tier A detectors for error-handling configuration.

Grounded against the real corpus (Zie619/n8n-workflows @ 94007c1445d92,
2061 files) before being written — see versioned_manifest.json for the
exact numbers this reproduces.

Fixes two bugs identified before this rewrite:

1. `settings.errorWorkflow` (a workflow-level setting pointing at the ID of
   another *instance-local* workflow to run on failure) is present in this
   export but its value is `None` in literally every file that has the key
   at all — 2057/2061 in the corpus. That is not "0/2061 workflows configure
   an error workflow"; it is a template-export artifact: an instance ID
   reference cannot survive being exported as a shareable template, so the
   field is scrubbed/nulled by n8n's own export path. `error_workflow_setting`
   therefore returns the `NOT_MEASURABLE` sentinel for every workflow rather
   than `False` — asserting "no error workflow" from this field would be
   asserting something the data cannot actually tell us.

2. `n8n-nodes-base.stopAndError` is a node that *deliberately* aborts a
   workflow and raises an error — the opposite of recovery. An earlier
   version of this analysis folded it into "has error handling"; it is kept
   here as its own, separate detector (`stop_and_error_present`) and is
   explicitly excluded from `has_recovery_mechanism`.
"""

from __future__ import annotations

from ..sticky_notes import executable_nodes
from .base import NOT_MEASURABLE, Detector, Tier, register
from .retry import node_retry_on_fail

STOP_AND_ERROR_TYPE = "n8n-nodes-base.stopAndError"
ERROR_TRIGGER_TYPE = "n8n-nodes-base.errorTrigger"

# n8n node schema versions >=1 use `onError` (enum); older exports use the
# boolean `continueOnFail`. Both are read; either counts toward recovery.
ON_ERROR_RECOVERY_VALUES = {"continueRegularOutput", "continueErrorOutput"}


def error_workflow_setting(workflow: dict) -> str:
    """Always NOT_MEASURABLE — see module docstring, point 1."""
    return NOT_MEASURABLE


def error_workflow_setting_key_present(workflow: dict) -> bool:
    """Whether the `errorWorkflow` key exists at all in `settings` — a
    structural fact distinct from its (unusable) value. Reported alongside
    `error_workflow_setting` for transparency, not as a reliability metric.
    """
    settings = workflow.get("settings") or {}
    return "errorWorkflow" in settings


def stop_and_error_present(workflow: dict) -> bool:
    """A deliberate, intentional interrupt — NOT error handling/recovery."""
    return any(n.get("type") == STOP_AND_ERROR_TYPE for n in executable_nodes(workflow))


def error_trigger_present(workflow: dict) -> bool:
    """Workflow contains a dedicated Error Trigger node (i.e. this workflow
    itself is built to receive/handle another workflow's failure)."""
    return any(n.get("type") == ERROR_TRIGGER_TYPE for n in executable_nodes(workflow))


def node_on_error_recovery(workflow: dict) -> bool:
    """Any node configured with `onError` set to a value that lets the
    workflow continue past that node's failure (v1+ schema)."""
    return any(
        n.get("onError") in ON_ERROR_RECOVERY_VALUES for n in executable_nodes(workflow)
    )


def node_continue_on_fail(workflow: dict) -> bool:
    """Legacy pre-`onError` boolean equivalent of the above."""
    return any(n.get("continueOnFail") is True for n in executable_nodes(workflow))


def has_recovery_mechanism(workflow: dict) -> bool:
    """Composite: does this workflow have *any* configured way to survive a
    node failure and keep running (recovery), as opposed to configuring an
    intentional abort (`stopAndError`, tracked separately)?

    True if: any node has onError/continueOnFail recovery configured, OR
    any node has retryOnFail=true, OR the workflow contains an Error
    Trigger node. Deliberately does NOT look at `stop_and_error_present` or
    `error_workflow_setting` (unmeasurable).
    """
    return (
        node_on_error_recovery(workflow)
        or node_continue_on_fail(workflow)
        or node_retry_on_fail(workflow)
        or error_trigger_present(workflow)
    )


DETECTOR_VERSION = "1.0.0"

register(
    Detector(
        key="error_workflow_setting",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="Workflow-level settings.errorWorkflow reference",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=error_workflow_setting,
        notes=(
            "Zawsze zwraca NOT_MEASURABLE_FROM_EXPORT — pole istnieje w eksporcie, "
            "ale wartość jest null w każdym sprawdzonym pliku (referencja ID "
            "workflow instancji nie przenosi się do eksportu template'a). Patrz "
            "error_workflow_setting_key_present dla surowej obecności klucza."
        ),
    )
)

register(
    Detector(
        key="stop_and_error_present",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="Node typu n8n-nodes-base.stopAndError obecny w workflow",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=stop_and_error_present,
        notes="Celowe przerwanie/rzucenie błędu — NIE liczone jako error handling.",
    )
)

register(
    Detector(
        key="error_trigger_present",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="Node typu n8n-nodes-base.errorTrigger obecny w workflow",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=error_trigger_present,
    )
)

register(
    Detector(
        key="node_on_error_recovery",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="Co najmniej jeden node ma onError w {continueRegularOutput, continueErrorOutput}",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=node_on_error_recovery,
    )
)

register(
    Detector(
        key="node_continue_on_fail",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="Co najmniej jeden node ma continueOnFail=true (schemat legacy)",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=node_continue_on_fail,
    )
)

register(
    Detector(
        key="has_recovery_mechanism",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="Kompozyt: onError recovery LUB continueOnFail LUB retryOnFail LUB errorTrigger",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=has_recovery_mechanism,
        notes="Explicite wyklucza stop_and_error_present — patrz docstring modułu.",
    )
)
