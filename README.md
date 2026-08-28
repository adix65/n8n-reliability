# n8n-reliability

Static reliability analysis of publicly available n8n workflow exports — no
runtime experiments, no crawling, only what is already downloadable. See
`n8n_reliability/` for the detector package (`fetch_corpus.py`,
`detectors/`, `dedupe.py`, `analyze.py`) and `research/` for the underlying
article research.

## Corpus provenance

The primary corpus this package analyzes, [Zie619/n8n-workflows](https://github.com/Zie619/n8n-workflows)
(MIT), has a documented data-quality defect: 99.93% of its `connections`
field's target references point to nodes that no longer exist, following
an `error-handler-<uuid>` pattern. We traced this to a specific commit in
the source repository's history — [`5ffee225`](https://github.com/Zie619/n8n-workflows/commit/5ffee225b7c9e314cacefd7f0a46a1c10ae3d20e)
(2025-11-03), whose message claims to have "restored connection
definitions to enable n8n import" but, verified directly against the file
history, did not fix the reference it was supposed to fix — and the break
was never repaired afterward. Full detail, including how each claim above
was independently re-verified rather than taken on trust, is in
`n8n_reliability/detectors/connections_integrity.py`. Because of this, any
statistic derived from this corpus's workflow *topology* (as opposed to
per-node fields) should be treated as unreliable; this package also
analyzes a second, independently-licensed corpus
([enescingoz/awesome-n8n-templates](https://github.com/enescingoz/awesome-n8n-templates),
CC BY 4.0) to cross-check which findings hold up outside the primary
corpus's defect.