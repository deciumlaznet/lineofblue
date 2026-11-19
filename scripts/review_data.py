"""Line of Blue: strategy and policy drafting support, inbound drafts for mark-up, and a
synthetic trend stream.

Everything here is fictional except the public frameworks and published campaigns named
as sources (behaviour change models, government guidance, international exemplars).
Forces, people, places, incidents and the conflict in "Karvelia" are invented.

Mark-up model: each inbound draft is a list of paragraphs plus a list of issues. An issue
points at an exact span of text ("find"). It either replaces the span ("repl"), deletes it
(repl ""), or adds text after it ("insert"). Every issue carries a category, a severity
(red = must fix before release, amber = should fix, blue = would improve), the reason in
plain words, and the knowledge base ids it relies on.
"""
import math
import random

GOV = "https://www.gov.uk/government/publications/"

# ------------------------------------------------------------------ behaviour change and strategy sources
BEHAVIOUR_KB = [
    {"id": "KB-COMB", "kind": "behaviour", "owner": "Michie, van Stralen and West (UCL), Implementation Science", "title": "COM-B model and the Behaviour Change Wheel (2011)",
     "url": "https://implementationscience.biomedcentral.com/articles/10.1186/1748-5908-6-42",
     "summary": "Behaviour happens when people have the Capability, the Opportunity and the Motivation to act. The wheel links each barrier to intervention types (education, persuasion, incentives, enablement, environmental restructuring) and policy levers.",
     "comms": "Name the one behaviour you want, from whom, then say which barrier stops it. Awareness alone rarely changes behaviour; pair messages with an easy route to act."},
    {"id": "KB-EAST", "kind": "behaviour", "owner": "Behavioural Insights Team", "title": "EAST: four simple ways to apply behavioural insights (2014)",
     "url": "https://www.bi.team/publications/east-four-simple-ways-to-apply-behavioural-insights/",
     "summary": "Make it Easy (simplify, remove friction, defaults), Attractive (attention, salience, rewards), Social (norms, networks, commitments) and Timely (prompt when people are most receptive; immediate costs and benefits).",
     "comms": "One action, one link or number, said at the moment people need it. Use accurate social norms ('most people...') and never normalise the harmful behaviour by saying how common it is."},
    {"id": "KB-MINDSPACE", "kind": "behaviour", "owner": "Cabinet Office and Institute for Government", "title": "MINDSPACE: influencing behaviour through public policy (2010)",
     "url": "https://www.instituteforgovernment.org.uk/publication/report/mindspace",
     "summary": "Nine robust influences on behaviour: Messenger, Incentives, Norms, Defaults, Salience, Priming, Affect, Commitments, Ego. Written for government as a checklist for policy and communication design.",
     "comms": "Choose the messenger the audience trusts (often not the police), and check the message for priming and affect that could backfire, such as fear appeals without a clear action."},
    {"id": "KB-GCSBEH", "kind": "behaviour", "owner": "Government Communication Service", "title": "Strategic communication: a behavioural approach (GCS, 2018)",
     "url": "https://gcs.civilservice.gov.uk/publications/strategic-communication-a-behavioural-approach/",
     "summary": "GCS guide to using behavioural science in government campaigns: define the behaviour, understand the audience through insight, design with the barriers in mind, test and evaluate.",
     "comms": "Every campaign objective should be a behaviour or attitude that can be measured, not an output such as posts or press releases."},
    {"id": "KB-OASIS", "kind": "behaviour", "owner": "Government Communication Service", "title": "OASIS campaign planning guide (GCS)",
     "url": "https://gcs.civilservice.gov.uk/guidance/marketing/delivering-government-campaigns/guide-to-campaign-planning-oasis/",
     "summary": "Objectives, Audience insight, Strategy and ideas, Implementation, Scoring (evaluation). The standard structure for every UK government communication plan.",
     "comms": "Line of Blue uses OASIS as the spine of every strategy template and as the first test in a strategy review."},
    {"id": "KB-GCSEVAL", "kind": "behaviour", "owner": "Government Communication Service", "title": "GCS Evaluation Cycle and evaluation framework",
     "url": "https://gcs.civilservice.gov.uk/publications/gcs-evaluation-cycle/",
     "summary": "Measure inputs, outputs, outtakes, intermediate outcomes and final outcomes, with baselines and targets set before launch.",
     "comms": "Set a baseline and a target for each objective before launch. Reach and impressions are outputs, not results."},
    {"id": "KB-COLLWW", "kind": "behaviour", "owner": "College of Policing", "title": "What Works Centre for Crime Reduction and the Crime Reduction Toolkit",
     "url": "https://www.college.police.uk/research/crime-reduction-toolkit",
     "summary": "Rates the evidence for crime prevention interventions by effect, mechanism, moderators, implementation and economic cost (EMMIE).",
     "comms": "Check that a prevention message asks for a behaviour with evidence behind it, and that it does not shift responsibility onto potential victims."},
    {"id": "KB-VAWG", "kind": "strategy", "owner": "NPCC and College of Policing", "title": "Policing VAWG national framework for delivery, and the government ambition to halve VAWG in a decade",
     "url": "https://www.npcc.police.uk/our-work/violence-against-women-and-girls/",
     "summary": "Three pillars: build trust and confidence, relentless pursuit of perpetrators, safer spaces. The government has committed to halving VAWG within a decade.",
     "comms": "Put the focus on perpetrators and on men's behaviour, not on what women should do to stay safe. Victim-blaming language undermines trust and reporting."},
    {"id": "KB-CSEAUDIT", "kind": "inspection", "owner": "Baroness Casey for the Home Office", "title": "National audit on group-based child sexual exploitation and abuse (June 2025)",
     "url": GOV + "national-audit-on-group-based-child-sexual-exploitation-and-abuse",
     "summary": "Found failures to protect children, poor data, and that ethnicity was not recorded in most cases, which let the issue be avoided. Recommended mandatory recording of ethnicity and nationality for suspects, and a national inquiry, which the government accepted.",
     "comms": "Lead with victims and survivors, be specific about what has changed and by when, and be factual about ethnicity data rather than avoiding or generalising."},
    {"id": "KB-PRAP", "kind": "strategy", "owner": "NPCC and College of Policing", "title": "Police Race Action Plan (2022, with progress reports)",
     "url": "https://www.college.police.uk/support-forces/diversity-and-inclusion/police-race-action-plan",
     "summary": "Policing's commitment to be anti-racist and to tackle race disparities in use of force, stop and search, workforce representation and Black victims' experience, overseen by an independent scrutiny board.",
     "comms": "Acknowledge the evidence of disparity, say what is being done and how progress is measured, and avoid defensive 'vast majority' framing that reads as dismissing lived experience."},
    {"id": "KB-CONTEST", "kind": "strategy", "owner": "Home Office", "title": "CONTEST: UK counter-terrorism strategy (2023) and the Prevent duty",
     "url": GOV + "counter-terrorism-strategy-contest-2023",
     "summary": "Prevent, Pursue, Protect, Prepare. Prevent applies to all ideologies; the 2023 Shawcross review asked for a sharper focus on the threat.",
     "comms": "Describe ideologies and behaviours, never communities. Publicise ACT and 'Run Hide Tell' for public preparedness; only CTP comments on terrorism investigations."},
    {"id": "KB-POA", "kind": "law", "owner": "UK Parliament", "title": "Public Order Act 1986 ss.12 and 14, and Public Order Act 2023", "url": "https://www.legislation.gov.uk/ukpga/1986/64",
     "summary": "Police may impose conditions on processions and assemblies to prevent serious disorder, damage, disruption or intimidation. Displaying a lawful national flag is not an offence; support for a proscribed group is (Terrorism Act 2000 ss.12-13).",
     "comms": "Explain the conditions and the legal test. Do not threaten arrest for lawful expression, and do not characterise a whole protest by the conduct of a few."},
    {"id": "KB-SPIKE", "kind": "policy", "owner": "Home Office", "title": "Spiking: government actions and new offence commitment",
     "url": "https://www.gov.uk/government/news/spiking-to-be-made-a-specific-criminal-offence",
     "summary": "Government plans to make spiking a specific offence, with police training and venue guidance; spiking is already an offence under existing law.",
     "comms": "Tell people how to report and get tested quickly (urine tests within 12 hours, blood within 72), and focus warnings on perpetrators, not on victims' drinking."},
    {"id": "KB-LFR", "kind": "guidance", "owner": "College of Policing", "title": "Live facial recognition APP and Bridges v South Wales Police [2020] EWCA Civ 1058",
     "url": "https://www.college.police.uk/app/live-facial-recognition",
     "summary": "Forces must publish where and why they deploy, the watchlist criteria, and that non-matched images are deleted immediately. The Court of Appeal found an early deployment unlawful for lack of clear rules and an equality assessment.",
     "comms": "Say in advance where and when, who is on the watchlist and why, and that other images are deleted. Do not overstate accuracy."},
    {"id": "KB-FRAUD", "kind": "policy", "owner": "Home Office and City of London Police", "title": "Fraud strategy and Stop! Think Fraud campaign; report to Report Fraud and 7726",
     "url": "https://stopthinkfraud.campaign.gov.uk/",
     "summary": "Fraud is the most common crime in England and Wales. The national campaign uses one consistent call to action. Suspicious texts can be forwarded free to 7726.",
     "comms": "Use the national call to action and wording so the public hears one voice. 'Police will never ask you to...' is the most remembered line."},
]

