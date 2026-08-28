"""Tier B: webhook authentication.

Structural anchor: `node.type == "n8n-nodes-base.webhook"`, field
`node.parameters.authentication`. Never scans any other node type, and
never scans the raw parameter blob as text — only this one field, on this
one node type. Sticky notes are excluded upstream by `executable_nodes`.

Caveat worth carrying into the article: in this corpus, the two "has auth"
values observed are the literal strings
`"{{ $credentials.basicAuth }}"` / `"{{ $credentials.headerAuth }}"`
rather than n8n's real enum values (`basicAuth` / `headerAuth` / `jwtAuth`
in a live instance). That is very likely a scrubbing artifact of whatever
tool exported/curated this corpus, substituting a template expression for
the real field value. It does not change the detector's binary
have-auth-configured-or-not answer, but it means this corpus cannot be used
to distinguish *which* auth method was configured, only whether one was.
"""

from __future__ import annotations

from ..sticky_notes import executable_nodes
from .base import NOT_APPLICABLE, Detector, Tier, register

WEBHOOK_TYPE = "n8n-nodes-base.webhook"
NO_AUTH_VALUES = {"none", None, ""}


def _webhook_nodes(workflow: dict) -> list[dict]:
    # sticky notes can never be type==webhook, but every detector routes
    # through executable_nodes() uniformly so the exclusion rule has one
    # single, auditable enforcement point across the whole package.
    return [n for n in executable_nodes(workflow) if n.get("type") == WEBHOOK_TYPE]


def webhook_present(workflow: dict) -> bool:
    return len(_webhook_nodes(workflow)) > 0


def webhook_missing_auth(workflow: dict):
    """NOT_APPLICABLE if the workflow has no webhook node at all.
    Otherwise True if ANY webhook node's `parameters.authentication` is
    missing/empty/'none'.
    """
    nodes = _webhook_nodes(workflow)
    if not nodes:
        return NOT_APPLICABLE
    return any(n.get("parameters", {}).get("authentication") in NO_AUTH_VALUES for n in nodes)


DETECTOR_VERSION = "1.0.0"

register(
    Detector(
        key="webhook_present",
        tier=Tier.B_STRUCTURAL,
        version=DETECTOR_VERSION,
        summary="Co najmniej jeden node typu n8n-nodes-base.webhook",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=webhook_present,
    )
)

register(
    Detector(
        key="webhook_missing_auth",
        tier=Tier.B_STRUCTURAL,
        version=DETECTOR_VERSION,
        summary="Webhook bez uwierzytelnienia (parameters.authentication puste/none)",
        denominator_definition=(
            "TYLKO pliki workflow zawierające co najmniej jeden node webhook "
            "(pozostałe raportowane jako NOT_APPLICABLE, nie False)"
        ),
        fn=webhook_missing_auth,
        notes="Kotwica strukturalna: node.type==webhook + pole parameters.authentication, nic więcej.",
    )
)
