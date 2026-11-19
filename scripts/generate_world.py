#!/usr/bin/env python3
"""Generate the Line of Blue synthetic demo world.

Everything produced here is FICTIONAL: forces, places, people, accounts,
outlets, platforms, threat actors and posts are invented for demonstration
and testing. No real person, private individual or real account appears.

Run:  python3 scripts/generate_world.py        (writes data/world.json + CSVs)
The output is deterministic (fixed seed), so test expectations stay stable.
"""
import csv, hashlib, json, os, random
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from knowledge_base import KNOWLEDGE, PLAYBOOKS  # noqa: E402
import review_data as RV  # noqa: E402
KNOWLEDGE = KNOWLEDGE + RV.BEHAVIOUR_KB
_kb_ids = {k["id"] for k in KNOWLEDGE}
for _d in RV.DRAFTS:
    _txt = "\n".join(_d["paras"])
    for _i in _d["issues"]:
        assert _txt.count(_i["find"]) == 1, (_d["id"], _i["find"])
        assert all(k in _kb_ids for k in _i["kb"]), (_d["id"], _i["kb"])
for _t in RV.STRATEGY_TOPICS + RV.THEMES:
    assert all(k in _kb_ids for k in _t["kb"]), (_t["id"], _t["kb"])


random.seed(20261121)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data")

SCENARIO_DATE = "Saturday 21 November 2026 (synthetic)"

# ---------------------------------------------------------------- organisations
orgs = [
    {"id": "npcc", "name": "NPCC Communications", "kind": "national", "short": "NPCC"},
    {"id": "npocc", "name": "NPoCC Strategic Intelligence and Briefing", "kind": "national", "short": "NPoCC"},
    {"id": "nmp", "name": "Northmoor Police", "kind": "force", "short": "Northmoor", "region": "North West (fictional)", "welsh": False},
    {"id": "svc", "name": "Severnvale Constabulary", "kind": "force", "short": "Severnvale", "region": "West Midlands (fictional)", "welsh": False},
    {"id": "dgp", "name": "Dyfed-Glas Police / Heddlu Dyfed-Glas", "kind": "force", "short": "Dyfed-Glas", "region": "Wales (fictional)", "welsh": True},
    {"id": "kmp", "name": "Kingsbridge Metropolitan Police", "kind": "force", "short": "Kingsbridge", "region": "London and South East (fictional)", "welsh": False},
    {"id": "ho", "name": "Home Office", "kind": "government", "short": "Home Office"},
    {"id": "gov", "name": "Government online information team", "kind": "government", "short": "Gov info team"},
    {"id": "ctp", "name": "Counter Terrorism Policing (liaison)", "kind": "partner", "short": "CTP"},
    {"id": "cps", "name": "CPS Area Communications", "kind": "partner", "short": "CPS"},
    {"id": "col", "name": "College of Policing", "kind": "national", "short": "College"},
    {"id": "pcc", "name": "Office of the Northmoor PCC", "kind": "governance", "short": "PCC office"},
    {"id": "eth", "name": "Line of Blue Independent Ethics Panel", "kind": "governance", "short": "Ethics panel"},
]
FORCES = [o for o in orgs if o["kind"] == "force"]

# ------------------------------------------------------------------- personas
# Capabilities are checked by the app for every action (role-based access).
personas = [
    ("nc-head", "Priya Hallam", "Head of NPCC Communications", "npcc", ["line:approve", "radar:triage", "cell:join", "audit:view"]),
    ("nc-duty", "Tom Ashdown", "NPCC duty press officer", "npcc", ["line:draft", "line:cascade", "statement:draft", "cell:join", "radar:triage"]),
    ("nc-insight", "Leah Marwood", "NPCC insight and narrative analyst", "npcc", ["radar:triage", "radar:alert", "referral:log", "referral:update", "state:handover", "cell:join"]),
    ("sib", "Dev Raman", "NPoCC SIB analyst", "npocc", ["radar:triage", "tension:assess", "cell:join"]),
    ("nm-head", "Claire Fenwick", "Head of Corporate Communications, Northmoor", "nmp", ["statement:draft", "line:ack", "cell:open", "cell:join", "radar:triage", "referral:log"]),
    ("nm-press", "Jordan Pike", "Duty press officer, Northmoor", "nmp", ["statement:draft", "statement:publish", "fact:add", "line:ack", "cell:join", "referral:log"]),
    ("nm-sio", "DCI Sam Oduya", "Senior Investigating Officer, Northmoor", "nmp", ["fact:verify", "fact:add", "statement:approve-sio", "disclosure:recommend", "cell:join"]),
    ("nm-gold", "ACC Rachel Thorne", "Gold commander, Northmoor", "nmp", ["cell:open", "statement:approve-gold", "disclosure:decide", "cell:join"]),
    ("nm-legal", "Martin Leigh", "Force legal adviser, Northmoor", "nmp", ["statement:legal", "cell:join"]),
    ("sv-comms", "Aisha Bell", "Communications manager, Severnvale", "svc", ["statement:draft", "statement:publish", "line:ack", "radar:triage", "referral:log", "cell:join"]),
    ("dg-comms", "Rhys Pritchard", "Bilingual communications officer, Dyfed-Glas", "dgp", ["statement:draft", "statement:publish", "line:ack", "line:localise", "radar:triage", "cell:join"]),
    ("km-comms", "Nadia Cole", "Head of Media, Kingsbridge", "kmp", ["statement:draft", "statement:publish", "line:ack", "radar:triage", "referral:log", "cell:join"]),
    ("ho-press", "Oliver Grange", "Home Office press officer", "ho", ["immigration:confirm", "brief:read"]),
    ("ho-psg", "Helen Marsh", "Home Office public safety official", "ho", ["brief:read"]),
    ("gov-info", "Ben Carver", "Government online information team liaison", "gov", ["state:receive", "brief:read"]),
    ("ctp", "DS Imran Kade", "Counter Terrorism Policing liaison", "ctp", ["state:receive", "referral:update", "brief:read"]),
    ("cps", "Joanna Price", "CPS area communications manager", "cps", ["statement:cps", "brief:read"]),
    ("col", "Dr Fiona Hale", "College of Policing learning lead", "col", ["audit:view", "debrief:write"]),
    ("pcc", "Gareth Moss", "Communications lead, Northmoor PCC office", "pcc", ["brief:read"]),
    ("eth", "Prof. Anne Lowry", "Chair, Independent Ethics Panel", "eth", ["audit:view"]),
]
personas = [{"id": p, "name": n, "role": r, "org": o, "caps": c, "synthetic": True} for p, n, r, o, c in personas]

