#!/usr/bin/env python3
"""Build data/uk_map.json: a real UK and Ireland outline plus reference layers for the National map.

Geography: Natural Earth 1:10m countries (public domain), via the world-atlas npm package
(countries-10m.json). Pass its path as the first argument; the output is committed so the
build needs no network.

Reference layers are PUBLIC facts at approximate, town-level positions (force headquarters,
civil nuclear sites, major defence sites, rail hubs, ports). They are for orientation, not
operational use, and must be checked against official sources before any real deployment.
Official police force area boundaries (ONS Open Geography, OGL) replace the HQ points once
the environment can reach the ONS geoportal.

The message layer is SYNTHETIC: deterministic volumes by force area, clearly labelled.
"""
import json, math, os, random, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, "data", "countries-10m.json")

LON0, LAT0, K = -4.0, 54.5, math.cos(math.radians(54.5))
BOX = (-10.8, 49.8, 2.0, 60.95)  # lon/lat window
W = 560


def proj_raw(lon, lat):
    return (lon - LON0) * K, -(lat - LAT0)


x0, y0 = proj_raw(BOX[0], BOX[3])
x1, y1 = proj_raw(BOX[2], BOX[1])
S = W / (x1 - x0)
H = round((y1 - y0) * S)


def P(lon, lat):
    x, y = proj_raw(lon, lat)
    return round((x - x0) * S, 1), round((y - y0) * S, 1)


def decode_arcs(t):
    sx, sy = t["transform"]["scale"]; tx, ty = t["transform"]["translate"]
    out = []
    for arc in t["arcs"]:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        out.append(pts)
    return out


def ring(arcs, idx):
    pts = []
    for i in idx:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts


def simplify(pts, eps):
    if len(pts) < 4: return pts
    def d(p, a, b):
        (x, y), (x1_, y1_), (x2, y2) = p, a, b
        dx, dy = x2 - x1_, y2 - y1_
        if dx == dy == 0: return math.hypot(x - x1_, y - y1_)
        return abs(dy * x - dx * y + x2 * y1_ - y2 * x1_) / math.hypot(dx, dy)
    stack, keep = [(0, len(pts) - 1)], {0, len(pts) - 1}
    while stack:
        s, e = stack.pop(); dm, im = 0, s
        for i in range(s + 1, e):
            dd = d(pts[i], pts[s], pts[e])
            if dd > dm: dm, im = dd, i
        if dm > eps: keep.add(im); stack += [(s, im), (im, e)]
    return [pts[i] for i in sorted(keep)]


t = json.load(open(SRC))
arcs = decode_arcs(t)
land = {}
for g in t["objects"]["countries"]["geometries"]:
    name = g["properties"]["name"]
    if name not in ("United Kingdom", "Ireland", "Isle of Man", "Jersey", "Guernsey", "France"): continue
    polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
    d = []
    for poly in polys:
        for k, r in enumerate(poly[:1]):  # outer rings only
            pts = ring(arcs, r)
            if not any(BOX[0] - 1 <= lo <= BOX[2] + 1 and BOX[1] - 1 <= la <= BOX[3] + 1 for lo, la in pts): continue
            xy = [P(lo, la) for lo, la in pts]
            xy = simplify(xy, 0.6)
            if len(xy) < 4: continue
            xs = [p[0] for p in xy]; ys = [p[1] for p in xy]
            if (max(xs) - min(xs)) * (max(ys) - min(ys)) < 4: continue
            d.append("M" + "L".join(f"{x} {y}" for x, y in xy) + "Z")
    land[name] = "".join(d)

