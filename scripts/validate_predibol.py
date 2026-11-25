#!/usr/bin/env python3
"""Validate core PrediBol files before deployment."""
import json, re, sys, subprocess, tempfile
from pathlib import Path

root=Path(".")
errors=[]
def fail(msg): errors.append(msg)
def load_json(file_path):
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"{file_path}: invalid JSON: {e}")
        return None

bank=load_json(root/"preguntas_extra.json")
if not isinstance(bank,list):
    fail("preguntas_extra.json: expected a JSON array")
else:
    ids=set()
    for i,q in enumerate(bank,1):
        if not isinstance(q,dict):
            fail(f"question {i}: not an object"); continue
        for key in ("id","cat","level","q","exp"):
            if not isinstance(q.get(key),str) or not q[key].strip():
                fail(f"question {i}: missing/blank {key")
        opts=q.get("opts")
        if not isinstance(opts,list) or len(opts)<2 or not all(isinstance(o,str) and o.strip() for o in opts):
            fail(f"question {i}: options invalid")
        elif len(set(opts))!=len(opts):
            fail(f"question {i}: duplicate options")
        a=q.get("a")
        if not isinstance(a,int) or isinstance(a,bool) or not isinstance(opts,list) or a<0 or a>=len(opts):
            fail(f"question {i}: answer index invalid")
        qid=q.get("id")
        if qid in ids: fail(f"question {i}: duplicate id {qid}")
        ids.add(qid)
    print(f"Supplemental trivia bank: {len(bank)} questions checked")

html=root/"index.html"
if not html.exists(): fail("index.html missing")
else:
    src=html.read_text(encoding="utf-8")
    for needle,label in (("manifest.webmanifest","manifest link"),("preguntas_extra.json","supplemental trivia fetch"),("loadExtraQuestions();","supplemental bank loader call"),("newQuiz()","quiz function")):
        if needle not in src: fail(f"{label} missing")
manifest=load_json(root/"manifest.webmanifest")
if manifest:
    for key in ("name","short_name","start_url","display","icons"):
        if not manifest.get(key): fail(f"manifest: missing {key}")
    if manifest.get("display") not in ("standalone","fullscreen","minimal-ui"):
        fail("manifest: display mode should support app-like install")
news=load_json(root/"noticias.json")
if news is not None:
    if not isinstance(news,dict): fail("noticias.json: expected an object")
    else:
        if not isinstance(news.get("items"),list): fail("noticias.json: items should be an array")
        for i,item in enumerate(news.get("items",[]),1):
            if not isinstance(item,dict): fail(f"news item {i}: expected object"); continue
            for key in ("title","url","source","category"):
                if not isinstance(item.get(key),str) or not item[key].strip():
                    fail(f"news item {i}: missing/blank {key")
            if item.get("url","").strip() and not item["url"].startswith(("https://","http://")):
                fail(f"news item {i}: url must be HTTP(S)")
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
    scripts=re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>", html.read_text(encoding="utf-8"), re.S|re.I)
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
