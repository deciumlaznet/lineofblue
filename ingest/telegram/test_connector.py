"""python -m unittest ingest/telegram/test_connector.py   (no Telegram sign-in or network needed)"""
import asyncio, json, os, sys, tempfile, unittest
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from connector import Budget, CapError, collect, keep, load_sources, pseudonym, scrub, to_post  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = json.load(open(os.path.join(HERE, "fixture.json")))
SALT = "test-salt-0123456789"
SRC = {"id": "TS-T", "mode": "search", "query": "police", "status": "approved", "maxPerRun": 50}
NOW = lambda: datetime(2026, 11, 19, 10, tzinfo=timezone.utc)  # noqa: E731


def budget(cap=100):
    return Budget(os.path.join(tempfile.mkdtemp(), "l.json"), cap, now=NOW)


def fetcher(calls):
    async def f(source, limit, since):
        calls.append(limit); return FIX[:limit]
    return f


class T(unittest.TestCase):
    def test_pseudonyms(self):
        self.assertEqual(pseudonym("chan", 9001, SALT), pseudonym("chan", 9001, SALT))
        self.assertNotIn("9001", pseudonym("chan", 9001, SALT))
        with self.assertRaises(ValueError):
            pseudonym("chan", 9001, "")

    def test_scrub(self):
        self.assertEqual(scrub("see @someone t.me/chan/12"), "see @user [link]")

    def test_post_shape_has_no_identity(self):
        p = to_post(FIX[0], SRC, SALT)
        self.assertEqual(p["platform"], "telegram"); self.assertEqual(p["reach"], 1500); self.assertEqual(p["shares"], 40)
        s = json.dumps(p)
        for leak in ("9001", "someone", "somechannel"):
            self.assertNotIn(leak, s)

    def test_only_public_broadcast_channels_kept(self):
        self.assertTrue(keep(FIX[0], SRC)); self.assertFalse(keep(FIX[2], SRC))

    def test_channel_keywords_filter(self):
        src = dict(SRC, mode="channel", keywords=["curfew"])
        self.assertTrue(keep(FIX[0], src)); self.assertFalse(keep(FIX[1], src))

    def test_sources_refuse_accounts(self):
        d = tempfile.mkdtemp()
        for bad in ({"id": "B", "mode": "search", "query": "@someone police"}, {"id": "B", "mode": "channel", "channel": "https://t.me/x"}):
            p = os.path.join(d, "s.json"); json.dump({"sources": [bad]}, open(p, "w"))
            with self.assertRaises(ValueError):
                load_sources(p)
        self.assertEqual(len(load_sources(os.path.join(HERE, "sources.json"))), 8)

    def test_only_approved_run(self):
        with self.assertRaises(CapError):
            asyncio.run(collect(dict(SRC, status="proposed"), fetcher([]), budget(), SALT, {}))

    def test_cap_shrinks_and_stops(self):
        b, calls = budget(2), []
        posts = asyncio.run(collect(SRC, fetcher(calls), b, SALT, {}))
        self.assertEqual(calls, [2]); self.assertEqual(len(posts), 2); self.assertEqual(b.used(), 2)
        with self.assertRaises(CapError):
            asyncio.run(collect(SRC, fetcher(calls), b, SALT, {}))
        self.assertEqual(calls, [2])

    def test_dropped_messages_still_count_and_state_advances(self):
        b, st = budget(), {}
        posts = asyncio.run(collect(SRC, fetcher([]), b, SALT, st))
        self.assertEqual(len(posts), 2); self.assertEqual(b.used(), 3)
        self.assertEqual(st["TS-T"], "2026-11-19T09:45:00+00:00")


if __name__ == "__main__":
    unittest.main()