# ---------------------------------------------------------------- places
places = [
    {"id": "port-ellery", "name": "Port Ellery", "force": "nmp", "x": 0.22, "y": 0.30},
    {"id": "harrowgate-vale", "name": "Harrowgate Vale", "force": "nmp", "x": 0.40, "y": 0.15},
    {"id": "castlewick", "name": "Castlewick", "force": "nmp", "x": 0.44, "y": 0.40},
    {"id": "brennford", "name": "Brennford", "force": "svc", "x": 0.55, "y": 0.58},
    {"id": "aberteg", "name": "Aberteg", "force": "dgp", "x": 0.16, "y": 0.60},
    {"id": "llanfair-is-coed", "name": "Llanfair-is-Coed", "force": "dgp", "x": 0.26, "y": 0.75},
    {"id": "kingsbridge-centre", "name": "Kingsbridge city centre", "force": "kmp", "x": 0.76, "y": 0.82},
]

# -------------------------------------------------------------- media and platforms
platforms = [
    {"id": "chirp", "name": "Chirp", "type": "Short-post social network (fictional)"},
    {"id": "vidstream", "name": "VidStream", "type": "Short video platform (fictional)"},
    {"id": "facespace", "name": "FaceSpace", "type": "Community groups platform (fictional)"},
    {"id": "groupcast", "name": "Groupcast", "type": "Public broadcast channels (fictional)"},
    {"id": "forumly", "name": "Forumly", "type": "Open discussion forum (fictional)"},
]
outlets = [
    {"id": "echo", "name": "Port Ellery Echo", "type": "Local newspaper (fictional)", "reliability": "established"},
    {"id": "nep", "name": "Northmoor Evening Post", "type": "Regional newspaper (fictional)", "reliability": "established"},
    {"id": "ledger", "name": "The National Ledger", "type": "National newspaper (fictional)", "reliability": "established"},
    {"id": "nbc1", "name": "Northern Broadcast One", "type": "Regional broadcaster (fictional)", "reliability": "established"},
    {"id": "brightline", "name": "Brightline News24", "type": "Unverified aggregator site (fictional)", "reliability": "low"},
    {"id": "spoof", "name": "northmoor-police-news.info", "type": "Spoof site imitating a force (fictional)", "reliability": "spoof"},
]

# ---------------------------------------------------------------- threat actors
# Tier rules come from the research report, section 5. All names are fictional.
actors = [
    {"id": "act-irondawn", "tier": "A", "name": "Iron Dawn Network", "fictional": True,
     "basis": "Fictional proscribed organisation (stands in for an entry on the Home Office proscribed list)",
     "allowed": "Track content and narratives; refer illegal content to CTIRU; flag symbols and slogans",
     "indicators": ["Black sun-and-anchor emblem (fictional)", "Slogan 'Dawn is coming' (fictional)"]},
    {"id": "act-lantern", "tier": "B", "name": "Lantern Bureau", "fictional": True,
     "basis": "Fictional state-linked influence operation named in a fictional government sanctions notice",
     "allowed": "Track narratives; pass indicators to CTP and government; never attribute publicly through police comms",
     "indicators": ["Spoof domains imitating forces (e.g. northmoor-police-news.info)", "Recycled templates across European cities"]},
    {"id": "act-harbourwatch", "tier": "C", "name": "Harbour Watch Patriots", "fictional": True,
     "basis": "Fictional street network whose organiser has a (fictional) public order conviction",
     "allowed": "Monitor public narratives and planned events only; monitoring of individuals needs a recorded RIPA authorisation",
     "indicators": ["Event pages for gatherings near asylum accommodation"]},
]
# Tier D: lawful but controversial. Never stored as entities. The app holds only
# this rule, and refuses any attempt to track such an account.
tier_d_rule = "Politicians, parties, campaigners, journalists and commentators are never entities in Line of Blue. Narrative and topic analysis only."

