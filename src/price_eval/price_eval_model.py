from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import os, logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.get_json()
        file_path = os.path.join(os.path.dirname(__file__), 'property_rentals.csv')
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

app.run(debug=True, port=5000)