# ------------------------------------------------------------------ strategy template library
# Each topic: id, title, cluster, why it is hard for NPCC Comms, the behaviour sought, audiences,
# sensitivities, the measures that matter, sources (KB ids) and a global exemplar.
T = lambda *a: dict(zip(["id", "title", "cluster", "challenge", "behaviour", "audiences", "sensitivities", "measures", "kb", "exemplar"], a))
STRATEGY_TOPICS = [
    T("ST-VAWG", "Violence against women and girls", "Protecting people", "Trust is low after high-profile officer offending; messages that tell women to change their behaviour cause backlash.",
      "Men challenge misogyny among peers; women and girls report, and trust they will be believed.", ["Men 18-34", "Women and girls", "Bystanders", "Night-time economy staff"],
      ["Victim blaming", "Officer misconduct cases", "Anonymity (SOAA 1992)"], ["Reporting rates and attrition", "Confidence among women (CSEW)", "Peer intervention intent"], ["KB-VAWG", "KB-COMB", "KB-EAST", "KB-SOAA92"],
      "Police Scotland 'Don't Be That Guy' (2021) spoke to men about everyday misogyny; Australia's 'Stop it at the Start' targets the attitudes of parents and influencers."),
    T("ST-CSE", "Child sexual exploitation and grooming gangs", "Protecting people", "Past failures, a national inquiry, and intense political and far-right exploitation of the issue.",
      "Survivors come forward; professionals and the public report concerns.", ["Survivors", "Parents and carers", "Taxi, hotel and fast-food staff", "Local communities"],
      ["Ethnicity data and generalisation", "Survivor anonymity", "Active trials", "Exploitation by extremists"], ["Referrals and disclosures", "Survivor confidence", "Trust in local response"], ["KB-CSEAUDIT", "KB-SOAA92", "KB-CCA81", "KB-EQUAL"],
      "The Casey audit (2025) shows candour on data is now expected; the NSPCC and Barnardo's 'Spot the signs' work uses trusted non-police messengers."),
    T("ST-RASSO", "Rape and serious sexual offences (Operation Soteria)", "Protecting people", "Charge rates and attrition are low; survivors fear not being believed and intrusive digital requests.",
      "Survivors report and stay engaged with the investigation.", ["Survivors", "ISVAs and support services", "Universities"], ["Anonymity", "Digital evidence and Art 8", "Consent myths"],
      ["Reports", "Victim withdrawal", "Charge rate"], ["KB-SOAA92", "KB-ART8", "KB-COMB"], "Operation Soteria national operating model; 'Consent is everything' style myth-busting in Scotland and New Zealand."),
    T("ST-DA", "Domestic abuse", "Protecting people", "Victims face practical barriers to reporting; seasonal spikes (football tournaments, Christmas).",
      "Victims and concerned others seek help through a safe route.", ["Victims", "Friends and family", "Pharmacy and workplace staff"], ["Perpetrators monitoring devices", "Safe exits on websites"],
      ["Helpline and Ask for ANI use", "Repeat victimisation"], ["KB-COMB", "KB-EAST"], "Home Office 'Ask for ANI' codeword scheme in pharmacies (2021); Spain's VioGén risk system and coordinated public messaging."),
    T("ST-SPIKE", "Spiking", "Protecting people", "Fear spreads faster than facts on social media, and early warnings often told victims to watch their drinks.",
      "People report quickly and get tested; venue staff act.", ["Students", "Venue staff", "Parents"], ["Victim blaming", "Unverified injection claims"], ["Time from incident to report", "Tests taken"],
      ["KB-SPIKE", "KB-EAST", "KB-VAWG"], "University and venue partnerships with testing kits and 'Ask for Angela'."),
    T("ST-IMM", "Immigration, asylum and hotel protests", "Public order and security", "Policy is government's to explain, not policing's; misinformation about residents drives disorder.",
      "Lawful protest stays lawful; people do not share claims about individuals.", ["Local residents", "Protest organisers", "Hotel residents and staff", "Local media"],
      ["Only the Home Office confirms immigration status", "Political impartiality", "Speculation about suspects"], ["Tension indicators", "Arrests for disorder", "Rumour reach after the police line"],
      ["KB-ETHNAT", "KB-IMPART", "KB-POA", "KB-HMIC24"], "Southport and 2024 disorder lessons (HMICFRS 2024): fill the information void early, with facts."),
    T("ST-PRAP", "Police Race Action Plan", "Confidence and legitimacy", "Black communities report lower trust; defensive language is quickly called out.",
      "Black communities see change they can check; officers understand why it matters.", ["Black communities", "Community groups", "Officers and staff"], ["Defensiveness", "Data accuracy", "Use of force footage"],
      ["Trust and confidence by ethnicity", "Disproportionality ratios", "Scrutiny board findings"], ["KB-PRAP", "KB-EQUAL"], "Police Race Action Plan independent scrutiny and community oversight model."),
    T("ST-FAR", "Far-right extremism", "Public order and security", "Online mobilisation is fast; amplifying a group's name can help it.",
      "Young people at risk seek support; the public reports concerns.", ["Parents", "Teachers", "Gaming and online communities"], ["Amplification", "Proscribed groups", "Free speech"],
      ["Prevent referrals by ideology", "ACT reports"], ["KB-CONTEST", "KB-TACT", "KB-HRA1011"], "EXIT-Deutschland exit programme; the Christchurch Call on terrorist content online."),
    T("ST-ISL", "Islamist extremism and Prevent", "Public order and security", "Prevent is contested in some Muslim communities; mistakes damage trust.",
      "Concerned family and friends seek help early.", ["Families", "Faith leaders", "Schools"], ["Stigmatising communities", "Shawcross review findings"], ["Referrals", "Community confidence"],
      ["KB-CONTEST", "KB-EQUAL"], "Denmark's Aarhus model of early intervention with families."),
    T("ST-CT", "Terrorism threat level and public preparedness", "Public order and security", "Messages must raise vigilance without fear.",
      "People know what to do in an attack and report suspicious activity.", ["General public", "Venue and event staff"], ["Fear appeals", "Live investigations (CTP lead)"], ["ACT awareness", "Run Hide Tell recall"],
      ["KB-CONTEST", "KB-MINDSPACE"], "ACT 'Run Hide Tell' (2017) and Protect duty (Martyn's Law) training."),
    T("ST-WAR", "War, international conflict and protest", "Public order and security", "Protests about overseas wars divide communities; any wording can read as taking sides.",
      "Protest remains peaceful and lawful; communities report hate crime.", ["Protest groups", "Affected diaspora communities", "Jewish and Muslim communities"],
      ["Impartiality", "Flags, chants and proscription", "Hate crime"], ["Hate crime reports", "Disorder", "Community confidence"], ["KB-POA", "KB-HRA1011", "KB-TACT", "KB-IMPART"],
      "Clear, published conditions for large marches with an explainer of the law (UK policing practice since 2023)."),
    T("ST-PROT", "Public order and protest", "Public order and security", "Policing is criticised from all sides; conditions are often misreported.",
      "Organisers engage early and follow conditions.", ["Organisers", "Counter-protesters", "Businesses"], ["Art 10 and 11", "Impartiality"], ["Conditions complied with", "Complaints"],
      ["KB-POA", "KB-HRA1011"], "Swedish and Danish 'dialogue police' models."),
    T("ST-KNIFE", "Knife crime and serious violence", "Crime types", "Fear messages can make young people more likely to carry.",
      "Young people do not carry, and know most peers do not.", ["Young people 12-24", "Parents", "Youth workers"], ["Fear appeals", "Stereotyping"], ["Carrying intent", "Admissions for assault with a sharp object"],
      ["KB-COMB", "KB-EAST", "KB-COLLWW"], "Glasgow Violence Reduction Unit (2005) public health approach; accurate social norms ('most young people don't carry')."),
    T("ST-CLINES", "County lines and child criminal exploitation", "Crime types", "Exploited children are victims, not just offenders.",
      "Adults spot and report signs of exploitation.", ["Parents", "Rail and bus staff", "Teachers"], ["Language about 'gangs'", "Child anonymity"], ["Referrals", "Safeguarding outcomes"],
      ["KB-CYPA49", "KB-COMB"], "The Children's Society '#LookCloser' campaign with British Transport Police."),
    T("ST-HATE", "Hate crime", "Crime types", "Under-reporting is high; non-crime hate incidents are politically contested.",
      "Victims report, including through third-party centres.", ["Victims", "Faith and disability groups"], ["NCHI policy changes", "Free speech"], ["Reports", "Satisfaction"],
      ["KB-NCHI", "KB-EQUAL", "KB-HRA1011"], "True Vision third-party reporting."),
    T("ST-MISOG", "Standards, vetting and misogyny in policing", "Confidence and legitimacy", "Each new case reopens the Casey review findings on the Met.",
      "Public and staff report misconduct; trust recovers.", ["Women", "Staff", "Media"], ["Live misconduct proceedings", "Officer anonymity orders"], ["Trust", "Reports of misconduct"],
      ["KB-IMPART", "KB-VAWG"], "Publishing vetting outcomes and dismissals in full."),
    T("ST-SAS", "Stop and search", "Confidence and legitimacy", "Disproportionality and viral footage.",
      "Communities understand their rights; officers explain grounds.", ["Young Black men", "Parents", "Scrutiny panels"], ["Use of force footage", "Data accuracy"], ["Disproportionality", "Complaints"],
      ["KB-PRAP", "KB-EQUAL"], "Community scrutiny panels publishing body-worn video reviews."),
    T("ST-MH", "Mental health and Right Care Right Person", "Confidence and legitimacy", "Change is misread as police 'walking away'.",
      "People in crisis reach the right service first.", ["Health partners", "Public", "Families"], ["Deaths in custody", "Partner tension"], ["Police time on health calls", "Outcomes for people in crisis"],
      ["KB-COMB"], "Humberside Police Right Care Right Person (2020) and the national partnership agreement (2023)."),
    T("ST-FRAUD", "Fraud and cyber crime", "Crime types", "Fraud is the most common crime but feels low priority to the public.",
      "People stop, check and report.", ["Older people", "Small businesses", "Young people (money mules)"], ["Victim shame"], ["Reports", "Losses prevented", "7726 forwards"],
      ["KB-FRAUD", "KB-EAST"], "Australia's Scamwatch and the UK 'Stop! Think Fraud' single call to action."),
    T("ST-ONLINE", "Online child sexual abuse", "Protecting people", "Parents feel helpless; offenders exploit platforms.",
      "Parents talk to children; children report.", ["Parents", "Children 8-15", "Schools"], ["Platform liability", "Image sharing"], ["Reports to CEOP", "Parental conversations"],
      ["KB-OSA", "KB-COMB"], "AFP ThinkUKnow and CEOP Education."),
    T("ST-MSHT", "Modern slavery and human trafficking", "Crime types", "Victims are hidden and may fear police.", "Public and businesses report signs.", ["Car wash and nail bar customers", "Businesses"],
      ["Immigration status", "Victim identification"], ["Referrals (NRM)"], ["KB-COMB"], "Unseen helpline partnerships."),
    T("ST-ROAD", "Road safety", "Crime types", "Messages are familiar and ignored.", "Drivers stop the 'fatal four' behaviours.", ["Young male drivers", "Commercial drivers"], ["Graphic content"], ["Killed and seriously injured"],
      ["KB-EAST", "KB-MINDSPACE"], "Victoria's TAC 'Towards Zero' and its long-run evaluation."),
    T("ST-ELEC", "Elections and defending democracy", "Events and elections", "Pre-election rules, threats to candidates, and deepfakes.",
      "Candidates report threats; voters check sources.", ["Candidates", "Electoral officers", "Voters"], ["Pre-election period", "Impartiality", "Foreign interference"], ["Reports by candidates", "Deepfake takedown time"],
      ["KB-PURDAH", "KB-IMPART", "KB-NSA", "KB-RESIST"], "Sweden's Psychological Defence Agency (2022); Taiwan's 'humour over rumour'."),
    T("ST-MAJ", "Major events", "Events and elections", "Huge audiences and many partners.", "Visitors plan travel and know how to get help.", ["Visitors", "Residents", "Businesses"], ["Terror threat", "Ticketless fans"], ["Incidents", "Satisfaction"],
      ["KB-JESIP", "KB-CONTEST"], "London 2012 and Paris 2024 joint information cells."),
    T("ST-FOOT", "Football disorder", "Events and elections", "Fans distrust police; tournaments bring spikes in domestic abuse.", "Fans comply with bans and travel advice.", ["Fans", "Clubs"], ["Collective blame"], ["Arrests", "Banning orders"],
      ["KB-POA"], "Casey review of the Euro 2020 final (2021)."),
    T("ST-NPS", "National Police Service and police reform", "Reform and resources", "Structural change worries staff and the public; it is government policy.",
      "Staff and public understand what changes and what stays.", ["Officers and staff", "PCCs", "Public"], ["Political impartiality", "Staff consultation"], ["Staff understanding", "Media accuracy"],
      ["KB-WHITE26", "KB-IMPART"], "New Zealand's 2017 police reform and Scotland's 2013 merger lessons."),
    T("ST-FUND", "Police funding and demand", "Reform and resources", "Asking for money can read as political lobbying.", "Decision makers act on evidence.", ["Government", "Parliament", "Public"], ["Impartiality", "Pre-election"], ["Coverage accuracy"],
      ["KB-IMPART", "KB-PURDAH"], "Evidence-led submissions such as the NPCC spending review case."),
    T("ST-RECR", "Recruitment and retention", "Reform and resources", "Leaving rates are high; the workforce is not representative.", "Under-represented groups apply and stay.", ["Women", "Ethnic minority candidates", "Career changers"], ["Gendered language", "Overpromising"], ["Applications by group", "Retention"],
      ["KB-EQUAL", "KB-EAST", "KB-PRAP"], "Police Now and positive action programmes."),
    T("ST-NBH", "Neighbourhood policing guarantee", "Reform and resources", "Promises are tested street by street.", "Residents know their team and how to contact it.", ["Residents", "Councillors"], ["Overpromising", "Political ownership"], ["Know your neighbourhood officer", "Confidence"],
      ["KB-WHITE26", "KB-IMPART"], "Published named-officer pages and ward meetings."),
    T("ST-ASB", "Antisocial behaviour", "Crime types", "Low-level harm with high public concern.", "People report and use the community trigger.", ["Residents", "Housing providers"], ["Naming young people"], ["Reports", "Repeat locations"],
      ["KB-CYPA49"], "Community trigger publicity."),
    T("ST-RETAIL", "Retail crime", "Crime types", "Viral videos fuel 'police don't come'.", "Retailers report with evidence; the public sees results.", ["Retailers", "Shop workers", "Public"], ["Naming suspects", "Overpromising attendance"], ["Reports", "Charges"],
      ["KB-CCA81", "KB-COMB"], "Retail crime action plans with published attendance commitments."),
    T("ST-IOPC", "Deaths and serious injury after police contact", "Confidence and legitimacy", "The IOPC leads; police comment is constrained and grief is high.", "Families and communities trust the process.", ["Family", "Community", "Media"],
      ["IOPC independence", "Footage release", "Contempt"], ["Community tension", "Complaints"], ["KB-CCA81", "KB-ART8", "KB-APP"], "IOPC release of footage protocols."),
    T("ST-LFR", "Facial recognition and AI in policing", "Confidence and legitimacy", "Privacy concerns and accuracy claims.", "The public understands safeguards.", ["Privacy groups", "Public"], ["Accuracy claims", "Bias"], ["Trust in technology use"],
      ["KB-LFR", "KB-DPA", "KB-EQUAL"], "Published deployment records and watchlist policies."),
    T("ST-PRIS", "Prison capacity and early release", "Reform and resources", "Government policy with public safety concerns.", "Victims know their rights to information.", ["Victims", "Public"], ["Policy is government's", "Impartiality"], ["Victim contact"],
      ["KB-IMPART"], "Victim contact scheme publicity."),
    T("ST-CLIM", "Climate and disruptive protest", "Public order and security", "Disruption versus rights; accusations of bias from both sides.", "Protest stays within the law.", ["Organisers", "Commuters"], ["Art 10 and 11", "Impartiality"], ["Disruption minutes", "Complaints"],
      ["KB-POA", "KB-HRA1011"], "Published operational updates during major disruption."),
    T("ST-WELL", "Officer and staff wellbeing", "Reform and resources", "Stigma about mental health.", "Staff seek support early.", ["Officers", "Staff", "Families"], ["Privacy"], ["Uptake of support", "Sickness"],
      ["KB-COMB"], "Oscar Kilo, the national police wellbeing service."),
]