# ---------------------------------------------------------------- incidents and cases
incidents = [
    {"id": "INC-NMP-0412", "force": "nmp", "place": "port-ellery", "title": "Harbourside Market stabbing, Port Ellery",
     "type": "Critical incident", "declaredAt": 0, "status": "pending",
     "summary": "Two people injured, one seriously, at Harbourside Market at about 13:50. A man was arrested at the scene.",
     "case": {"id": "CASE-NMP-7781", "status": "arrested", "suspectAge": 34, "suspectName": "Callum Breward (fictional)",
              "suspectNationality": "British (fictional, verified by SIO at 15:10)", "sexualOffence": False, "childInvolved": False,
              "immigrationClaim": True},
     "gold": "nm-gold", "sio": "nm-sio"},
    {"id": "INC-SVC-0090", "force": "svc", "place": "brennford", "title": "Missing child found safe, Brennford",
     "type": "Missing person (resolved)", "declaredAt": None, "status": "pending",
     "summary": "A 9-year-old reported missing at 12:10 was found safe and well at a relative's home at 13:05.",
     "case": None, "gold": None, "sio": None},
    {"id": "INC-KMP-2211", "force": "kmp", "place": "kingsbridge-centre", "title": "March and counter-protest, Kingsbridge",
     "type": "Planned public order operation", "declaredAt": None, "status": "planned",
     "summary": "A march of about 6,000 and a counter-protest of about 800 are planned for Saturday afternoon.",
     "case": None, "gold": None, "sio": None},
    {"id": "INC-DGP-0031", "force": "dgp", "place": "aberteg", "title": "River Teg flood warning, Aberteg",
     "type": "Civil emergency (multi-agency)", "declaredAt": None, "status": "pending",
     "summary": "Severe flood warning for the lower Teg valley. Rest centre open at Ysgol Aberteg (fictional).",
     "case": None, "gold": None, "sio": None},
]
cases = [  # other live cases used by Safe to Say
    {"id": "CASE-SVC-3120", "force": "svc", "label": "Halden Street trial (Brennford Crown Court)", "status": "charged",
     "defendantAge": 16, "defendantName": "Kieran Doyle (fictional)", "sexualOffence": False, "childInvolved": True,
     "note": "Defendant is 16: reporting restrictions apply (YJCEA 1999 s.45)."},
    {"id": "CASE-KMP-0457", "force": "kmp", "label": "Rivermead sexual assault investigation", "status": "charged",
     "defendantAge": 41, "defendantName": "Mark Ellison (fictional)", "sexualOffence": True, "childInvolved": False,
     "complainantDetails": ["Rivermead Close", "aged 23", "café on Lower Quay"],
     "note": "Complainant has lifelong anonymity (Sexual Offences (Amendment) Act 1992)."},
]

# ---------------------------------------------------------------- narratives
narratives = [
    {"id": "NAR-01", "title": "False suspect identity: 'man from the Harbourside hotel'", "verdict": "false",
     "incident": "INC-NMP-0412", "places": ["port-ellery", "harrowgate-vale", "castlewick"], "risk": "critical",
     "claim": "The attacker is an asylum seeker living at the Harbourside hotel.",
     "truth": "The arrested man is a 34-year-old British man from Port Ellery (verified by the SIO).",
     "tags": ["suspect identity", "asylum", "disorder risk"], "actor": None},
    {"id": "NAR-02", "title": "Cover-up: 'police are hiding who did it'", "verdict": "misleading",
     "incident": "INC-NMP-0412", "places": ["port-ellery"], "risk": "high",
     "claim": "Police silence proves they are covering up the attacker's identity.",
     "truth": "Proceedings are active; police publish verified facts as they are confirmed.",
     "tags": ["cover-up", "trust"], "actor": None},
    {"id": "NAR-03", "title": "Recycled footage: 2019 disorder video posted as 'Port Ellery tonight'", "verdict": "false",
     "incident": "INC-NMP-0412", "places": ["port-ellery"], "risk": "high",
     "claim": "Video shows rioting in Port Ellery this afternoon.",
     "truth": "The clip is from an unrelated 2019 event in another country (fictional reverse-search match).",
     "tags": ["recycled media", "disorder"], "actor": None, "media": "recycled"},
    {"id": "NAR-04", "title": "Fake 'police curfew notice' on a spoof force website", "verdict": "false",
     "incident": "INC-NMP-0412", "places": ["port-ellery", "castlewick"], "risk": "high",
     "claim": "Northmoor Police has imposed a 6pm curfew on all residents.",
     "truth": "No curfew exists. The notice is on a spoof domain with indicators matching a state-linked network.",
     "tags": ["spoof", "state-linked indicators"], "actor": "act-lantern"},
    {"id": "NAR-05", "title": "Call to gather at the Harbourside hotel on Saturday night", "verdict": "mobilisation",
     "incident": "INC-NMP-0412", "places": ["port-ellery"], "risk": "critical",
     "claim": "Posts urge people to 'take back the harbour' at the hotel at 19:00, some with threats.",
     "truth": "A small share of posts contain threats and may be illegal content for referral.",
     "tags": ["mobilisation", "threats"], "actor": "act-harbourwatch"},
    {"id": "NAR-06", "title": "AI-generated image of an officer kneeling on a child", "verdict": "false",
     "incident": None, "places": ["kingsbridge-centre"], "risk": "medium",
     "claim": "Photo shows a Kingsbridge officer kneeling on a child at the march.",
     "truth": "The image carries generation artefacts and matches no event (fictional forensic check).",
     "tags": ["synthetic media", "protest"], "actor": None, "media": "ai-generated"},
    {"id": "NAR-07", "title": "'Two-tier policing' at the Kingsbridge march", "verdict": "opinion",
     "incident": "INC-KMP-2211", "places": ["kingsbridge-centre"], "risk": "medium",
     "claim": "Police treat one side of the march more leniently than the other.",
     "truth": "Contested opinion. Lawful speech: monitor the narrative only; respond with facts about the policing plan.",
     "tags": ["impartiality", "protest", "lawful opinion"], "actor": None},
    {"id": "NAR-08", "title": "'Second child taken' rumour in Brennford", "verdict": "false",
     "incident": "INC-SVC-0090", "places": ["brennford"], "risk": "medium",
     "claim": "A second child has been abducted from the same park.",
     "truth": "No second child is missing. The first child was found safe at 13:05.",
     "tags": ["child safety", "rumour"], "actor": None},
    {"id": "NAR-09", "title": "Flood hoax: 'dam about to fail, evacuate now' (Welsh and English)", "verdict": "false",
     "incident": "INC-DGP-0031", "places": ["aberteg", "llanfair-is-coed"], "risk": "high",
     "claim": "Llyn Teg dam is failing and everyone must leave immediately.",
     "truth": "The dam is sound (fictional reservoir operator). Follow the official flood warning only.",
     "tags": ["civil emergency", "Welsh language"], "actor": None},
    {"id": "NAR-10", "title": "Jury speculation in the Halden Street trial", "verdict": "contempt risk",
     "incident": None, "places": ["brennford"], "risk": "medium",
     "claim": "Posts name the 16-year-old defendant and claim he has previous convictions.",
     "truth": "Reporting restrictions apply. Refer contempt breaches; police comms must not repeat details.",
     "tags": ["contempt", "youth", "trial"], "actor": None},
]

