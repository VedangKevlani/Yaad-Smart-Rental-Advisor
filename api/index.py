"""Yaad backend: AI-generated property image check + rent evaluator.

Runs as a Vercel Python function (all /api/* requests are routed here by
vercel.json) and locally via `python app.py`.

The image detector is haywoodsloan/ai-image-detector-deploy (SwinV2, Apache-2.0)
exported to ONNX and int8-quantized: ~200-330 MB instead of 780 MB, runs on
onnxruntime instead of torch, ~300 MB RAM, ~1 s per image on CPU, and gives the
same real/fake verdict as the original fp32 model. The weights are too big to
ship inside the function bundle, so they are downloaded once per instance and
kept in memory for every later request (scripts/export_onnx.py rebuilds them).
"""
import hashlib
import logging
import os
import threading
import time
import urllib.request

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image as PilImage
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True  # phone uploads are sometimes cut short

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The weights are stored as 17 x 20 MB parts on the `detector-v2` GitHub release:
# the int8 model saved *after* onnxruntime's graph optimisation, so it loads ~2x
# faster and runs ~25-30% faster than the raw export (same verdicts on the test
# set; needs the onnxruntime version pinned in requirements.txt). On a cold start
# the parts are fetched in parallel, each is checksum-verified in its own thread,
# and the model is built straight from memory (no disk round trip).
MODEL_BASE_URL = os.environ.get(
    "DETECTOR_MODEL_BASE_URL",
    "https://github.com/VedangKevlani/Yaad-Smart-Rental-Advisor/releases/download/detector-v2/",
)
MODEL_PARTS = {
    f"ai-image-detector-int8-opt.onnx.part{i:02d}": sha
    for i, sha in enumerate([
        "319af673158a0bfdf3f6c04c7069ab38e539e340be61db0c7fc3b0aef43bdb52",
        "bc7999f6c5b69856eb6ff41b4bc33497809358c56e7bfbefbbe032ff9c808fdf",
        "7cd4de3b38640ac3beaa203c618bf08f6a32500bc034f1efba64d639208084a6",
        "08e21e4ae29ee044ca0bcec81d7bbbec6185b65838ec48b84207ddf66709d5f6",
        "fb2100191c3849069707fb35bd2a39c8c35e6d40b709f5551f646c500f7562be",
        "15178bed9db4aadd7101d03ed44b3d77644f0a598aaeec8c67380c3f9ef10ffe",
        "2e09e147e61c4b0b73d9a7f9fa29256fbbe403f81ed581bea4aa33d20916ce35",
        "d9f44e6d22f71b484f4b857be077ea9b451a7ae05ed21176b1a8412ecf486671",
        "517918d76485c4e61a0281473cb645ef63a3cb079813c258fc1d512169dcac75",
        "bb537de1c78230203f93b9185613e7a2467fb7a90dbbb64be6c62611e0f46d29",
        "c98bc028c42e6f8f794a590c7f9ea5748b7c508fab3e3cd9e227352e8164ff7c",
        "b73a04ec52e40f408132b5a0c955ad4885eb03622b9e1a2df66df934a1e4bcbb",
        "3d88cfc24b156546c247da8fb75dcc63f4e67de2c10a6ae60a3d44cb26c125cb",
        "5ea468e92bdb274e48d8e8e90f0c173aa0d05cb837dcfc6671a49c9f64e6e25f",
        "5a0cf87ca5d39958aba4a5001c93975739c63d622d5a4ba477a2ddac2fd6c1d9",
        "055064eb8afed628dc742c770ebbd857b502410701ef847d65043db77993bc10",
        "4ed3c223459dee279b4be189b77a57ff1dcf392cba7d1d711ac24a83b40d47fb",    ])
}
LOCAL_MODEL = os.path.join(ROOT, "models", "ai-image-detector-int8-opt.onnx")

FAKE_INDEX = 0  # model labels: 0 = artificial, 1 = real
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("yaad")

_session = None
_session_lock = threading.Lock()
_load_timings = {}