OASIS = [
    ("Objectives", "What will change, for whom, by how much, by when? Policy aim, communication objective (a behaviour or attitude), and a measurable target with a baseline."),
    ("Audience insight", "Who must act or think differently? What do they believe now, what stops them (COM-B: capability, opportunity, motivation), and whom do they trust?"),
    ("Strategy and ideas", "The single-minded proposition, the messengers, the behavioural levers (EAST, MINDSPACE), partners, and what you will not say."),
    ("Implementation", "Channels, timeline and triggers, sign-off, Welsh language, accessibility, risk register (legal, impartiality, community tension), and the information void plan."),
    ("Scoring", "Outputs, outtakes and outcomes with baselines and targets (GCS evaluation framework); when you will review and what would make you change course."),
]

# ------------------------------------------------------------------ inbound drafts with mark-up
def I(find, cat, sev, why, kb, repl=None, insert=None):
    d = {"find": find, "cat": cat, "sev": sev, "why": why, "kb": kb}
    if insert is not None:
        d["insert"] = insert
    else:
        d["repl"] = repl if repl is not None else ""
    return d

CATS = {"law": "Law and compliance", "accuracy": "Accuracy", "tone": "Tone and language", "behaviour": "Behaviour change", "complete": "Missing", "impartial": "Impartiality", "access": "Accessibility and Welsh", "structure": "Strategy structure"}

