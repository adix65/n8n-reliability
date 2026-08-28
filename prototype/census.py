import json, hashlib, os, glob
from collections import Counter, defaultdict

files = sorted(glob.glob("n8n-workflows/workflows/**/*.json", recursive=True))
ok, bad = [], []
for f in files:
    try:
        with open(f, encoding="utf-8") as fh: ok.append((f, json.load(fh)))
    except Exception as e: bad.append((f, str(e)[:60]))

print(f"plikow: {len(files)} | sparsowanych: {len(ok)} | bledne: {len(bad)}")

def nodes(w): return w.get("nodes") or []

# --- mechanizmy error handling, KAZDY OSOBNO ---
m = Counter()
node_total = 0
node_retry = 0
for f, w in ok:
    ns = nodes(w); node_total += len(ns)
    settings = w.get("settings") or {}
    types = [str(n.get("type","")) for n in ns]
    has_errwf = bool(settings.get("errorWorkflow"))
    has_errtrig = any("errorTrigger" in t for t in types)
    has_stoperr = any("stopAndError" in t for t in types)
    n_retry = sum(1 for n in ns if n.get("retryOnFail") is True)
    n_onerr = sum(1 for n in ns if n.get("onError") and n.get("onError") != "stopWorkflow")
    n_always = sum(1 for n in ns if n.get("alwaysOutputData") is True)
    node_retry += n_retry
    if has_errwf: m["settings.errorWorkflow"] += 1
    if has_errtrig: m["Error Trigger node"] += 1
    if has_stoperr: m["Stop and Error node"] += 1
    if n_retry: m["≥1 node z retryOnFail"] += 1
    if n_onerr: m["≥1 node z onError (continue)"] += 1
    if n_always: m["≥1 node z alwaysOutputData"] += 1
    if any([has_errwf, has_errtrig, has_stoperr, n_retry, n_onerr]):
        m["JAKIKOLWIEK z powyzszych (bez alwaysOutputData)"] += 1

N = len(ok)
print(f"\n=== MECHANIZMY ERROR HANDLING (mianownik = {N} workflow) ===")
for k, v in m.most_common():
    print(f"{v:5d}  {100*v/N:5.1f}%  {k}")
print(f"\nnodow lacznie: {node_total} | z retryOnFail: {node_retry} ({100*node_retry/node_total:.2f}%)")