def _fetch(name):
    """Download one model part and verify its checksum (hashlib releases the GIL)."""
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(MODEL_BASE_URL + name, timeout=30) as r:
                data = r.read()
            if hashlib.sha256(data).hexdigest() == MODEL_PARTS[name]:
                return data
            log.warning("Checksum mismatch for %s (attempt %d)", name, attempt)
        except Exception as e:
            log.warning("Download of %s failed (attempt %d): %s", name, attempt, e)
    raise RuntimeError(f"Could not download {name}")


def _download_model():
    from concurrent.futures import ThreadPoolExecutor

    log.info("Downloading detector model from %s", MODEL_BASE_URL)
    with ThreadPoolExecutor(max_workers=len(MODEL_PARTS)) as pool:
        return b"".join(pool.map(_fetch, MODEL_PARTS))


def get_session():
    """Load the ONNX detector once per process (thread-safe)."""
    global _session
    if _session is None:
        with _session_lock:
            if _session is None:
                t0 = time.perf_counter()
                import onnxruntime as ort

                t1 = time.perf_counter()
                model = LOCAL_MODEL if os.path.exists(LOCAL_MODEL) else _download_model()
                t2 = time.perf_counter()
                opts = ort.SessionOptions()
                # The model is already optimised offline; re-optimising at load time
                # would only add ~1.5 s and ~800 MB of peak RAM.
                opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
                session = ort.InferenceSession(model, opts, providers=["CPUExecutionProvider"])
                del model
                t3 = time.perf_counter()
                # The first run allocates buffers and is noticeably slower; do it now
                # so the user's first real check runs at warm speed.
                session.run(None, {"pixel_values": np.zeros((1, 3, 256, 256), np.float32)})
                t4 = time.perf_counter()
                _load_timings.update(
                    import_s=round(t1 - t0, 2), download_s=round(t2 - t1, 2),
                    load_s=round(t3 - t2, 2), first_run_s=round(t4 - t3, 2),
                )
                _session = session
                log.info("Detector model ready: %s", _load_timings)
    return _session


def preprocess(img):
    """Same as the model's ViTImageProcessor: bicubic 256x256, ImageNet normalisation."""
    img = img.convert("RGB").resize((256, 256), PilImage.BICUBIC)
    arr = (np.asarray(img, dtype=np.float32) / 255.0 - MEAN) / STD
    return arr.transpose(2, 0, 1)[None].astype(np.float32)


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "model_loaded": _session is not None, "load_timings": _load_timings})


@app.route("/api/warmup", methods=["GET", "POST"])
def warmup():
    """Called when the page loads so the model is ready before the user submits."""
    try:
        t = time.perf_counter()
        get_session()
        return jsonify({"ok": True, "waited_s": round(time.perf_counter() - t, 2),
                        "load_timings": _load_timings})
    except Exception as e:
        log.exception("warmup failed")
        return jsonify({"ok": False, "error": str(e)}), 503


