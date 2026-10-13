from flask import Flask, request, jsonify
import numpy as np
from PIL import Image as PilImage
from flask_cors import CORS
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import logging
import os
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

app = Flask(__name__)
CORS(app) 
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
logging.basicConfig(level=logging.DEBUG)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Pretrained AI-generated image detector (SwinV2). Scored 87% on a real-vs-AI property
# test set, versus 53% for the old property_classifier_model.h5.
DETECTOR = 'haywoodsloan/ai-image-detector-deploy'
processor = AutoImageProcessor.from_pretrained(DETECTOR)
model = AutoModelForImageClassification.from_pretrained(DETECTOR).eval()
FAKE_INDEX = model.config.label2id['artificial']

@app.route('/check-image', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['image']

    try:
        img = PilImage.open(file.stream).convert("RGB")

        with torch.no_grad():
            logits = model(**processor(images=img, return_tensors="pt")).logits
        fake_prob = logits.softmax(-1)[0, FAKE_INDEX].item()

        label = "fake" if fake_prob >= 0.5 else "real"
        confidence = fake_prob if label == "fake" else 1 - fake_prob

        return jsonify({
            "label": label,
            "confidence": round(confidence * 100, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.get_json()
        file_path = os.path.join(BASE_DIR, "src", "price_eval", "property_rentals.csv")
        df = pd.read_csv(file_path)

        target = 'Price'
        features = [
            'Square Footage', 'Bedrooms', 'Bathrooms',
            '24_Hour_Security', 'Furnished', 'Garden_Area',
            'Swimming_Pool', 'Central_Location', 'Gated_Community',
            'View_-_Ocean', 'Waterfront_-_Ocean'
        ]
        df = df.dropna(subset=features + [target])
        X = df[features]
        y = df[target]

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        input_data = [
            float(data.get('Square Footage', 0)),
            int(data.get('Bedrooms', 0)),
            int(data.get('Bathrooms', 0)),
            int(data.get('24_Hour_Security', 0)),
            int(data.get('Furnished', 0)),
            int(data.get('Garden_Area', 0)),
            int(data.get('Swimming_Pool', 0)),
            int(data.get('Central_Location', 0)),
            int(data.get('Gated_Community', 0)),
            int(data.get('View_-_Ocean', 0)),
            int(data.get('Waterfront_-_Ocean', 0)),
        ]

        est_rent = float(data.get('EstimatedRent', 0))
        input_array = np.array(input_data).reshape(1, -1)
        predicted_rent = model.predict(input_array)[0]
        diff_percent = abs(predicted_rent - est_rent) / est_rent

        if est_rent < predicted_rent: 
            verdict = 'strong_positive' if diff_percent <= 0.2 else 'neutral'
        elif diff_percent <= 0.1:
            verdict = 'strong_positive'
        elif diff_percent <= 0.25:
            verdict = 'neutral'
        else:
            verdict = 'negative'

        return jsonify({'predicted_value': round(predicted_rent, 2), 'verdict': verdict})
    except Exception as e:
        logging.error(e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
