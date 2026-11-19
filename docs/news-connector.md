# News connector (UK national and local)

`ingest/news/` reads public news without any account or key:
- **National feeds:** BBC (UK, England, Scotland, Wales, NI), Guardian, Sky, ITV, Independent, Telegraph, Daily Mail, Mirror, GB News, plus Full Fact.
- **Local feeds:** every BBC English region and the Scottish and Welsh regions, and 24 local papers (for example Manchester Evening News, Liverpool Echo, Telegraph & Argus, Yorkshire Evening Post, WalesOnline, Daily Record, Belfast Telegraph). Local stories carry the area in `place`.
- **Searches:** Google News (UK edition) for disorder, misinformation, incidents and scams; GDELT for UK outlets.

General feeds are filtered to policing stories; search sources are already targeted. Only the headline, a summary of up to 300 characters and the link are stored, never the full article. Publishers are organisations, so the publisher name is kept as the account.

Run: `python ingest/news/run.py` (also part of `scripts/ingest_all.sh` and the Collect now button). `--check` tests every feed once and stores nothing; `--source NS-BBC-UK` runs one; `--dry-run` uses the offline fixture. Seen stories are remembered in `data/ingest/news-seen.json`, so each story is stored once.

Feed addresses change from time to time: run `--check` and fix or remove any that fail.
