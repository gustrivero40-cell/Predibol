#!/usr/bin/env python3
"""Offline tests for PrediBol RSS/Atom normalization and news file safety."""
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_news

class NewsParserTests(unittest.TestCase):
    def test_rss_fields_and_html_cleaning(self):
        item = ET.fromstring("""<item><title>Bolivia gana el partido</title>
        <link>https://example.test/story</link>
        <description>&lt;b&gt;Resumen&lt;/b&gt; &amp; detalles</description>
        <pubDate>2026-11-25</pubDate></item>""")
        self.assertEqual(update_news.entry_fields(item), (
            "Bolivia gana el partido", "https://example.test/story",
            "Resumen & detalles", "2026-11-25"))

    def test_atom_fields(self):
        entry = ET.fromstring("""<entry xmlns="http://www.w3.org/2005/Atom">
        <title>Noticia</title><link href="https://example.test/a"/>
        <summary>Breve</summary><updated>2026-11-25T10:00:00Z</updated></entry>""")
        self.assertEqual(update_news.entry_fields(entry, atom=True), (
            "Noticia", "https://example.test/a", "Breve", "2026-11-25T10:00:00Z"))

    def test_nested_atom_summary_text(self):
        entry = ET.fromstring('''<entry xmlns="http://www.w3.org/2005/Atom"><summary><b>Texto</b> adicional</summary></entry>''')
        self.assertEqual(update_news.child_text(entry, {"summary"}), "Texto adicional")

    def test_sports_category(self):
        self.assertIsNotNone(update_news.SPORTS_WORDS.search("El fútbol boliviano"))
        self.assertIsNone(update_news.SPORTS_WORDS.search("La economía crece"))

    def test_main_writes_valid_news_feed(self):
        rss = b"""<rss><channel><item><title>Futbol: Bolivia vence</title><link>https://example.test/bolivia</link><description>Resumen</description><pubDate>2026-11-25</pubDate></item></channel></rss>"""
        with TemporaryDirectory() as temp:
            with patch("update_news.FEEDS", [("Bolivia","TestFeed","https://example.test/rss")]), \
                 patch("update_news.urllib.request.urlopen", return_value=BytesIO(rss)), \
                 patch("update_news.Path", Path):
                import os
                old = os.getcwd()
                try:
                    os.chdir(temp)
                    update_news.main()
                    import json
                    result=json.loads(Path("noticias.json").read_text(encoding="utf-8"))
                    self.assertEqual(len(result["items"]),1)
                    self.assertEqual(result["items"][0]["category"],"Deportes")
                    self.assertEqual(result["items"][0]["url"],"https://example.test/bolivia")
                    self.assertTrue(result["updated"])
                finally:
                    os.chdir(old)

    def test_main_keeps_existing_file_if_feeds_fail(self):
        with TemporaryDirectory() as temp:
            with patch("update_news.FEEDS", [("Bolivia","TestFeed","https://example.test/rss")]), \
                 patch("update_news.urllib.request.urlopen", side_effect=URLError("offline")):
                import os
                old = os.getcwd()
                try:
                    os.chdir(temp)
                    original='{"updated":"old","items":[{"title":"old"}]}\\n'
                    Path("noticias.json").write_text(original, encoding="utf-8")
                    update_news.main()
                    self.assertEqual(Path("noticias.json").read_text(encoding="utf-8"), original)
                finally:
                    os.chdir(old)

if __name__ == "__main__":
    unittest.main()