# ---------------------------------------------------------------- post templates
T = {
    "NAR-01": ["Hearing it was a bloke from the Harbourside hotel. Police won't say. Why not?",
               "My cousin works near the market. Says the guy came out of the hotel this morning.",
               "So it's the hotel lot again. How many more times?",
               "Name going round is foreign. Police confirming nothing. Make of that what you will.",
               "Everyone knows where he's from. They just won't say it.",
               "Shared from Brightline: 'Harbourside suspect is recent arrival, sources say'"],
    "NAR-02": ["Three hours and not a word on who did it. Cover-up as usual.",
               "If it was one of us they'd have his face everywhere by now.",
               "Police statement says nothing. What are they hiding?",
               "Silence from Northmoor Police. Draw your own conclusions."],
    "NAR-03": ["Port Ellery right now. It's kicking off.", "This is the harbour tonight, look at it",
               "Riots already starting in Port Ellery. Stay away from town."],
    "NAR-04": ["Curfew from 6pm tonight in Port Ellery, police notice here: northmoor-police-news.info",
               "Just got sent this, 6pm curfew for everyone? Is this real?",
               "Official: Northmoor Police curfew. Stay indoors after 6."],
    "NAR-05": ["Harbourside hotel 7pm Saturday. Take back the harbour.",
               "Everyone down the hotel tonight, bring your mates.",
               "Time for talking is over. Hotel. 7pm.",
               "[THREAT] They'll get what's coming at 7. (synthetic threat text for referral testing)"],
    "NAR-06": ["Look at this. Kingsbridge police kneeling on a CHILD.", "This photo should end careers. Kingsbridge march today."],
    "NAR-07": ["Watch how gently they treat the other lot. Two-tier policing.",
               "Different rules for different marches. Every time.",
               "Kingsbridge police escorting one side, kettling the other. Two-tier."],
    "NAR-08": ["Another child taken from the same park in Brennford?? Keep your kids in.",
               "Second kid missing in Brennford, police saying nothing"],
    "NAR-09": ["DAM IS FAILING. Leave Aberteg NOW.", "ARGAE YN TORRI. Gadewch Aberteg NAWR.",
               "Neighbour says the dam is going. Get to high ground."],
    "NAR-10": ["The Halden Street lad has form, everyone in Brennford knows it.",
               "Why is nobody naming him? He's 16 not 6."],
}
# schedule: (narrative, first minute, last minute, count, base reach)
schedule = [
    ("NAR-01", 12, 150, 36, 9000), ("NAR-02", 40, 170, 20, 5000), ("NAR-03", 55, 140, 12, 14000),
    ("NAR-04", 85, 160, 10, 7000), ("NAR-05", 95, 180, 16, 4000), ("NAR-06", 60, 150, 8, 11000),
    ("NAR-07", 20, 180, 18, 3000), ("NAR-08", -40, 25, 10, 6000), ("NAR-09", 30, 120, 12, 5000),
    ("NAR-10", -300, 180, 6, 900),
]
plat_for = {"NAR-03": ["vidstream", "chirp"], "NAR-04": ["chirp", "facespace"], "NAR-05": ["groupcast", "facespace", "chirp"],
            "NAR-06": ["chirp", "vidstream"], "NAR-09": ["facespace", "chirp"], "NAR-10": ["forumly", "facespace"]}
nar_by_id = {n["id"]: n for n in narratives}

def acct(seed):
    # Pseudonymous, hashed handle: Line of Blue never stores real account names.
    return "acct_" + hashlib.sha1(seed.encode()).hexdigest()[:6]

