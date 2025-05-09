from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
CORS(app)

FEATURES = ['Square Footage', 'Bedrooms', 'Bathrooms', '24_Hour_Security', 'Furnished',
            'Garden_Area', 'Swimming_Pool', 'Central_Location', 'Gated_Community',
            'View_-_Ocean', 'Waterfront_-_Ocean']

model = None
pipeline = None

def load_model():
    global model, pipeline
    data = pd.read_csv("property_rentals.csv")
    X = data[FEATURES]
    y = data['Price']

    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    X_transformed = pipeline.fit_transform(X)

    model = RandomForestRegressor(n_estimators=100, max_depth=12, min_samples_leaf=2, random_state=42)
    model.fit(X_transformed, y)

@app.before_request
def ensure_model_loaded():
    if model is None or pipeline is None:
        load_model()

@app.route('/api/evaluate', methods=['POST'])
def evaluate_property():
    data = request.get_json()

    try:
        features = {f: float(data[f]) if f in ['Square Footage', 'Bedrooms', 'Bathrooms'] else int(data[f]) for f in FEATURES}
        asking_price = float(data['AskingPrice'])
        estimated_rent = float(data['EstimatedRent'])
    except (KeyError, ValueError):
        return jsonify({'error': 'Invalid or missing input values'}), 400

    df = pd.DataFrame([features])
    X_input = pipeline.transform(df)
    predicted_value = model.predict(X_input)[0]

    one_percent_rule = estimated_rent >= 0.01 * asking_price

    if predicted_value > 1.1 * asking_price and one_percent_rule:
        verdict = "strong_positive"
    elif predicted_value > asking_price:
        verdict = "neutral"
    else:
        verdict = "negative"

    return jsonify({
        'predicted_value': round(predicted_value, 2),
        'verdict': verdict
    })

if __name__ == '__main__':
    app.run(debug=True)
