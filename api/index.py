"""Yaad backend: AI-generated property image check + rent evaluator.

Runs as a Vercel Python function (all /api/* requests are routed here by
vercel.json) and locally via `python app.py`.

The image detector is haywoodsloan/ai-image-detector-deploy (SwinV2, Apache-2.0)
exported to ONNX and int8-quantized: 199 MB instead of 780 MB, runs on
onnxruntime instead of torch, ~300 MB RAM, ~1 s per image on CPU, and gives the
same real/fake verdict as the original fp32 model. The weights are too big to
ship inside the function bundle, so they are downloaded once per instance into
/tmp and reused for every later request (scripts/export_onnx.py rebuilds them).
"""
import hashlib
import logging
import os
import threading
import urllib.request

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image as PilImage
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True  # phone uploads are sometimes cut short

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The weights are stored as 10 x 20 MB parts on the `detector-v1` GitHub release
# (fetched in parallel, then joined and checksum-verified).
MODEL_BASE_URL = os.environ.get(
    "DETECTOR_MODEL_BASE_URL",
    "https://github.com/VedangKevlani/Yaad-Smart-Rental-Advisor/releases/download/detector-v1/",
)
MODEL_PARTS = [f"ai-image-detector-int8.onnx.part{i:02d}" for i in range(10)]
MODEL_SHA256 = "ff9992e5c700597cdffa512a6a8cab31fab35f23c8d94e6695e63d66de7c82df"
LOCAL_MODEL = os.path.join(ROOT, "models", "ai-image-detector-int8.onnx")
TMP_MODEL = os.path.join("/tmp" if os.path.isdir("/tmp") else ROOT, "ai-image-detector-int8.onnx")

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


def _fetch(name):
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(MODEL_BASE_URL + name, timeout=30) as r:
                return r.read()
        except Exception as e:
            log.warning("Download of %s failed (attempt %d): %s", name, attempt, e)
    raise RuntimeError(f"Could not download {name}")


def _download_model():
    from concurrent.futures import ThreadPoolExecutor

    for attempt in range(1, 3):
        log.info("Downloading detector model from %s", MODEL_BASE_URL)
        with ThreadPoolExecutor(max_workers=len(MODEL_PARTS)) as pool:
            parts = list(pool.map(_fetch, MODEL_PARTS))
        data = b"".join(parts)
        del parts
        if hashlib.sha256(data).hexdigest() == MODEL_SHA256:
            tmp = TMP_MODEL + ".tmp"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, TMP_MODEL)
            return TMP_MODEL
        log.warning("Model checksum mismatch (attempt %d)", attempt)
    raise RuntimeError("Could not download the image detector model")


def get_session():
    """Load the ONNX detector once per process (thread-safe)."""
    global _session
    if _session is None:
        with _session_lock:
            if _session is None:
                import onnxruntime as ort

                path = LOCAL_MODEL if os.path.exists(LOCAL_MODEL) else TMP_MODEL
                if not os.path.exists(path):
                    path = _download_model()
                opts = ort.SessionOptions()
                # Graph optimisation at load time triples peak RAM (~1.2 GB) for no
                # accuracy gain; skipping it keeps the peak around 450 MB.
                opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
                _session = ort.InferenceSession(path, opts, providers=["CPUExecutionProvider"])
                log.info("Detector model loaded from %s", path)
    return _session


def preprocess(img):
    """Same as the model's ViTImageProcessor: bicubic 256x256, ImageNet normalisation."""
    img = img.convert("RGB").resize((256, 256), PilImage.BICUBIC)
    arr = (np.asarray(img, dtype=np.float32) / 255.0 - MEAN) / STD
    return arr.transpose(2, 0, 1)[None].astype(np.float32)


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "model_loaded": _session is not None})


@app.route("/api/warmup", methods=["GET", "POST"])
def warmup():
    """Called when the page loads so the model is ready before the user submits."""
    try:
        get_session()
        return jsonify({"ok": True})
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
