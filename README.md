# Line of Blue synthetic demo

Website: [lineofblue.co.uk](https://lineofblue.co.uk)

A working prototype of **Line of Blue**, a communications capability for UK policing built around NPCC Communications, running entirely on a synthetic world. It demonstrates the first-release functional areas from the research report: **Narrative Radar**, the **Golden Hour incident cell** and the **Safe to Say checker**, plus national lines and cascade, platform referrals, the event horizon, scripted multi-actor scenarios and a decision log.

> **Everything here is fictional.** Forces, places, people, accounts, outlets, platforms, threat actors and posts are invented. No real person or private individual appears. Real proscribed groups and sanctioned state actors are represented by fictional stand-ins; in production Tier A and B reference data would be loaded from the Home Office and government lists.

## Run it

```bash
python3 scripts/generate_world.py   # synthetic world -> data/world.json and CSVs (deterministic)
python3 scripts/build.py            # -> dist/index.html (standalone) and dist/artifact.html
python3 -m http.server 8765 -d dist # open http://127.0.0.1:8765
```

No dependencies, no network calls apart from Google Fonts. State is kept in the browser; **Data and safeguards → Reset demo** starts again at 13:50.

Use **Acting as** to switch between the 20 personas and **Scenario clock** to move time forward. The **Scenarios** screen lists each exercise step by step, who acts, and ticks steps as they happen. **Act as** on a step switches persona and opens the right screen.

## What is in the synthetic world

| Item | Count | Notes |
|---|---|---|
| Organisations | 13 | NPCC, NPoCC SIB, four fictional forces (one Welsh, bilingual), Home Office, government online information team, CTP, CPS, College, PCC office, ethics panel |
| Personas | 20 | Each with role-based permissions. See `data/personas.csv` |
| Threat actors | 3 + rule | Fictional Tier A, B and C stand-ins; Tier D is a rule, never an entity |
| Narratives | 10 | False identity, cover-up, recycled footage, spoof curfew, mobilisation, AI image, two-tier, child rumour, Welsh flood hoax, youth trial speculation |
| Posts | 148 | Timed, pseudonymised (`acct_` hashes), with platform, place, reach and flags |
| Incidents and cases | 4 + 2 | Critical incident, resolved missing person, planned protest, flood; youth trial and sexual offence case for anonymity rules |
| Event horizon | 8 | Trials, protest, pre-election period, derby, anniversary |
| Scenarios | 6 | 26 multi-actor steps with machine-checkable outcomes |

## Scenarios

| ID | Scenario | Actors |
|---|---|---|
| SC-01 | Golden Hour: Harbourside Market stabbing (facts, Safe to Say, legal, SIO, Gold, Radar link, disclosure decision, Home Office, national line, cascade, ethics review) | 12 |
| SC-02 | Spoof curfew notice with state-linked indicators (handover to CTP and government, attribution blocked) | 5 |
| SC-03 | Mobilisation and threats (tension assessment, platform referral, response time) | 4 |
| SC-04 | Two-tier narrative at a protest (Tier D tracking refused, impartial explainer) | 3 |
| SC-05 | Bilingual flood hoax (Welsh version required) | 2 |
| SC-06 | Youth trial and complainant anonymity (hard blocks) | 3 |

## Testing

`uat/profiles/lineofblue-demo.json` is a profile for the shared UAT operator (`runner/uat.mjs`) used by the other apps. It runs one conductor persona per scenario, role personas that check what each organisation can and cannot do, and a desktop and mobile tour.

```bash
node runner/uat.mjs run profiles/lineofblue-demo.json            # LINE_OF_BLUE_BASE_URL overrides http://127.0.0.1:8765
```

Latest run: `uat/runs/2026-11-19T13-46-28/` (220 steps, 0 failures) with `verdicts.md`.

Regenerate the profile with `python3 scripts/make_uat_profile.py`.

## Layout

```
app/        shell.html, styles.css, app.js (vanilla JS, rules engine, scenario checks)
data/       world.json + CSV exports (generated)
scripts/    generate_world.py, build.py, make_uat_profile.py
dist/       built demo
uat/        UAT profile and run evidence
```

## Limits of the demo

- Safe to Say rules summarise England and Wales law from the research report. They are not legal advice and need review by police legal services.
- Single-browser state: the multi-actor scenarios run in one browser by switching persona. A shared backend would let each actor work in their own session.
- No live data sources. Radar replays the synthetic post timeline against the scenario clock.