posts = []
pid = 0
for nid, t0, t1, n, reach in schedule:
    nar = nar_by_id[nid]
    for i in range(n):
        pid += 1
        # front-load growth so velocity curves look realistic
        frac = (i / max(1, n - 1)) ** 1.4
        t = int(t0 + frac * (t1 - t0) + random.randint(-4, 4))
        text = T[nid][i % len(T[nid])]
        p = {
            "id": f"P{pid:04d}", "narrative": nid, "t": t,
            "platform": random.choice(plat_for.get(nid, ["chirp", "facespace", "forumly", "vidstream"])),
            "account": acct(f"{nid}-{i % max(3, n // 2)}"),
            "place": random.choice(nar["places"]),
            "text": text,
            "lang": "cy" if text.startswith("ARGAE") else "en",
            "reach": int(reach * random.uniform(0.2, 1.8) * (1 + frac)),
            "shares": int(random.uniform(5, 400) * (1 + frac)),
            "flags": [],
            "synthetic": True,
        }
        if nar.get("media") == "recycled": p["flags"].append("recycled media")
        if nar.get("media") == "ai-generated": p["flags"].append("likely AI-generated")
        if "northmoor-police-news.info" in text: p["flags"].append("spoof domain")
        if text.startswith("[THREAT]"): p["flags"].append("possible illegal content")
        if nid == "NAR-10": p["flags"].append("possible contempt breach")
        posts.append(p)
posts.sort(key=lambda p: p["t"])

articles = [
    {"id": "A01", "outlet": "brightline", "t": 48, "title": "Harbourside suspect 'recent arrival', unnamed sources claim", "narrative": "NAR-01"},
    {"id": "A02", "outlet": "echo", "t": 20, "title": "Two hurt in Harbourside Market stabbing", "narrative": None},
    {"id": "A03", "outlet": "nep", "t": 75, "title": "Police appeal for calm as rumours spread online", "narrative": "NAR-02"},
    {"id": "A04", "outlet": "nbc1", "t": 110, "title": "Fake curfew notice circulating, say officials", "narrative": "NAR-04"},
    {"id": "A05", "outlet": "ledger", "t": 130, "title": "Port Ellery: how a false name spread in two hours", "narrative": "NAR-01"},
    {"id": "A06", "outlet": "spoof", "t": 86, "title": "NOTICE: Curfew in force from 18:00", "narrative": "NAR-04"},
    {"id": "A07", "outlet": "nep", "t": 5, "title": "Brennford child found safe", "narrative": "NAR-08"},
]

# ---------------------------------------------------------------- event horizon
events = [
    {"id": "EV01", "date": "2026-11-21", "title": "Kingsbridge march and counter-protest", "force": "kmp", "risk": "high", "kind": "protest", "prebunk": "Policing plan explainer and 'what to expect' Q&A"},
    {"id": "EV02", "date": "2026-11-23", "title": "Halden Street trial resumes, Brennford Crown Court", "force": "svc", "risk": "medium", "kind": "trial", "prebunk": "Reporting restrictions reminder for partners"},
    {"id": "EV03", "date": "2026-11-26", "title": "Northmoor mayoral by-election (pre-election period from 12 Nov)", "force": "nmp", "risk": "medium", "kind": "election", "prebunk": "Impartiality guidance for all Northmoor content", "purdah": True},
    {"id": "EV04", "date": "2026-11-28", "title": "Northmoor v Severnvale derby, Castlewick", "force": "nmp", "risk": "medium", "kind": "sport", "prebunk": "Travel and ticket fraud advice"},
    {"id": "EV05", "date": "2026-12-03", "title": "Anniversary of the 2025 Castlewick disorder", "force": "nmp", "risk": "high", "kind": "anniversary", "prebunk": "Community reassurance message with partners"},
    {"id": "EV06", "date": "2026-12-08", "title": "Sentencing: Rivermead case", "force": "kmp", "risk": "medium", "kind": "sentencing", "prebunk": "Complainant anonymity reminder"},
    {"id": "EV07", "date": "2026-12-12", "title": "Winter festival, Kingsbridge", "force": "kmp", "risk": "low", "kind": "major event", "prebunk": "Safety campaign"},
    {"id": "EV08", "date": "2026-12-15", "title": "Inspection report on online disorder response published", "force": None, "risk": "medium", "kind": "publication", "prebunk": "NPCC response lines"},
]

# ---------------------------------------------------------------- national lines library
lines = [
    {"id": "LN-001", "title": "Misinformation during live investigations", "status": "approved", "expires": "2026-12-31",
     "text": "We understand the public want answers quickly. We publish facts once they are confirmed. Please do not share speculation about people involved, which can harm victims and the course of justice.",
     "cy": "Rydym yn deall bod y cyhoedd eisiau atebion yn gyflym. Rydym yn cyhoeddi ffeithiau unwaith y cânt eu cadarnhau. Peidiwch â rhannu dyfalu am bobl dan sylw.",
     "checks": ["Contempt", "Impartiality"], "owner": "nc-head"},
    {"id": "LN-002", "title": "Spoof police websites and notices", "status": "approved", "expires": "2027-03-31",
     "text": "Only trust information on your force's official website and verified accounts. If you see a notice that claims to be from the police, check it on our website before sharing.",
     "cy": "Ymddiriedwch yn unig mewn gwybodaeth ar wefan swyddogol eich heddlu a chyfrifon wedi'u dilysu.",
     "checks": ["Impartiality"], "owner": "nc-head"},
    {"id": "LN-003", "title": "Protest policing is impartial", "status": "approved", "expires": "2026-12-31",
     "text": "Police do not take sides. We facilitate lawful protest and act against crime whoever commits it.",
     "cy": "Nid yw'r heddlu'n cymryd ochr. Rydym yn hwyluso protest gyfreithlon.",
     "checks": ["Impartiality", "Pre-election"], "owner": "nc-head"},
    {"id": "LN-004", "title": "AI-generated and recycled images", "status": "expired", "expires": "2026-10-31",
     "text": "Old or fake images are being shared. Check the source before you share.", "cy": "", "checks": [], "owner": "nc-head"},
]

