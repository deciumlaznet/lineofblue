import json, os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import tune


class Tune(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        tune.DATA, tune.PROBES = self.tmp / "data", self.tmp / "probes"
        tune.DATA.mkdir(); tune.PROBES.mkdir()
        probe = {"variants": [
            {"id": "P01", "query": "q1", "returned": 4, "samples": [{"text": f"post {i}"} for i in range(4)]},
            {"id": "P03", "query": "q3", "returned": 2, "samples": [{"text": "scam pcn text"}, {"text": "pcn scam uk"}]},
            {"id": "P05", "query": "q5", "error": "Spending cap reached"}]}
        (tune.DATA / "x-probe-round1.json").write_text(json.dumps(probe))

        def fake_ask(messages, want_json=True):
            sys_msg = messages[0]["content"]
            if "write X" in sys_msg:
                return {"variants": [{"query": "better -is:retweet lang:en", "why": "w"}, {"query": "other -is:retweet lang:en"}]}
            n = len(json.loads(messages[1]["content"])["posts"])
            return {"posts": [{"n": i, "onTopic": i == 0 or n == 2, "uk": True} for i in range(n)]}
        tune.ask = fake_ask

    def test_scores_keeps_best_and_writes_next_round_for_weak_topics_only(self):
        self.assertTrue(tune.tune_once(1))
        rep = json.loads((tune.DATA / "x-tuning-report.json").read_text())
        rates = {r["id"]: r.get("hitRate") for r in rep["rounds"][0]["variants"]}
        self.assertEqual(rates, {"P01": 0.25, "P03": 1.0, "P05": None})
        nxt = json.loads((tune.PROBES / "round2.json").read_text())["sets"]
        self.assertEqual([s["id"] for s in nxt], ["P01a", "P01b"])  # P03 already good, P05 errored

    def test_no_key_means_no_call(self):
        import importlib; real = importlib.reload(tune)
        os.environ.pop("OPENROUTER_API_KEY", None)
        with self.assertRaises(RuntimeError):
            real.ask([{"role": "user", "content": "x"}])


if __name__ == "__main__":
    unittest.main()
