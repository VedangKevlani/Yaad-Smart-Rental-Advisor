from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    try:
        logging.debug(f"Received data: {request.get_json()}")

        df = pd.read_csv('property_rentals.csv')

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

        data = request.get_json()

        logging.debug(f"Parsed input data: {data}")

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
            if diff_percent <= 0.2: 
                verdict = 'strong_positive'
            else:
                verdict = 'neutral'  
        elif diff_percent <= 0.1:
            verdict = 'strong_positive'
        elif diff_percent <= 0.25:
            verdict = 'neutral'
        else:
            verdict = 'negative'

        return jsonify({
            'predicted_value': round(predicted_rent, 2),
            'verdict': verdict
        })

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
