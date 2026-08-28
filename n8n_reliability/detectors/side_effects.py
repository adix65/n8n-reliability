"""Reproduces prototype/surface.py's conditional metrics: rather than
asking "does this workflow have X" over the whole corpus, it asks "among
workflows that plausibly NEED X, how many have it" — e.g. "among webhooks
that also do something with real-world side effects, how many require
webhook auth or show an idempotency pattern", not "among all webhooks".

Implemented via the existing NOT_APPLICABLE sentinel mechanism (the same
one `webhook_missing_auth` already uses to exclude workflows with no
webhook at all): a detector here returns NOT_APPLICABLE for any workflow
outside its intended conditional subset, so the subset becomes the
detector's `denominator` automatically through analyze.py's existing
aggregation — no separate "conditional metrics" pipeline was needed.

Every substring/type list below (WRITE_METHODS, SEND_TYPE_SUBSTRINGS,
DB_WRITE_TYPE_SUBSTRINGS, DB_WRITE_OPERATIONS) is copied verbatim from the
recovered prototype for continuity with its results, not independently
re-derived. Sticky notes are excluded throughout via `executable_nodes`,
which the prototype's surface.py did not do (it iterated
`workflow["nodes"]` directly) — that is a deliberate fix, not an
oversight; see db_upsert.py for the same class of bug in a different
detector.

One more bug found (not previously known, distinct from the three the
rewrite was briefed on): the prototype tried to exclude "Respond to
Webhook" nodes from its webhook-trigger count by checking `"response" not
in type`. The real n8n type string is `n8n-nodes-base.respondToWebhook`,
which does not contain the substring "response" (it has "respond", not
"response") — so that exclusion never actually fired, and the prototype's
webhook-trigger counts silently included every Respond to Webhook node in
the corpus as if it were a trigger. Verified directly: only
`n8n-nodes-base.webhook` and `n8n-nodes-base.respondToWebhook` exist in
this corpus among "*webhook*"-typed nodes, so the fix is a one-word
substring change (check "respond", not "response") — done below.

Measured impact on the pinned corpus: the prototype's own
"webhook + side effect" denominator was 221; with the fix it is 213 — the
exact 8 files where the only "webhook"-matching node was a Respond to
Webhook action with no real trigger webhook in the same file, each also
carrying an unrelated detected side effect. The "...z auth na webhooku"
NUMERATOR is unaffected (17 either way, confirmed) — none of those 8 files
could have contributed to it, since a Respond to Webhook node has no
`authentication` parameter to read in the first place. So the fix moves
that ratio from 17/221 (7.7%) to 17/213 (8.0%): a small, fully explained
correction, not a new unresolved discrepancy.

Separately, `idempotency_within_webhook_and_side_effect` will NOT
numerically match the prototype's reported 12/221: this module's
`idempotency_candidate` (idempotency.py) carries more signals than the
prototype's narrower `idempotency()` (it also flags a conditional node
positioned before a known write-capable node type — see
`_has_conditional_before_write`). That was already true before this
reconciliation and is left as-is: Tier C is a candidate signal, not a
metric that needs to reproduce the prototype exactly, and the reasons for
the wider net are documented in idempotency.py.
"""

from __future__ import annotations

import json

from ..sticky_notes import executable_nodes
from .base import NOT_APPLICABLE, Detector, Tier, register
from .idempotency import idempotency_candidate
from .throttling import throttling_node_present

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
SEND_TYPE_SUBSTRINGS = ("gmail", "slack", "discord", "telegram", "emailSend", "twilio", "whatsApp", "mattermost")
DB_WRITE_TYPE_SUBSTRINGS = (
    "postgres", "mySql", "mongoDb", "supabase", "airtable",
    "googleSheets", "notion", "baserow", "mssql", "redis",
)
DB_WRITE_OPERATIONS = {"", "insert", "update", "upsert", "create", "append", "appendorupdate", "write", "set"}


