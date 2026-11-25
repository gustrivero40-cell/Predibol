#!/usr/bin/env python3
"""Fetch a small, attributed RSS news digest for PrediBol."""
import json, re, html, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

FEEDS = [
    ("Bolivia", "EL DEBER", "https://eldeber.com.bo/feed"),
    ("Mundo", "BBC Mundo", "https://feeds.bbci.co.uk/mundo/rss.xml"),
]
SPORTS_WORDS = re.compile(r"\b(fútbol|futbol|deporte|deportes|liga|selección|seleccion|mundial|copa|gol|partido|tenis|básquet|basquet|olimpi|bolívar|bolivar|strongest|tigres|real madrid|barcelona)\b", re.I)

def text(node, names):
    for name in names:
        el = node.find(name)
        if el is not None and el.text:
            return html.unescape(re.sub(r"<[^>]+>", "", el.text)).strip()
    return ""

def main():
    items, seen = [], set()
    for section, source, url in FEEDS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"PrediBolNewsBot/1.0 (RSS reader)"})
            with urllib.request.urlopen(req, timeout=20) as response:
                root = ET.fromstring(response.read())
            for entry in root.findall(".//item")[:30]:
                title = text(entry, ["title"])
                link = text(entry, ["link"])
                desc = text(entry, ["description"])
                date = text(entry, ["pubDate"])
                if not title or not link or link in seen: continue
                seen.add(link)
                cat = "Deportes" if SPORTS_WORDS.search(title) else section
                items.append({"category":cat,"source":source,"title":title[:220],"summary":desc[:380],"url":link,"published":date})
        except Exception as e:
            print(f"Feed error {source}: {e}")
    items.sort(key=lambda x:x.get("published",""), reverse=True)
    out={"updated":datetime.now(timezone.utc).isoformat(),"items":items[:60]}
    Path("noticias.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Saved {len(out['items'])} news items")
if __name__=="__main__":
    main()
