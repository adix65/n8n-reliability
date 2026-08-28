"""Tier A: integrity of the `connections` graph itself.

Discovered while building dedupe.py's structural signature and while
debugging why `detectors.validation.validation_candidate` returned 0/2061:
on this corpus (Zie619/n8n-workflows @ 94007c1445d92), the `connections`
object's edge targets (`connections[X]["main"][i][j]["node"]`) essentially
never resolve to a real node `name` or `id` in the same file.

Measured directly against the pinned corpus:
  - 1367/2061 files have a non-empty `connections` object at all.
  - Across those, out of 27,544 individual connection-target references,
    only 19 resolve to a real node name, 0 resolve to a real node id, and
    27,525 (99.93% of all targets, in 1363/2061 files) follow the exact
    pattern `error-handler-<uuid>[-<8 hex chars>]` — a string that matches
    no node in the file.

This package does not know why (curation-tool artifact when this corpus was
assembled, an n8n export quirk around per-node error-output branches, or
something else) — that is an open question, not something to guess at.
What is established is the fact itself: for the overwhelming majority of
files with any connections, **the graph topology in this export cannot be
trusted to describe how nodes actually connect.**

Consequence for this package: dedupe.py's family signature is node-type
MULTISET only (see its docstring) — an edge-based component would have
added no real signal, since it could not have resolved above 4/1367 files.
`detectors.validation.validation_candidate`, which needs real topology to
judge "does this conditional sit right after the entry point", is reliably
unusable on this corpus for that reason and its 0/2061 result should be
read as "this signal is absent from the export", not "no workflow does
this".

CORRUPTION PROVENANCE (established from the full git history of the source
repository, not from static analysis of the pinned commit alone — every
claim below was independently re-verified against that history, not taken
on faith):

Commit `5ffee225b7c9e314cacefd7f0a46a1c10ae3d20e`, authored by `zie619`
(the repository owner) on 2025-11-03, titled "Fix: Comprehensive resolution
of 18 issues including critical security fixes", co-authored by Claude
(`noreply@anthropic.com`). Its message claims, verbatim (confirmed with
`git show`): "Fixed all 2,057 workflows by removing 11,855 orphaned
nodes..." and "Restored connection definitions to enable n8n import", and
lists "Created fix_workflow_connections.py for ongoing maintenance".

`fix_workflow_connections.py`, present at that commit (read, never
executed by this package), does remove orphaned nodes whose `id` starts
with `error-handler-`/`documentation-`/`doc-` and prune the corresponding
`connections` entries — but its orphan/connection logic keys everything by
node `name` (`node['name']`), while most files in this corpus key
`connections` by node `id`, not `name` (see the resolvable-by-name-only
count above: 19). That mismatch is a plausible, but not independently
proven, mechanism for why the fix did not do what its commit message
claims — offered here as an observation, not a confirmed root cause.

Direct, file-level verification (`git show <rev>:<path>` at three points)
of `workflows/Mongodbtool/0511_Mongodbtool_Stickynote_Automation_Triggered.json`:
BEFORE this commit, a node with id
`error-handler-d8c07efe-eca0-48cb-80e6-ea8117073c5f-b87d9f57` (name "Error
Handler for d8c07efe") existed, and the `connections` reference to it
resolved. AT this commit, that node is gone from the node list — replaced
by a different node (id `error-274539ee`, name "Error Handler") — but the
`connections` entry was NOT updated: it still points at the now-nonexistent
old id. That exact file is byte-identical between this commit and the
pinned corpus HEAD (`git diff` empty) — the break was never fixed
afterward.

Ancestry (`git merge-base --is-ancestor`, confirmed true): PINNED_COMMIT_SHA
(`94007c1445d9258a7da116646b79473e7c7c3282`) is a descendant of
`5ffee225`. There are 57 commits in total between them in the repository's
history — more than a first pass assumed — but only TWO of those 57 touch
any file under `workflows/*.json` at all: the merge of PR #144
(`criptolandiatv/claude/medcards-ai-rebuild-...`) and "feat: Add new n8n
workflow templates (#3)". Both are pure additions of 3-4 new template
files (ids 9001-9004) with zero deletions or modifications to any existing
workflow file (`git show --stat` for both shows insertions only). None of
the other 55 commits (CI/CD, documentation, GitHub Pages, the unrelated
medcards-ai product, the ai-stack/ComfyUI addition) touches `workflows/`
at all. In other words: the corruption introduced at `5ffee225` was
neither fixed nor measurably deepened by anything between it and the
pinned commit this package analyzes.

Citable directly from the source repository's public history at:
https://github.com/Zie619/n8n-workflows/commit/5ffee225b7c9e314cacefd7f0a46a1c10ae3d20e
"""