DRAFTS = [
    {"id": "DR-01", "kind": "strategy", "topic": "ST-VAWG", "from": "nm-head", "org": "nmp", "t": -120, "title": "Northmoor Police VAWG communications strategy 2027 (draft v0.3)",
     "ask": "Claire Fenwick has sent the Northmoor VAWG comms strategy for national alignment before it goes to the force's chief officer group.",
     "paras": [
        "1. Purpose. This strategy sets out how Northmoor Police will raise awareness of violence against women and girls (VAWG) across the county in 2027.",
        "2. Objectives. Raise awareness of VAWG. Increase engagement on social media by 20%. Show that Northmoor Police takes VAWG extremely seriously and has zero tolerance.",
        "3. Audience. Women and girls in Northmoor.",
        "4. Key messages. Women should avoid walking alone at night and should always plan their route home. Never leave your drink unattended. If you are an alleged victim, call us and we will investigate.",
        "5. Context. VAWG has gone up by 300% in Northmoor, which shows it is an epidemic.",
        "6. Channels. Press releases, Facebook, X and posters in police stations. We will issue a press release every month.",
        "7. Case studies. We will use the Brook Lane case to show the impact, including the victim's photo and the street where it happened, as it got a lot of coverage.",
        "8. Evaluation. Success will be measured by the number of press releases issued and total impressions.",
     ],
     "issues": [
        I("raise awareness of violence against women and girls (VAWG) across the county", "behaviour", "amber", "Awareness is not a behaviour and cannot be measured as a result. The national framework asks for trust, pursuit of perpetrators and safer spaces. Name the behaviours you want: men challenging misogyny, women and girls reporting.", ["KB-COMB", "KB-VAWG", "KB-GCSBEH"],
          repl="increase reporting of VAWG by women and girls, and get men to challenge misogyny among their peers, in support of the national ambition to halve VAWG in a decade"),
        I("Raise awareness of VAWG. Increase engagement on social media by 20%.", "structure", "amber", "Engagement is an output. OASIS objectives need a baseline, a target and a date for an outcome you can check.", ["KB-OASIS", "KB-GCSEVAL"],
          repl="(a) Increase the share of women in Northmoor who say they would report sexual harassment to police from the 2026 baseline to a target agreed with the PCC by March 2028. (b) Increase men aged 18 to 34 who say they would intervene if a friend harassed a woman (survey baseline in January 2027)."),
        I("has zero tolerance", "tone", "amber", "'Zero tolerance' is an unprovable promise and invites stories about cases that were not pursued. Say what you will do instead.", ["KB-APP", "KB-VAWG"],
          repl="will relentlessly pursue perpetrators, including officers and staff who offend"),
        I("Women and girls in Northmoor.", "complete", "amber", "The strategy speaks only to potential victims. The behaviour that has to change is men's. Add perpetrators, bystanders, night-time economy staff, and partners such as universities and support services, with the insight that shows what each believes now.", ["KB-COMB", "KB-MINDSPACE", "KB-VAWG"],
          repl="Primary: men aged 18 to 34 (behaviour: challenge misogyny among peers). Secondary: women and girls (behaviour: report, knowing they will be believed). Enablers: bar and taxi staff, universities, independent sexual violence advisers. Insight to gather: the 2026 force confidence survey and focus groups with Northmoor University students."),
        I("Women should avoid walking alone at night and should always plan their route home. Never leave your drink unattended.", "tone", "red", "This is victim-blaming. It places responsibility on women, contradicts the national VAWG framework and has caused public backlash for forces that used it. Focus on perpetrators and bystanders.", ["KB-VAWG", "KB-COLLWW", "KB-SPIKE"],
          repl="Harassment and abuse are a choice the perpetrator makes. If you see a mate cross the line, say something. If it happens to you, you will be believed: report it online, on 101 or in an emergency on 999."),
        I("alleged victim", "tone", "amber", "'Alleged victim' signals disbelief to the very people you need to come forward. Use 'victim' or 'survivor' in public messages; legal precision about allegations belongs in case reporting, not in prevention campaigns.", ["KB-VAWG"], repl="victim"),
        I("call us and we will investigate", "behaviour", "blue", "Make it easy: give the exact routes, including ones that do not mean phoning police, and say what happens next.", ["KB-EAST"],
          repl="report online, on 101, through an independent sexual violence adviser, or in an emergency on 999. We will keep you updated and you can bring someone with you"),
        I("VAWG has gone up by 300% in Northmoor, which shows it is an epidemic.", "accuracy", "red", "No source, no time period, and a rise in recorded crime often reflects more reporting rather than more offending. 'Epidemic' frightens people without telling them what to do. Use a sourced figure and explain what it means.", ["KB-APP", "KB-GCSEVAL"],
          repl="[Insert sourced figure: recorded VAWG offences in Northmoor, 2023 to 2026, from the force performance dataset.] Part of the rise reflects more people coming forward, which we welcome."),
        I("Press releases, Facebook, X and posters in police stations.", "behaviour", "blue", "The people you need to reach rarely visit police stations. Use the messengers they trust and the places they already are.", ["KB-MINDSPACE", "KB-EAST"],
          repl="Partner channels first: university and students' union channels, sports clubs, licensed venues and gyms, plus Instagram, TikTok and Snapchat with creators the audience trusts. Police channels for reporting routes and outcomes."),
        I("including the victim's photo and the street where it happened", "law", "red", "Hard block. If Brook Lane involved a sexual offence the complainant has lifelong anonymity, and a photo or street can identify her. Even without a sexual offence, using a victim's image needs her informed consent.", ["KB-SOAA92", "KB-ART8"],
          repl="only with the survivor's informed, written consent, through her independent adviser, and never with details that could identify her"),
        I("Success will be measured by the number of press releases issued and total impressions.", "structure", "amber", "These are outputs. Score against the objectives: reporting rates, confidence among women, men's intent to intervene, and attrition.", ["KB-GCSEVAL", "KB-OASIS"],
          repl="Success will be measured against the objectives above: reporting rates and attrition, confidence among women (force survey and CSEW), and men's intent to intervene (pre and post campaign survey). Reach and engagement will be tracked as outputs only."),
        I("We will issue a press release every month.", "complete", "blue", "Add the risk and sign-off plan: what you will do if an officer is charged with a VAWG offence mid-campaign, who signs off, and how you will measure and adapt.", ["KB-OASIS", "KB-APP"],
          insert=" Risks: an officer charged with a VAWG offence during the campaign (holding line prepared, campaign paused for review); backlash to men-focused content (moderation plan). Sign-off: Head of Corporate Communications and the force VAWG lead."),
     ],
     "assessment": {"verdict": "Return for revision", "summary": "A sincere draft that would currently do harm: the key messages blame victims, the case study would breach anonymity, and the objectives cannot be measured. The structure is fixable in a day using the OASIS template. Re-centre it on men's behaviour and on confidence to report.",
                    "scores": {"Objectives": 1, "Audience insight": 0, "Strategy and ideas": 1, "Implementation": 1, "Scoring": 0}, "comb": {"Capability": "partly", "Opportunity": "missing", "Motivation": "missing"}}},

    {"id": "DR-02", "kind": "line", "topic": "ST-RASSO", "from": "km-comms", "org": "kmp", "t": -40, "title": "Kingsbridge holding line: arrest after an assault near Ashford Road",
     "ask": "Kingsbridge want the national desk to sense-check a holding line before it goes out this afternoon.",
     "paras": [
        "A 42-year-old man from Kingsbridge, who is known to police for similar offences, has been arrested after a 15-year-old girl from Ashford Road School was sexually assaulted on Tuesday evening.",
        "We are confident we have got the right man and the community can be reassured.",
        "Anyone with information should contact us.",
     ],
     "issues": [
        I(", who is known to police for similar offences,", "law", "red", "Previous convictions or police history must not be mentioned once proceedings are active (from arrest). It creates a substantial risk of serious prejudice.", ["KB-CCA81", "KB-APP"], repl=""),
        I("a 15-year-old girl from Ashford Road School", "law", "red", "Hard block. A complainant of a sexual offence has lifelong anonymity, and age plus school can identify her. She is also a child.", ["KB-SOAA92", "KB-CYPA49"], repl="a teenage girl"),
        I("We are confident we have got the right man and the community can be reassured.", "law", "red", "Comment on guilt before charge is contempt risk and can collapse a trial. Reassure with facts about what police are doing instead.", ["KB-CCA81", "KB-CPSPROT"],
          repl="He remains in custody and enquiries are continuing. Officers are carrying out extra patrols in the area and are available to speak to anyone with concerns."),
        I("Anyone with information should contact us.", "behaviour", "blue", "Give the route and a reference so people can act straight away, and signpost support.", ["KB-EAST"],
          repl="Anyone with information should call 101 or report online quoting reference 44/2611, or contact Crimestoppers anonymously on 0800 555 111. Support for anyone affected by sexual violence is available from [local support service]."),
     ],
     "assessment": {"verdict": "Do not publish", "summary": "Three hard blocks: police history after arrest, details that identify a child complainant, and comment on guilt. With the changes accepted it becomes a safe, factual holding line.", "scores": None, "comb": None}},

    {"id": "DR-03", "kind": "line", "topic": "ST-IMM", "from": "sv-comms", "org": "svc", "t": -25, "title": "Severnvale line: arrest after a disturbance near the Riverside Hotel",
     "ask": "Severnvale want to get ahead of rumours about the man arrested near the hotel used to house asylum seekers.",
     "paras": [
        "A man arrested last night after a disturbance in Castle Street is believed to be an asylum seeker staying at the Riverside Hotel.",
        "We know feelings are running high about the hotel and we understand residents' frustration with government policy.",
        "A protest is planned for Saturday. Anyone causing trouble will be arrested.",
     ],
     "issues": [
        I("is believed to be an asylum seeker staying at the Riverside Hotel", "law", "red", "Police do not speculate on immigration status; only the Home Office confirms it, and 'believed to be' spreads a claim that may be false. Linking him to the hotel puts its residents at risk. If misinformation is causing tension, the interim guidance allows confirming verified nationality and ethnicity, with the decision recorded.", ["KB-ETHNAT", "KB-CCA81", "KB-HMIC24"],
          repl="is a 29-year-old man. He remains in custody. Please do not share claims about who he is or where he lives: they are not from us and can put people at risk"),
        I("and we understand residents' frustration with government policy", "impartial", "red", "Police must be politically impartial. Commenting on asylum policy, sympathetically or otherwise, is outside the police role.", ["KB-IMPART", "KB-APP"], repl=""),
        I("Anyone causing trouble will be arrested.", "law", "amber", "Peaceful protest is a right. Explain the legal basis for any conditions and the specific behaviour that will lead to arrest.", ["KB-POA", "KB-HRA1011"],
          repl="We will facilitate peaceful protest. Conditions under the Public Order Act will be published on our website on Friday, and anyone who commits offences, including intimidation of hotel residents or staff, will be dealt with."),
     ],
     "assessment": {"verdict": "Do not publish", "summary": "The line repeats the rumour it hopes to calm and takes a view on government policy. The rewrite fills the information void with verified facts and a clear position on lawful protest. Check whether a Home Office confirmation is needed before saying any more.", "scores": None, "comb": None}},

    {"id": "DR-04", "kind": "line", "topic": "ST-CSE", "from": "nc-duty", "org": "npcc", "t": -15, "title": "National line: response to the (fictional) Northmoor CSE review",
     "ask": "Tom Ashdown drafted the national response to a fictional independent review into child sexual exploitation in Northmoor, for publication tomorrow at 10:00.",
     "paras": [
        "The NPCC welcomes the review into so-called grooming gangs in Northmoor. Lessons have been learned.",
        "It is important to remember that the Asian community is not responsible for the actions of a few.",
        "Policing has changed beyond recognition since these events.",
     ],
     "issues": [
        I("welcomes the review into so-called grooming gangs in Northmoor. Lessons have been learned.", "tone", "amber", "'Welcomes' and 'lessons have been learned' read as complacent when children were failed, and 'so-called' minimises it. Start with the survivors and an apology where the review finds failure, then name what will change.", ["KB-CSEAUDIT", "KB-APP"],
          repl="accepts the findings of the review into group-based child sexual exploitation in Northmoor. Children were failed, and we are sorry. Policing will act on every recommendation: progress will be published every quarter, starting in March."),
        I("It is important to remember that the Asian community is not responsible for the actions of a few.", "accuracy", "amber", "Well meant, but it introduces a broad ethnic label the review may not use, and it reads as deflection. The Casey audit asks for candour on data: state what the review found about offenders, factually, and what is now recorded.", ["KB-CSEAUDIT", "KB-EQUAL"],
          repl="The review sets out what is known about the offenders, including their ethnicity, and we will not avoid that. All forces now record the ethnicity and nationality of suspects in these cases."),
        I("Policing has changed beyond recognition since these events.", "complete", "amber", "An unevidenced claim, and survivors have heard it before. Replace it with specifics, and signpost support for survivors.", ["KB-CSEAUDIT", "KB-EAST"],
          repl="Anyone who was abused, at any time, can report to us and will be listened to: call 101 or report online. Support is available from the NSPCC on 0808 800 5000 and from local survivor services."),
     ],
     "assessment": {"verdict": "Approve with changes", "summary": "Short and calm, but defensive in a way survivors and the media will notice. The rewrite apologises where the review finds failure, is factual about ethnicity, commits to dates, and gives survivors a route.", "scores": None, "comb": None}},

    {"id": "DR-05", "kind": "line", "topic": "ST-PRAP", "from": "nm-head", "org": "nmp", "t": -60, "title": "Northmoor response: race disparity in use of force figures",
     "ask": "A local paper has asked Northmoor about new figures showing Black people are four times more likely to have force used on them.",
     "paras": [
        "The vast majority of our officers do a fantastic job and are not racist.",
        "Use of force is always a last resort and every use is justified.",
        "We are committed to the Police Race Action Plan.",
     ],
     "issues": [
        I("The vast majority of our officers do a fantastic job and are not racist.", "tone", "amber", "Defensive 'vast majority' framing answers a question nobody asked and reads as dismissing the disparity. Acknowledge the figure first.", ["KB-PRAP"],
          repl="These figures show Black people in Northmoor are four times more likely to have force used on them than white people. That disparity is not acceptable and we have to understand and reduce it."),
        I("every use is justified", "accuracy", "red", "An absolute claim the force cannot evidence, and some uses may be under review or before the IOPC. It also risks prejudging misconduct proceedings.", ["KB-APP", "KB-DEFAM"],
          repl="every use is recorded and reviewed, and body-worn video is examined by our independent scrutiny panel"),
        I("We are committed to the Police Race Action Plan.", "complete", "amber", "Commitment without actions. Say what you are doing, by when, and how the public can check.", ["KB-PRAP", "KB-GCSEVAL"],
          insert=" By June we will publish use of force data by ethnicity every quarter, with the scrutiny panel's findings, and community members can join the panel."),
     ],
     "assessment": {"verdict": "Approve with changes", "summary": "Rewrite leads with the evidence, avoids an unprovable absolute, and turns commitment into checkable actions.", "scores": None, "comb": None}},

    {"id": "DR-06", "kind": "line", "topic": "ST-NPS", "from": "nc-duty", "org": "npcc", "t": -10, "title": "NPCC response to a (fictional) cut in neighbourhood funding",
     "ask": "Draft reactive line for the national desk on a fictional Treasury decision to reduce the neighbourhood policing grant. Note: a by-election is under way in Kingsbridge.",
     "paras": [
        "This Government's reckless decision will put lives at risk and shows ministers do not care about community safety.",
        "Chief constables will have no choice but to close stations.",
        "Vote for the candidates who back the police.",
     ],
     "issues": [
        I("This Government's reckless decision will put lives at risk and shows ministers do not care about community safety.", "impartial", "red", "Police leaders can and should set out operational impact, but this is party-political and attacks ministers' motives. A by-election is under way, so pre-election guidance also applies. Make the case on evidence.", ["KB-IMPART", "KB-PURDAH"],
          repl="Chief constables are assessing the operational impact of the change to the neighbourhood policing grant. Our initial estimate is that it would fund around [number] fewer neighbourhood officers in 2027-28."),
        I("will have no choice but to close stations", "accuracy", "amber", "A prediction presented as fact. Decisions on stations are local and may not follow. Say what is known and when you will say more.", ["KB-APP"],
          repl="will set out what this means locally once budgets are confirmed in February. We will share our assessment with the Home Office"),
        I("Vote for the candidates who back the police.", "impartial", "red", "Hard block. Police bodies must never advise people how to vote.", ["KB-IMPART", "KB-PURDAH"], repl=""),
     ],
     "assessment": {"verdict": "Do not publish", "summary": "Pushback on government policy is legitimate when it is evidence-led and non-partisan. This version is a campaign leaflet. The rewrite keeps the force of the argument (impact in officers) without the politics.", "scores": None, "comb": None}},

    {"id": "DR-07", "kind": "line", "topic": "ST-WAR", "from": "km-comms", "org": "kmp", "t": -90, "title": "Kingsbridge line: march over the (fictional) Karvelia conflict",
     "ask": "Kingsbridge plan to publish this ahead of Saturday's march about the war in Karvelia.",
     "paras": [
        "We will not tolerate hate marchers on our streets this weekend.",
        "Anyone waving a Karvelian flag will be arrested.",
        "Officers will be out in force.",
     ],
     "issues": [
        I("We will not tolerate hate marchers on our streets this weekend.", "impartial", "red", "Labels a whole protest as hateful before it happens, takes a side in a divisive issue, and will inflame tensions. Describe what police will do and the law.", ["KB-IMPART", "KB-HRA1011", "KB-POA"],
          repl="A march about the conflict in Karvelia will take place in Kingsbridge on Saturday. We will police it to keep everyone safe and to protect the right to protest."),
        I("Anyone waving a Karvelian flag will be arrested.", "law", "red", "Wrong in law. Displaying a national flag is lawful. Support for a proscribed organisation is an offence, as are hate crimes and breach of conditions.", ["KB-POA", "KB-TACT"],
          repl="Conditions will be published on Friday. Showing support for a proscribed organisation, or chants and placards that stir up racial or religious hatred, are offences and will be dealt with"),
        I("Officers will be out in force.", "complete", "blue", "Tell communities who may feel targeted how to report hate crime, and give a route for organisers.", ["KB-EAST", "KB-EQUAL"],
          repl="Officers will be visible throughout. If you experience or witness hate crime, report it to any officer, online or through True Vision. Organisers can contact our protest liaison team on 101."),
     ],
     "assessment": {"verdict": "Do not publish", "summary": "Two legal errors and a partisan label. The rewrite is firm about offences, neutral about the cause, and reassures communities on both sides.", "scores": None, "comb": None}},

    {"id": "DR-08", "kind": "line", "topic": "ST-MAJ", "from": "dg-comms", "org": "dgp", "t": -5, "title": "Dyfed-Glas traffic line: A487 closure (English only)",
     "ask": "Dyfed-Glas duty officer drafted this for the force's social channels.",
     "paras": [
        "Op THUNDER is now live. Due to an RTC the A487 is closed in both directions between J4 and J6. MOPs should avoid the area and RV at alternative routes. ETA for reopening TBC.",
        "#A487 #Traffic",
     ],
     "issues": [
        I("Op THUNDER is now live. Due to an RTC the A487 is closed in both directions between J4 and J6. MOPs should avoid the area and RV at alternative routes.", "access", "amber", "Police jargon (Op, RTC, MOPs, RV) excludes most readers. Plain English, with the alternative route spelled out.", ["KB-EAST", "KB-APP"],
          repl="The A487 is closed both ways between Aberglas and Llanfair after a crash. Please avoid the area: use the B4333 through Pontmawr instead."),
        I("ETA for reopening TBC.", "behaviour", "blue", "'TBC' leaves people refreshing the page. Say when the next update will come.", ["KB-EAST"], repl="We will update you by 3pm."),
        I("#A487 #Traffic", "access", "red", "Dyfed-Glas is a Welsh force: public messages must be published in Welsh and English, with Welsh treated no less favourably.", ["KB-WELSH"],
          insert="\n\nMae'r A487 ar gau i'r ddau gyfeiriad rhwng Aberglas a Llanfair ar ôl gwrthdrawiad. Osgowch yr ardal: defnyddiwch y B4333 drwy Bontmawr. Byddwn yn rhoi diweddariad erbyn 3pm. [Welsh to be checked by the force translation service.]"),
     ],
     "assessment": {"verdict": "Approve with changes", "summary": "Accurate but unreadable to the public and English only. The rewrite is plain, gives one action, and adds the Welsh version for checking.", "scores": None, "comb": None}},

    {"id": "DR-09", "kind": "line", "topic": "ST-RECR", "from": "nm-head", "org": "nmp", "t": -200, "title": "Northmoor recruitment post",
     "ask": "Recruitment campaign post for Northmoor's careers channels.",
     "paras": [
        "Northmoor Police needs more manpower! Do you have what it takes to become one of our brave policemen? Applications are now open via the portal subject to eligibility criteria and vetting requirements as set out in the candidate information pack.",
     ],
     "issues": [
        I("more manpower", "tone", "amber", "Gendered language deters women, who the force needs to recruit to be representative.", ["KB-EQUAL", "KB-PRAP"], repl="more officers"),
        I("Do you have what it takes to become one of our brave policemen?", "behaviour", "amber", "'Policemen' excludes, and 'do you have what it takes' triggers self-doubt in under-represented groups. Use a social norm and real people.", ["KB-EQUAL", "KB-MINDSPACE", "KB-EAST"],
          repl="Nurses, carers, shop managers and coaches have all joined us this year. Bring what you already know about people."),
        I("Applications are now open via the portal subject to eligibility criteria and vetting requirements as set out in the candidate information pack.", "behaviour", "blue", "Make it easy: one link, one deadline, and a low-commitment first step.", ["KB-EAST"],
          repl="Apply by 31 January at northmoor.police.uk/join (fictional), or come to an open evening first and ask anything."),
     ],
     "assessment": {"verdict": "Approve with changes", "summary": "Easy fixes: inclusive language, a social norm, and one clear call to action.", "scores": None, "comb": None}},
]