# ---------------------------------------------------------------- reference layers (approximate public locations)
# Territorial forces: headquarters towns. nation: E (England), W (Wales), S, NI.
FORCES = [
    ("Avon and Somerset", 51.48, -2.77, "E"), ("Bedfordshire", 52.11, -0.50, "E"), ("Cambridgeshire", 52.33, -0.18, "E"),
    ("Cheshire", 53.19, -2.52, "E"), ("City of London", 51.515, -0.09, "E"), ("Cleveland", 54.57, -1.23, "E"),
    ("Cumbria", 54.66, -2.75, "E"), ("Derbyshire", 53.05, -1.40, "E"), ("Devon and Cornwall", 50.72, -3.53, "E"),
    ("Dorset", 50.67, -2.27, "E"), ("Durham", 54.79, -1.59, "E"), ("Dyfed-Powys", 51.86, -4.31, "W"),
    ("Essex", 51.73, 0.47, "E"), ("Gloucestershire", 51.82, -2.28, "E"), ("Greater Manchester", 53.48, -2.24, "E"),
    ("Gwent", 51.65, -3.02, "W"), ("Hampshire and Isle of Wight", 50.97, -1.35, "E"), ("Hertfordshire", 51.80, -0.20, "E"),
    ("Humberside", 53.74, -0.33, "E"), ("Kent", 51.27, 0.52, "E"), ("Lancashire", 53.73, -2.70, "E"),
    ("Leicestershire", 52.59, -1.20, "E"), ("Lincolnshire", 53.26, -0.49, "E"), ("Merseyside", 53.41, -2.98, "E"),
    ("Metropolitan Police", 51.50, -0.13, "E"), ("Norfolk", 52.57, 1.11, "E"), ("North Wales", 53.29, -3.72, "W"),
    ("North Yorkshire", 54.34, -1.43, "E"), ("Northamptonshire", 52.20, -0.89, "E"), ("Northumbria", 55.05, -1.75, "E"),
    ("Nottinghamshire", 53.00, -1.13, "E"), ("South Wales", 51.50, -3.58, "W"), ("South Yorkshire", 53.40, -1.42, "E"),
    ("Staffordshire", 52.81, -2.12, "E"), ("Suffolk", 52.06, 1.27, "E"), ("Surrey", 51.24, -0.57, "E"),
    ("Sussex", 50.87, 0.01, "E"), ("Thames Valley", 51.82, -1.29, "E"), ("Warwickshire", 52.31, -1.57, "E"),
    ("West Mercia", 52.22, -2.17, "E"), ("West Midlands", 52.48, -1.90, "E"), ("West Yorkshire", 53.68, -1.50, "E"),
    ("Wiltshire", 51.35, -1.99, "E"), ("Police Scotland", 56.06, -3.72, "S"), ("PSNI", 54.60, -5.93, "NI"),
]
LAYERS = {
    "btp": {"label": "British Transport Police: rail hubs", "note": "BTP polices the railways of England, Wales and Scotland. Hubs are major stations, not its full estate.",
            "points": [("BTP HQ, London", 51.53, -0.14), ("Birmingham", 52.48, -1.90), ("Manchester", 53.48, -2.23), ("Leeds", 53.79, -1.55), ("Newcastle", 54.97, -1.62),
                       ("Glasgow", 55.86, -4.25), ("Edinburgh", 55.95, -3.19), ("Cardiff", 51.48, -3.18), ("Bristol", 51.45, -2.58), ("York", 53.96, -1.09), ("Crewe", 53.09, -2.43), ("Preston", 53.76, -2.71), ("Carlisle", 54.89, -2.93), ("Peterborough", 52.57, -0.25), ("Reading", 51.46, -0.97), ("Swansea", 51.62, -3.94), ("Sheffield", 53.38, -1.46), ("Leicester", 52.63, -1.13)],
            "lines": [["BTP HQ, London", "Peterborough", "York", "Newcastle", "Edinburgh"], ["BTP HQ, London", "Birmingham", "Crewe", "Preston", "Carlisle", "Glasgow"],
                      ["BTP HQ, London", "Reading", "Bristol", "Cardiff", "Swansea"], ["BTP HQ, London", "Leicester", "Sheffield", "Leeds"], ["Crewe", "Manchester"], ["Edinburgh", "Glasgow"]]},
    "cnc": {"label": "Civil Nuclear Constabulary: civil nuclear sites", "note": "CNC protects civil nuclear sites and nuclear material in transit.",
            "points": [("CNC HQ, Culham", 51.66, -1.24), ("Sellafield", 54.42, -3.50), ("Dounreay", 58.58, -3.75), ("Heysham", 54.03, -2.92), ("Hartlepool", 54.64, -1.18),
                       ("Torness", 55.97, -2.41), ("Hunterston", 55.72, -4.89), ("Hinkley Point", 51.21, -3.13), ("Sizewell", 52.21, 1.62), ("Dungeness", 50.91, 0.96),
                       ("Capenhurst", 53.26, -2.95), ("Springfields", 53.77, -2.80), ("Harwell", 51.58, -1.31), ("Wylfa", 53.42, -4.48)]},
    "mdp": {"label": "Ministry of Defence Police: major defence sites", "note": "MDP protects the defence estate, including the nuclear deterrent and some visiting-forces bases.",
            "points": [("MDP HQ, Wethersfield", 51.97, 0.50), ("HMNB Clyde (Faslane)", 56.07, -4.82), ("RNAD Coulport", 56.05, -4.88), ("HMNB Devonport", 50.38, -4.18),
                       ("HMNB Portsmouth", 50.80, -1.11), ("AWE Aldermaston", 51.37, -1.15), ("AWE Burghfield", 51.40, -1.03), ("RAF Lakenheath and Mildenhall", 52.41, 0.56),
                       ("Menwith Hill", 54.01, -1.69), ("RAF Fairford", 51.68, -1.79), ("RAF Fylingdales", 54.36, -0.67)]},
    "mil": {"label": "Service police", "note": "Royal Navy Police, Royal Military Police and RAF Police, with the joint Defence Serious Crime Command.",
            "points": [("Defence Serious Crime Command, Southwick Park", 50.87, -1.11), ("Royal Navy Police, Portsmouth", 50.81, -1.12), ("RAF Police, RAF Honington", 52.34, 0.77), ("Royal Military Police, Andover", 51.21, -1.48)]},
    "port": {"label": "Port and other specialist police", "note": "Port police forces with their own constables.",
             "points": [("Port of Dover Police", 51.12, 1.32), ("Port of Liverpool Police", 53.45, -3.01), ("Port of Tilbury Police", 51.46, 0.36), ("Port of Felixstowe Police", 51.96, 1.31), ("Port of Bristol Police", 51.50, -2.70)]},
}

