import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from connector import approved, collect, keep, load_sources, parse_feed, url_for

HERE = Path(__file__).parent
FX = json.loads((HERE / "fixture.json").read_text())
RSS = {"id": "T-RSS", "kind": "rss", "publisher": "Test", "url": "https://example.org/rss", "status": "approved"}
GN = {"id": "T-GN", "kind": "google_news", "publisher": "Google News", "query": "police UK", "status": "approved"}
GD = {"id": "T-GD", "kind": "gdelt", "publisher": "GDELT", "query": "police sourcecountry:UK", "status": "approved"}


class News(unittest.TestCase):
    def test_sources_file_is_valid(self):
        s = load_sources(HERE / "sources.json")
        self.assertGreaterEqual(len(approved(s)), 15)
        self.assertEqual(len({x["id"] for x in s}), len(s))

    def test_general_feeds_keep_only_policing_stories_and_strip_html(self):
        posts, n = collect(RSS, lambda u: FX["rss"].encode())
        self.assertEqual(n, 3)
        self.assertEqual([p["link"] for p in posts], ["https://example.org/news/1", "https://example.org/news/3"])
        self.assertNotIn("<p>", posts[0]["text"]); self.assertIn("&", posts[1]["text"])
        self.assertEqual(posts[1]["account"], "Example Gazette")  # item's own source wins over the feed name
        self.assertEqual(posts[0]["platform"], "news")

    def test_search_sources_keep_everything_and_gdelt_parses(self):
        posts, _ = collect(GN, lambda u: FX["rss"].encode())
        self.assertEqual(len(posts), 3)
        g, _ = collect(GD, lambda u: FX["gdelt"].encode())
        self.assertEqual(g[0]["account"], "example.co.uk"); self.assertTrue(g[0]["t"].startswith("2026-11-19T12:00"))

    def test_seen_stories_are_not_stored_twice(self):
        seen = set()
        a, _ = collect(RSS, lambda u: FX["rss"].encode(), seen)
        b, _ = collect(RSS, lambda u: FX["rss"].encode(), seen)
        self.assertEqual((len(a), len(b)), (2, 0))

    def test_urls(self):
        self.assertIn("ceid=GB%3Aen", url_for(GN)); self.assertIn("timespan=2d", url_for(GD))

    def test_summary_only_never_full_text(self):
        long = "<rss><channel><item><title>Police t</title><description>" + "word " * 500 + "</description><link>https://x/1</link></item></channel></rss>"
        self.assertLessEqual(len(parse_feed(long.encode())[0]["summary"]), 300)


if __name__ == "__main__":
    unittest.main()