# ---------------------------------------------------------------- scenarios (multi-actor, end to end)
# Each step: who acts, what they do, which screen, and a machine check the app
# evaluates against demo state so progress ticks automatically.
scenarios = [
    {"id": "SC-01", "title": "Golden Hour: Harbourside Market stabbing",
     "goal": "Shrink time to truth on a false suspect identity, with every release legally checked and signed off.",
     "actors": ["nm-gold", "nm-press", "nm-sio", "nm-legal", "nc-insight", "nc-duty", "nc-head", "ho-press", "sv-comms", "dg-comms", "km-comms", "eth"],
     "steps": [
        {"t": 0, "actor": "nm-gold", "view": "golden-hour", "do": "Declare the critical incident and open the Golden Hour cell", "check": "cellOpen:INC-NMP-0412"},
        {"t": 10, "actor": "nm-press", "view": "golden-hour", "do": "Log the first facts: time, place, two injured, one man arrested", "check": "factCount:INC-NMP-0412:2"},
        {"t": 15, "actor": "nm-sio", "view": "golden-hour", "do": "Verify the facts in the fact log", "check": "factsVerified:INC-NMP-0412:2"},
        {"t": 20, "actor": "nm-press", "view": "safe-to-say", "do": "Draft a holding statement and run it through Safe to Say", "check": "statementAtLeast:INC-NMP-0412:checked"},
        {"t": 25, "actor": "nm-legal", "view": "golden-hour", "do": "Legal review of the holding statement", "check": "statementAtLeast:INC-NMP-0412:legal"},
        {"t": 28, "actor": "nm-sio", "view": "golden-hour", "do": "SIO approves the statement", "check": "statementAtLeast:INC-NMP-0412:sio"},
        {"t": 30, "actor": "nm-gold", "view": "golden-hour", "do": "Gold signs off; press officer publishes", "check": "statementAtLeast:INC-NMP-0412:published"},
        {"t": 60, "actor": "nc-insight", "view": "radar", "do": "Radar alert on NAR-01 (false identity). Triage it and link it to the incident", "check": "narrativeLinked:NAR-01"},
        {"t": 70, "actor": "nm-gold", "view": "golden-hour", "do": "Record a disclosure decision on nationality (interim ethnicity and nationality guidance)", "check": "disclosureDecided:INC-NMP-0412"},
        {"t": 75, "actor": "ho-press", "view": "inbox", "do": "Home Office responds to the request to confirm immigration status", "check": "hoResponded:INC-NMP-0412"},
        {"t": 90, "actor": "nc-duty", "view": "lines", "do": "Draft a national line on speculation about the suspect", "check": "lineDrafted:SC-01"},
        {"t": 95, "actor": "nc-head", "view": "lines", "do": "Approve and cascade the national line to all forces", "check": "lineCascaded:SC-01"},
        {"t": 100, "actor": "sv-comms", "view": "lines", "do": "Forces acknowledge the line (Severnvale, Dyfed-Glas with Welsh version, Kingsbridge)", "check": "lineAcks:SC-01:3"},
        {"t": 110, "actor": "eth", "view": "audit", "do": "Ethics panel reviews the decision trail: every decision has a named person and a reason", "check": "auditViewed"},
     ]},
    {"id": "SC-02", "title": "Spoof curfew notice with state-linked indicators",
     "goal": "Debunk a spoof notice fast, pass indicators to CTP and government, and never attribute publicly.",
     "actors": ["nc-insight", "nm-press", "ctp", "gov-info", "nc-head"],
     "steps": [
        {"t": 90, "actor": "nc-insight", "view": "radar", "do": "Triage NAR-04 and hand state-linked indicators to CTP and government", "check": "stateHandover:NAR-04"},
        {"t": 95, "actor": "ctp", "view": "inbox", "do": "CTP liaison accepts the handover", "check": "stateAccepted:NAR-04"},
        {"t": 100, "actor": "nm-press", "view": "safe-to-say", "do": "Draft a rebuttal. Safe to Say blocks any public attribution to a state actor", "check": "ruleFired:state-attribution"},
        {"t": 105, "actor": "nm-press", "view": "safe-to-say", "do": "Publish the corrected rebuttal (no attribution, points to official channels as in LN-002)", "check": "publishedMatch:no curfew"},
     ]},
    {"id": "SC-03", "title": "Mobilisation and threats: platform referral",
     "goal": "Refer possible illegal content to the platform and CTIRU, and track response times as evidence.",
     "actors": ["nc-insight", "nm-head", "ctp", "sib"],
     "steps": [
        {"t": 100, "actor": "sib", "view": "radar", "do": "SIB analyst assesses community tension for Port Ellery from NAR-05", "check": "tensionAssessed:port-ellery"},
        {"t": 105, "actor": "nc-insight", "view": "escalations", "do": "Log a referral of the threatening post to the platform", "check": "referralCount:1"},
        {"t": 140, "actor": "nc-insight", "view": "escalations", "do": "Record the platform's response and time taken", "check": "referralResolved:1"},
     ]},
    {"id": "SC-04", "title": "Two-tier narrative at a protest (lawful opinion)",
     "goal": "Respond with facts about the policing plan without treating lawful opinion as a threat or profiling commentators.",
     "actors": ["km-comms", "nc-insight", "eth"],
     "steps": [
        {"t": 30, "actor": "nc-insight", "view": "radar", "do": "Try to add the commentator account behind NAR-07 to a watchlist: Line of Blue refuses (Tier D)", "check": "guardrailRefused:tier-d"},
        {"t": 40, "actor": "km-comms", "view": "safe-to-say", "do": "Draft a policing plan explainer and pass the impartiality checks", "check": "statementPublishedBy:km-comms"},
     ]},
    {"id": "SC-05", "title": "Bilingual flood hoax (civil emergency)",
     "goal": "Counter a hoax in Welsh and English under the warning and informing duty.",
     "actors": ["dg-comms", "nc-duty"],
     "steps": [
        {"t": 35, "actor": "dg-comms", "view": "safe-to-say", "do": "Draft a bilingual rebuttal. Safe to Say flags a missing Welsh version until one is added", "check": "statementPublishedBy:dg-comms"},
     ]},
    {"id": "SC-06", "title": "Youth trial and complainant anonymity (hard blocks)",
     "goal": "Prove that drafts naming a child defendant or identifying a complainant cannot be released.",
     "actors": ["sv-comms", "km-comms", "cps"],
     "steps": [
        {"t": 0, "actor": "sv-comms", "view": "safe-to-say", "do": "Draft about the Halden Street trial that names the defendant: hard block", "check": "ruleFired:child-defendant"},
        {"t": 0, "actor": "km-comms", "view": "safe-to-say", "do": "Draft that mentions Rivermead Close and the complainant's age: hard block", "check": "ruleFired:complainant-anonymity"},
     ]},
    {"id": "SC-07", "title": "Get ahead: pre-bunk the spoof curfew before it appears",
     "goal": "Use the rumour forecast and the L.O.B Agent to publish a signed-off pre-bunk before the first spoof notice is posted.",
     "actors": ["nm-gold", "nm-head", "nm-press", "nm-legal", "nm-sio", "nc-insight"],
     "steps": [
        {"t": 0, "actor": "nm-gold", "view": "golden-hour", "do": "Declare the critical incident. The rumour forecast appears in the cell", "check": "cellOpen:INC-NMP-0412"},
        {"t": 4, "actor": "nm-head", "view": "agent", "do": "Ask the L.O.B Agent for a get-ahead plan, with the guidance it rests on", "check": "agentAsked:plan"},
        {"t": 8, "actor": "nm-press", "view": "golden-hour", "do": "Send the spoof-notice pre-bunk from the forecast to Safe to Say and submit it", "check": "prebunkAtLeast:NAR-04:checked"},
        {"t": 12, "actor": "nm-legal", "view": "golden-hour", "do": "Legal review of the pre-bunk", "check": "prebunkAtLeast:NAR-04:legal"},
        {"t": 14, "actor": "nm-sio", "view": "golden-hour", "do": "SIO approves the pre-bunk", "check": "prebunkAtLeast:NAR-04:sio"},
        {"t": 16, "actor": "nm-gold", "view": "golden-hour", "do": "Gold signs off the pre-bunk", "check": "prebunkAtLeast:NAR-04:gold"},
        {"t": 18, "actor": "nm-press", "view": "golden-hour", "do": "Publish the pre-bunk", "check": "prebunkAtLeast:NAR-04:published"},
        {"t": 90, "actor": "nc-insight", "view": "picture", "do": "On the National picture, confirm the police line was out before the first spoof notice", "check": "aheadOf:NAR-04"},
     ]},
    {"id": "SC-08", "title": "Strategy review and trend-led lines",
     "goal": "The Head of NPCC Comms asks the L.O.B Agent to mark up an inbound force strategy and a non-compliant holding line, decides each change, and the insight team turns an emerging trend into a checked line.",
     "actors": ["nc-head", "nc-insight", "nc-duty"],
     "steps": [
        {"t": 0, "actor": "nc-head", "view": "review", "do": "Open the Northmoor VAWG strategy and ask the L.O.B Agent for feedback", "check": "reviewRequested:DR-01"},
        {"t": 2, "actor": "nc-head", "view": "review", "do": "Accept or reject at least eight of the agent's proposed changes", "check": "reviewDecided:DR-01:8"},
        {"t": 4, "actor": "nc-head", "view": "review", "do": "Return the strategy to Northmoor for revision with the mark-up", "check": "reviewOutcome:DR-01"},
        {"t": 6, "actor": "nc-head", "view": "review", "do": "Mark up the Kingsbridge holding line and accept every must-fix change", "check": "redResolved:DR-02"},
        {"t": 8, "actor": "nc-insight", "view": "trends", "do": "Find the emerging trend the agent flagged and read why it was flagged", "check": "trendOpened:TR-01"},
        {"t": 10, "actor": "nc-duty", "view": "trends", "do": "Send the agent's proposed line for the trend to Safe to Say and submit it", "check": "trendLineChecked:TR-01"},
     ]},
]

