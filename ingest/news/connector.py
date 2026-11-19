"""Line of Blue: public news connector. Publishers' RSS feeds, Google News search (UK edition) and GDELT.
Stores the headline, a short summary and the link, never the full article. Publishers are organisations, so
the publisher name is kept as the account. Standard library only."""
import gzip, hashlib, html, json, re, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

UA = "line-of-blue-news/0.1 (+https://lineofblue.co.uk)"
POLICE = re.compile(r"\b(police|policing|officers?|constabulary|met|arrest(ed|s)?|charged|riot|disorder|protest|stabbing|"
                    r"misinformation|disinformation|fake|hoax|rumou?rs?|home office|curfew|spiking|scam)\b", re.I)
TAGS = re.compile(r"<[^>]+>")


def clean(text, n=300):
    t = html.unescape(TAGS.sub(" ", text or ""))
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + "…"


def load_sources(path):
    srcs = json.load(open(path))["sources"]
    for s in srcs:
        if s["kind"] not in ("rss", "google_news", "gdelt"):
            raise ValueError(f"{s['id']}: kind must be rss, google_news or gdelt")
        if s["kind"] == "rss" and not s.get("url", "").startswith("https://"):
            raise ValueError(f"{s['id']}: rss sources need an https url")
        if s["kind"] != "rss" and not s.get("query"):
            raise ValueError(f"{s['id']}: search sources need a query")
    return srcs


def approved(srcs):
    return [s for s in srcs if s.get("status") == "approved"]


def url_for(s):
    if s["kind"] == "rss":
        return s["url"]
    if s["kind"] == "google_news":
        return "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": s["query"], "hl": "en-GB", "gl": "GB", "ceid": "GB:en"})
    return "https://api.gdeltproject.org/api/v2/doc/doc?" + urllib.parse.urlencode(
        {"query": s["query"], "mode": "artlist", "format": "json", "maxrecords": "50", "timespan": "2d", "sort": "datedesc"})


def http_get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, application/json, */*"})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
            return gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw  # some publishers gzip regardless
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 1:  # GDELT allows one request every 5 seconds
                time.sleep(6); continue
            raise


def _iso(value):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone().isoformat()
    except (TypeError, ValueError):
        pass
    m = re.match(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z", value)  # GDELT seendate
    return f"{m[1]}-{m[2]}-{m[3]}T{m[4]}:{m[5]}:{m[6]}+00:00" if m else value


def parse_feed(raw):
    """RSS 2.0 or Atom -> list of {title, summary, link, published, publisher?}."""
    root = ET.fromstring(raw)
    items = []
    for it in root.iter("item"):
        src = it.find("source")
        items.append({"title": clean(it.findtext("title"), 200), "summary": clean(it.findtext("description")),
                      "link": (it.findtext("link") or "").strip(), "published": _iso(it.findtext("pubDate")),
                      "publisher": src.text.strip() if src is not None and src.text else None})
    ns = "{http://www.w3.org/2005/Atom}"
    for it in root.iter(ns + "entry"):
        link = it.find(ns + "link")
        items.append({"title": clean(it.findtext(ns + "title"), 200), "summary": clean(it.findtext(ns + "summary") or it.findtext(ns + "content")),
                      "link": link.get("href") if link is not None else "", "published": it.findtext(ns + "updated") or it.findtext(ns + "published"),
                      "publisher": None})
    return items


def parse_gdelt(raw):
    body = json.loads(raw or b"{}") if raw.strip() else {}
    return [{"title": clean(a.get("title"), 200), "summary": "", "link": a.get("url", ""), "published": _iso(a.get("seendate")),
             "publisher": a.get("domain")} for a in body.get("articles", [])]


def keep(item, source):
    if not item["title"] or not item["link"]:
        return False
    if source["kind"] != "rss" or source.get("allTopics"):
        return True  # search sources are already targeted
    return bool(POLICE.search(item["title"] + " " + item["summary"]))


def to_post(item, source):
    pub = item.get("publisher") or source["publisher"]
    text = item["title"] + (" — " + item["summary"] if item["summary"] and item["summary"] != item["title"] else "")
    return {"id": "N" + hashlib.sha256(item["link"].encode()).hexdigest()[:12], "narrative": None, "set": source["id"],
            "platform": "news", "source": "news-" + source.get("scope", source["kind"]), "synthetic": False, "t": item["published"],
            "account": pub, "place": source.get("area"), "text": text, "link": item["link"], "lang": "en", "reach": 0, "shares": 0, "flags": []}


def collect(source, get=http_get, seen=None):
    """Fetch one source and return new posts. seen: set of post ids already stored (updated in place)."""
    seen = set() if seen is None else seen
    raw = get(url_for(source))
    items = parse_gdelt(raw) if source["kind"] == "gdelt" else parse_feed(raw)
    posts = []
    for it in items:
        if keep(it, source):
            p = to_post(it, source)
            if p["id"] not in seen:
                seen.add(p["id"]); posts.append(p)
    return posts, len(items)
