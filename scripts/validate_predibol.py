#!/usr/bin/env python3
"""Validate core PrediBol files before deployment."""
import json, re, sys, subprocess, tempfile
from pathlib import Path

root=Path(".")
errors=[]
def fail(msg): errors.append(msg)
def load_json(path):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"{path}: invalid JSON: {e}"); return None

bank=load_json(root/"preguntas_extra.json")
if isinstance(bank,list):
    ids=set()
    for i,q in enumerate(bank,1):
        if not isinstance(q,dict): fail(f"question {i}: not an object"); continue
        for key in ("id","cat","level","q","exp"):
            if not isinstance(q.get(key),str) or not q[key].strip(): fail(f"question {i}: missing/blank {key}")
        opts=q.get("opts")
        if not isinstance(opts,list) or len(opts)<2 or not all(isinstance(o,str) and o.strip() for o in opts):
            fail(f"question {i}: options invalid")
        elif len(set(opts))!=len(opts): fail(f"question {i}: duplicate options")
        a=q.get("a")
        if not isinstance(a,int) or isinstance(a,bool) or not isinstance(opts,list) or a<0 or a>=len(opts):
            fail(f"question {i}: answer index invalid")
        if q.get("id") in ids: fail(f"question {i}: duplicate id {q.get('id')}")
        ids.add(q.get("id"))
    print(f"Supplemental trivia bank: {len(bank)} questions checked")
html=root/"index.html"
if not html.exists(): fail("index.html missing")
else:
    src=html.read_text(encoding="utf-8")
    if "manifest.webmanifest" not in src: fail("manifest link missing")
    if "preguntas_extra.json" not in src: fail("supplemental trivia fetch missing")
    if "loadExtraQuestions();" not in src: fail("supplemental bank loader call missing")
    if "newQuiz()" not in src: fail("quiz function missing")
manifest=load_json(root/"manifest.webmanifest")
if manifest and not manifest.get("name"): fail("manifest name missing")
sw=root/"sw.js"
if not sw.exists(): fail("sw.js missing")
else:
    swsrc=sw.read_text(encoding="utf-8")
    if "predibol-v" not in swsrc: fail("service worker cache version missing")
    if "preguntas_extra.json" not in swsrc: fail("service worker bank cache missing")
for p in ("assets/icon.svg","noticias.json"):
    if not (root/p).exists(): fail(f"{p} missing")
# Check inline JavaScript syntax with Node's parser; this does not execute the app.
if html.exists():
    scripts=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html.read_text(encoding="utf-8"), re.S|re.I)
    for n,code in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as f:
            f.write(code); temp=f.name
        result=subprocess.run(["node","--check",temp],capture_output=True,text=True)
        Path(temp).unlink(missing_ok=True)
        if result.returncode: fail(f"inline script {n} syntax error: {result.stderr.strip()}")
if errors:
    print("VALIDATION FAILED:")
    for e in errors: print(" - "+e)
    sys.exit(1)
print("Core files and links validated successfully.")