# ---------------------------------------------------------------- core comms workflows and autonomy levels
# From the international research (19 Nov 2026): seven workflows, 28 sub-activities, five autonomy levels.
# 1 fully agentic, 2 agentic with human sign-off, 3 iterative human and agent, 4 human-led with agent QA, 5 fully human.
AUTONOMY = ["", "Fully agentic", "Agentic, human signs off", "Iterative human and agent", "Human-led, agent QA", "Fully human"]
_wf = [
    ("W1", "Early warning", "Identify", [("Watch public content against approved narrative and keyword sets", 1, "Approves the sets"), ("Spot acceleration and weak signals", 1, "Reviews flags"), ("Triage alerts and set severity", 2, "Duty officer confirms severity"), ("Daily national picture briefing", 2, "Head of comms signs off")]),
    ("W2", "Situational insight", "Insight", [("Group posts into narratives and map spread", 1, "Spot checks"), ("Assess harm and impact", 3, "Analyst and agent refine together"), ("Judge coordination or foreign involvement", 4, "Analyst decides; refer to CTP or partners"), ("Read community mood with neighbourhood teams", 4, "Officers report; agent summarises")]),
    ("W3", "Golden hour", "Response", [("Draft the holding line from confirmed facts", 2, "Gold or SIO approves"), ("Decide what to say, when and who says it", 5, "Gold, SIO and comms lead"), ("Legal and victim safety check", 4, "Comms lead or legal decides; agent flags risks"), ("Publish and cascade to forces, officers and partners", 2, "Approver presses send"), ("Keep the update rhythm and timeline", 3, "Comms lead sets rhythm")]),
    ("W4", "Rebuttal", "Response", [("Decide whether to respond (amplification risk)", 3, "Comms lead decides on agent's evidence"), ("Draft rebuttal and platform versions", 2, "Approver edits and signs off"), ("Escalate to platforms, Ofcom and fact-checkers", 4, "Named liaison sends; agent prepares the pack"), ("Update the Rumour and fact page", 2, "Approver signs off")]),
    ("W5", "Pre-bunking", "Strategic communication", [("Forecast likely rumours around events", 3, "Planner and agent refine"), ("Make pre-bunk content and local versions", 3, "Creative lead and agent"), ("Schedule, boost and repeat", 2, "Planner approves the calendar")]),
    ("W6", "Engagement", "Response", [("Answer routine public questions from approved lines", 1, "Reviews samples; new questions go to a human"), ("Media enquiries and briefings", 4, "Press officer leads; agent preps facts"), ("Contact with victims, families and affected communities", 5, "Family liaison and community leads only")]),
    ("W7", "Learning and governance", "Tracking", [("Log every decision, source and approval", 1, "Audit reviews"), ("Measure time to first fact, share of voice and narrative decay", 1, "Reviews the numbers"), ("Post-incident debrief and lessons", 3, "Debrief lead and agent"), ("Approve mandate, monitoring scope and keyword lists", 5, "Governance board"), ("Exercises and scenario training", 3, "Trainers and agent run scenarios")]),
    ("W8", "Strategy, policy and review", "Strategic communication", [("Scan public trends, bills, white papers and consultations", 1, "Agent; policy lead reviews the weekly digest"), ("Summarise what each proposal or trend means for policing", 2, "Portfolio lead signs off"), ("Agree the national position: support, support with conditions, challenge", 5, "Chiefs' council or portfolio lead"), ("Draft the strategy, statement and Q&A from the template", 3, "Comms lead and agent refine together"), ("Review inbound strategies and lines: mark-up for law, tone and behaviour change", 4, "Comms lead decides; agent marks up"), ("Give partners notice before release", 4, "Named lead makes the calls; agent prepares the pack"), ("Track coverage, reaction and outcomes", 1, "Agent; insight lead reviews")]),
]
workflows = [{"id": wid, "title": t, "resist": r, "steps": [{"id": f"{wid}.{i + 1}", "title": st, "level": lv, "role": role} for i, (st, lv, role) in enumerate(steps)]} for wid, t, r, steps in _wf]

