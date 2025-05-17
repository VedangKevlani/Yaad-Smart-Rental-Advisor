from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image as PilImage

app = Flask(__name__)
CORS(app)

model = tf.keras.models.load_model('property_classifier_model.h5')

@app.route('/check-image', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['image']
    try:
        img = PilImage.open(file.stream).convert("RGB")
        img = img.resize((128, 128))
        img_array = np.expand_dims(np.array(img), axis=0) / 255.0
        prediction = model.predict(img_array)[0][0]
        label = "Real" if prediction >= 0.5 else "Fake"
        confidence = float(prediction if prediction >= 0.5 else 1 - prediction)
        return jsonify({"label": label, "confidence": round(confidence * 100, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_image_api():
    app.run(debug=True, port=3000)