def _webhook_trigger_nodes(workflow: dict) -> list[dict]:
    """Single, shared implementation of the "webhook trigger" match — see
    webhook_trigger_present's docstring for why "respond" (not the
    prototype's non-matching "response") is excluded. Used by both
    webhook_trigger_present and webhook_auth_within_webhook_and_side_effect
    so the two can never silently drift apart the way the prototype's own
    two independent copies of this check did not (only one of surface.py's
    two webhook filters would have needed the fix, since it only wrote it
    once — but the risk of a second, forked copy diverging is exactly why
    this package keeps a single implementation)."""
    return [
        n for n in executable_nodes(workflow)
        if "webhook" in str(n.get("type", "")).lower() and "respond" not in str(n.get("type", "")).lower()
    ]


def webhook_trigger_present(workflow: dict) -> bool:
    """Broader than webhook_auth.webhook_present: substring match on
    `type` ("webhook" present, "respond" absent — excludes Respond to
    Webhook), not an exact type equality. Kept distinct and separately
    documented rather than replacing the exact-match detector. See module
    docstring for why the exclusion checks "respond", not the prototype's
    original (non-matching) "response".
    """
    return len(_webhook_trigger_nodes(workflow)) > 0


def external_http_present(workflow: dict) -> bool:
    return any("httpRequest" in str(n.get("type", "")) for n in executable_nodes(workflow))


def http_write_present(workflow: dict) -> bool:
    for n in executable_nodes(workflow):
        t = str(n.get("type", ""))
        if "httpRequest" not in t:
            continue
        method = str((n.get("parameters") or {}).get("method", "GET")).upper()
        if method in WRITE_METHODS:
            return True
    return False


def send_node_present(workflow: dict) -> bool:
    for n in executable_nodes(workflow):
        t = str(n.get("type", "")).lower()
        if any(s.lower() in t for s in SEND_TYPE_SUBSTRINGS):
            return True
    return False


def db_write_present(workflow: dict) -> bool:
    for n in executable_nodes(workflow):
        t = str(n.get("type", "")).lower()
        if not any(d.lower() in t for d in DB_WRITE_TYPE_SUBSTRINGS):
            continue
        op = str((n.get("parameters") or {}).get("operation", "")).lower()
        if op in DB_WRITE_OPERATIONS:
            return True
    return False


def has_side_effect(workflow: dict) -> bool:
    """Composite: an HTTP write, a message/notification-send node, or a
    database write-type operation. Deterministic OR of anchored field
    checks — Tier B, not Tier C, despite aggregating several signal
    families: none of the components require interpreting intent."""
    return http_write_present(workflow) or send_node_present(workflow) or db_write_present(workflow)


def idempotency_within_webhook_and_side_effect(workflow: dict):
    """NOT_APPLICABLE unless the workflow has both a webhook trigger and a
    detected side effect. Where applicable, delegates to the Tier-C
    idempotency_candidate — this detector's own tier follows that
    candidate's, i.e. still Tier C, still not a validated metric."""
    if not (webhook_trigger_present(workflow) and has_side_effect(workflow)):
        return NOT_APPLICABLE
    return idempotency_candidate(workflow)


def webhook_auth_within_webhook_and_side_effect(workflow: dict):
    """NOT_APPLICABLE unless the workflow has both a webhook trigger and a
    detected side effect. Where applicable: does at least one such webhook
    node have authentication configured (the inverse framing of
    webhook_auth.webhook_missing_auth, matching the prototype's own
    "...z auth na webhooku" wording)."""
    if not (webhook_trigger_present(workflow) and has_side_effect(workflow)):
        return NOT_APPLICABLE
    webhooks = _webhook_trigger_nodes(workflow)
    return any(
        str((n.get("parameters") or {}).get("authentication", "none")).lower() not in ("none", "")
        for n in webhooks
    )


