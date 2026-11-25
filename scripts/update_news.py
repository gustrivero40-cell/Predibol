#!/usr/bin/env python3
"""Fetch and normalize a small, attributed RSS/Atom news digest for PrediBol."""
import json, re, html, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

FEEDS = [
    ("Bolivia", "EL DEBER", "https://eldeber.com.bo/feed"),
    ("Mundo", "BBC Mundo", "https://feeds.bbci.co.uk/mundo/rss.xml"),
]
SPORTS_WORDS = re.compile(r"\b(fútbol|futbol|deporte|deportes|liga|selección|seleccion|mundial|copa|gol|partido|tenis|básquet|basquet|olimpi|bolívar|bolivar|strongest|tigres|real madrid|barcelona)\b", re.I)
TAG_RE = re.compile(r"<[^>]+>")

def clean(value):
    return html.unescape(TAG_RE.sub("", value or "")).strip()

def child_text(node, wanted):
    for child in list(node):
        tag = child.tag.rsplit("}", 1)[-1].lower()
        if tag in wanted:
            # ElementTree's .text may only contain the first fragment of XHTML.
            raw = "".join(child.itertext())
            if raw:
                return clean(raw)
    return ""

def entry_fields(entry, atom=False):
    title = child_text(entry, {"title"})
    if atom:
        link = next((c.attrib.get("href", "") for c in list(entry)
                     if c.tag.rsplit("}", 1)[-1].lower() == "link"
                     and c.attrib.get("rel", "alternate") == "alternate"), "")
        summary = child_text(entry, {"summary", "content"})
        date = child_text(entry, {"published", "updated"})
    else:
        link = child_text(entry, {"link"})
        summary = child_text(entry, {"description", "summary"})
        date = child_text(entry, {"pubdate", "date"})
    return title, link, summary, date

def main():
    items, seen = [], set()
    successful_feeds = 0
    for section, source, url in FEEDS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"PrediBolNewsBot/1.1"})
            with urllib.request.urlopen(req, timeout=20) as response:
                root = ET.fromstring(response.read())
            atom = root.tag.rsplit("}", 1)[-1].lower() == "feed"
            entries = root.findall(".//{*}entry") if atom else root.findall(".//item")
            successful_feeds += 1
            for entry in entries[:30]:
                title, link, summary, date = entry_fields(entry, atom)
                if not title or not link or link in seen:
                    continue
                seen.add(link)
                category = "Deportes" if SPORTS_WORDS.search(title) else section
                items.append({"category":category,"source":source,"title":title[:220],
                             "summary":summary[:380],"url":link,"published":date})
            print(f"{source}: parsed {len(entries)} entries")
        except Exception as exc:
            print(f"Feed error {source}: {exc}")
    if not items:
        print(f"No usable items (successful feeds: {successful_feeds}); keeping noticias.json unchanged")
        return
    items.sort(key=lambda item:item.get("published",""), reverse=True)
    out={"updated":datetime.now(timezone.utc).isoformat(),"items":items[:60]}
    Path("noticias.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Saved {len(out['items'])} news items")

if __name__ == "__main__":
    main()