world = {
    "meta": {"name": "Line of Blue synthetic demo world", "version": "1.0.0", "scenarioDate": SCENARIO_DATE,
             "clockStart": "13:50", "notice": "Entirely fictional. No real people, accounts, forces, places or groups. For demonstration and testing only.",
             "generatedBy": "scripts/generate_world.py (seed 20261121)"},
    "orgs": orgs, "personas": personas, "places": places, "platforms": platforms, "outlets": outlets,
    "actors": actors, "tierDRule": tier_d_rule, "incidents": incidents, "cases": cases,
    "narratives": narratives, "posts": posts, "articles": articles, "events": events, "lines": lines,
    "scenarios": scenarios,
    "knowledge": KNOWLEDGE, "playbooks": PLAYBOOKS, "workflows": workflows, "autonomy": AUTONOMY,
    "strategyTopics": RV.STRATEGY_TOPICS, "oasis": RV.OASIS, "drafts": RV.DRAFTS, "markCats": RV.CATS,
    "trends": {"days": RV.DAYS, "endDate": "2026-11-18", "sources": RV.SOURCES, "themes": RV.THEMES, "series": RV.trend_series(), "signals": RV.SIGNALS},
    "ukmap": json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "uk_map.json"))),
}

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "world.json"), "w", encoding="utf-8") as f:
    json.dump(world, f, ensure_ascii=False, indent=1)
for name, rows in [("posts", posts), ("personas", personas), ("narratives", narratives), ("events", events)]:
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(os.path.join(OUT, f"{name}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, restval="")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("; ".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})
print(f"personas={len(personas)} narratives={len(narratives)} posts={len(posts)} scenarios={len(scenarios)} steps={sum(len(s['steps']) for s in scenarios)}")