def throttling_within_external_http(workflow: dict):
    """NOT_APPLICABLE unless the workflow calls out to an external HTTP
    endpoint. Where applicable, delegates to the existing Tier-B
    throttling_node_present."""
    if not external_http_present(workflow):
        return NOT_APPLICABLE
    return throttling_node_present(workflow)


def retry_after_mentioned(workflow: dict) -> bool:
    """Free-text heuristic (Tier C): the string "retry-after" inside a
    non-sticky node's own parameters. Scoped per-node (not the whole
    workflow blob) for the same reason as idempotency_keyword_present."""
    return any(
        "retry-after" in json.dumps(n.get("parameters") or {}).lower()
        for n in executable_nodes(workflow)
    )


DETECTOR_VERSION = "1.0.0"

register(
    Detector(
        key="webhook_trigger_present",
        tier=Tier.B_STRUCTURAL,
        version=DETECTOR_VERSION,
        summary="Node z 'webhook' w type (poza Respond to Webhook) — dopasowanie szersze niż webhook_present",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=webhook_trigger_present,
        notes="Dopasowanie przez podciąg w polu type, nie dokładna równość — patrz webhook_auth.webhook_present dla wersji dokładnej.",
    )
)

register(
    Detector(
        key="external_http_present",
        tier=Tier.B_STRUCTURAL,
        version=DETECTOR_VERSION,
        summary="Node z 'httpRequest' w type",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=external_http_present,
    )
)

register(
    Detector(
        key="has_side_effect",
        tier=Tier.B_STRUCTURAL,
        version=DETECTOR_VERSION,
        summary="Kompozyt: HTTP write, node typu 'send', lub zapis do bazy danych",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=has_side_effect,
        notes="Listy typów/operacji skopiowane z odzyskanego prototypu (prototype/surface.py) verbatim.",
    )
)

register(
    Detector(
        key="idempotency_within_webhook_and_side_effect",
        tier=Tier.C_SEMANTIC,
        version=DETECTOR_VERSION,
        summary="KANDYDAT — idempotencja, WŚRÓD workflow z webhookiem I efektem ubocznym",
        denominator_definition=(
            "TYLKO pliki workflow z webhook_trigger_present ORAZ has_side_effect "
            "(pozostałe NOT_APPLICABLE) — UWAGA: to nie jest zwalidowana metryka."
        ),
        fn=idempotency_within_webhook_and_side_effect,
    )
)

register(
    Detector(
        key="webhook_auth_within_webhook_and_side_effect",
        tier=Tier.B_STRUCTURAL,
        version=DETECTOR_VERSION,
        summary="Webhook MA uwierzytelnienie, WŚRÓD workflow z webhookiem I efektem ubocznym",
        denominator_definition=(
            "TYLKO pliki workflow z webhook_trigger_present ORAZ has_side_effect "
            "(pozostałe NOT_APPLICABLE)"
        ),
        fn=webhook_auth_within_webhook_and_side_effect,
        notes="Odwrotne ujęcie webhook_auth.webhook_missing_auth, na węższym mianowniku — patrz docstring modułu.",
    )
)

register(
    Detector(
        key="throttling_within_external_http",
        tier=Tier.B_STRUCTURAL,
        version=DETECTOR_VERSION,
        summary="Throttling/batching, WŚRÓD workflow z zewnętrznym wywołaniem HTTP",
        denominator_definition="TYLKO pliki workflow z external_http_present (pozostałe NOT_APPLICABLE)",
        fn=throttling_within_external_http,
    )
)

register(
    Detector(
        key="retry_after_mentioned",
        tier=Tier.C_SEMANTIC,
        version="0.1.0-candidate",
        summary="KANDYDAT — 'retry-after' w parametrach node'a (nie w sticky note)",
        denominator_definition=(
            "wszystkie pliki workflow w korpusie — UWAGA: to nie jest zwalidowana metryka."
        ),
        fn=retry_after_mentioned,
    )
)