# ---------------------------------------------------------------- synthetic message layer
rnd = random.Random(20261121)
URBAN = {"Metropolitan Police": 3.2, "West Midlands": 2.1, "Greater Manchester": 2.0, "West Yorkshire": 1.6, "Merseyside": 1.4, "Police Scotland": 1.8,
         "Thames Valley": 1.3, "Kent": 1.2, "Hampshire and Isle of Wight": 1.2, "South Yorkshire": 1.1, "Lancashire": 1.1, "Avon and Somerset": 1.1, "Northumbria": 1.1, "PSNI": 1.2}
THEMES = ["false identity", "cover-up", "two-tier", "spoof notice", "recycled footage", "calls to gather"]
synthetic = []
for name, lat, lon, nation in FORCES:
    base = URBAN.get(name, 0.6 + rnd.random() * 0.5)
    vol = round(base * (60 + rnd.random() * 40))
    mix = [rnd.random() for _ in THEMES]; tot = sum(mix)
    synthetic.append({"force": name, "volume": vol, "trend": round(rnd.uniform(-0.3, 0.9), 2), "mix": {th: round(m / tot, 2) for th, m in zip(THEMES, mix)}})
# A synthetic cross-border spread: a claim that started in one area and moved.
flows = [("Merseyside", "Greater Manchester", 0.8), ("Merseyside", "Lancashire", 0.5), ("Merseyside", "Cheshire", 0.4), ("Greater Manchester", "West Yorkshire", 0.35), ("Merseyside", "North Wales", 0.3), ("Greater Manchester", "Metropolitan Police", 0.25)]

pt = lambda items: [{"name": n, "x": P(lo, la)[0], "y": P(lo, la)[1]} for n, la, lo in items]
out = {
    "viewBox": [0, 0, W, H],
    "source": "Coastline: Natural Earth 1:10m (public domain). Reference sites: public information, approximate town-level positions, to verify before operational use.",
    "land": land,
    "forces": [{"name": n, "nation": nat, "x": P(lo, la)[0], "y": P(lo, la)[1]} for n, la, lo, nat in FORCES],
    "layers": {k: {"label": v["label"], "note": v["note"], "points": pt(v["points"]), "lines": v.get("lines", [])} for k, v in LAYERS.items()},
    "synthetic": {"label": "Synthetic misinformation volume by force area, last 24 hours", "themes": THEMES, "byForce": synthetic,
                  "flows": [{"from": a, "to": b, "share": s} for a, b, s in flows], "flowLabel": "Synthetic spread of one claim from its first area"},
}
json.dump(out, open(os.path.join(R, "data", "uk_map.json"), "w"), ensure_ascii=False)
print("uk_map.json", W, "x", H, "land paths", {k: len(v) for k, v in land.items()})
