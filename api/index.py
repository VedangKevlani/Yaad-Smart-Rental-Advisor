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
