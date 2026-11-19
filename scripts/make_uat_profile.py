#!/usr/bin/env python3
"""Write uat/profiles/lineofblue-demo.json for the shared UAT operator (runner/uat.mjs).

The demo keeps state in the browser, so each end-to-end scenario is run by one
"conductor" persona that switches 'Acting as' between the real actors in order.
Role personas then check what each organisation can and cannot do."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

act = lambda p: {"do": "select", "target": {"label": "Acting as"}, "value": p, "note": f"act as {p}"}
go = lambda v: {"do": "goto", "path": f"/#{v}"}
tid = lambda t, **k: {"do": "click", "target": {"testid": t}, **k}
css = lambda c, **k: {"do": "click", "target": {"css": c}, **k}
txt = lambda t: {"do": "expectText", "text": t}
notxt = lambda t: {"do": "expectNotText", "text": t}
fill = lambda target, v: {"do": "fill", "target": target, "value": v}
wait = {"do": "waitFor", "ms": 600}
judge = lambda n, q: {"do": "judge", "name": n, "prompt": q}
disabled = lambda t: {"do": "expectVisible", "target": {"css": f"[data-testid='{t}'][disabled]"}, "note": f"{t} is disabled for this role"}
all_done = lambda sc: {"do": "expectHidden", "target": {"css": f"[data-testid^='step-{sc}-'][data-done='false']"}, "note": f"every {sc} step is ticked"}
scen = lambda sc: [go("scenarios"), tid(f"scenario-{sc}"), all_done(sc)]
clock = lambda n: [tid("clock-30")] * n

sc01 = [go("governance"), tid("reset"),
    act("nm-gold"), go("golden-hour"), tid("open-cell"), txt("Open since"),
    act("nm-press"), {"do": "click", "target": {"button": "/Officers were called/"}}, {"do": "click", "target": {"button": "/Two people were injured/"}},
    act("nm-sio"), css("[data-testid^='verify-']"), css("[data-testid^='verify-']"), txt("2/2"),
    act("nm-press"), go("safe-to-say"), tid("example-0"), wait, txt("No legal or policy risks found"), tid("submit-draft"),
    act("nm-legal"), go("golden-hour"), tid("legal-approve"),
    act("nm-sio"), tid("sio-approve"), act("nm-gold"), tid("gold-approve"), act("nm-press"), tid("publish"), txt("Published"),
    *clock(2),
    act("nc-insight"), go("radar"), tid("narr-NAR-01"), txt("False suspect identity"), tid("link-incident"),
    judge("radar-nar01", "Narrative Radar at 14:50: is NAR-01 shown as a false claim with velocity, reach, platforms and places, pseudonymised accounts only, and a time to truth once linked?"),
    act("nm-gold"), go("golden-hour"), txt("false identity claim is spreading"),
    fill({"css": "#discReason"}, "UAT synthetic: a false identity claim is driving tension; confirming nationality is necessary and proportionate."),
    tid("decide-confirm"), tid("ho-request"),
    act("ho-press"), go("inbox"), txt("confirm immigration status"), tid("ho-confirm"),
    act("nc-duty"), go("lines"), tid("draft-line"),
    act("nc-head"), tid("approve-line"),
    act("sv-comms"), tid("ack-line"), act("dg-comms"), tid("ack-line"), act("km-comms"), tid("ack-line"),
    judge("cascade-receipts", "National lines: do read receipts show the three receiving forces acknowledged (the host force, Northmoor, owns the incident) and the Welsh force localised?"),
    act("eth"), go("audit"), txt("Disclosure decision"),
    judge("decision-log", "Decision log: does every decision show a named (synthetic) person, a time and the reason, with nothing that profiles a member of the public?"),
    *scen("SC-01"),
    judge("sc01-complete", "Scenario SC-01: are all 14 steps ticked, each naming the actor and organisation?")]

sc02 = [go("governance"), tid("reset"), *clock(3),
    act("nc-insight"), go("radar"), tid("narr-NAR-04"), txt("Tier B indicators"), tid("handover"),
    act("ctp"), go("inbox"), tid("accept-handover"),
    act("nm-press"), go("safe-to-say"), tid("example-2"), wait, txt("Public attribution to a state actor"), disabled("submit-draft"),
    fill({"testid": "draft-text"}, "UAT synthetic: There is no curfew in Port Ellery. The notice is fake. Check our official website and verified accounts before sharing."), wait,
    notxt("Public attribution to a state actor"),
    fill({"css": "#dReason"}, "UAT synthetic: holding rebuttal ahead of SIO-verified facts; it states only that no curfew exists."), tid("submit-draft"),
    act("nm-legal"), tid("legal-approve"), act("nm-sio"), tid("sio-approve"), act("nm-gold"), tid("gold-approve"), act("nm-press"), tid("publish"),
    *scen("SC-02")]

sc03 = [go("governance"), tid("reset"), *clock(4),
    act("sib"), go("radar"), tid("narr-NAR-05"), tid("tension"),
    act("nc-insight"), go("escalations"), css("[data-testid^='refer-']"), txt("awaiting platform"), tid("clock-30"), css("[data-testid^='resolve-']"), txt("removed after"),
    *scen("SC-03")]

sc04 = [go("governance"), tid("reset"), tid("clock-30"),
    act("nc-insight"), go("radar"), tid("narr-NAR-07"), css("[data-testid='track-account']"), txt("Line of Blue analyses narratives, not people"),
    act("km-comms"), go("safe-to-say"), tid("example-6"), wait, txt("Political impartiality"),
    fill({"css": "#dReason"}, "UAT synthetic: we name the label only to rebut it with facts about the policing plan."), tid("submit-draft"), tid("publish"),
    *scen("SC-04")]

sc05 = [go("governance"), tid("reset"), tid("clock-30"),
    act("dg-comms"), go("safe-to-say"), tid("example-7"), wait, txt("Welsh version missing"), tid("welsh-template"), wait, notxt("Welsh version missing"),
    tid("submit-draft"), tid("publish"), *scen("SC-05")]

sc06 = [go("governance"), tid("reset"),
    act("sv-comms"), go("safe-to-say"), tid("example-4"), wait, txt("Identifies a child defendant"), disabled("submit-draft"),
    act("km-comms"), tid("example-5"), wait, txt("Could identify a sexual offence complainant"), disabled("submit-draft"),
    *scen("SC-06")]

sc07 = [go("governance"), tid("reset"),
    act("nm-gold"), go("golden-hour"), tid("open-cell"), txt("Rumour forecast"), txt("Spoof official notices"),
    act("nm-head"), go("agent"), tid("agent-quick-plan"), {"do": "waitFor", "ms": 800}, txt("Get-ahead plan"), txt("KB-ISD24"),
    css("button.cite[data-k='KB-ISD24']"), {"do": "expectVisible", "target": {"testid": "kb-selected"}},
    judge("agent-plan", "L.O.B Agent: does the answer give a timed get-ahead plan for each likely rumour, cite public sources by id, offer a pre-bunk that names no one, and say people decide?"),
    act("nm-press"), go("golden-hour"), tid("prebunk-NAR-04"), wait, txt("pre-bunk for NAR-04"), txt("No legal or policy risks found"), tid("submit-draft"),
    act("nm-legal"), go("golden-hour"), tid("legal-approve"), act("nm-sio"), tid("sio-approve"), act("nm-gold"), tid("gold-approve"), act("nm-press"), tid("publish"),
    txt("line out first"), *clock(3),
    act("nc-insight"), go("picture"), {"do": "expectVisible", "target": {"testid": "velocity-chart"}}, {"do": "expectVisible", "target": {"testid": "race-NAR-04"}}, txt("min ahead"),
    judge("national-picture", "National picture at 15:20: do the charts show claim velocity over time, each claim's race between first post, threshold and police line (with NAR-04 ahead), and the map, readably and without overlaps?"),
    act("nm-gold"), go("golden-hour"), {"do": "expectVisible", "target": {"testid": "swimlane"}},
    *scen("SC-07")]

agent_role = [go("governance"), tid("reset"), act("nc-insight"), go("agent"),
    fill({"css": "#agentQ"}, "UAT synthetic: which guidance covers Welsh language duties for a bilingual rebuttal?"), tid("agent-ask"), {"do": "waitFor", "ms": 800},
    txt("KB-WELSH"), disabled("agent-draft") if False else txt("Offline playbook answer"),
    act("nm-press"), go("safe-to-say"), tid("example-1"), wait, go("agent"), tid("agent-quick-check"), {"do": "waitFor", "ms": 800}, txt("Not yet"), txt("KB-CCA81"),
    judge("agent-check", "L.O.B Agent: when asked about a risky draft, does it say what must be fixed, why, and cite the relevant law or guidance?")]

leader = [go("governance"), tid("reset"), act("nc-head"), go("nmap"), {"do": "expectVisible", "target": {"testid": "uk-map"}}, txt("Real geography, synthetic messages"),
    {"do": "click", "target": {"testid": "layer-cnc"}}, {"do": "expectHidden", "target": {"css": ".ukmap .lyr.cnc"}}, {"do": "click", "target": {"testid": "layer-cnc"}}, {"do": "expectVisible", "target": {"css": ".ukmap .lyr.cnc"}},
    {"do": "click", "target": {"css": "tr[data-f='Cumbria']"}}, txt("Who else may need to act nearby"), txt("Sellafield"),
    judge("national-map", "National map: is it a recognisable map of the UK with force HQs, British Transport Police rail hubs, civil nuclear, defence, service police and port sites as distinct marks, synthetic message bubbles, and a clear note on what is real and what is synthetic?"),
    go("workflows"), {"do": "expectVisible", "target": {"testid": "wf-lanes"}}, txt("Autonomy mix"), {"do": "expectVisible", "target": {"testid": "signoff-queue"}},
    {"do": "select", "target": {"css": "select[data-s='W1.3']"}, "value": "1"}, go("audit"), txt("Autonomy level changed"),
    act("pcc"), go("workflows"), txt("Only the Head of NPCC Communications"),
    judge("workflows", "Workflows and autonomy: are the seven workflows shown as lanes, each step coloured by autonomy level with a live status, an autonomy mix bar, clocks against standards, and a queue of what waits on a person?")]

sc08 = [go("governance"), tid("reset"),
    act("nc-head"), go("review"), tid("draft-DR-01"), tid("ask-review"), txt("Return for revision"), txt("victim-blaming"),
    *[tid(f"accept-{n}") for n in (1, 2, 3, 4, 5, 6, 7, 8)], tid("reject-9"), txt("9/12 decided"),
    judge("markup-dr01", "Review and mark-up: does the VAWG strategy show tracked changes (struck-through original, proposed text), numbered markers coloured by severity, and a comment per change explaining why with a source?"),
    tid("mode-clean"), notxt("Women should avoid walking alone"), tid("mode-markup"),
    tid("return-draft"), txt("Returned for revision"),
    tid("draft-DR-02"), tid("ask-review"), txt("Do not publish"), disabled("approve-draft"), tid("accept-all"), txt("4/4 decided"), tid("approve-draft"), txt("Approved"),
    tid("draft-DR-07"), tid("ask-review"), txt("Displaying a national flag is lawful"),
    tid("draft-DR-08"), tid("ask-review"), txt("Welsh"),
    fill({"testid": "paste-text"}, "UAT synthetic: Northmoor Police needs more manpower. We have zero tolerance for crime and the vast majority of officers are brilliant."), tid("paste-add"), tid("ask-review"), wait, txt("Gendered language"),
    act("nc-insight"), go("trends"), txt("morning trend brief"), tid("trend-TR-01"), txt("broke out of its normal range"), txt("Emerging"),
    judge("trend-chart", "Trend watch: does the chart show six weeks of daily items, a normal-range band, a dashed projection, and does the panel explain why the agent flagged the theme and propose a line with sources?"),
    tid("trend-TR-05"), txt("Fading"), notxt("Send to Safe to Say"),
    act("nc-duty"), tid("trend-TR-01"), tid("trend-to-sts"), wait, txt("No legal or policy risks found"), tid("submit-draft"),
    go("strategy"), txt("Behaviour change toolkit"), tid("topic-ST-CSE"), txt("Casey"), tid("topic-ST-WAR"), txt("Impartiality"), tid("start-template"), txt("Paste a draft"),
    act("nc-head"), go("workflows"), txt("Strategy, policy and review"),
    *scen("SC-08"),
    judge("sc08-complete", "Scenario SC-08: are all six steps ticked, naming the Head of NPCC Comms, the insight analyst and the duty press officer?")]

views = ["inbox", "picture", "nmap", "radar", "trends", "agent", "review", "strategy", "workflows", "golden-hour", "safe-to-say", "lines", "escalations", "horizon", "scenarios", "audit", "governance"]

profile = {
  "app": "lineofblue-demo",
  "name": "Line of Blue synthetic demo (NPCC Communications)",
  "baseUrl": os.environ.get("LINE_OF_BLUE_BASE_URL", "http://127.0.0.1:8765"),
  "notes": [
    "Synthetic demo: every force, person, account, place, group and post is fictional. Safe to click and type, but only fictional values are allowed.",
    "State lives in the browser, so each end-to-end scenario runs as one conductor persona that switches 'Acting as' between actors in order. Once Line of Blue has a shared backend, split each conductor into one browser per actor running in parallel.",
    "Serve dist/index.html (python3 -m http.server 8765 -d dist) or set LINE_OF_BLUE_BASE_URL.",
  ],
  "expectations": [
    "A synthetic-data banner is on every screen.",
    "Narrative-first: Radar shows narratives and pseudonymised accounts; any attempt to track an individual is refused and logged.",
    "Safe to Say hard-blocks: state attribution, naming a child defendant, identifying a sexual offence complainant, confirming immigration status without the Home Office, naming an uncharged suspect while proceedings are active.",
    "Amber items need a recorded reason; every release in a Golden Hour cell goes draft, checked, legal, SIO, Gold, published, each by the role allowed to do it.",
    "Only the Home Office confirms immigration status; only CTP and government receive state-linked indicators; comms never attributes publicly.",
    "Every decision appears in the decision log with a named person, time and reason.",
    "Roles outside a step see its button disabled, with the missing permission in the tooltip.",
  ],
  "guardrails": {
    "readOnly": False,
    "neverClick": [],
    "allowRequests": [],
    "fictionalOnly": {"allowedValues": ["/^UAT synthetic:/"]},
  },
  "personas": [
    {"id": "conductor-sc01", "title": "SC-01 conductor: Golden Hour, 12 actors", "viewports": ["desktop"], "scenarios": [{"id": "sc01", "title": "Harbourside Market stabbing end to end", "steps": sc01}]},
    {"id": "conductor-sc02", "title": "SC-02 conductor: spoof curfew and state indicators", "viewports": ["desktop"], "scenarios": [{"id": "sc02", "title": "Spoof notice, handover, no attribution", "steps": sc02}]},
    {"id": "conductor-sc03", "title": "SC-03 conductor: mobilisation and referral", "viewports": ["desktop"], "scenarios": [{"id": "sc03", "title": "Tension, referral, response time", "steps": sc03}]},
    {"id": "conductor-sc04", "title": "SC-04 conductor: lawful opinion at a protest", "viewports": ["desktop"], "scenarios": [{"id": "sc04", "title": "Tier D refusal and impartial explainer", "steps": sc04}]},
    {"id": "conductor-sc05", "title": "SC-05 conductor: bilingual flood hoax", "viewports": ["desktop", "mobile"], "scenarios": [{"id": "sc05", "title": "Welsh and English rebuttal", "steps": sc05}]},
    {"id": "conductor-sc06", "title": "SC-06 conductor: hard blocks", "viewports": ["desktop"], "scenarios": [{"id": "sc06", "title": "Child defendant and complainant anonymity", "steps": sc06}]},
    {"id": "conductor-sc07", "title": "SC-07 conductor: get ahead with the forecast and the L.O.B Agent", "viewports": ["desktop"], "scenarios": [{"id": "sc07", "title": "Pre-bunk the spoof notice before it appears", "steps": sc07}]},
    {"id": "conductor-sc08", "title": "SC-08 conductor: strategy review, mark-up and trend-led lines", "viewports": ["desktop"], "scenarios": [{"id": "sc08", "title": "Mark up a weak strategy and a non-compliant line; turn a trend into a checked line", "steps": sc08}]},
    {"id": "role-agent-user", "title": "Analyst and press officer using the L.O.B Agent", "viewports": ["desktop", "mobile"], "charter": ["Every answer cites a public source.", "The agent never names a suspect or profiles a person."], "scenarios": [{"id": "agent", "title": "Ask, cite, check a draft", "steps": agent_role}]},
    {"id": "role-comms-leader", "title": "National comms leader: map and workflows", "viewports": ["desktop", "mobile"], "charter": ["Map separates real geography from synthetic messages.", "Only the governance role can change an autonomy level, and every change is logged."], "scenarios": [{"id": "lead", "title": "Map overlays, autonomy levels, sign-off queue", "steps": leader}]},
    {"id": "role-home-office", "title": "Home Office public safety official (read-only brief)", "viewports": ["desktop"],
     "charter": ["Confirm nothing in the brief identifies a member of the public.", "Confirm the official cannot change any force release."],
     "scenarios": [{"id": "limits", "title": "Sees the brief, cannot act on force work", "steps": [go("governance"), tid("reset"), act("ho-psg"), go("inbox"), txt("National situation summary"), go("golden-hour"), disabled("open-cell"), go("safe-to-say"), tid("example-0"), wait, disabled("submit-draft")]}]},
    {"id": "role-pcc", "title": "PCC office (governance observer)", "viewports": ["desktop", "mobile"],
     "scenarios": [{"id": "limits", "title": "Read-only governance view", "steps": [go("governance"), tid("reset"), act("pcc"), go("inbox"), txt("National situation summary"), go("lines"), disabled("draft-line"), judge("pcc-inbox", "PCC office: is the view read-only and free of operational detail they should not change?")]}]},
    {"id": "role-force-officer", "title": "Force comms officer from another force", "viewports": ["desktop"],
     "scenarios": [{"id": "limits", "title": "Cannot sign off another force's incident", "steps": [go("governance"), tid("reset"), act("sv-comms"), go("golden-hour"), disabled("open-cell"), go("lines"), disabled("draft-line")]}]},
    {"id": "tour-mobile", "title": "Smoke tour of every screen", "viewports": ["desktop", "mobile"],
     "scenarios": [{"id": "tour", "title": "Every workspace renders", "steps": [x for v in views for x in (go(v), {"do": "expectText", "text": "Synthetic demo."})] + [judge("tour-end", "Does the Data and safeguards screen read cleanly at this width with no clipped text?")]}]},
  ],
}
os.makedirs(os.path.join(R, "uat/profiles"), exist_ok=True)
json.dump(profile, open(os.path.join(R, "uat/profiles/lineofblue-demo.json"), "w"), indent=1)
print("steps:", sum(len(s["steps"]) for p in profile["personas"] for s in p["scenarios"]))