# ------------------------------------------------------------------ trend stream
DAYS = 42  # 8 Oct to 18 Nov 2026; day 41 is yesterday
THEMES = [
    {"id": "TR-01", "title": "Spiking claims at Kingsbridge student venues", "force": "kmp", "topic": "ST-SPIKE", "shape": "surge", "base": 4, "start": 32, "peak": 39, "kb": ["KB-SPIKE", "KB-VAWG", "KB-EAST"],
     "drivers": "Three posts from one student account cluster reshared across TikTok and Instagram; two venues named; one verified report of a suspected spiking on 14 Nov.",
     "truth": "One spiking report is under investigation. Claims of 'dozens of injections' are not supported by reports or hospital data.",
     "line": "We are investigating one report of suspected spiking at a venue in Kingsbridge on 14 November. We have not received other reports, but we want to hear from anyone who thinks they were spiked. Report it straight away online or on 101, or 999 in an emergency, and get tested quickly: you will be believed. Spiking is a crime and the responsibility lies with the person who does it.",
     "prebunk": "Seen posts about 'injection spiking' in Kingsbridge? Check what we have confirmed on our page before sharing."},
    {"id": "TR-02", "title": "Fake 'police fine' text messages", "force": "national", "topic": "ST-FRAUD", "shape": "ramp", "base": 10, "start": 20, "peak": 41, "kb": ["KB-FRAUD", "KB-EAST"],
     "drivers": "Reports to 7726 and calls to forces about a text claiming an unpaid 'police speeding fine' with a payment link; spread across all four forces.",
     "truth": "Police never send texts asking for payment of fines.",
     "line": "Police will never text you asking you to pay a fine. If you get a text like this, do not click the link. Forward it free to 7726 and report it to Report Fraud. If you have paid, call your bank straight away on the number on the back of your card.",
     "prebunk": ""},
    {"id": "TR-03", "title": "Calls to protest at the Riverside Hotel, Severnvale", "force": "svc", "topic": "ST-IMM", "shape": "spike", "base": 3, "start": 40, "peak": 40, "kb": ["KB-ETHNAT", "KB-POA", "KB-IMPART", "KB-HMIC24"],
     "drivers": "Posts after the Castle Street arrest (DR-03) claim the man lives at the hotel; a Telegram channel linked to Harbour Watch Patriots (fictional, Tier C) shares a meeting time.",
     "truth": "No information has been released about where the arrested man lives.",
     "line": "A man arrested after a disturbance in Castle Street on Tuesday remains in custody. Claims online about who he is or where he lives have not come from us. Please do not share them: they can put innocent people at risk. We will facilitate peaceful protest on Saturday, and conditions will be published on Friday.",
     "prebunk": "Before sharing claims about the Castle Street arrest, check what we have actually confirmed."},
    {"id": "TR-04", "title": "'Police don't come to shoplifting' videos", "force": "nmp", "topic": "ST-RETAIL", "shape": "ramp", "base": 6, "start": 16, "peak": 41, "kb": ["KB-COMB", "KB-CCA81"],
     "drivers": "Viral clips from two Northmoor shops; local media enquiries rising; retail association statement on 10 Nov.",
     "truth": "Northmoor attended 71% of reported retail crimes with a suspect present in October (synthetic figure).",
     "line": "Shop workers should never have to face abuse or theft. In October we attended 71% of reported shoplifting where a suspect was present, and charged 112 people. Every report helps us target repeat offenders and hotspots, so please report every incident, with CCTV, online or on 101.",
     "prebunk": ""},
    {"id": "TR-05", "title": "Facial recognition van in Port Ellery", "force": "nmp", "topic": "ST-LFR", "shape": "spike", "base": 2, "start": 35, "peak": 36, "kb": ["KB-LFR", "KB-DPA"],
     "drivers": "Photos of a marked live facial recognition van; claims it 'stores everyone's face'; a privacy group post.",
     "truth": "Non-matched images are deleted immediately; the deployment and watchlist criteria were published (synthetic).",
     "line": "Live facial recognition was used in Port Ellery town centre on 13 November between 10am and 4pm to look for people wanted for serious offences. If you are not on the watchlist your image is deleted immediately and automatically. Details of where and why we deploy, and our watchlist policy, are on our website.",
     "prebunk": ""},
    {"id": "TR-06", "title": "Old flood footage reshared, Dyfed-Glas", "force": "dgp", "topic": "ST-MAJ", "shape": "flat", "base": 5, "start": 0, "peak": 0, "kb": ["KB-RESIST"],
     "drivers": "Background resharing of 2020 footage during heavy rain.", "truth": "", "line": "", "prebunk": ""},
    {"id": "TR-07", "title": "Remembrance weekend disorder rumours", "force": "national", "topic": "ST-PROT", "shape": "decay", "base": 3, "start": 29, "peak": 31, "kb": ["KB-POA"],
     "drivers": "Peaked around 8 to 11 November, now fading.", "truth": "", "line": "", "prebunk": ""},
    {"id": "TR-08", "title": "Knife 'gang map' of Northmoor estates", "force": "nmp", "topic": "ST-KNIFE", "shape": "ramp", "base": 2, "start": 34, "peak": 41, "kb": ["KB-COMB", "KB-EAST", "KB-COLLWW"],
     "drivers": "An image claiming to map 'gang territories' shared in parent groups; names three estates.",
     "truth": "The map is not from police and does not reflect police data.",
     "line": "A 'gang map' being shared online is not from us and is not based on police information. Most young people in Northmoor never carry a knife. If you are worried about a young person, talk to them, or speak to your neighbourhood team. Information can be given anonymously to Fearless.org.",
     "prebunk": ""},
]
SOURCES = ["Public posts", "Media enquiries", "Calls to 101", "Partner reports"]
MIX = {"TR-01": [0.72, 0.1, 0.12, 0.06], "TR-02": [0.35, 0.05, 0.4, 0.2], "TR-03": [0.85, 0.08, 0.05, 0.02], "TR-04": [0.6, 0.25, 0.05, 0.1],
       "TR-05": [0.75, 0.15, 0.05, 0.05], "TR-06": [0.9, 0.02, 0.05, 0.03], "TR-07": [0.8, 0.1, 0.05, 0.05], "TR-08": [0.7, 0.05, 0.1, 0.15]}