from __future__ import annotations

import re

from .base import NOT_APPLICABLE, Detector, Tier, register

ERROR_HANDLER_TARGET_RE = re.compile(r"^error-handler-")

DETECTOR_VERSION = "1.0.0"


def _all_targets(workflow: dict) -> list[str]:
    out = []
    for outputs in (workflow.get("connections") or {}).values():
        for branches in (outputs or {}).values():
            for branch in branches or []:
                for target in branch or []:
                    node_ref = target.get("node")
                    if node_ref is not None:
                        out.append(node_ref)
    return out


def corruption_commit_citation() -> dict:
    """Not a detector — a citable record of the corruption provenance
    established in the module docstring above, for use in
    versioned_manifest.json and directly in the article. Every field was
    independently verified against the source repository's git history
    (see docstring), not copied on trust.
    """
    return {
        "commit_sha": "5ffee225b7c9e314cacefd7f0a46a1c10ae3d20e",
        "commit_url": "https://github.com/Zie619/n8n-workflows/commit/5ffee225b7c9e314cacefd7f0a46a1c10ae3d20e",
        "author": "zie619",
        "date": "2025-11-03",
        "claimed_fix": "Restored connection definitions to enable n8n import",
        "verified_still_broken_on_pinned_commit": True,
        "pinned_commit_is_descendant": True,
    }


def connections_present(workflow: dict) -> bool:
    return bool(workflow.get("connections"))


def connections_have_unresolvable_targets(workflow: dict):
    """NOT_APPLICABLE if there are no connections at all. Otherwise True if
    at least one connection target does not resolve to any node's `name`
    or `id` in this file."""
    targets = _all_targets(workflow)
    if not targets:
        return NOT_APPLICABLE
    node_names = {n.get("name") for n in workflow.get("nodes", [])}
    node_ids = {n.get("id") for n in workflow.get("nodes", [])}
    return any(t not in node_names and t not in node_ids for t in targets)


def unresolvable_targets_match_error_handler_pattern(workflow: dict):
    """NOT_APPLICABLE if there are no connections. Otherwise True if every
    unresolvable target follows the `error-handler-<uuid>` pattern observed
    corpus-wide (as opposed to some other, unexplained form of breakage)."""
    targets = _all_targets(workflow)
    if not targets:
        return NOT_APPLICABLE
    node_names = {n.get("name") for n in workflow.get("nodes", [])}
    node_ids = {n.get("id") for n in workflow.get("nodes", [])}
    unresolved = [t for t in targets if t not in node_names and t not in node_ids]
    if not unresolved:
        return NOT_APPLICABLE
    return all(ERROR_HANDLER_TARGET_RE.match(t) for t in unresolved)


register(
    Detector(
        key="connections_present",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="Workflow ma niepusty obiekt connections",
        denominator_definition="wszystkie pliki workflow w korpusie",
        fn=connections_present,
    )
)

register(
    Detector(
        key="connections_have_unresolvable_targets",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="connections zawiera referencję do node'a, który nie istnieje w pliku",
        denominator_definition=(
            "TYLKO pliki z niepustym connections (pozostałe NOT_APPLICABLE)"
        ),
        fn=connections_have_unresolvable_targets,
        notes=(
            "Kluczowe znalezisko o jakości korpusu — patrz docstring modułu. "
            "99,93% referencji celu w connections tego korpusu nie rozwiązuje się "
            "do żadnego realnego node'a."
        ),
    )
)

register(
    Detector(
        key="unresolvable_targets_match_error_handler_pattern",
        tier=Tier.A_DETERMINISTIC,
        version=DETECTOR_VERSION,
        summary="Nierozwiązywalne cele connections pasują do wzorca 'error-handler-<uuid>'",
        denominator_definition=(
            "TYLKO pliki z co najmniej jedną nierozwiązywalną referencją w connections "
            "(pozostałe NOT_APPLICABLE)"
        ),
        fn=unresolvable_targets_match_error_handler_pattern,
    )
)
