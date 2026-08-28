import json, hashlib, glob
from collections import Counter, defaultdict

def graph_hash(w):
    ns = w.get("nodes") or []
    # kanoniczny: posortowane (typ, typeVersion) + znormalizowane polaczenia po TYPACH
    name2type = {n.get("name"): str(n.get("type","")) for n in ns}
    sig = sorted(f"{n.get('type','')}@{n.get('typeVersion','')}" for n in ns)
    edges = []
    for src, outs in (w.get("connections") or {}).items():
        st = name2type.get(src, "?")
        for _, conns in (outs.items() if isinstance(outs, dict) else []):
            for grp in (conns or []):
                for c in (grp or []):
                    edges.append(f"{st}->{name2type.get(c.get('node'),'?')}")
    blob = "|".join(sig) + "||" + "|".join(sorted(edges))
    return hashlib.sha256(blob.encode()).hexdigest()[:16]

fams = defaultdict(list); content = Counter()
for f in sorted(glob.glob("n8n-workflows/workflows/**/*.json", recursive=True)):
    raw = open(f,'rb').read()
    content[hashlib.md5(raw).hexdigest()] += 1
    fams[graph_hash(json.load(open(f,encoding="utf-8")))].append(f)

N = sum(len(v) for v in fams.values())
uniq = len(fams)
print(f"plikow: {N}")
print(f"duplikaty bajt-w-bajt: {sum(v-1 for v in content.values() if v>1)}")
print(f"unikalnych rodzin (hash grafu): {uniq}")
print(f"REDUKCJA: {100*(1-uniq/N):.1f}%  |  wspolczynnik napompowania: {N/uniq:.2f}x")
print("\n=== 10 najliczniejszych rodzin ===")
for h, fs in sorted(fams.items(), key=lambda x:-len(x[1]))[:10]:
    print(f"{len(fs):4d}x  {h}  np. {fs[0].split('/')[-1][:60]}")