def trend_series(seed=20261119):
    rnd = random.Random(seed)
    out = []
    for th in THEMES:
        b, s, p, sh = th["base"], th["start"], th["peak"], th["shape"]
        vals = []
        for d in range(DAYS):
            if sh == "surge":
                lvl = b if d < s else b + (28 if d >= p else 28 * (d - s + 1) / (p - s + 1))
            elif sh == "ramp":
                lvl = b if d < s else b * (1 + 2.6 * (d - s) / (p - s + 1))
            elif sh == "spike":
                lvl = b if d < s else b + 22 * math.exp(-abs(d - p) / 1.3)
            elif sh == "decay":
                lvl = b if d < s else b + 16 * math.exp(-max(0, d - p) / 2.2) * (1 if d >= p else (d - s + 1) / (p - s + 1))
            else:
                lvl = b + 1.2 * math.sin(d / 3)
            if d % 7 in (5, 6):
                lvl *= 0.85
            vals.append(max(0, round(lvl + rnd.gauss(0, max(1, lvl ** 0.5) * 0.7))))
        out.append({"id": th["id"], "daily": vals, "mix": MIX[th["id"]]})
    return out


SIGNALS = [  # sample event items shown on the trend feed (all synthetic)
    {"d": 33, "theme": "TR-01", "src": "Public posts", "text": "Student account posts that 'loads of girls got injected' at a Kingsbridge club; 4,100 views in six hours."},
    {"d": 35, "theme": "TR-01", "src": "Partner reports", "text": "Kingsbridge University welfare team reports rising anxiety among first-year students."},
    {"d": 37, "theme": "TR-01", "src": "Calls to 101", "text": "One report of suspected spiking at a venue on Union Street; victim taken to hospital and tested."},
    {"d": 40, "theme": "TR-01", "src": "Media enquiries", "text": "Kingsbridge Courier asks whether police are 'covering up' a spate of injections."},
    {"d": 22, "theme": "TR-02", "src": "Calls to 101", "text": "Severnvale call handlers log 14 calls about a 'police fine' text in one shift."},
    {"d": 36, "theme": "TR-02", "src": "Partner reports", "text": "Mobile network partner reports 7726 forwards of the fake fine text up sharply."},
    {"d": 40, "theme": "TR-03", "src": "Public posts", "text": "Post claims the Castle Street suspect 'lives at the Riverside'; 12,000 shares overnight."},
    {"d": 41, "theme": "TR-03", "src": "Public posts", "text": "Channel linked to Harbour Watch Patriots (fictional) posts a Saturday meeting time outside the hotel."},
    {"d": 30, "theme": "TR-04", "src": "Media enquiries", "text": "Regional TV asks for Northmoor attendance figures after a viral shoplifting clip."},
    {"d": 40, "theme": "TR-04", "src": "Partner reports", "text": "Northmoor retail association says members 'have stopped reporting'."},
    {"d": 36, "theme": "TR-05", "src": "Public posts", "text": "Photo of the facial recognition van with claim 'they store everyone's face for 30 years'."},
    {"d": 36, "theme": "TR-08", "src": "Public posts", "text": "'Gang map' image naming three Northmoor estates shared in local parent groups."},
    {"d": 40, "theme": "TR-08", "src": "Partner reports", "text": "Two schools report parents keeping children home after seeing the map."},
]
