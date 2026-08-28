import json, glob, re
from collections import Counter

WRITE_METHODS = {"POST","PUT","PATCH","DELETE"}
SEND = ("gmail","slack","discord","telegram","emailSend","twilio","whatsApp","mattermost")
DB_WRITE = ("postgres","mySql","mongoDb","supabase","airtable","googleSheets","notion","baserow","mssql","redis")

def has_side_effect(ns):
    ev=[]
    for n in ns:
        t=str(n.get("type","")); p=n.get("parameters") or {}
        if "httpRequest" in t and str(p.get("method","GET")).upper() in WRITE_METHODS: ev.append("http_write")
        if any(s.lower() in t.lower() for s in SEND): ev.append("send")
        if any(d.lower() in t.lower() for d in DB_WRITE):
            op=str(p.get("operation","")).lower()
            if op in ("","insert","update","upsert","create","append","appendorupdate","write","set"): ev.append("db_write")
    return ev

def idempotency(w, ns):
    blob=json.dumps(w).lower(); ev=[]
    if "idempotency" in blob: ev.append("idempotency_key")
    for n in ns:
        p=json.dumps(n.get("parameters") or {}).lower()
        if "upsert" in p or "appendorupdate" in p: ev.append("upsert")
    if "removeduplicates" in blob or "n8n-nodes-base.removeduplicates" in blob: ev.append("dedupe_node")
    return ev

def throttle(w, ns):
    ev=[]
    types=[str(n.get("type","")) for n in ns]
    if any("wait" in t.lower() for t in types): ev.append("wait_node")
    if any("splitInBatches" in t for t in types): ev.append("batching")
    if "retry-after" in json.dumps(w).lower(): ev.append("retry_after")
    return ev

c=Counter(); rows=0
for f in glob.glob("n8n-workflows/workflows/**/*.json", recursive=True):
    w=json.load(open(f,encoding="utf-8")); ns=w.get("nodes") or []; rows+=1
    types=[str(n.get("type","")) for n in ns]
    wh=[n for n in ns if "webhook" in str(n.get("type","")).lower() and "response" not in str(n.get("type","")).lower()]
    se=has_side_effect(ns)
    ext_http=any("httpRequest" in t for t in types)
    if wh: c["webhook_trigger"]+=1
    if se: c["side_effect"]+=1
    if wh and se:
        c["MIANOWNIK: webhook + side effect"]+=1
        if idempotency(w,ns): c["  ...z jakimkolwiek wzorcem idempotencji"]+=1
        if any(str((n.get("parameters") or {}).get("authentication","none")).lower() not in ("none","") for n in wh):
            c["  ...z auth na webhooku"]+=1
    if ext_http:
        c["MIANOWNIK: zewnetrzne HTTP"]+=1
        if throttle(w,ns): c["  ...z jawnym throttlingiem/batchingiem"]+=1

print(f"workflow: {rows}\n")
for k,v in c.items(): print(f"{v:5d}  {100*v/rows:5.1f}% (calego korpusu)  {k}")
d=c["MIANOWNIK: webhook + side effect"]; h=c["MIANOWNIK: zewnetrzne HTTP"]
print(f"\n>>> WARUNKOWO, mianownik {d} (webhook+side effect):")
print(f"    idempotencja: {c['  ...z jakimkolwiek wzorcem idempotencji']}/{d} = {100*c['  ...z jakimkolwiek wzorcem idempotencji']/d:.1f}%")
print(f"    auth webhooka: {c['  ...z auth na webhooku']}/{d} = {100*c['  ...z auth na webhooku']/d:.1f}%")
print(f">>> WARUNKOWO, mianownik {h} (zewnetrzne HTTP):")
print(f"    throttling: {c['  ...z jawnym throttlingiem/batchingiem']}/{h} = {100*c['  ...z jawnym throttlingiem/batchingiem']/h:.1f}%")
