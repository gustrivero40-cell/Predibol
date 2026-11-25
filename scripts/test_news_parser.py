#!/usr/bin/env python3
"""Offline tests for PrediBol RSS/Atom normalization."""
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

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

    def test_sports_category(self):
        self.assertIsNotNone(update_news.SPORTS_WORDS.search("El fútbol boliviano"))
        self.assertIsNone(update_news.SPORTS_WORDS.search("La economía crece"))

if __name__ == "__main__":
    unittest.main()
