"""Automatic search-term tuning. Run in Replit (it needs the secret OPENROUTER_API_KEY):
    python ingest/tune.py                      score the latest X probe round, write the next round's variants
    python ingest/tune.py --run --rounds 2     also run the next probe(s) itself, inside the normal X caps
What it does for each round:
  1. Reads data/ingest/x-probe-roundN.json (made by ingest/x/probe.mjs).
  2. Asks a model, through OpenRouter, to judge every returned post against the topic definitions in
     ingest/topics.json with a fixed checklist (on topic? UK? quote the words that decide it).
  3. Scores each variant: hit rate = on-topic UK posts / posts returned. Keeps the best query per topic.
  4. Asks the model for 2 improved variants per topic that scored under 60%, using the hits and misses.
  5. Writes ingest/x/probes/roundN+1.json and data/ingest/x-tuning-report.json.
It never changes the live searches (ingest/x/queries.json): a person promotes winners.
Settings: TUNE_MODEL (default deepseek/deepseek-chat), TUNE_MAX_CALLS (default 40 model calls a run).
Post text is already scrubbed of handles; no account ids are sent."""
import json, os, re, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA, PROBES = ROOT / "data" / "ingest", ROOT / "ingest" / "x" / "probes"
TOPICS = json.loads((ROOT / "ingest" / "topics.json").read_text())["topics"]
MODEL = os.environ.get("TUNE_MODEL", "deepseek/deepseek-chat")
MAX_CALLS, GOOD = int(os.environ.get("TUNE_MAX_CALLS", "40")), 0.6
calls = 0


def topic_key(variant_id):
    return variant_id[:3]  # P01a, P01b ... all belong to topic P01


def ask(messages, want_json=True):
    """One OpenRouter call. Falls back to plain mode once if structured output is refused."""
    global calls
    if calls >= MAX_CALLS:
        raise RuntimeError(f"Model call cap reached ({MAX_CALLS}). Raise TUNE_MAX_CALLS to allow more.")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set, so automatic scoring is off. Nothing was billed.")
    body = {"model": MODEL, "messages": messages, "temperature": 0}
    if want_json:
        body["response_format"] = {"type": "json_object"}
    for attempt in (1, 2):
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                              "X-Title": "Line of Blue tuning"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                calls += 1
                text = json.loads(r.read())["choices"][0]["message"]["content"]
                return parse_json(text) if want_json else text
        except urllib.error.HTTPError as e:
            if e.code == 400 and attempt == 1 and "response_format" in body:
                body.pop("response_format"); continue
            raise RuntimeError(f"OpenRouter error {e.code}: {e.read()[:300]!r}") from e


def parse_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0) if m else text)


def judge(variant):
    t = TOPICS[topic_key(variant["id"])]
    posts = [{"n": i, "text": s["text"][:400]} for i, s in enumerate(variant.get("samples", []))]
    if not posts:
        return []
    out = ask([{"role": "system", "content": "You check social media search results for a UK police communications team. "
                "Judge each post only against the definition. Lawful political opinion alone is not a hit. "
                'Answer JSON: {"posts":[{"n":0,"onTopic":true,"uk":true,"evidence":"short quote"}]}'},
               {"role": "user", "content": json.dumps({"topic": t["label"], "definition": t["hit"], "posts": posts}, ensure_ascii=False)}])
    return out.get("posts", [])


def score(verdicts, returned):
    hits = sum(1 for v in verdicts if v.get("onTopic") and v.get("uk"))
    return round(hits / returned, 2) if returned else 0.0


def improve(topic_id, tried):
    t = TOPICS[topic_id]
    out = ask([{"role": "system", "content": "You write X (Twitter) recent-search queries. Rules: X search syntax, under 400 characters, "
                "end with -is:retweet lang:en, never use from:, to:, @ or account names, target UK posts, use the words people "
                "actually post. Learn from the hits and misses. "
                'Answer JSON: {"variants":[{"query":"...","why":"..."}]} with exactly 2 variants.'},
               {"role": "user", "content": json.dumps({"topic": t["label"], "definition": t["hit"], "tried": tried}, ensure_ascii=False)}])
    return out.get("variants", [])[:2]


