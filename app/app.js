/* Line of Blue synthetic demo. Vanilla JS, no build step, no network calls.
   WORLD (synthetic data) is injected by scripts/build.py. All data is fictional. */
(function () {
  'use strict';
  const W = window.LINE_OF_BLUE_WORLD;
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const byId = (arr) => Object.fromEntries(arr.map((x) => [x.id, x]));
  const P = byId(W.personas), O = byId(W.orgs), N = byId(W.narratives), I = byId(W.incidents), PL = byId(W.places), PF = byId(W.platforms), SC = byId(W.scenarios), A = byId(W.actors), C = byId(W.cases);
  const STORE = 'lineofblue-demo-state-v1';
  const STAGES = ['draft', 'checked', 'legal', 'sio', 'gold', 'published'];
  const STAGE_LABEL = { draft: 'Draft', checked: 'Safe to Say checked', legal: 'Legal reviewed', sio: 'SIO approved', gold: 'Gold signed off', published: 'Published' };
  const VIEWS = [
    ['inbox', 'My work', 'Work'], ['picture', 'National picture', 'Listen'], ['radar', 'Narrative Radar', 'Listen'], ['agent', 'L.O.B Agent', 'Act'], ['golden-hour', 'Golden Hour cell', 'Act'], ['safe-to-say', 'Safe to Say', 'Act'],
    ['lines', 'National lines', 'Act'], ['escalations', 'Platform referrals', 'Act'], ['horizon', 'Event horizon', 'Plan'],
    ['scenarios', 'Scenarios', 'Demo'], ['audit', 'Decision log', 'Assure'], ['governance', 'Data and safeguards', 'Assure'],
  ];

  // ------------------------------------------------------------------ state
  const fresh = () => ({
    persona: 'nc-insight', clock: 0, threshold: 6, trigger: 'arrest', selNarr: 'NAR-01', selInc: 'INC-NMP-0412', scenario: 'SC-01',
    cells: {}, narr: {}, releases: [], lines: [], acks: {}, referrals: [], handovers: {}, tension: {}, fired: [], guardrails: [], auditViewed: false, audit: [], seq: 1, agent: { msgs: [], asked: [] }, agentQ: '', kbSel: null,
  });
  let S;
  try { S = Object.assign(fresh(), JSON.parse(localStorage.getItem(STORE) || 'null') || {}); } catch (e) { S = fresh(); }
  const save = () => { try { localStorage.setItem(STORE, JSON.stringify(S)); } catch (e) { /* storage unavailable: demo still works for this visit */ } };
  const me = () => P[S.persona];
  const can = (cap) => me().caps.includes(cap);
  const org = (p) => O[(p || me()).org];
  const nid = (pfx) => `${pfx}-${String(S.seq++).padStart(3, '0')}`;
  const clockStr = (m) => { const base = 13 * 60 + 50 + m; const h = Math.floor(((base % 1440) + 1440) % 1440 / 60), mm = (((base % 60) + 60) % 60); return `${String(h).padStart(2, '0')}:${String(mm).padStart(2, '0')}`; };
  const log = (action, detail, extra = {}) => { S.audit.unshift({ id: nid('D'), t: S.clock, who: S.persona, org: me().org, action, detail, ...extra }); };
  const cell = (id) => (S.cells[id] = S.cells[id] || { open: false, facts: [], disclosure: null, ho: null });
  const narr = (id) => (S.narr[id] = S.narr[id] || { triaged: false, linked: false });
  const fire = (r) => { if (!S.fired.includes(r)) S.fired.push(r); };
  let toastMsg = '';
  const toast = (m) => { toastMsg = m; };

  // ------------------------------------------------------------------ derived data
  const livePosts = () => W.posts.filter((p) => p.t <= S.clock);
  function narrStats(n) {
    const ps = livePosts().filter((p) => p.narrative === n.id);
    const recent = ps.filter((p) => p.t > S.clock - 30);
    const first = W.posts.filter((p) => p.narrative === n.id).reduce((m, p) => Math.min(m, p.t), Infinity);
    const truth = truthAt(n, first);
    return {
      count: ps.length, velocity: recent.length, reach: ps.reduce((s, p) => s + p.reach, 0),
      platforms: [...new Set(ps.map((p) => PF[p.platform].name))], places: [...new Set(ps.map((p) => PL[p.place].name))],
      first: ps.length ? first : null, truth, ttt: ps.length && truth != null ? truth - first : null,
      alert: recent.length >= S.threshold || (n.risk === 'critical' && recent.length >= Math.ceil(S.threshold / 2)),
      flags: [...new Set(ps.flatMap((p) => p.flags))], posts: ps,
    };
  }
  function truthAt(n, first) {
    const times = [];
    S.releases.filter((r) => r.status === 'published' && (r.narratives || []).includes(n.id)).forEach((r) => times.push(r.publishedAt));
    S.lines.filter((l) => l.cascadedAt != null && l.narrative === n.id).forEach((l) => times.push(l.cascadedAt));
    return times.length ? Math.min(...times) : null; // a pre-bunk published before the first post counts: the line was ahead
  }
  const activeAlerts = () => W.narratives.filter((n) => { const s = narrStats(n); return s.alert && !narr(n.id).triaged; });

  // ------------------------------------------------------------------ Safe to Say rules engine
  // Configurable: proceedings become "active" at arrest (current law) or charge (Law Commission proposal, Nov 2025).
  function runChecks(text, cy, incId, orgId, opts = {}) {
    const out = [];
    const add = (id, level, title, why, fix) => out.push({ id, level, title, why, fix });
    const inc = incId ? I[incId] : null, cs = inc && inc.case, c = cell(incId || '_');
    const t = text || '';
    if (!t.trim()) return [{ id: 'empty', level: 'info', title: 'Nothing to check yet', why: 'Write or paste a draft.', fix: '' }];
    if (/lantern bureau|state[- ](backed|linked|sponsored)|foreign (state|government)|hostile state/i.test(t))
      add('state-attribution', 'red', 'Public attribution to a state actor', 'Attribution is a national security decision. Comms must not attribute publicly (National Security Act 2023 context).', 'Remove the attribution. Say the notice is fake and point to official channels (line LN-002). Indicators go to CTP and government through Narrative Radar.');
    const halden = C['CASE-SVC-3120'];
    if (/halden/i.test(t) && (/doyle|kieran/i.test(t) || /previous convictions|has form/i.test(t)))
      add('child-defendant', 'red', 'Identifies a child defendant or prejudices a youth trial', halden.note + ' Speculation about previous convictions risks contempt.', 'Do not name or describe the defendant. Refer to "a 16-year-old" only if already reported by the court.');
    const riv = C['CASE-KMP-0457'];
    if (/rivermead/i.test(t) && (riv.complainantDetails.some((d) => t.toLowerCase().includes(d.toLowerCase())) || /\b\d{1,2}-year-old woman|\baged \d+/i.test(t)))
      add('complainant-anonymity', 'red', 'Could identify a sexual offence complainant', riv.note, 'Remove street names, ages, workplaces and any detail that could identify the complainant.');
    if (cs) {
      const active = S.trigger === 'arrest' ? ['arrested', 'charged'].includes(cs.status) : cs.status === 'charged';
      const surname = cs.suspectName.split(' ')[1];
      if (new RegExp(surname, 'i').test(t))
        add('suspect-named', active ? 'red' : 'amber', 'Names a suspect who has not been charged', 'College of Policing guidance: suspects are not normally named before charge. Privacy expectation (Art 8; Richard v BBC).', 'Describe the person as "a 34-year-old man from Port Ellery".');
      if (active && /\b(guilty|the (killer|attacker) (is|was)|confess|motive|previous convictions|has form|terror(ist)? attack)\b/i.test(t))
        add('contempt', 'red', 'Contempt risk: proceedings are active', `Proceedings are active from ${S.trigger}. Comment on guilt, motive or character risks serious prejudice (Contempt of Court Act 1981).`, 'Stick to verified facts: what happened, where, when, and that a person is in custody.');
      if (!opts.prebunk && !c.facts.some((f) => f.verifiedBy)) add('no-verified-facts', 'amber', 'No verified facts in the incident log', 'Statements in a Golden Hour cell should rest on SIO-verified facts.', 'Ask the SIO to verify facts in the Golden Hour cell first.');
    }
    if (/asylum|immigration status|refugee|\bvisa\b|migrant|recent arrival/i.test(t)) {
      if (c.ho && c.ho.status === 'confirmed') add('immigration', 'amber', 'Immigration status: Home Office confirmation on record', 'Only the Home Office confirms immigration status. Confirmation recorded by ' + P[c.ho.by].name + '.', 'Quote the Home Office confirmation wording.');
      else add('immigration', 'red', 'Immigration status is for the Home Office to confirm', 'Interim ethnicity and nationality guidance (Aug 2025): police do not confirm immigration status.', 'Remove immigration claims, or request Home Office confirmation from the Golden Hour cell.');
    }
    if (/\b(british|nationality|ethnicity|white|black|asian|foreign national|born in|uk national)\b/i.test(t)) {
      if (c.disclosure) add('ethnicity', 'green', 'Nationality disclosure decision recorded', `Decided by ${P[c.disclosure.by].name}: ${c.disclosure.decision}.`, '');
      else add('ethnicity', 'amber', 'Ethnicity or nationality disclosure needs a recorded decision', 'Interim guidance: consider disclosure where misinformation is causing tension, and record the decision and reasons.', 'Gold records a disclosure decision in the Golden Hour cell.');
    }
    if (/https?:\/\/|\.info\b|\bRT @|sharing (this|from)|shared from/i.test(t))
      add('repost', 'amber', 'Links to or reposts third-party content', 'Reposting can repeat a falsehood or be defamatory (Defamation Act 2013).', 'Do not link the spoof or third-party source. Describe it instead.');
    const purdah = W.events.find((e) => e.purdah && e.force === orgId);
    if (/two-tier|labour|conservative|reform uk|lib dem|green party|candidate|mayor(al)?|vote/i.test(t) || purdah)
      if (/two-tier|labour|conservative|reform uk|lib dem|green party|candidate|mayor(al)?|vote/i.test(t))
        add('impartiality', 'amber', purdah ? 'Pre-election period: political content' : 'Political impartiality', (purdah ? purdah.title + '. ' : '') + 'Police must not appear partisan (Standards of Professional Behaviour; Code of Ethics).', 'Talk about the policing plan and facts, not about parties, candidates or the "two-tier" label itself.');
    if (O[orgId] && O[orgId].welsh && !(cy || '').trim())
      add('welsh', 'amber', 'Welsh version missing', 'Welsh Language Standards apply to Dyfed-Glas Police.', 'Add the Welsh text before release.');
    const long = t.split(/(?<=[.!?])\s+/).filter((s) => s.split(/\s+/).length > 30).length;
    if (long) add('plain-english', 'info', `${long} long sentence${long > 1 ? 's' : ''}`, 'Aim for under 25 words a sentence for public messages.', 'Split long sentences.');
    if (!out.some((r) => r.level === 'red' || r.level === 'amber')) add('clear', 'green', 'No legal or policy risks found', 'The human still decides. This check is advisory and recorded.', '');
    return out;
  }

  // ------------------------------------------------------------------ scenario checks
  function check(expr) {
    const [k, a, b, c2] = expr.split(':');
    const rel = (inc) => S.releases.filter((r) => r.incident === inc);
    switch (k) {
      case 'cellOpen': return cell(a).open;
      case 'factCount': return cell(a).facts.length >= +b;
      case 'factsVerified': return cell(a).facts.filter((f) => f.verifiedBy).length >= +b;
      case 'statementAtLeast': return rel(a).some((r) => STAGES.indexOf(r.status) >= STAGES.indexOf(b));
      case 'narrativeLinked': return narr(a).linked;
      case 'disclosureDecided': return !!cell(a).disclosure;
      case 'hoResponded': return !!(cell(a).ho && cell(a).ho.status !== 'requested');
      case 'lineDrafted': return S.lines.some((l) => l.scenario === a);
      case 'lineCascaded': return S.lines.some((l) => l.scenario === a && l.cascadedAt != null);
      case 'lineAcks': return S.lines.some((l) => l.scenario === a && (S.acks[l.id] || []).length >= +b);
      case 'auditViewed': return S.auditViewed;
      case 'stateHandover': return !!S.handovers[a];
      case 'stateAccepted': return S.handovers[a] && S.handovers[a].status === 'accepted';
      case 'ruleFired': return S.fired.includes(a);
      case 'tensionAssessed': return !!S.tension[a];
      case 'referralCount': return S.referrals.length >= +a;
      case 'referralResolved': return S.referrals.filter((r) => r.status === 'resolved').length >= +a;
      case 'guardrailRefused': return S.guardrails.includes(a);
      case 'publishedMatch': return S.releases.some((r) => r.status === 'published' && new RegExp(a, 'i').test(r.text));
      case 'agentAsked': return (S.agent.asked || []).includes(a);
      case 'prebunkAtLeast': return S.releases.some((r) => r.prebunk === a && STAGES.indexOf(r.status) >= STAGES.indexOf(b));
      case 'aheadOf': return aheadBy(a) != null;
      case 'statementPublishedBy': return S.releases.some((r) => r.author === a && r.status === 'published');
      default: return false;
    }
  }
  const myOpenSteps = () => W.scenarios.flatMap((sc) => sc.steps.map((st, i) => ({ sc, st, i }))).filter((x) => x.st.actor === S.persona && !check(x.st.check));

  // ------------------------------------------------------------------ small render helpers
  const pill = (txt, cls = '') => `<span class="pill ${cls}">${esc(txt)}</span>`;
  const riskPill = (r) => pill(r, { critical: 'crit', high: 'crit', medium: 'warn', low: 'ok' }[r] || '');
  const verdictPill = (v) => pill(v, { false: 'crit', misleading: 'warn', mobilisation: 'crit', opinion: 'plain', 'contempt risk': 'warn' }[v] || '');
  const btn = (label, action, args = {}, opts = {}) => {
    const cap = opts.cap; const ok = !cap || can(cap);
    const data = Object.entries(args).map(([k, v]) => `data-${k}="${esc(v)}"`).join(' ');
    return `<button class="btn ${opts.cls || ''} ${opts.sm ? 'sm' : ''}" data-action="${action}" ${data} ${opts.testid ? `data-testid="${opts.testid}"` : ''} ${ok && !opts.disabled ? '' : 'disabled'} title="${ok ? esc(opts.title || '') : 'Your role cannot do this (' + esc(cap) + ')'}">${esc(label)}</button>`;
  };
  const who = (id) => P[id] ? `${esc(P[id].name)} <span class="muted small">(${esc(O[P[id].org].short)})</span>` : esc(id);
  const head = (title, sub) => `<div class="head"><span class="eyebrow">${esc(org().name)} · synthetic</span><h1>${esc(title)}</h1>${sub ? `<p>${sub}</p>` : ''}</div>`;
  function bars(nid) {
    const bins = [];
    for (let m = -60; m <= 180; m += 10) bins.push(m);
    const counts = bins.map((b) => W.posts.filter((p) => p.narrative === nid && p.t > b - 10 && p.t <= b).length);
    const max = Math.max(1, ...counts);
    return `<div class="bars" role="img" aria-label="Posts per 10 minutes, 12:50 to 16:50">${bins.map((b, i) => `<i class="${b > S.clock ? 'future' : ''}" style="height:${b > S.clock ? 2 : Math.round((counts[i] / max) * 100)}%"></i>`).join('')}</div><div class="row small muted" style="justify-content:space-between"><span>12:50</span><span>now ${clockStr(S.clock)}</span><span>16:50</span></div>`;
  }


  // ------------------------------------------------------------------ getting ahead: forecasts, first sightings, thresholds
  const KB = byId(W.knowledge || []);
  const firstCache = {};
  const firstEver = (nid) => (nid in firstCache ? firstCache[nid] : (firstCache[nid] = W.posts.filter((p) => p.narrative === nid).reduce((m, p) => Math.min(m, p.t), Infinity)));
  function thresholdAt(nid) {
    const ts = W.posts.filter((p) => p.narrative === nid && p.t <= S.clock).map((p) => p.t).sort((a, b) => a - b);
    for (const t of ts) if (ts.filter((x) => x > t - 30 && x <= t).length >= S.threshold) return t;
    return null;
  }
  const aheadBy = (nid) => { const t = truthAt(N[nid]); const f = firstEver(nid); return t != null && t < f ? f - t : null; };
  function forecasts(incId) {
    const inc = I[incId]; if (!inc || !inc.gold) return [];
    const c = cell(incId), base = c.open ? c.openedAt : 0;
    return ((W.playbooks || {})['Critical incident'] || []).filter((f) => N[f.narrative] && N[f.narrative].incident === incId).map((f) => {
      const s = narrStats(N[f.narrative]), pre = S.releases.find((r) => r.prebunk === f.narrative);
      const out = pre && pre.status === 'published';
      const state = out ? (pre.publishedAt < firstEver(f.narrative) ? 'ahead' : 'late') : s.count ? 'circulating' : 'expected';
      return { ...f, s, pre, state, from: base + f.window[0], to: base + f.window[1], base };
    });
  }
  const tttText = (s) => s.ttt == null ? null : s.ttt < 0 ? `police line ${-s.ttt} min ahead` : `time to truth ${s.ttt} min`;

  // ------------------------------------------------------------------ charts (hand-rolled SVG, palette tokens from styles.css)
  function velocityChart() {
    const top = W.narratives.map((n) => [n, narrStats(n)]).filter(([, s]) => s.count).sort((a, b) => b[1].count - a[1].count).slice(0, 5);
    if (!top.length) return '<p class="empty">No posts seen yet at this time.</p>';
    const lo = -60, hi = Math.max(60, Math.ceil(S.clock / 10) * 10), bins = [];
    for (let b = lo + 10; b <= hi; b += 10) if (b - 10 < S.clock) bins.push(b);
    const cnt = (nid, b) => W.posts.filter((p) => p.narrative === nid && p.t > b - 10 && p.t <= Math.min(b, S.clock)).length;
    const series = top.map(([n], i) => { const v = bins.map((bb) => [bb, cnt(n.id, bb)]); const k = v.findIndex(([, x]) => x > 0); return { n, i: i + 1, v: v.slice(Math.max(0, k - 1)) }; });
    const ymax = Math.max(4, Math.ceil(Math.max(...series.flatMap((s) => s.v.map((x) => x[1]))) / 2) * 2);
    const w = 720, h = 240, l = 36, r = 20, t = 14, bt = 28;
    const X = (b) => l + ((b - lo) / (hi - lo)) * (w - l - r), Y = (v) => t + (1 - v / ymax) * (h - t - bt);
    const xt = []; for (let m = lo; m <= hi; m += 30) xt.push(m);
    const grid = [0, ymax / 2, ymax].map((v) => `<line class="grid" x1="${l}" x2="${w - r}" y1="${Y(v)}" y2="${Y(v)}"/><text class="tick" x="${l - 6}" y="${Y(v) + 4}" text-anchor="end">${v}</text>`).join('');
    const ticks = xt.map((m) => `<text class="tick" x="${X(m)}" y="${h - 8}" text-anchor="middle">${clockStr(m)}</text>`).join('');
    const now = S.clock >= lo ? `<line class="now" x1="${X(S.clock)}" x2="${X(S.clock)}" y1="${t}" y2="${h - bt}"/><text class="tick" x="${X(S.clock) - 4}" y="${t + 10}" text-anchor="end">now</text>` : '';
    const lines = series.map((s) => `<path class="ln s${s.i}" d="${s.v.map(([b, v], k) => `${k ? 'L' : 'M'}${X(b).toFixed(1)} ${Y(v).toFixed(1)}`).join('')}"/>`).join('');
    const pts = series.map((s) => s.v.filter(([, v]) => v).map(([b, v]) => `<g class="pt s${s.i}"><circle cx="${X(b).toFixed(1)}" cy="${Y(v).toFixed(1)}" r="4"/><circle class="hit" cx="${X(b).toFixed(1)}" cy="${Y(v).toFixed(1)}" r="10"><title>${esc(s.n.id + ' ' + s.n.title)}: ${v} posts, ${clockStr(b - 10)} to ${clockStr(b)}</title></circle></g>`).join('')).join('');
    const legend = `<div class="legend">${series.map((s) => `<span><i class="sw s${s.i}"></i><span class="mono small">${s.n.id}</span> ${esc(s.n.title)}</span>`).join('')}</div>`;
    const table = `<details class="small"><summary>Show as a table</summary><div class="scroll"><table><thead><tr><th>Narrative</th>${bins.map((b) => `<th class="num">${clockStr(b)}</th>`).join('')}</tr></thead><tbody>${series.map((s) => `<tr><td class="mono">${s.n.id}</td>${s.v.map(([, v]) => `<td class="num">${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div></details>`;
    return `${legend}<svg class="chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="Posts per 10 minutes for the five largest narratives" data-testid="velocity-chart">${grid}${ticks}${now}${lines}${pts}</svg>${table}`;
  }
  function raceChart() {
    const rows = W.narratives.map((n) => ({ n, first: firstEver(n.id), truth: truthAt(n), thr: thresholdAt(n.id) })).filter((r) => r.first <= S.clock || r.truth != null).sort((a, b) => Math.min(a.first, a.truth ?? Infinity) - Math.min(b.first, b.truth ?? Infinity));
    if (!rows.length) return '<p class="empty">No claims seen yet.</p>';
    const lo = Math.max(-60, Math.min(...rows.map((r) => Math.min(r.first, r.truth ?? Infinity))) - 5), hi = Math.max(S.clock, ...rows.map((r) => r.truth ?? -Infinity)) + 5;
    const w = 640, L = 64, R = 210, rh = 28, t = 12, h = t + rows.length * rh + 30;
    const X = (m) => L + ((Math.max(lo, m) - lo) / (hi - lo || 1)) * (w - L - R);
    const body = rows.map((r, k) => {
      const y = t + k * rh + rh / 2, seen = r.first <= S.clock;
      let a, b, cls, words;
      if (r.truth == null) { a = r.first; b = S.clock; cls = 'bad'; words = `no police line yet · ${S.clock - r.first} min`; }
      else if (r.truth < r.first) { a = r.truth; b = seen ? r.first : S.clock; cls = 'good'; words = seen ? `line out ${r.first - r.truth} min ahead` : 'line out, claim not seen yet'; }
      else { a = r.first; b = r.truth; const late = r.thr != null && r.truth > r.thr; cls = late ? 'late' : 'good'; words = `line after ${r.truth - r.first} min${late ? ', after it took off' : ''}`; }
      return `<g data-testid="race-${r.n.id}"><title>${esc(r.n.id + ' ' + r.n.title)}</title><text class="tick" x="8" y="${y + 4}">${r.n.id}</text><line class="track" x1="${L}" x2="${w - R}" y1="${y}" y2="${y}"/><line class="seg ${cls}" x1="${X(a)}" x2="${X(b)}" y1="${y}" y2="${y}"/>${seen ? `<circle class="m-first" cx="${X(r.first)}" cy="${y}" r="4.5"/>` : ''}${r.thr != null ? `<path class="m-thr" d="M${X(r.thr)} ${y - 6}l6 6l-6 6l-6 -6z"/>` : ''}${r.truth != null ? `<rect class="m-truth" x="${X(r.truth) - 4.5}" y="${y - 4.5}" width="9" height="9" rx="1.5"/>` : ''}<text class="lbl" x="${w - R + 12}" y="${y + 4}">${esc(words)}</text></g>`;
    }).join('');
    const xt = []; for (let m = Math.ceil(lo / 30) * 30; m <= hi; m += 30) xt.push(m);
    const axis = xt.map((m) => `<text class="tick" x="${X(m)}" y="${h - 8}" text-anchor="middle">${clockStr(m)}</text>`).join('');
    return `<div class="legend"><span><i class="mk first"></i>first post</span><span><i class="mk thr"></i>crossed the alert threshold</span><span><i class="mk truth"></i>police line out</span><span><i class="sw good"></i>line first or before it took off</span><span><i class="sw late"></i>line after it took off</span><span><i class="sw bad"></i>no line yet</span></div><svg class="chart race" viewBox="0 0 ${w} ${h}" role="img" aria-label="For each claim: first post, alert threshold and police line" data-testid="race-chart">${body}${axis}</svg>`;
  }
  function swimlane(inc, c) {
    const ev = S.audit.filter((d) => d.incident === inc.id).slice().reverse();
    if (!ev.length) return '';
    const online = W.narratives.filter((n) => n.incident === inc.id && firstEver(n.id) <= S.clock).map((n) => ({ n, t: firstEver(n.id) }));
    const lanes = [...new Set(ev.map((d) => d.org))];
    const lo = Math.min(c.openedAt, ...ev.map((d) => d.t), ...online.map((x) => x.t)) - 5, hi = Math.max(S.clock, lo + 30) + 5;
    const w = 720, L = 150, R = 20, rh = 30, t = 10, h = t + (lanes.length + 1) * rh + 28;
    const X = (m) => L + ((m - lo) / (hi - lo)) * (w - L - R);
    const step = hi - lo > 150 ? 30 : hi - lo > 60 ? 15 : 10, xt = [];
    for (let m = Math.ceil(lo / step) * step; m <= hi; m += step) xt.push(m);
    const lane = (k, label) => `<line class="track" x1="${L}" x2="${w - R}" y1="${t + k * rh + rh / 2}" y2="${t + k * rh + rh / 2}"/><text class="tick" x="8" y="${t + k * rh + rh / 2 + 4}">${esc(label)}</text>`;
    const onl = online.map((x) => `<path class="m-thr" d="M${X(x.t)} ${t + rh / 2 - 6}l6 6l-6 6l-6 -6z"><title>${clockStr(x.t)} first post: ${esc(x.n.id + ' ' + x.n.title)}</title></path>`).join('');
    const dots = ev.map((d) => { const k = lanes.indexOf(d.org) + 1; return `<circle class="m-act" cx="${X(d.t)}" cy="${t + k * rh + rh / 2}" r="5"><title>${clockStr(d.t)} ${esc(P[d.who] ? P[d.who].name : d.who)}: ${esc(d.action)}. ${esc(d.detail)}</title></circle>`; }).join('');
    return `<section class="panel" data-testid="swimlane"><header><h2>Who did what, when</h2><span class="small muted">every logged action in this cell, by organisation · hover a mark</span></header>
      <svg class="chart lanes" viewBox="0 0 ${w} ${h}" role="img" aria-label="Timeline of actions in the cell by organisation, with first posts of each claim">${lane(0, 'Online claims')}${lanes.map((o, k) => lane(k + 1, O[o].short)).join('')}${xt.map((m) => `<text class="tick" x="${X(m)}" y="${h - 8}" text-anchor="middle">${clockStr(m)}</text>`).join('')}${onl}${dots}</svg>
      <div class="legend"><span><i class="mk thr"></i>first post of a claim</span><span><i class="mk act"></i>logged action</span></div></section>`;
  }
  function forecastPanel(incId) {
    const fc = forecasts(incId); if (!fc.length) return '';
    const bar = (f) => { const nowAt = S.clock - f.base; return `<svg class="fcbar" viewBox="0 0 240 12" preserveAspectRatio="none" aria-hidden="true"><rect class="track" x="0" y="4" width="240" height="4" rx="2"/><rect class="win" x="${f.window[0]}" y="2" width="${f.window[1] - f.window[0]}" height="8" rx="3"/>${nowAt >= 0 && nowAt <= 240 ? `<rect class="nowm" x="${nowAt - 0.75}" y="0" width="1.5" height="12"/>` : ''}</svg>`; };
    const state = (f) => ({ ahead: pill('line out first', 'ok'), late: pill('line out after it appeared', 'warn'), circulating: pill('circulating now', 'crit'), expected: pill(`${Math.round(f.likelihood * 100)}% · usually ${clockStr(f.from)} to ${clockStr(f.to)}`, 'plain') }[f.state]);
    return `<section class="panel" data-testid="forecast"><header><h2>Rumour forecast</h2><span class="small muted">what usually follows an incident like this</span></header>
      <p class="small muted">From public lessons of the 2024 disorder (${KB['KB-ISD24'] ? 'ISD' : ''}, HMICFRS). A pre-bunk names no one and does not repeat the claim, so it can go out before the claim appears.</p>
      ${fc.map((f) => `<div class="fc ${f.state}" data-testid="fc-${f.narrative}"><div class="row" style="justify-content:space-between"><b>${esc(f.pattern)}</b>${state(f)}</div>${bar(f)}<span class="small">${esc(f.action)}</span>
        <div class="row">${f.pre ? pill('pre-bunk: ' + STAGE_LABEL[f.pre.status].toLowerCase(), f.pre.status === 'published' ? 'ok' : '') : btn('Send pre-bunk to Safe to Say', 'prebunk', { inc: incId, n: f.narrative }, { sm: true, cap: 'statement:draft', testid: 'prebunk-' + f.narrative })}</div></div>`).join('')}
    </section>`;
  }

  // ------------------------------------------------------------------ L.O.B Agent
  // With the artifact's `sample` capability the agent is Claude, grounded in the knowledge base and live state.
  // Without it (standalone file, UAT runs) a deterministic offline engine answers from the playbook and keyword retrieval.
  const RULE_KB = { 'state-attribution': ['KB-NSA'], 'child-defendant': ['KB-CYPA49'], 'complainant-anonymity': ['KB-SOAA92'], 'suspect-named': ['KB-APP', 'KB-ART8'], contempt: ['KB-CCA81'], 'no-verified-facts': ['KB-APP'], immigration: ['KB-ETHNAT'], ethnicity: ['KB-ETHNAT'], repost: ['KB-DEFAM'], impartiality: ['KB-PURDAH', 'KB-IMPART'], welsh: ['KB-WELSH'] };
  const QUICK = [['plan', 'Give me a get-ahead plan for the Harbourside Market incident'], ['prebunk', 'Draft a pre-bunk for the next likely rumour'], ['check', 'Is my current Safe to Say draft safe to say?'], ['ask', "Which guidance applies to confirming a suspect's nationality?"]];
  const STOP = new Set('the a an and or of to in on for is are be it this that what which how do does we our i my with as at by from can should about any applies apply guidance'.split(' '));
  const agentInc = () => (I[S.selInc] && I[S.selInc].gold ? S.selInc : 'INC-NMP-0412');
  function retrieve(q, k = 3) {
    const terms = (q.toLowerCase().match(/[a-z0-9]+/g) || []).filter((x) => x.length > 2 && !STOP.has(x)).map((x) => x.replace(/(ies|es|s)$/, ''));
    return W.knowledge.map((e) => { const hay = `${e.title} ${e.summary} ${e.comms} ${e.owner} ${e.kind}`.toLowerCase(); let sc = 0; terms.forEach((x) => { if (x.length > 2 && hay.includes(x)) sc += x.length > 5 ? 2 : 1; }); return [e, sc]; }).filter(([, s]) => s > 0).sort((a, b) => b[1] - a[1]).slice(0, k).map(([e]) => e);
  }
  function agentKind(q) {
    if (/ahead|plan|forecast|next (few )?hours|coming next/i.test(q)) return 'plan';
    if (/pre-?bunk|draft (a|an|the|me)|write (a|an|the|me)/i.test(q)) return 'prebunk';
    if (/safe to say|check (my|the|this) draft|my (current )?draft/i.test(q)) return 'check';
    return 'ask';
  }
  function nextForecast(fc) { return fc.find((f) => f.state === 'expected' && !f.pre) || fc.find((f) => f.state === 'circulating' && !f.pre) || null; }
  const fcDraft = (f, incId) => (f ? { narrative: f.narrative, title: 'Pre-bunk: ' + f.pattern.toLowerCase(), text: f.prebunk, incident: incId } : null);
  function offlineAnswer(q) {
    const kind = agentKind(q), incId = agentInc(), fc = forecasts(incId), next = nextForecast(fc);
    if (kind === 'plan') {
      if (!fc.length) return { text: 'There is no critical incident with a forecast yet. Open a Golden Hour cell first.', cites: [] };
      const ls = fc.map((f) => `• ${f.pattern} (${Math.round(f.likelihood * 100)}% likely, usually ${clockStr(f.from)} to ${clockStr(f.to)}): ${f.state === 'ahead' ? 'pre-bunk already out.' : f.state === 'late' ? 'line out, after it appeared.' : f.state === 'circulating' ? 'already circulating, respond now.' : 'not seen yet. ' + f.action}`);
      return { text: `Get-ahead plan for ${I[incId].title}, from what usually follows an incident like this [KB-ISD24]:\n${ls.join('\n')}\nPre-bunk the next likely claim before it appears, keep an hourly update rhythm even when there is little new [KB-HMIC24], and record every decision.`, cites: [...new Set(['KB-ISD24', 'KB-HMIC24', ...fc.flatMap((f) => f.sources)])], draft: fcDraft(next, incId) };
    }
    if (kind === 'prebunk') {
      if (!next) return { text: 'Every forecast claim for this incident already has a police line or a pre-bunk in progress.', cites: [] };
      return { text: `The next likely claim is "${next.pattern.toLowerCase()}" (${Math.round(next.likelihood * 100)}% likely, usually ${clockStr(next.from)} to ${clockStr(next.to)}). This pre-bunk names no one and does not repeat the claim, so it can go out before the claim appears. Also: ${next.action}`, cites: next.sources, draft: fcDraft(next, incId) };
    }
    if (kind === 'check') {
      const d = S.draft;
      if (!d || !d.text.trim()) return { text: 'There is no draft in Safe to Say yet. Write one there, or ask me to draft a pre-bunk.', cites: [] };
      const res = runChecks(d.text, d.cy, d.incident, me().org, { prebunk: d.prebunk }).filter((r) => r.level === 'red' || r.level === 'amber');
      if (!res.length) return { text: 'I found no legal or policy risks in the current draft. You still decide, and the check is recorded when you submit it.', cites: ['KB-APP'] };
      return { text: 'Not yet.\n' + res.map((r) => `• ${r.level === 'red' ? 'Must fix' : 'Needs a decision'}: ${r.title}. ${r.fix}`).join('\n'), cites: [...new Set(res.flatMap((r) => RULE_KB[r.id] || []))] };
    }
    const hits = retrieve(q);
    if (!hits.length) return { text: 'I could not find that in the knowledge base. Try naming the topic, for example contempt, nationality, Welsh language, elections or spoof notices.', cites: [] };
    return { text: hits.map((e) => `• ${e.title} (${e.owner}) [${e.id}]: ${e.comms}`).join('\n'), cites: hits.map((e) => e.id) };
  }
  function agentPrompt(q) {
    const incId = agentInc(), inc = I[incId], c = cell(incId), fc = forecasts(incId);
    const kb = W.knowledge.map((e) => `[${e.id}] ${e.title} (${e.owner}). ${e.summary} For comms: ${e.comms}`).join('\n');
    const narrs = W.narratives.map((n) => [n, narrStats(n)]).filter(([, s]) => s.count).map(([n, s]) => `${n.id} ${n.title}: verdict ${n.verdict}, ${s.count} posts, ${s.velocity} in the last 30 min, ${tttText(s) || 'no police line yet'}. What is known: ${n.truth}`).join('\n');
    return `You are the L.O.B Agent inside Line of Blue, a synthetic demonstration of a national policing communications system for England and Wales. Everything in it is fictional. Answer the comms officer's question using only the knowledge base and the live picture below.
Rules: UK English. Plain and short, under 180 words, no headings. Cite each point you take from the knowledge base with its id in square brackets, like [KB-APP]. Never name or describe a suspect beyond verified facts, never comment on guilt, never attribute activity to a foreign state publicly, never suggest monitoring or profiling individual people (only narratives), and remember only the Home Office confirms immigration status. You advise; people decide and sign off. If a public message would help, add one fenced block that starts with \`\`\`draft and holds a message of under 60 words that names no one and does not repeat the false claim.

Knowledge base:
${kb}

Live picture at ${clockStr(S.clock)} (scenario clock):
Asking: ${me().name}, ${me().role}, ${org().name}
Incident: ${inc.title} (${O[inc.force].name}). ${inc.summary} Golden Hour cell ${c.open ? 'open since ' + clockStr(c.openedAt) : 'not open'}. Verified facts: ${c.facts.filter((f) => f.verifiedBy).map((f) => f.text).join(' ') || 'none yet'}. Proceedings active from ${S.trigger}; case status ${inc.case ? inc.case.status : 'none'}.
Narratives seen:
${narrs || 'none yet'}
Rumour forecast for this incident:
${fc.map((f) => `${f.narrative} ${f.pattern}: ${Math.round(f.likelihood * 100)}% likely, usually ${clockStr(f.from)} to ${clockStr(f.to)}, status ${f.state}. Suggested action: ${f.action}`).join('\n') || 'none'}
Current Safe to Say draft: ${(S.draft && S.draft.text) || 'none'}

Question: ${q}`;
  }
  function parseAgent(t, kind) {
    const m = t.match(/```draft\s*([\s\S]*?)(```|$)/);
    const text = t.replace(/```draft[\s\S]*?(```|$)/, '').trim();
    const cites = [...new Set((t.match(/KB-[A-Z0-9]+/g) || []).filter((id) => KB[id]))];
    let draft = null;
    if (m && m[1].trim()) { const incId = agentInc(), next = nextForecast(forecasts(incId)); draft = { narrative: kind === 'plan' || kind === 'prebunk' ? (next && next.narrative) : null, title: next && (kind === 'plan' || kind === 'prebunk') ? 'Pre-bunk: ' + next.pattern.toLowerCase() : 'Agent draft', text: m[1].trim(), incident: incId }; }
    return { text, cites, draft };
  }
  let samplerP = null, agentMode = 'checking';
  const inflight = new Set();
  function sampler() {
    if (!samplerP) samplerP = (window.claude && typeof window.claude.use === 'function' ? Promise.resolve(window.claude.use('sample')).catch(() => null) : Promise.resolve(null)).then((s) => { agentMode = s ? 'claude' : 'offline'; return s; });
    return samplerP;
  }
  function paintAgent(m) { const el = document.querySelector(`#msg-${m.id} .ans`); if (el) el.innerHTML = fmtAnswer(m.text); }
  async function runAgent(q) {
    const m = { id: nid('Q'), q, by: S.persona, t: S.clock, kind: agentKind(q), text: 'Thinking…', cites: [], draft: null, mode: 'offline', pending: true };
    S.agent.msgs.push(m); S.agent.asked.push(m.kind); inflight.add(m.id);
    log('L.O.B Agent asked', q.slice(0, 140), { incident: agentInc() });
    render();
    const sample = await sampler();
    if (sample) {
      try {
        const res = await sample(agentPrompt(q), { modelTier: 'default', onText: ({ text }) => { m.text = text; paintAgent(m); } });
        Object.assign(m, parseAgent(res.text || '', m.kind), { mode: 'claude' });
      } catch (e) {
        Object.assign(m, offlineAnswer(q), { mode: 'offline', note: e && e.code === 'not_granted' ? 'Claude was not allowed on this page, so the offline playbook answered.' : e && e.code === 'rate_limited' ? 'Claude is busy, so the offline playbook answered. Try again in a minute.' : 'Claude was unavailable, so the offline playbook answered.' });
      }
    } else Object.assign(m, offlineAnswer(q), { mode: 'offline' });
    m.pending = false; inflight.delete(m.id);
    render();
  }
  const fmtAnswer = (t) => esc(t).split(/\n+/).map((p) => `<p>${p.replace(/\[?(KB-[A-Z0-9]+)\]?/g, (all, id) => (KB[id] ? `<button class="cite" data-action="kbOpen" data-k="${id}">${id}</button>` : all))}</p>`).join('');
  const msgCard = (m) => `<div class="post msg" id="msg-${m.id}" data-testid="agent-msg"><span class="small muted">${who(m.by)} asked at ${clockStr(m.t)}</span><b>${esc(m.q)}</b><div class="ans">${fmtAnswer(m.text)}</div>
    ${m.note ? `<span class="small muted">${esc(m.note)}</span>` : ''}
    ${m.cites && m.cites.length ? `<div class="row">${m.cites.map((id) => `<button class="chip" data-action="kbOpen" data-k="${id}" title="${esc(KB[id].title)}">${id} · ${esc(KB[id].owner)}</button>`).join('')}</div>` : ''}
    ${m.draft ? `<div class="sev green"><span class="eyebrow">Suggested draft${m.draft.narrative ? ' · pre-bunk for ' + m.draft.narrative : ''}</span><span>${esc(m.draft.text)}</span><div class="row">${btn('Send to Safe to Say', 'agentDraft', { m: m.id }, { sm: true, cap: 'statement:draft', testid: 'agent-draft' })}</div></div>` : ''}
    <span class="small muted">${m.pending ? 'Answering…' : m.mode === 'claude' ? 'Answered by Claude from the knowledge base. Check the cited sources.' : 'Offline playbook answer'}</span></div>`;

  // ------------------------------------------------------------------ views
  const V = {};
  V.inbox = () => {
    const steps = myOpenSteps();
    const tasks = [];
    Object.entries(S.cells).forEach(([incId, c]) => { if (c.ho && c.ho.status === 'requested' && can('immigration:confirm')) tasks.push(`<div class="sev amber"><b>Request from ${esc(O[I[incId].force].name)}: confirm immigration status</b><span>${esc(I[incId].title)}. Requested by ${who(c.ho.requestedBy)} at ${clockStr(c.ho.at)}. Claim circulating online: "${esc(N['NAR-01'].claim)}"</span><span class="small">Facts held by the force: ${esc(I[incId].case.suspectNationality)}.</span><div class="row">${btn('Confirm: no immigration case', 'hoRespond', { inc: incId, status: 'confirmed' }, { cap: 'immigration:confirm', cls: 'primary', testid: 'ho-confirm' })}${btn('Decline to comment', 'hoRespond', { inc: incId, status: 'declined' }, { cap: 'immigration:confirm' })}</div></div>`); });
    Object.entries(S.handovers).forEach(([n, h]) => { if (h.status === 'sent' && can('state:receive')) tasks.push(`<div class="sev amber"><b>Handover: state-linked indicators on ${esc(n)}</b><span>${esc(N[n].title)}. Sent by ${who(h.by)} at ${clockStr(h.at)}. Indicators: ${esc(A['act-lantern'].indicators.join('; '))}.</span><div class="row">${btn('Accept handover', 'acceptHandover', { n }, { cap: 'state:receive', cls: 'primary', testid: 'accept-handover' })}</div></div>`); });
    S.lines.filter((l) => l.cascadedAt != null && can('line:ack') && !(S.acks[l.id] || []).includes(me().org)).forEach((l) => tasks.push(`<div class="sev amber"><b>National line to acknowledge: ${esc(l.title)}</b><span>${esc(l.text)}</span><div class="row"><a class="btn sm" href="#lines">Open in National lines</a></div></div>`));
    if (can('brief:read')) tasks.push(`<div class="sev"><b>National situation summary</b>${brief()}</div>`);
    return `${head('My work', `You are acting as <b>${esc(me().name)}</b>, ${esc(me().role)}. Everything below is routed to your role.`)}
    <div class="grid2"><section class="panel"><header><h2>Your scenario steps</h2><span class="muted small">${steps.length} open</span></header>
      ${steps.length ? `<ul class="steps">${steps.map(({ sc, st }) => `<li><span class="mono">${clockStr(st.t)}</span><span class="tick next"></span><span><b>${esc(st.do)}</b><br><span class="small muted">${esc(sc.id)} ${esc(sc.title)}</span></span><a class="btn sm" href="#${st.view}">Go</a></li>`).join('')}</ul>` : '<p class="empty">No open scenario steps for this role. Switch persona or pick a scenario.</p>'}
    </section><section class="panel"><header><h2>Requests and notifications</h2></header>${tasks.join('') || '<p class="empty">Nothing waiting for you.</p>'}</section></div>
    <section class="panel"><header><h2>What this role can do</h2></header><div class="row">${me().caps.map((c) => pill(c, 'plain')).join('')}</div><p class="small muted">Actions outside these permissions are disabled across Line of Blue, and every action you take is written to the decision log with your name.</p></section>`;
  };
  function brief() {
    const al = W.narratives.map((n) => [n, narrStats(n)]).filter(([, s]) => s.count);
    const cells = Object.entries(S.cells).filter(([, c]) => c.open).map(([k]) => I[k].title);
    return `<span>At ${clockStr(S.clock)}: ${cells.length ? 'Golden Hour cell open for ' + esc(cells.join(', ')) : 'no Golden Hour cell open'}. ${al.filter(([, s]) => s.alert).length} narratives over threshold; ${al.length} active in total.</span><span class="small">${al.slice(0, 4).map(([n, s]) => `${esc(n.title)}: ${s.count} posts, reach ${s.reach.toLocaleString('en-GB')}${s.ttt != null ? ', time to truth ' + s.ttt + ' min' : ''}`).join('<br>')}</span><span class="small muted">Aggregated narrative data only. No personal data is shared in briefings.</span>`;
  }

  V.radar = () => {
    const rows = W.narratives.map((n) => [n, narrStats(n)]).sort((a, b) => (b[1].alert - a[1].alert) || b[1].velocity - a[1].velocity);
    const sel = N[S.selNarr] || W.narratives[0], ss = narrStats(sel), ns = narr(sel.id);
    const tot = livePosts().length, alerts = rows.filter(([, s]) => s.alert).length;
    const ttts = rows.map(([, s]) => s.ttt).filter((x) => x != null);
    const placeVol = {}; livePosts().forEach((p) => { placeVol[p.place] = (placeVol[p.place] || 0) + 1; });
    return `${head('Narrative Radar', 'Emerging claims about policing, grouped into narratives by velocity, reach, platform and place. Narrative-first: Line of Blue analyses public content, not people.')}
    <div class="strip">
      <div class="stat"><span class="eyebrow">Posts seen</span><span class="v">${tot}</span><span class="small muted">public, pseudonymised</span></div>
      <div class="stat"><span class="eyebrow">Over threshold</span><span class="v" style="color:var(--crit)">${alerts}</span><span class="small muted">≥ ${S.threshold} posts in 30 min</span></div>
      <div class="stat"><span class="eyebrow">Median time to truth</span><span class="v">${ttts.length ? ttts.sort((a, b) => a - b)[Math.floor(ttts.length / 2)] + ' min' : '–'}</span><span class="small muted">first post to first police line</span></div>
      <div class="stat"><span class="eyebrow">Alert threshold</span><span class="row"><input id="threshold" type="range" min="2" max="12" value="${S.threshold}" aria-label="Alert threshold, posts in 30 minutes" data-change="threshold"><b class="num">${S.threshold}</b></span></div>
    </div>
    <div class="grid2"><section class="panel"><header><h2>Narratives</h2><span class="small muted">select a row</span></header><div class="scroll"><table><thead><tr><th>Narrative</th><th>Verdict</th><th class="num">30 min</th><th class="num">Reach</th><th>Status</th></tr></thead><tbody>
      ${rows.map(([n, s]) => `<tr class="click ${n.id === sel.id ? 'sel' : ''}" data-action="selNarr" data-n="${n.id}" data-testid="narr-${n.id}"><td><span class="mono small">${n.id}</span> ${esc(n.title)}</td><td>${verdictPill(n.verdict)}</td><td class="num">${s.velocity}</td><td class="num">${s.reach.toLocaleString('en-GB')}</td><td>${s.count === 0 ? pill('not yet seen', 'plain') : s.alert && !narr(n.id).triaged ? pill('ALERT', 'crit') : narr(n.id).triaged ? pill('triaged', 'ok') : pill('watching', 'plain')}</td></tr>`).join('')}
      </tbody></table></div>
      <h3>Where it is spreading</h3>${map(placeVol)}
    </section>
    <section class="panel" data-testid="narr-detail"><header><h2>${esc(sel.title)}</h2>${riskPill(sel.risk)}</header>
      <div class="sev red"><span class="eyebrow">Claim</span><span>${esc(sel.claim)}</span></div>
      <div class="sev green"><span class="eyebrow">What is known</span><span>${esc(sel.truth)}</span></div>
      ${bars(sel.id)}
      <div class="small"><b>${ss.count}</b> posts · reach <b>${ss.reach.toLocaleString('en-GB')}</b> · ${esc(ss.platforms.join(', ') || 'no platforms yet')} · ${esc(ss.places.join(', '))}${ss.ttt != null ? ` · <b>${tttText(ss)}</b>` : ''}</div>
      ${ss.flags.length ? `<div class="row">${ss.flags.map((f) => pill(f, 'warn')).join('')}</div>` : ''}
      ${sel.actor ? `<div class="sev amber"><b>Tier ${A[sel.actor].tier} indicators: ${esc(A[sel.actor].name)}</b><span class="small">${esc(A[sel.actor].allowed)}</span></div>` : ''}
      <div class="row">
        ${btn(ns.triaged ? 'Triaged' : 'Triage alert', 'triage', { n: sel.id }, { cap: 'radar:triage', cls: ns.triaged ? '' : 'primary', disabled: ns.triaged || !ss.count, testid: 'triage' })}
        ${sel.incident ? btn(ns.linked ? 'Linked to ' + sel.incident : 'Link to incident', 'linkNarr', { n: sel.id }, { cap: 'radar:triage', disabled: ns.linked || !ss.count, testid: 'link-incident' }) : ''}
        ${sel.actor && A[sel.actor].tier === 'B' ? btn(S.handovers[sel.id] ? 'Handed to CTP and government' : 'Hand indicators to CTP and government', 'handover', { n: sel.id }, { cap: 'state:handover', disabled: !!S.handovers[sel.id] || !ss.count, testid: 'handover' }) : ''}
        ${btn(S.tension[sel.places[0]] ? 'Tension assessed' : 'Assess community tension', 'tension', { n: sel.id }, { cap: 'tension:assess', disabled: !!S.tension[sel.places[0]] || !ss.count, testid: 'tension' })}
      </div>
      <h3>Sample posts <span class="muted small">(accounts pseudonymised)</span></h3>
      <div class="stack">${ss.posts.slice(-6).reverse().map((p) => `<div class="post"><span>${esc(p.text)}</span><div class="meta"><span class="mono">${p.account}</span><span>${esc(PF[p.platform].name)}</span><span>${esc(PL[p.place].name)}</span><span class="mono">${clockStr(p.t)}</span><span>reach ${p.reach.toLocaleString('en-GB')}</span>${p.flags.map((f) => pill(f, 'warn')).join('')}</div><div class="row">${p.flags.includes('possible illegal content') || p.flags.includes('possible contempt breach') ? btn('Refer to platform', 'refer', { p: p.id }, { cap: 'referral:log', sm: true, testid: 'refer-' + p.id }) : ''}${btn('Track this account', 'track', { p: p.id }, { sm: true, testid: 'track-account' })}</div></div>`).join('') || '<p class="empty">No posts yet at this time. Advance the clock.</p>'}</div>
    </section></div>`;
  };
  function map(vol) {
    const w = 360, h = 260;
    return `<svg class="map" viewBox="0 0 ${w} ${h}" role="img" aria-label="Fictional map of post volume by place"><path class="land" d="M70 20 L170 10 L230 60 L290 120 L330 200 L280 245 L170 250 L90 230 L40 190 L50 120 Z"/>${W.places.map((p) => { const v = vol[p.id] || 0; const x = p.x * w, y = p.y * h; return `<circle class="base" cx="${x}" cy="${y}" r="2.5"/>${v ? `<circle class="dot" cx="${x}" cy="${y}" r="${4 + Math.sqrt(v) * 3}"/>` : ''}<text x="${x > w * 0.6 ? x - 10 : x + 10}" y="${y + 4}" text-anchor="${x > w * 0.6 ? 'end' : 'start'}">${esc(p.name)}${v ? ' · ' + v : ''}</text>`; }).join('')}</svg>`;
  }

  V['golden-hour'] = () => {
    const inc = I[S.selInc], c = cell(inc.id), rels = S.releases.filter((r) => r.incident === inc.id);
    const linked = W.narratives.filter((n) => n.incident === inc.id && narr(n.id).linked);
    const sel = `<label class="f" style="max-width:420px">Incident<select class="f" id="incSel" data-change="selInc">${W.incidents.map((x) => `<option value="${x.id}" ${x.id === inc.id ? 'selected' : ''}>${esc(x.id)} · ${esc(x.title)}</option>`).join('')}</select></label>`;
    if (!c.open) return `${head('Golden Hour cell', 'A ready workspace for the first hours of a critical incident: verified facts, holding lines, approvals and one shared timeline across the force, Gold, NPoCC and NPCC.')}${sel}
      <section class="panel"><header><h2>${esc(inc.title)}</h2>${pill(inc.type)}</header><p>${esc(inc.summary)}</p><p class="small muted">${esc(O[inc.force].name)} · ${esc(PL[inc.place].name)}</p>
      <div class="row">${btn('Declare critical incident and open cell', 'openCell', { inc: inc.id }, { cap: 'cell:open', cls: 'primary', testid: 'open-cell' })}</div><p class="small muted">Gold or the force Head of Communications opens the cell. Opening it notifies NPCC Comms and NPoCC.</p></section>`;
    const factRows = c.facts.map((f) => `<tr><td class="mono">${clockStr(f.t)}</td><td>${esc(f.text)}</td><td>${who(f.by)}</td><td>${f.verifiedBy ? pill('verified', 'ok') + ' <span class="small">' + who(f.verifiedBy) + '</span>' : btn('Verify', 'verifyFact', { inc: inc.id, f: f.id }, { cap: 'fact:verify', sm: true, testid: 'verify-' + f.id })}</td></tr>`).join('');
    const tl = S.audit.filter((d) => d.incident === inc.id).slice(0, 14);
    return `${head('Golden Hour cell', `Open since ${clockStr(c.openedAt)} · ${esc(inc.title)}`)}${sel}
    <div class="strip">
      <div class="stat"><span class="eyebrow">Cell open</span><span class="v">${S.clock - c.openedAt} min</span><span class="small muted">golden hour ${S.clock - c.openedAt <= 60 ? 'running' : 'passed'}</span></div>
      <div class="stat"><span class="eyebrow">Verified facts</span><span class="v">${c.facts.filter((f) => f.verifiedBy).length}/${c.facts.length}</span></div>
      <div class="stat"><span class="eyebrow">Proceedings</span><span class="v small" style="font-size:1rem">${inc.case ? esc(inc.case.status) : 'none'}</span><span class="small muted">active from ${S.trigger}</span></div>
      <div class="stat"><span class="eyebrow">Linked narratives</span><span class="v">${linked.length}</span></div>
    </div>
    <div class="grid2"><div class="stack">
      <section class="panel"><header><h2>Fact log</h2><span class="small muted">only verified facts may be published</span></header>
        <div class="scroll"><table><thead><tr><th>Time</th><th>Fact</th><th>Logged by</th><th>Status</th></tr></thead><tbody>${factRows || '<tr><td colspan="4" class="empty">No facts logged yet.</td></tr>'}</tbody></table></div>
        <div class="row"><input type="text" id="factText" aria-label="New fact" placeholder="e.g. Two people were injured at Harbourside Market at about 13:50" style="flex:1 1 260px">${btn('Log fact', 'addFact', { inc: inc.id }, { cap: 'fact:add', testid: 'add-fact' })}</div>
        <div class="row small">${['Officers were called to Harbourside Market, Port Ellery, at 13:52.', 'Two people were injured; one is in a serious condition in hospital.', 'A 34-year-old man was arrested at the scene and is in custody.'].map((s) => `<button class="btn sm" data-action="quickFact" data-inc="${inc.id}" data-text="${esc(s)}" ${can('fact:add') ? '' : 'disabled'}>+ ${esc(s.slice(0, 34))}…</button>`).join('')}</div>
      </section>
      <section class="panel"><header><h2>Releases and sign-off</h2><a class="btn sm" href="#safe-to-say">Draft in Safe to Say</a></header>
        ${rels.length ? rels.map((r) => releaseCard(r)).join('') : '<p class="empty">No release drafted yet. The duty press officer drafts the holding statement in Safe to Say.</p>'}
      </section></div>
      <div class="stack">
      ${forecastPanel(inc.id)}
      <section class="panel"><header><h2>Disclosure decision</h2><span class="small muted">ethnicity and nationality guidance</span></header>
        ${linked.some((n) => n.id === 'NAR-01') ? '<div class="sev red"><b>Narrative Radar: false identity claim is spreading on this case.</b><span class="small">Guidance says consider confirming nationality where misinformation is causing tension. Record the decision and reasons.</span></div>' : '<p class="small muted">No identity narrative linked yet.</p>'}
        ${c.disclosure ? `<div class="sev green"><b>${esc(c.disclosure.decision)}</b><span class="small">${esc(c.disclosure.rationale)}</span><span class="small">${who(c.disclosure.by)} at ${clockStr(c.disclosure.t)}</span></div>` : `<label class="f">Reasons (recorded)<textarea id="discReason" placeholder="Why this decision is necessary and proportionate"></textarea></label><div class="row">${btn('Confirm nationality publicly', 'decide', { inc: inc.id, d: 'Confirm the suspect is a British national' }, { cap: 'disclosure:decide', cls: 'primary', testid: 'decide-confirm' })}${btn('Do not confirm yet', 'decide', { inc: inc.id, d: 'Do not confirm nationality at this stage' }, { cap: 'disclosure:decide' })}</div>`}
        ${inc.case && inc.case.immigrationClaim ? `<div class="row">${c.ho ? pill('Home Office: ' + c.ho.status, c.ho.status === 'confirmed' ? 'ok' : 'warn') : btn('Ask Home Office to confirm immigration status', 'hoRequest', { inc: inc.id }, { cap: 'cell:join', testid: 'ho-request' })}</div><p class="small muted">Only the Home Office confirms immigration status.</p>` : ''}
      </section>
      <section class="panel"><header><h2>Shared timeline</h2></header>${tl.length ? `<ul class="steps">${tl.map((d) => `<li><span class="mono">${clockStr(d.t)}</span><span class="tick done"></span><span><b>${esc(d.action)}</b> <span class="small">${esc(d.detail)}</span><br><span class="small muted">${who(d.who)}</span></span><span></span></li>`).join('')}</ul>` : '<p class="empty">Nothing yet.</p>'}</section>
      <section class="panel"><header><h2>Linked narratives</h2></header>${linked.map((n) => { const s = narrStats(n); return `<div class="row"><span class="mono small">${n.id}</span><span>${esc(n.title)}</span>${s.ttt != null ? pill(tttText(s), 'ok') : pill('no police line yet', 'crit')}</div>`; }).join('') || '<p class="empty">Link narratives from Narrative Radar.</p>'}</section>
    </div></div>${swimlane(inc, c)}`;
  };
  function releaseCard(r) {
    const idx = STAGES.indexOf(r.status), inCell = !!r.incident && I[r.incident].gold;
    const flow = (inCell ? STAGES : ['draft', 'checked', 'published']).map((s) => `<span class="${s === r.status ? 'cur' : STAGES.indexOf(s) < idx ? 'on' : ''}">${STAGE_LABEL[s]}</span>`).join('');
    const nextBtn = {
      checked: inCell ? btn('Legal review: approve', 'advance', { r: r.id, to: 'legal' }, { cap: 'statement:legal', cls: 'primary', testid: 'legal-approve' }) : btn('Publish', 'advance', { r: r.id, to: 'published' }, { cap: 'statement:publish', cls: 'primary', testid: 'publish' }),
      legal: btn('SIO approve', 'advance', { r: r.id, to: 'sio' }, { cap: 'statement:approve-sio', cls: 'primary', testid: 'sio-approve' }),
      sio: btn('Gold sign-off', 'advance', { r: r.id, to: 'gold' }, { cap: 'statement:approve-gold', cls: 'primary', testid: 'gold-approve' }),
      gold: btn('Publish', 'advance', { r: r.id, to: 'published' }, { cap: 'statement:publish', cls: 'primary', testid: 'publish' }),
    }[r.status] || '';
    return `<div class="post" data-testid="release-${r.id}"><div class="row" style="justify-content:space-between"><b>${esc(r.id)} · ${esc(r.title)}</b>${pill(STAGE_LABEL[r.status], r.status === 'published' ? 'ok' : '')}</div><div class="flow">${flow}</div><span>${esc(r.text)}</span>${r.cy ? `<span class="small muted" lang="cy">${esc(r.cy)}</span>` : ''}<span class="small muted">Author ${who(r.author)}${r.decision ? ' · decision recorded: ' + esc(r.decision) : ''}</span><div class="row">${nextBtn}${r.status !== 'published' && r.status !== 'draft' ? btn('Return to author', 'advance', { r: r.id, to: 'draft' }, { sm: true, cap: r.status === 'checked' ? 'statement:legal' : 'cell:join' }) : ''}</div></div>`;
  }

  V['safe-to-say'] = () => {
    const d = S.draft || (S.draft = { text: '', cy: '', incident: S.selInc, title: 'Holding statement' });
    const res = runChecks(d.text, d.cy, d.incident, me().org, { prebunk: d.prebunk });
    if (d.text.trim()) res.forEach((r) => fire(r.id)); // a rule shown to the author counts as fired, even when submit stays blocked
    const reds = res.filter((r) => r.level === 'red'), ambers = res.filter((r) => r.level === 'amber');
    const examples = [
      ['Holding statement (clean)', 'Officers were called to Harbourside Market, Port Ellery, at 13:52 today. Two people were injured and one is in a serious condition in hospital. A 34-year-old man from Port Ellery was arrested at the scene and is in custody. Please do not share speculation about the people involved.', 'INC-NMP-0412'],
      ['Holding statement (risky)', 'Callum Breward, the attacker, was arrested after the terror attack. He is not an asylum seeker. Shared from northmoor-police-news.info', 'INC-NMP-0412'],
      ['Spoof curfew rebuttal (attributes)', 'There is no curfew in Port Ellery. The fake notice was created by the Lantern Bureau, a foreign state operation.', 'INC-NMP-0412'],
      ['Nationality confirmation', 'The man arrested is a 34-year-old British national from Port Ellery. Claims that he lives at the Harbourside hotel are false.', 'INC-NMP-0412'],
      ['Halden Street (youth trial)', 'Kieran Doyle appears at Brennford Crown Court today. He has previous convictions.', ''],
      ['Rivermead (complainant)', 'A man has been charged after a woman aged 23 was assaulted near Rivermead Close.', ''],
      ['Kingsbridge policing plan', 'Our policing plan for Saturday is the same for both groups. We facilitate lawful protest and act on any crime, whoever commits it. Some people say this is two-tier policing; it is not.', ''],
      ['Flood hoax rebuttal', 'Llyn Teg dam is safe. Follow the official flood warning for the lower Teg valley and use the rest centre at Ysgol Aberteg if you need to leave home.', ''],
    ];
    return `${head('Safe to Say', 'Check a draft against contempt, anonymity, the ethnicity and nationality guidance, privacy, impartiality and Welsh language duties before release. It suggests safer wording and records who decided and why. The human always decides.')}
    <div class="grid2"><section class="panel"><header><h2>Draft</h2><span class="small muted">${d.prebunk ? pill('pre-bunk for ' + d.prebunk, 'ok') + ' ' : ''}for ${esc(org().name)}</span></header>
      <div class="row">${examples.map(([l, t, inc], i) => `<button class="btn sm" data-action="example" data-i="${i}" data-testid="example-${i}">${esc(l)}</button>`).join('')}</div>
      <label class="f">Title<input type="text" id="dTitle" value="${esc(d.title)}" data-input="dTitle"></label>
      <label class="f">Linked incident<select class="f" id="dInc" data-change="dInc"><option value="">None</option>${W.incidents.map((x) => `<option value="${x.id}" ${x.id === d.incident ? 'selected' : ''}>${esc(x.id)} · ${esc(x.title)}</option>`).join('')}</select></label>
      <label class="f">Statement (English)<textarea id="dText" data-input="dText" data-testid="draft-text">${esc(d.text)}</textarea></label>
      <label class="f">Welsh version (Cymraeg)<textarea id="dCy" data-input="dCy" lang="cy" style="min-height:60px">${esc(d.cy)}</textarea></label>
      ${org().welsh ? `<div class="row">${btn('Use national Welsh template (LN-001)', 'cyTemplate', {}, { sm: true, cap: 'line:localise', testid: 'welsh-template' })}</div>` : ''}
      <label class="f">Rules: proceedings become active at<select class="f" id="trigger" data-change="trigger"><option value="arrest" ${S.trigger === 'arrest' ? 'selected' : ''}>Arrest (current law)</option><option value="charge" ${S.trigger === 'charge' ? 'selected' : ''}>Charge (Law Commission proposal, not yet law)</option></select></label>
    </section>
    <section class="panel" data-testid="check-results"><header><h2>Check result</h2>${!d.text.trim() ? pill('waiting for a draft', 'plain') : reds.length ? pill(reds.length + ' must fix', 'crit') : ambers.length ? pill(ambers.length + ' need a decision', 'warn') : pill('clear', 'ok')}</header>
      ${res.map((r) => `<div class="sev ${r.level === 'info' ? '' : r.level}" data-rule="${r.id}"><b>${esc(r.title)}</b><span class="small">${esc(r.why)}</span>${r.fix ? `<span class="small"><b>Safer:</b> ${esc(r.fix)}</span>` : ''}</div>`).join('')}
      ${ambers.length && !reds.length ? `<label class="f">Decision record for the amber items<textarea id="dReason" style="min-height:60px" placeholder="Why it is right to release with these points"></textarea></label>` : ''}
      <div class="row">${btn('Record check and submit', 'submitDraft', {}, { cap: 'statement:draft', cls: 'primary', disabled: !!reds.length || !d.text.trim(), testid: 'submit-draft' })}${reds.length ? '<span class="small" style="color:var(--crit)">Fix the red items before it can be submitted.</span>' : ''}</div>
      <p class="small muted">Research summary of England and Wales rules, not legal advice. Rules are configurable for law changes and need sign-off by police legal services.</p>
    </section></div>
    <section class="panel"><header><h2>Releases by ${esc(org().short)}</h2></header>${S.releases.filter((r) => r.org === me().org).map(releaseCard).join('') || '<p class="empty">None yet.</p>'}</section>`;
  };
  V['safe-to-say'].examples = null;

  V.lines = () => {
    const all = [...S.lines, ...W.lines.map((l) => ({ ...l, base: true }))];
    return `${head('National lines and cascade', 'Approved lines-to-take pushed to every force comms team, with read receipts, expiry dates and Welsh variants. NPCC coordinates and informs; forces decide locally.')}
    <div class="grid2"><section class="panel"><header><h2>Draft a national line</h2></header>
      <label class="f">Title<input type="text" id="lTitle" value="Speculation about the Port Ellery suspect"></label>
      <label class="f">Line<textarea id="lText">We understand people want answers about the incident in Port Ellery. A man is in custody. Northmoor Police will publish facts as they are confirmed. Claims about who he is that are circulating online are not from the police. Please do not share them.</textarea></label>
      <label class="f">Counters narrative<select class="f" id="lNarr">${W.narratives.map((n) => `<option value="${n.id}">${n.id} · ${esc(n.title)}</option>`).join('')}</select></label>
      <div class="row">${btn('Submit for approval', 'draftLine', {}, { cap: 'line:draft', cls: 'primary', testid: 'draft-line' })}</div>
    </section>
    <section class="panel"><header><h2>Read receipts</h2></header>${S.lines.filter((l) => l.cascadedAt != null).map((l) => `<b>${esc(l.id)} · ${esc(l.title)}</b><div class="scroll"><table><thead><tr><th>Force</th><th>Status</th><th>Welsh</th></tr></thead><tbody>${W.orgs.filter((o) => o.kind === 'force').map((f) => { const a = (S.acks[l.id] || []).includes(f.id); return `<tr><td>${esc(f.name)}</td><td>${a ? pill('acknowledged', 'ok') : pill('awaiting', 'warn')}</td><td>${f.welsh ? (l.cyBy ? pill('localised', 'ok') : pill('needed', 'warn')) : '<span class="muted">n/a</span>'}</td></tr>`; }).join('')}</tbody></table></div>`).join('') || '<p class="empty">No line cascaded yet.</p>'}</section></div>
    <section class="panel"><header><h2>Library</h2></header><div class="stack">${all.map((l) => {
      const st = l.base ? l.status : l.cascadedAt != null ? 'cascaded' : l.status;
      const acked = (S.acks[l.id] || []).includes(me().org);
      return `<div class="post" data-testid="line-${l.id}"><div class="row" style="justify-content:space-between"><b>${esc(l.id)} · ${esc(l.title)}</b><span class="row">${pill(st, st === 'expired' ? 'crit' : st === 'pending approval' ? 'warn' : 'ok')}${l.expires ? pill('expires ' + l.expires, 'plain') : ''}</span></div><span>${esc(l.text)}</span>${l.cy ? `<span class="small muted" lang="cy">${esc(l.cy)}</span>` : ''}
      ${l.base ? '' : `<span class="small muted">Drafted by ${who(l.by)}${l.approvedBy ? ' · approved by ' + who(l.approvedBy) : ''}${l.narrative ? ' · counters ' + l.narrative : ''}</span>`}
      <div class="row">${!l.base && st === 'pending approval' ? btn('Approve and cascade to all forces', 'approveLine', { l: l.id }, { cap: 'line:approve', cls: 'primary', testid: 'approve-line' }) : ''}
      ${!l.base && st === 'cascaded' && !acked ? (org().welsh && !l.cyBy ? btn('Add Welsh version and acknowledge', 'ackLine', { l: l.id, cy: 1 }, { cap: 'line:localise', cls: 'primary', testid: 'ack-line' }) : btn('Acknowledge', 'ackLine', { l: l.id }, { cap: 'line:ack', cls: 'primary', testid: 'ack-line' })) : ''}
      ${acked ? pill('acknowledged by ' + org().short, 'ok') : ''}</div></div>`;
    }).join('')}</div></section>`;
  };

  V.escalations = () => {
    const cands = livePosts().filter((p) => p.flags.includes('possible illegal content') || p.flags.includes('possible contempt breach'));
    return `${head('Platform referrals', 'A log of referrals of possibly illegal content to platforms, Ofcom or CTIRU, with response times. Police are not the regulator: Line of Blue logs referrals, it does not moderate.')}
    <div class="strip"><div class="stat"><span class="eyebrow">Referrals</span><span class="v">${S.referrals.length}</span></div><div class="stat"><span class="eyebrow">Resolved</span><span class="v">${S.referrals.filter((r) => r.status === 'resolved').length}</span></div><div class="stat"><span class="eyebrow">Average response</span><span class="v">${(() => { const d = S.referrals.filter((r) => r.status === 'resolved'); return d.length ? Math.round(d.reduce((s, r) => s + r.resolvedAt - r.t, 0) / d.length) + ' min' : '–'; })()}</span></div></div>
    <div class="grid2"><section class="panel"><header><h2>Referral log</h2></header><div class="scroll"><table><thead><tr><th>Ref</th><th>Content</th><th>Route</th><th>Status</th><th></th></tr></thead><tbody>${S.referrals.map((r) => `<tr><td class="mono">${r.id}</td><td class="small">${esc(W.posts.find((p) => p.id === r.post).text)}<br><span class="muted">${esc(PF[r.platform].name)} · logged ${clockStr(r.t)} by ${who(r.by)}</span></td><td>${esc(r.route)}</td><td>${r.status === 'resolved' ? pill('removed after ' + (r.resolvedAt - r.t) + ' min', 'ok') : pill('awaiting platform', 'warn')}</td><td>${r.status !== 'resolved' ? btn('Record removal', 'resolveRef', { r: r.id }, { cap: 'referral:update', sm: true, testid: 'resolve-' + r.id }) : ''}</td></tr>`).join('') || '<tr><td colspan="5" class="empty">No referrals yet.</td></tr>'}</tbody></table></div></section>
    <section class="panel"><header><h2>Flagged content to review</h2></header><label class="f">Route<select class="f" id="refRoute"><option>Platform trust and safety</option><option>CTIRU (terrorist content)</option><option>Ofcom (crisis response)</option></select></label>${cands.map((p) => `<div class="post"><span>${esc(p.text)}</span><div class="meta"><span class="mono">${p.account}</span><span>${esc(PF[p.platform].name)}</span>${p.flags.map((f) => pill(f, 'warn')).join('')}</div><div class="row">${S.referrals.some((r) => r.post === p.id) ? pill('referred', 'ok') : btn('Refer', 'refer', { p: p.id }, { cap: 'referral:log', sm: true, testid: 'refer-' + p.id })}</div></div>`).join('') || '<p class="empty">No flagged content at this time. Advance the clock.</p>'}</section></div>`;
  };

  V.horizon = () => `${head('Event horizon', 'A shared forward calendar of trials, protests, anniversaries, elections and major events, each with a risk rating and pre-prepared content (pre-bunking).')}
    <section class="panel"><div class="scroll"><table><thead><tr><th>Date</th><th>Event</th><th>Force</th><th>Risk</th><th>Pre-bunk content</th></tr></thead><tbody>${W.events.map((e) => `<tr><td class="mono">${e.date}</td><td>${esc(e.title)} ${e.purdah ? pill('pre-election period', 'warn') : ''}</td><td>${e.force ? esc(O[e.force].short) : 'National'}</td><td>${riskPill(e.risk)}</td><td class="small">${esc(e.prebunk)}</td></tr>`).join('')}</tbody></table></div></section>`;

  V.picture = () => {
    const rows = W.narratives.map((n) => [n, narrStats(n)]), live = rows.filter(([, s]) => s.count);
    const ahead = W.narratives.filter((n) => aheadBy(n.id) != null), waiting = live.filter(([, s]) => s.truth == null);
    const placeVol = {}; livePosts().forEach((p) => { placeVol[p.place] = (placeVol[p.place] || 0) + 1; });
    const cells = Object.entries(S.cells).filter(([, c]) => c.open).map(([id]) => I[id]);
    return `${head('National picture', 'Every force on one screen: which claims are growing, where they are spreading, and whether the police line got there first.')}
    <div class="strip">
      <div class="stat"><span class="eyebrow">Claims in play</span><span class="v">${live.length}</span><span class="small muted">${livePosts().length} public posts seen</span></div>
      <div class="stat"><span class="eyebrow">Over threshold</span><span class="v" style="color:var(--crit)">${live.filter(([, s]) => s.alert).length}</span><span class="small muted">≥ ${S.threshold} posts in 30 min</span></div>
      <div class="stat" data-testid="stat-ahead"><span class="eyebrow">Police line first</span><span class="v" style="color:var(--ok)">${ahead.length}</span><span class="small muted">pre-bunked before the claim appeared</span></div>
      <div class="stat"><span class="eyebrow">Waiting for a line</span><span class="v">${waiting.length}</span><span class="small muted">${cells.length ? 'cell open: ' + esc(cells.map((i) => O[i.force].short).join(', ')) : 'no Golden Hour cell open'}</span></div>
    </div>
    <section class="panel"><header><h2>How fast each claim is spreading</h2><span class="small muted">posts per 10 minutes · five largest claims · hover a point</span></header>${velocityChart()}</section>
    <div class="grid2"><section class="panel"><header><h2>Race to the truth</h2><span class="small muted">first post, alert threshold and police line for each claim</span></header>${raceChart()}</section>
    <section class="panel"><header><h2>Where it is spreading</h2></header>${map(placeVol)}
      <h3>Releases in the pipeline</h3><div class="row">${STAGES.map((st) => pill(`${STAGE_LABEL[st]}: ${S.releases.filter((r) => r.status === st).length}`, st === 'published' ? 'ok' : 'plain')).join(' ')}</div></section></div>`;
  };
  V.agent = () => {
    S.agent.msgs.filter((m) => m.pending && !inflight.has(m.id)).forEach((m) => Object.assign(m, offlineAnswer(m.q), { pending: false, mode: 'offline' }));
    const sel = S.kbSel && KB[S.kbSel];
    const kinds = [...new Set(W.knowledge.map((e) => e.kind))];
    const mode = agentMode === 'claude' ? pill('Claude, grounded in the knowledge base', 'ok') : agentMode === 'offline' ? pill('offline playbook mode', 'plain') : pill('connecting…', 'plain');
    return `${head('L.O.B Agent', 'Ask about any law, guidance, strategy or inspection finding that bears on police communications, or ask for a plan to get ahead of the next rumour. Answers cite the public source. The agent advises and drafts; people decide and sign off.')}
    <div class="grid2"><section class="panel"><header><h2>Ask the agent</h2>${mode}</header>
      <div class="row">${QUICK.map(([k, q], i) => `<button class="btn sm wrap" data-action="askQuick" data-i="${i}" data-testid="agent-quick-${k}">${esc(q)}</button>`).join('')}</div>
      <div class="row"><input type="text" id="agentQ" data-input="agentQ" value="${esc(S.agentQ || '')}" placeholder="e.g. Can we say the man is British?" aria-label="Question for the L.O.B Agent" style="flex:1 1 260px">${btn('Ask', 'askAgent', {}, { cls: 'primary', testid: 'agent-ask' })}</div>
      <div class="thread" data-testid="agent-thread">${S.agent.msgs.slice().reverse().map(msgCard).join('') || '<p class="empty">No questions yet. Try one of the prompts above.</p>'}</div>
      ${S.agent.msgs.length ? `<div class="row">${btn('Clear conversation', 'agentClear', {}, { sm: true })}</div>` : ''}
    </section>
    <section class="panel" data-testid="kb"><header><h2>What the agent knows</h2><span class="small muted">${W.knowledge.length} public sources · summaries, not legal advice</span></header>
      ${sel ? `<div class="sev green" data-testid="kb-selected"><span class="eyebrow">${esc(sel.id)} · ${esc(sel.kind)} · ${esc(sel.owner)}</span><b>${esc(sel.title)}</b><span class="small">${esc(sel.summary)}</span><span class="small"><b>For comms:</b> ${esc(sel.comms)}</span>${sel.url ? `<a class="small" href="${esc(sel.url)}" target="_blank" rel="noopener">Open the source</a>` : ''}</div>` : '<p class="small muted">Select a citation, or a source below, to see what it says.</p>'}
      <div class="scroll" style="max-height:520px">${kinds.map((k) => `<h3>${esc(k[0].toUpperCase() + k.slice(1))}</h3>${W.knowledge.filter((e) => e.kind === k).map((e) => `<button class="kbrow ${S.kbSel === e.id ? 'sel' : ''}" data-action="kbOpen" data-k="${e.id}"><span class="mono small">${e.id}</span> ${esc(e.title)} <span class="small muted">${esc(e.owner)}</span></button>`).join('')}`).join('')}</div>
      <p class="small muted">In production the agent would read the full texts from each owner, refresh them on a schedule and quote the passage it relied on.</p>
    </section></div>`;
  };
  V.scenarios = () => {
    const sc = SC[S.scenario];
    return `${head('Scenarios', 'Scripted end-to-end exercises across forces, NPCC, NPoCC, government and partners. Each step names who acts. Steps tick automatically when the demo state shows they happened.')}
    <div class="row">${W.scenarios.map((s) => { const done = s.steps.filter((st) => check(st.check)).length; return `<button class="btn ${s.id === sc.id ? 'primary' : ''}" data-action="pickScenario" data-s="${s.id}" data-testid="scenario-${s.id}">${esc(s.id)} ${done}/${s.steps.length}</button>`; }).join('')}</div>
    <section class="panel"><header><h2>${esc(sc.id)} · ${esc(sc.title)}</h2><span class="small muted">${sc.actors.length} actors</span></header><p>${esc(sc.goal)}</p>
      <ul class="steps">${sc.steps.map((st, i) => { const ok = check(st.check), nextIdx = sc.steps.findIndex((x) => !check(x.check)); return `<li data-testid="step-${sc.id}-${i}" data-done="${ok}"><span class="mono">${clockStr(st.t)}</span><span class="tick ${ok ? 'done' : i === nextIdx ? 'next' : ''}" aria-label="${ok ? 'done' : 'not done'}"></span><span><b>${who(st.actor)}</b> ${esc(P[st.actor].role)}<br>${esc(st.do)}</span><span>${ok ? pill('done', 'ok') : btn('Act as ' + P[st.actor].name.split(' ').slice(-1)[0], 'actAs', { p: st.actor, v: st.view, t: st.t }, { sm: true, testid: `act-${sc.id}-${i}` })}</span></li>`; }).join('')}</ul>
    </section>
    <section class="panel"><header><h2>Actors in this scenario</h2></header><div class="row">${sc.actors.map((a) => pill(P[a].name + ' · ' + O[P[a].org].short, 'plain')).join('')}</div></section>`;
  };

  V.audit = () => {
    if (can('audit:view') && !S.auditViewed) { S.auditViewed = true; log('Decision log reviewed', 'Independent review of the decision trail'); save(); }
    return `${head('Decision log', 'Every check, approval, disclosure decision, referral and refusal, with the person, the time and the reason. Decision records are kept; scraped content is short-retention and minimised.')}
    <section class="panel"><div class="scroll"><table><thead><tr><th>Ref</th><th>Time</th><th>Who</th><th>Action</th><th>Detail</th></tr></thead><tbody>${S.audit.map((d) => `<tr><td class="mono">${d.id}</td><td class="mono">${clockStr(d.t)}</td><td>${who(d.who)}</td><td>${esc(d.action)}</td><td class="small">${esc(d.detail)}</td></tr>`).join('') || '<tr><td colspan="5" class="empty">No decisions yet.</td></tr>'}</tbody></table></div></section>`;
  };

  V.governance = () => `${head('Data and safeguards', esc(W.meta.notice))}
    <div class="grid2"><section class="panel"><header><h2>Threat actor tiers</h2></header><div class="scroll"><table><thead><tr><th>Tier</th><th>Entity (fictional)</th><th>What Line of Blue may do</th></tr></thead><tbody>${W.actors.map((a) => `<tr><td>${pill('Tier ' + a.tier)}</td><td><b>${esc(a.name)}</b><br><span class="small muted">${esc(a.basis)}</span></td><td class="small">${esc(a.allowed)}</td></tr>`).join('')}<tr><td>${pill('Tier D', 'plain')}</td><td><b>No entities</b></td><td class="small">${esc(W.tierDRule)}</td></tr></tbody></table></div>
      <p class="small muted">In production, Tier A comes straight from the Home Office proscribed list and Tier B from government sanctions notices. The demo uses fictional stand-ins only.</p></section>
    <section class="panel"><header><h2>What Line of Blue does not do</h2></header><ul class="stack small" style="margin:0;padding-left:18px">
      <li>Read private messages or join closed groups.</li><li>Use fake accounts.</li><li>Build profiles or watchlists of lawful people. Any individual monitoring needs a recorded RIPA authorisation.</li>
      <li>Record lawful but offensive posts against people.</li><li>Attribute activity to foreign states in public messages.</li><li>Make decisions: every output is advisory and a named person decides.</li></ul>
      <h3>About Line of Blue</h3><p class="small">Product website: <a href="https://lineofblue.co.uk" target="_blank" rel="noopener">lineofblue.co.uk</a></p><h3>Synthetic dataset</h3><p class="small">${W.personas.length} personas across ${W.orgs.length} organisations, ${W.narratives.length} narratives, ${W.posts.length} posts, ${W.incidents.length} incidents, ${W.events.length} horizon events, ${W.scenarios.length} scenarios. ${esc(W.meta.generatedBy)}.</p>
      <div class="row">${btn('Reset demo to the start', 'reset', {}, { cls: 'danger', testid: 'reset' })}</div></section></div>`;

  // ------------------------------------------------------------------ actions
  const H = {
    selNarr: (d) => { S.selNarr = d.n; },
    triage: (d) => { narr(d.n).triaged = true; log('Alert triaged', `${d.n} ${N[d.n].title}`, { incident: N[d.n].incident }); toast('Alert triaged and logged.'); },
    linkNarr: (d) => { const n = N[d.n]; narr(d.n).linked = true; narr(d.n).triaged = true; log('Narrative linked to incident', `${d.n} linked to ${n.incident}`, { incident: n.incident }); toast(`${d.n} linked to ${n.incident}. The Golden Hour cell now shows it.`); },
    handover: (d) => { S.handovers[d.n] = { status: 'sent', by: S.persona, at: S.clock }; log('Indicators handed to CTP and government', `${d.n}: Tier B indicators. Not for public attribution.`, { incident: N[d.n].incident }); toast('Indicators sent to CTP and the government online information team.'); },
    acceptHandover: (d) => { S.handovers[d.n].status = 'accepted'; S.handovers[d.n].acceptedBy = S.persona; log('Handover accepted', `${d.n} accepted by ${me().name}`, { incident: N[d.n].incident }); toast('Handover accepted.'); },
    tension: (d) => { const n = N[d.n]; S.tension[n.places[0]] = { level: n.risk === 'critical' ? 'high' : 'elevated', by: S.persona }; log('Community tension assessed', `${PL[n.places[0]].name}: ${S.tension[n.places[0]].level} (from ${d.n})`, { incident: n.incident }); toast('Tension assessment recorded and shared with the cell.'); },
    track: (d) => {
      const p = W.posts.find((x) => x.id === d.p), n = N[p.narrative];
      const tierD = n.verdict === 'opinion' || !n.actor;
      S.guardrails.push(tierD ? 'tier-d' : 'tier-c'); fire('track-refused');
      log('Refused: track an individual account', `${p.account} on ${n.id}. ${tierD ? 'Lawful speech / no tiered actor: Line of Blue never profiles people (Tier D).' : 'Tier ' + A[n.actor].tier + ': individual monitoring needs a recorded RIPA authorisation, not available in Line of Blue.'}`);
      toast(tierD ? 'Refused. Line of Blue analyses narratives, not people. This account is not tracked, and the refusal is logged.' : 'Refused. Monitoring an individual needs a recorded RIPA authorisation through intelligence channels. Logged.');
    },
    refer: (d) => { const p = W.posts.find((x) => x.id === d.p); if (S.referrals.some((r) => r.post === p.id)) return; const route = ($('#refRoute') || {}).value || 'Platform trust and safety'; S.referrals.push({ id: nid('REF'), post: p.id, platform: p.platform, route, t: S.clock, by: S.persona, status: 'open' }); log('Referral logged', `${p.id} on ${PF[p.platform].name} via ${route}`, { incident: N[p.narrative].incident }); toast('Referral logged.'); },
    resolveRef: (d) => { const r = S.referrals.find((x) => x.id === d.r); r.status = 'resolved'; r.resolvedAt = Math.max(S.clock, r.t + 1); log('Referral outcome recorded', `${r.id}: content removed after ${r.resolvedAt - r.t} min`); },
    openCell: (d) => { const c = cell(d.inc); c.open = true; c.openedAt = S.clock; log('Critical incident declared', `${I[d.inc].title}. Golden Hour cell opened; NPCC Comms and NPoCC notified.`, { incident: d.inc }); toast('Golden Hour cell open. NPCC Comms and NPoCC have been notified.'); },
    addFact: (d) => { const v = ($('#factText') || {}).value || ''; if (!v.trim()) { toast('Write the fact first.'); return; } H.quickFact({ inc: d.inc, text: v }); },
    quickFact: (d) => { const c = cell(d.inc); if (c.facts.some((f) => f.text === d.text)) return; c.facts.push({ id: nid('F'), t: S.clock, text: d.text, by: S.persona }); log('Fact logged (unverified)', d.text, { incident: d.inc }); },
    verifyFact: (d) => { const f = cell(d.inc).facts.find((x) => x.id === d.f); f.verifiedBy = S.persona; log('Fact verified', f.text, { incident: d.inc }); },
    decide: (d) => { const r = ($('#discReason') || {}).value || ''; if (!r.trim()) { toast('Record the reasons first. A decision without reasons cannot be saved.'); return; } cell(d.inc).disclosure = { decision: d.d, rationale: r, by: S.persona, t: S.clock }; log('Disclosure decision', `${d.d}. Reasons: ${r}`, { incident: d.inc }); },
    hoRequest: (d) => { cell(d.inc).ho = { status: 'requested', requestedBy: S.persona, at: S.clock }; log('Home Office asked to confirm immigration status', I[d.inc].title, { incident: d.inc }); toast('Request sent to the Home Office press office.'); },
    hoRespond: (d) => { const c = cell(d.inc); c.ho.status = d.status; c.ho.by = S.persona; log('Home Office response', d.status === 'confirmed' ? 'Confirmed: no immigration case for the arrested man. Police may say so.' : 'Declined to comment.', { incident: d.inc }); },
    example: (d) => {
      const ex = [['Holding statement', 'INC-NMP-0412'], ['Holding statement', 'INC-NMP-0412'], ['Curfew rebuttal', 'INC-NMP-0412'], ['Nationality update', 'INC-NMP-0412'], ['Trial update', ''], ['Charge update', ''], ['Policing plan explainer', ''], ['Flood hoax rebuttal', 'INC-DGP-0031']];
      const texts = V['safe-to-say'].ex;
      S.draft = { title: ex[d.i][0], incident: ex[d.i][1], text: texts[d.i], cy: '' };
    },
    cyTemplate: () => { S.draft.cy = 'Mae argae Llyn Teg yn ddiogel. Dilynwch y rhybudd llifogydd swyddogol a defnyddiwch y ganolfan orffwys yn Ysgol Aberteg os oes angen i chi adael eich cartref.'; },
    submitDraft: () => {
      const d = S.draft, res = runChecks(d.text, d.cy, d.incident, me().org, { prebunk: d.prebunk });
      res.forEach((r) => fire(r.id));
      if (res.some((r) => r.level === 'red')) { log('Safe to Say: release blocked', `${d.title}: ${res.filter((r) => r.level === 'red').map((r) => r.title).join('; ')}`, { incident: d.incident }); toast('Blocked. Fix the red items.'); return; }
      const amb = res.filter((r) => r.level === 'amber');
      const reason = ($('#dReason') || {}).value || '';
      if (amb.length && !reason.trim()) { toast('Add a decision record for the amber items before submitting.'); return; }
      const narrs = d.prebunk ? [d.prebunk] : d.incident ? W.narratives.filter((n) => n.incident === d.incident && narrStats(n).count).map((n) => n.id) : W.narratives.filter((n) => narrStats(n).count && n.places.some((pl) => PL[pl].force === me().org)).map((n) => n.id);
      const r = { id: nid('REL'), title: d.title, text: d.text, cy: d.cy, incident: d.incident || null, org: me().org, author: S.persona, status: 'checked', decision: reason || null, narratives: narrs, prebunk: d.prebunk || null, history: [] };
      if (r.incident && !I[r.incident].gold) r.incident = r.incident; // non-critical incidents use the short flow
      S.releases.push(r);
      log('Safe to Say check recorded', `${r.id} ${r.title}: ${amb.length ? amb.length + ' amber item(s) accepted. Reason: ' + reason : 'clear'}`, { incident: r.incident });
      S.draft = { text: '', cy: '', incident: d.incident, title: 'Update' };
      toast(`${r.id} submitted. ${r.incident && I[r.incident].gold ? 'Next: legal review in the Golden Hour cell.' : 'You can now publish it.'}`);
    },
    advance: (d) => { const r = S.releases.find((x) => x.id === d.r); r.status = d.to; if (d.to === 'published') { r.publishedAt = S.clock; r.publishedBy = S.persona; } log(d.to === 'draft' ? 'Release returned to author' : 'Release: ' + STAGE_LABEL[d.to], `${r.id} ${r.title}`, { incident: r.incident }); if (d.to === 'published') toast(`${r.id} published at ${clockStr(S.clock)}. Time to truth updated on linked narratives.`); },
    draftLine: () => { const l = { id: nid('LN'), title: $('#lTitle').value, text: $('#lText').value, narrative: $('#lNarr').value, status: 'pending approval', by: S.persona, scenario: 'SC-01', checks: ['Contempt', 'Impartiality'] }; S.lines.unshift(l); log('National line drafted', `${l.id} ${l.title}`, { incident: N[l.narrative].incident }); toast('Submitted to the Head of NPCC Communications for approval.'); },
    approveLine: (d) => { const l = S.lines.find((x) => x.id === d.l); l.status = 'approved'; l.approvedBy = S.persona; l.cascadedAt = S.clock; l.expires = '2026-11-28'; log('National line approved and cascaded', `${l.id} sent to ${W.orgs.filter((o) => o.kind === 'force').length} forces`, { incident: N[l.narrative].incident }); toast('Cascaded to all forces with read receipts.'); },
    ackLine: (d) => { const l = S.lines.find((x) => x.id === d.l); if (d.cy) { l.cy = 'Rydym yn deall bod pobl eisiau atebion. Mae dyn yn y ddalfa. Peidiwch â rhannu honiadau heb eu cadarnhau.'; l.cyBy = S.persona; } (S.acks[l.id] = S.acks[l.id] || []).push(me().org); log('National line acknowledged', `${l.id} by ${org().name}${d.cy ? ' with Welsh version' : ''}`); },
    pickScenario: (d) => { S.scenario = d.s; },
    prebunk: (d) => { const f = forecasts(d.inc).find((x) => x.narrative === d.n); if (!f) return; S.draft = { title: 'Pre-bunk: ' + f.pattern.toLowerCase(), text: f.prebunk, cy: '', incident: d.inc, prebunk: f.narrative }; log('Pre-bunk drafted from the rumour forecast', `${f.narrative} ${f.pattern}`, { incident: d.inc }); toast('Pre-bunk loaded into Safe to Say. Check it and submit it for sign-off.'); location.hash = 'safe-to-say'; },
    askQuick: (d) => { runAgent(QUICK[+d.i][1]); },
    askAgent: () => { const el = $('#agentQ'), q = ((el && el.value) || S.agentQ || '').trim(); if (!q) { toast('Type a question first.'); return; } S.agentQ = ''; runAgent(q); },
    agentDraft: (d) => { const m = S.agent.msgs.find((x) => x.id === d.m); if (!m || !m.draft) return; S.draft = { title: m.draft.title, text: m.draft.text, cy: '', incident: m.draft.incident || '', prebunk: m.draft.narrative || null }; log('L.O.B Agent draft sent to Safe to Say', m.draft.title, { incident: m.draft.incident }); location.hash = 'safe-to-say'; },
    agentClear: () => { S.agent = { msgs: [], asked: S.agent.asked }; },
    kbOpen: (d) => { S.kbSel = d.k; if (current() !== 'agent') location.hash = 'agent'; },
    actAs: (d) => { S.persona = d.p; if (+d.t > S.clock) S.clock = +d.t; if (d.v === 'golden-hour') S.selInc = 'INC-NMP-0412'; location.hash = d.v === 'inbox' ? 'inbox' : d.v; },
    clock: (d) => { S.clock = Math.max(-60, Math.min(240, S.clock + +d.m)); },
    reset: () => { const keep = S.persona; S = fresh(); S.persona = keep; toast('Demo reset to 13:50.'); },
  };
  V['safe-to-say'].ex = [
    'Officers were called to Harbourside Market, Port Ellery, at 13:52 today. Two people were injured and one is in a serious condition in hospital. A 34-year-old man from Port Ellery was arrested at the scene and is in custody. Please do not share speculation about the people involved.',
    'Callum Breward, the attacker, was arrested after the terror attack. He is not an asylum seeker. Shared from northmoor-police-news.info',
    'There is no curfew in Port Ellery. The fake notice was created by the Lantern Bureau, a foreign state operation.',
    'The man arrested is a 34-year-old British national from Port Ellery. Claims that he lives at the Harbourside hotel are false.',
    'Kieran Doyle appears at Brennford Crown Court today in the Halden Street case. He has previous convictions.',
    'A man has been charged after a woman aged 23 was assaulted near Rivermead Close.',
    'Our policing plan for Saturday is the same for both groups. We facilitate lawful protest and act on any crime, whoever commits it. Some people call this two-tier policing; it is not.',
    'Llyn Teg dam is safe. Follow the official flood warning for the lower Teg valley and use the rest centre at Ysgol Aberteg if you need to leave home.',
  ];

  // ------------------------------------------------------------------ shell
  function current() { const h = (location.hash || '').replace('#', ''); return V[h] ? h : 'inbox'; }
  function render() {
    const v = current();
    const alerts = activeAlerts().length, work = myOpenSteps().length;
    let group = '';
    $('#rail').innerHTML = `<div class="brand"><span class="brand-mark" aria-hidden="true"></span><div><b>Line of Blue</b><div class="small muted">synthetic demo · <a href="https://lineofblue.co.uk" target="_blank" rel="noopener" style="display:inline;padding:0;color:var(--accent)">lineofblue.co.uk</a></div></div></div>` + VIEWS.map(([id, label, g]) => { const gh = g !== group ? `<span class="group eyebrow">${g}</span>` : ''; group = g; const badge = id === 'radar' && alerts ? `<span class="count">${alerts}</span>` : id === 'inbox' && work ? `<span class="count">${work}</span>` : ''; return `${gh}<a href="#${id}" ${id === v ? 'aria-current="page"' : ''}>${label}${badge}</a>`; }).join('');
    const groups = {}; W.personas.forEach((p) => { (groups[O[p.org].name] = groups[O[p.org].name] || []).push(p); });
    $('#who').innerHTML = `<label for="persona" class="eyebrow">Acting as</label><select id="persona" data-change="persona">${Object.entries(groups).map(([g, ps]) => `<optgroup label="${esc(g)}">${ps.map((p) => `<option value="${p.id}" ${p.id === S.persona ? 'selected' : ''}>${esc(p.name)} · ${esc(p.role)}</option>`).join('')}</optgroup>`).join('')}</select>`;
    $('#clock').innerHTML = `<span class="eyebrow">Scenario clock</span><span class="time" data-testid="clock">${clockStr(S.clock)}</span>${btn('+10 min', 'clock', { m: 10 }, { sm: true, testid: 'clock-10' })}${btn('+30 min', 'clock', { m: 30 }, { sm: true, testid: 'clock-30' })}`;
    $('#view').innerHTML = V[v]();
    const t = $('#toast'); t.hidden = !toastMsg; t.textContent = toastMsg; toastMsg = '';
    save();
  }
  document.addEventListener('click', (e) => {
    const b = e.target.closest('[data-action]'); if (!b || b.disabled) return;
    const fn = H[b.dataset.action]; if (!fn) return;
    fn({ ...b.dataset }); render();
  });
  document.addEventListener('change', (e) => {
    const k = e.target.dataset.change; if (!k) return;
    if (k === 'persona') S.persona = e.target.value;
    else if (k === 'threshold') S.threshold = +e.target.value;
    else if (k === 'trigger') { S.trigger = e.target.value; log('Rule setting changed', `Proceedings active from ${S.trigger}`); }
    else if (k === 'selInc') S.selInc = e.target.value;
    else if (k === 'dInc') S.draft.incident = e.target.value;
    render();
  });
  let tmr;
  document.addEventListener('input', (e) => {
    const k = e.target.dataset.input; if (!k) return;
    if (k === 'agentQ') { S.agentQ = e.target.value; return save(); }
    const map = { dTitle: 'title', dText: 'text', dCy: 'cy' }; S.draft[map[k]] = e.target.value;
    if (k === 'dTitle') return save();
    clearTimeout(tmr); tmr = setTimeout(() => { const pos = e.target.selectionStart, id = e.target.id; render(); const el = document.getElementById(id); if (el) { el.focus(); try { el.setSelectionRange(pos, pos); } catch (er) { /* ignore */ } } }, 350);
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Enter' && e.target.id === 'agentQ') { e.preventDefault(); H.askAgent(); render(); } });
  window.addEventListener('hashchange', render);
  sampler().then(() => { if (current() === 'agent') render(); });
  render();
})();