@app.route("/api/check-image", methods=["POST"])
@app.route("/check-image", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["image"]

    try:
        img = PilImage.open(file.stream)
        img.load()
    except Exception:
        return jsonify({"error": "That file is not a readable image"}), 400

    try:
        logits = get_session().run(None, {"pixel_values": preprocess(img)})[0][0]
        probs = np.exp(logits - logits.max())
        probs /= probs.sum()
        fake_prob = float(probs[FAKE_INDEX])

        label = "fake" if fake_prob >= 0.5 else "real"
        confidence = fake_prob if label == "fake" else 1 - fake_prob
        return jsonify({"label": label, "confidence": round(confidence * 100, 2)})
    except Exception as e:
        log.exception("image check failed")
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------- rent evaluator
FEATURES = [
    "Square Footage", "Bedrooms", "Bathrooms",
    "24_Hour_Security", "Furnished", "Garden_Area",
    "Swimming_Pool", "Central_Location", "Gated_Community",
    "View_-_Ocean", "Waterfront_-_Ocean",
]
# RandomForest (100 trees) trained on src/price_eval/property_rentals.csv and
# exported to ONNX by scripts/export_rent_model.py, so no scikit-learn is needed here.
RENT_MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rent_model.onnx")
_rent_session = None


def predict_rent(features):
    global _rent_session
    if _rent_session is None:
        import onnxruntime as ort

        _rent_session = ort.InferenceSession(RENT_MODEL, providers=["CPUExecutionProvider"])
    inp = _rent_session.get_inputs()[0]
    x = np.array([features], dtype=np.float64 if "double" in inp.type else np.float32)
    return float(np.ravel(_rent_session.run(None, {inp.name: x})[0])[0])


@app.route("/api/evaluate", methods=["POST"])
def evaluate():
    try:
        data = request.get_json()
        input_data = [float(data.get("Square Footage", 0))] + [
            int(data.get(c, 0)) for c in FEATURES[1:]
        ]
        est_rent = float(data.get("EstimatedRent", 0))
        predicted_rent = predict_rent(input_data)
        diff_percent = abs(predicted_rent - est_rent) / est_rent

        if est_rent < predicted_rent:
            verdict = "strong_positive" if diff_percent <= 0.2 else "neutral"
        elif diff_percent <= 0.1:
            verdict = "strong_positive"
        elif diff_percent <= 0.25:
            verdict = "neutral"
        else:
            verdict = "negative"

        return jsonify({"predicted_value": round(predicted_rent, 2), "verdict": verdict})
    except Exception as e:
        log.exception("evaluate failed")
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------- map: places nearby
# The dashboard used to call the public Overpass API straight from the browser
# with 11 parallel queries. overpass-api.de rate-limits that (429) and rejects
# many clients outright (406, including Vercel's servers), and its mirrors often
# time out, so nothing came back and no markers were drawn.
# Now: addresses in Jamaica are answered instantly from api/places_jm.json, an
# extract of every relevant OpenStreetMap place in Jamaica (rebuild with
# scripts/build_places.py). Anywhere else falls back to live Overpass (one
# combined query, identifying User-Agent, several mirrors). Results are cached
# in memory and on Vercel's CDN.
import json  # noqa: E402
import urllib.parse  # noqa: E402

USER_AGENT = "YaadSmartRentalAdvisor/1.0 (+https://yaad-smart-rental-advisor.vercel.app)"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
# category -> list of (OSM key, value). Fitness centres are leisure=*, malls shop=mall.
PLACE_CATEGORIES = {
    "restaurant": [("amenity", "restaurant"), ("amenity", "cafe")],
    "fast_food": [("amenity", "fast_food")],
    "school": [("amenity", "school"), ("amenity", "college"), ("amenity", "university"),
               ("amenity", "kindergarten")],
    "place_of_worship": [("amenity", "place_of_worship")],
    "hospital": [("amenity", "hospital")],
    "doctors": [("amenity", "doctors"), ("amenity", "clinic"), ("amenity", "dentist")],
    "pharmacy": [("amenity", "pharmacy"), ("shop", "chemist")],
    "bank": [("amenity", "bank"), ("amenity", "atm")],
    "police": [("amenity", "police")],
    "supermarket": [("shop", "supermarket"), ("shop", "convenience"), ("shop", "wholesale")],
    "mall": [("shop", "mall"), ("shop", "department_store")],
    "fitness_centre": [("leisure", "fitness_centre"), ("leisure", "sports_centre"),
                       ("amenity", "gym")],
}
_TAG_TO_CATEGORY = {kv: cat for cat, kvs in PLACE_CATEGORIES.items() for kv in kvs}
_places_cache = {}
_geocode_cache = {}
CACHE_SECONDS = 24 * 3600


def _cached(cache, key):
    hit = cache.get(key)
    if hit and time.time() - hit[0] < CACHE_SECONDS:
        return hit[1]
    return None


def _overpass(query):
    body = urllib.parse.urlencode({"data": query}).encode()
    errors = []
    for url in OVERPASS_ENDPOINTS:
        try:
            req = urllib.request.Request(url, data=body, headers={
                "User-Agent": USER_AGENT, "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            })
            with urllib.request.urlopen(req, timeout=12) as r:
                return json.loads(r.read())
        except Exception as e:
            errors.append(f"{url.split('/')[2]}: {e}")
            log.warning("Overpass %s failed: %s", url, e)
    raise RuntimeError("All Overpass servers failed: " + "; ".join(errors))


JAMAICA_BBOX = (17.55, -78.55, 18.65, -76.05)  # min lat, min lon, max lat, max lon
_local = None


def _local_places(lat, lon, radius):
    global _local
    if _local is None:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "places_jm.json"),
                  encoding="utf-8") as f:
            d = json.load(f)
        rows = d["places"]
        _local = (d["categories"], np.array([[r[1], r[2]] for r in rows]), rows)
    cats, coords, rows = _local
    rad = np.pi / 180
    dlat = (coords[:, 0] - lat) * rad
    dlon = (coords[:, 1] - lon) * rad
    h = np.sin(dlat / 2) ** 2 + np.cos(lat * rad) * np.cos(coords[:, 0] * rad) * np.sin(dlon / 2) ** 2
    dist = 2 * 6371000 * np.arcsin(np.sqrt(h))
    return [
        {"category": cats[rows[i][0]], "name": rows[i][3], "lat": rows[i][1], "lon": rows[i][2]}
        for i in np.nonzero(dist <= radius)[0]
    ]


@app.route("/api/amenities")
def amenities():
    try:
        lat = round(float(request.args["lat"]), 4)
        lon = round(float(request.args["lon"]), 4)
        radius = min(max(int(request.args.get("radius", 1500)), 200), 5000)
    except (KeyError, ValueError):
        return jsonify({"error": "lat and lon are required"}), 400

    if JAMAICA_BBOX[0] <= lat <= JAMAICA_BBOX[2] and JAMAICA_BBOX[1] <= lon <= JAMAICA_BBOX[3]:
        resp = jsonify({"places": _local_places(lat, lon, radius), "source": "osm-extract"})
        resp.headers["Cache-Control"] = "public, max-age=3600, s-maxage=86400"
        return resp

    key = (lat, lon, radius)
    places = _cached(_places_cache, key)
    if places is None:
        by_key = {}
        for k, v in _TAG_TO_CATEGORY:
            by_key.setdefault(k, []).append(v)
        filters = "".join(
            f'nwr["{k}"~"^({"|".join(sorted(vs))})$"](around:{radius},{lat},{lon});'
            for k, vs in by_key.items()
        )
        try:
            data = _overpass(f"[out:json][timeout:25];({filters});out center tags;")
        except Exception as e:
            return jsonify({"error": str(e)}), 502

        places, seen = [], set()
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            cat = next((_TAG_TO_CATEGORY[(k, tags[k])] for k in ("amenity", "shop", "leisure")
                        if (k, tags.get(k)) in _TAG_TO_CATEGORY), None)
            c = el if el.get("type") == "node" else el.get("center")
            if not cat or not c or (el["type"], el["id"]) in seen:
                continue
            seen.add((el["type"], el["id"]))
            places.append({
                "category": cat,
                "name": tags.get("name") or tags.get("brand") or tags.get("operator") or "",
                "lat": c["lat"], "lon": c["lon"],
            })
        _places_cache[key] = (time.time(), places)

    resp = jsonify({"places": places})
    resp.headers["Cache-Control"] = "public, max-age=3600, s-maxage=86400"
    return resp


@app.route("/api/geocode")
def geocode():
    """Address -> lat/lon via Nominatim, preferring results in Jamaica."""
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"error": "q is required"}), 400
    hit = _cached(_geocode_cache, q.lower())
    if hit is None:
        hit = {}
        for extra in ({"countrycodes": "jm"}, {}):  # Jamaica first, then anywhere
            params = urllib.parse.urlencode({"format": "json", "limit": 1, "q": q, **extra})
            req = urllib.request.Request("https://nominatim.openstreetmap.org/search?" + params,
                                         headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=10) as r:
                    res = json.loads(r.read())
            except Exception as e:
                log.warning("Nominatim failed: %s", e)
                return jsonify({"error": "Geocoding service unavailable"}), 502
            if res:
                hit = {"lat": float(res[0]["lat"]), "lon": float(res[0]["lon"]),
                       "display_name": res[0].get("display_name", "")}
                break
        _geocode_cache[q.lower()] = (time.time(), hit)
    if not hit:
        return jsonify({"error": "Address not found"}), 404
    resp = jsonify(hit)
    resp.headers["Cache-Control"] = "public, max-age=3600, s-maxage=86400"
    return resp