def latest_round():
    rounds = sorted(int(m.group(1)) for p in DATA.glob("x-probe-round*.json") if (m := re.fullmatch(r"x-probe-round(\d+)\.json", p.name)))
    return rounds[-1] if rounds else None


def tune_once(n):
    probe = json.loads((DATA / f"x-probe-round{n}.json").read_text())
    report_path = DATA / "x-tuning-report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {"rounds": [], "best": {}}
    rows, tried = [], {}
    for v in probe["variants"]:
        if v.get("error"):
            rows.append({"id": v["id"], "query": v["query"], "error": v["error"]}); continue
        verdicts = judge(v)
        r = {"id": v["id"], "query": v["query"], "returned": v["returned"], "hitRate": score(verdicts, v["returned"]),
             "hits": [v["samples"][x["n"]]["text"][:160] for x in verdicts if x.get("onTopic") and x.get("uk") and x.get("n", 99) < len(v["samples"])][:3]}
        rows.append(r)
        tid = topic_key(v["id"])
        tried.setdefault(tid, []).append({"query": v["query"], "hitRate": r["hitRate"], "returned": v["returned"],
                                          "examplesOfHits": r["hits"], "examplesOfMisses": [s["text"][:160] for i, s in enumerate(v["samples"]) if s["text"][:160] not in r["hits"]][:3]})
        best = report["best"].get(tid)
        if v["returned"] and (not best or r["hitRate"] > best["hitRate"]):
            report["best"][tid] = {"query": v["query"], "hitRate": r["hitRate"], "round": n}
    report["rounds"].append({"round": n, "model": MODEL, "variants": rows})
    nxt = []
    for tid, history in tried.items():
        if report["best"].get(tid, {}).get("hitRate", 0) >= GOOD:
            continue
        for i, v in enumerate(improve(tid, history)):
            nxt.append({"id": f"{tid}{'ab'[i]}", "label": TOPICS[tid]["label"], "query": v["query"], "why": v.get("why", "")})
    report_path.write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(f"Round {n} scored with {MODEL} ({calls} model calls):")
    for r in rows:
        print(f"  {r['id']:<5} " + (f"{r['hitRate']:.0%} of {r['returned']}" if "hitRate" in r else r["error"]))
    print("Best so far: " + ", ".join(f"{k} {v['hitRate']:.0%}" for k, v in sorted(report["best"].items())))
    if nxt:
        (PROBES / f"round{n + 1}.json").write_text(json.dumps({"note": f"Written by tune.py from round {n}.", "sets": nxt}, indent=1, ensure_ascii=False))
        print(f"Wrote {len(nxt)} new variants to ingest/x/probes/round{n + 1}.json")
    else:
        print("Every topic is at or above 60%. No new round needed.")
    return bool(nxt)


def main(args):
    rounds = int(args[args.index("--rounds") + 1]) if "--rounds" in args else 1
    n = latest_round()
    if n is None:
        sys.exit("No probe results yet. Run: node ingest/x/probe.mjs ingest/x/probes/round1.json")
    for _ in range(rounds):
        if not tune_once(n) or "--run" not in args:
            break
        n += 1
        if subprocess.run(["node", str(ROOT / "ingest" / "x" / "probe.mjs"), str(PROBES / f"round{n}.json")], cwd=ROOT).returncode:
            break
        if not (DATA / f"x-probe-round{n}.json").exists():
            break
    if "--run" in args and (DATA / f"x-probe-round{n}.json").exists() and not any(r["round"] == n for r in json.loads((DATA / "x-tuning-report.json").read_text())["rounds"]):
        tune_once(n)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except RuntimeError as e:
        sys.exit(str(e))
