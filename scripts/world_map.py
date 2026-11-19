"""Build a small world map (land outline + highlighted countries) for the Research and design page.
Source: Natural Earth 1:110m via the world-atlas npm package (public domain). Usage: world_map.py countries-110m.json"""
import json, sys, math
topo = json.load(open(sys.argv[1]))
sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]
arcs = []
for a in topo["arcs"]:
    x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)
W, H = 1000, 470
LAT_MAX, LAT_MIN = 83, -57
def proj(lon, lat):
    # Equal Earth-like compromise: equirectangular with mild latitude compression
    return ((lon + 180) / 360 * W, (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * H)
def ring(idx):
    out = []
    for i in idx:
        pts = arcs[i] if i >= 0 else arcs[~i][::-1]
        out.extend(pts if not out else pts[1:])
    return out
def path(geom):
    polys = geom["arcs"] if geom["type"] == "MultiPolygon" else [geom["arcs"]]
    d = []
    for poly in polys:
        for r in poly:
            raw = ring(r)
            if max(la for lo, la in raw) < -55: continue  # Antarctica
            lons = [lo for lo, la in raw]
            if max(lons) - min(lons) > 200:  # crosses the antimeridian (Russia, Fiji): keep it in one piece on the east side
                raw = [(lo + 360 if lo < 0 else lo, la) for lo, la in raw]
            pts = [proj(*p) for p in raw]
            simp = [pts[0]]
            for p in pts[1:]:
                if abs(p[0] - simp[-1][0]) + abs(p[1] - simp[-1][1]) > 2.2: simp.append(p)
            if len(simp) < 3: continue
            d.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in simp) + "Z")
    return "".join(d)
HL = {"752": "Sweden", "233": "Estonia", "246": "Finland", "826": "United Kingdom", "158": "Taiwan", "840": "United States",
      "804": "Ukraine", "036": "Australia", "554": "New Zealand", "528": "Netherlands", "124": "Canada", "578": "Norway"}
land, hl = [], {}
for g in topo["objects"]["countries"]["geometries"]:
    if not g.get("arcs"): continue
    p = path(g)
    if not p: continue
    if g.get("id") in HL: hl[HL[g["id"]]] = p
    else: land.append(p)
# Markers: [label, lon, lat, what was studied]
pins = [["Sweden", 18.07, 59.33], ["Estonia", 24.75, 59.44], ["Finland", 24.94, 60.17], ["United Kingdom", -0.13, 51.5],
        ["EU and NATO", 4.35, 50.85], ["Singapore", 103.82, 1.35], ["Taiwan", 121.56, 25.03], ["United States", -77.04, 38.9],
        ["Ukraine", 30.52, 50.45], ["Australia", 149.13, -35.28], ["New Zealand", 172.63, -43.53], ["Netherlands", 6.89, 52.22],
        ["Canada", -63.57, 44.65], ["Norway", 10.75, 59.91]]
out = {"w": W, "h": H, "land": "".join(land), "hl": hl, "pins": [[n, *[round(v, 1) for v in proj(lo, la)]] for n, lo, la in pins]}
json.dump(out, open("data/world_map.json", "w"), separators=(",", ":"))
print(len(json.dumps(out)) // 1024, "KB", sorted(hl))
