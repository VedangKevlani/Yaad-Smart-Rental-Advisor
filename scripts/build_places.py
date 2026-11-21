"""Build api/places_jm.json: every OpenStreetMap place in Jamaica that the map
shows (restaurants, schools, places of worship, malls, ...), so /api/amenities
can answer from local data instead of depending on public Overpass servers.

    pip install osmium
    curl -LO https://download.geofabrik.de/central-america/jamaica-latest.osm.pbf
    python scripts/build_places.py jamaica-latest.osm.pbf

Re-run every few months to pick up new OSM edits.
"""
import datetime
import json
import os
import sys

import osmium

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from api.index import PLACE_CATEGORIES  # noqa: E402  (single source of truth)

TAG_TO_CAT = {kv: cat for cat, kvs in PLACE_CATEGORIES.items() for kv in kvs}
CATS = list(PLACE_CATEGORIES)


def category(tags):
    for k in ("amenity", "shop", "leisure"):
        v = tags.get(k)
        if v and (k, v) in TAG_TO_CAT:
            return TAG_TO_CAT[(k, v)]
    return None


def name_of(tags):
    return tags.get("name") or tags.get("brand") or tags.get("operator") or ""


class Places(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.rows = []

    def add(self, tags, lat, lon):
        cat = category(tags)
        if cat:
            self.rows.append([CATS.index(cat), round(lat, 5), round(lon, 5), name_of(tags)])

    def node(self, n):
        if n.location.valid():
            self.add(n.tags, n.location.lat, n.location.lon)

    def way(self, w):
        if not category(w.tags):
            return
        pts = [(n.lat, n.lon) for n in w.nodes if n.location.valid()]
        if pts:
            self.add(w.tags, sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

    def area(self, a):
        if a.from_way() or not category(a.tags):
            return  # closed ways are already handled in way()
        pts = [(n.lat, n.lon) for ring in a.outer_rings() for n in ring if n.location.valid()]
        if pts:
            self.add(a.tags, sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def main(pbf):
    h = Places()
    h.apply_file(pbf, locations=True)
    rows = sorted(h.rows, key=lambda r: (r[0], r[1], r[2]))
    out = os.path.join(ROOT, "api", "places_jm.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({
            "source": "OpenStreetMap contributors (ODbL), Geofabrik Jamaica extract",
            "generated": datetime.date.today().isoformat(),
            "categories": CATS,
            "places": rows,
        }, f, ensure_ascii=False, separators=(",", ":"))
    counts = {c: 0 for c in CATS}
    for r in rows:
        counts[CATS[r[0]]] += 1
    print(f"wrote {out}: {len(rows)} places, {os.path.getsize(out) // 1024} KB")
    print(counts)


if __name__ == "__main__":
    main(sys.argv[1])
