"""Structural deduplication into "families" of near-identical workflows.

METHODOLOGY, REVISED: two workflow files are put in the same family iff,
after excluding sticky notes, they have the SAME MULTISET OF NODE TYPES.

An earlier version of this module also hashed a "connection edge" component
(source-type -> target-type pairs from `connections`), intending families
to match on graph *shape*, not just node inventory. That component was
removed after corpus inspection showed it carried no real signal on this
corpus: `detectors.connections_integrity` establishes that 27,525 of
27,544 connection-target references in this corpus (99.93%, across
1363/2061 files) follow the pattern `error-handler-<uuid>` and do not
resolve to any real node in the file — see that module's docstring for the
full finding. An edge signature built from unresolvable targets is not
"conservative", it's just noise dressed up as structure: two files with
identical topology could hash differently only because of which random,
non-resolving `error-handler-<uuid>` strings happened to appear, and this
was silently invisible before the connections_integrity finding (a
node-type-only signature produced the identical family count, 1720, as the
version that also tried to hash edges — because the edges never
contributed anything real).

This is a genuine limitation, not a stylistic choice: this package cannot
currently group workflows by connection topology on this corpus, only by
node-type inventory. Two families sharing a node-type multiset could still
differ in wiring. `validate_family_consistency` (below) is the check run
against the pinned corpus to see how much this matters in practice for the
detectors this package reports: 285/1720 families have >1 member; within
those, 0/285 disagree on `stop_and_error_present` and 2/285 disagree on
node-level `retryOnFail`. Per-family aggregation uses "any member exhibits
X" semantics and should be read as an upper bound on family-level
prevalence, not an exact one.

METHODOLOGY NOTE (unrecoverable prior prototype): this reproduces 1720
families out of 2061 files on the pinned corpus (commit 94007c1445d92). An
earlier, now-unrecoverable prototype run was cited as finding 1768
families; its exact normalization was not available to verify, so this
package reports its own, independently-derived and fully reproducible
number rather than attempting to reverse-engineer a match to the earlier
one.
"""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass

from .models import LoadedWorkflow
from .sticky_notes import executable_nodes


def structural_signature(workflow: dict) -> tuple:
    """Node-type multiset only — see module docstring for why an
    edge/connections component was removed rather than kept as
    "best effort"."""
    node_type_counts = Counter(n.get("type") for n in executable_nodes(workflow))
    return tuple(sorted(node_type_counts.items()))


def signature_hash(workflow: dict) -> str:
    return hashlib.sha1(repr(structural_signature(workflow)).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Family:
    signature_hash: str
    members: tuple[LoadedWorkflow, ...]

    @property
    def size(self) -> int:
        return len(self.members)


def group_families(workflows: list[LoadedWorkflow]) -> list[Family]:
    groups: dict[str, list[LoadedWorkflow]] = defaultdict(list)
    for wf in workflows:
        groups[signature_hash(wf.data)].append(wf)
    return [Family(signature_hash=h, members=tuple(m)) for h, m in groups.items()]


def validate_family_consistency(families: list[Family], detector_fn) -> dict:
    """For families with >1 member, count how many internally disagree on a
    given detector's output. Used to sanity-check the "any member exhibits
    X" aggregation before trusting it — see module docstring for the
    numbers this produced against detectors.error_handling.stop_and_error_present
    and detectors.retry.node_retry_on_fail.
    """
    multi = [f for f in families if f.size > 1]
    disagreements = 0
    for f in multi:
        values = {detector_fn(m.data) for m in f.members}
        if len(values) > 1:
            disagreements += 1
    return {
        "families_with_multiple_members": len(multi),
        "files_in_multi_member_families": sum(f.size for f in multi),
        "families_with_internal_disagreement": disagreements,
    }
