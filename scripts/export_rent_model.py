"""Train the rent RandomForest on src/price_eval/property_rentals.csv and save it
as api/rent_model.onnx, so the deployed function only needs onnxruntime (no
scikit-learn/scipy, which would push the Vercel bundle over 500 MB).

    pip install scikit-learn skl2onnx pandas onnxruntime
    python scripts/export_rent_model.py
"""
import os

import pandas as pd
from skl2onnx import to_onnx
from sklearn.ensemble import RandomForestRegressor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES = [
    "Square Footage", "Bedrooms", "Bathrooms",
    "24_Hour_Security", "Furnished", "Garden_Area",
    "Swimming_Pool", "Central_Location", "Gated_Community",
    "View_-_Ocean", "Waterfront_-_Ocean",
]
df = pd.read_csv(os.path.join(ROOT, "src", "price_eval", "property_rentals.csv"))
df = df.dropna(subset=FEATURES + ["Price"])
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(df[FEATURES].to_numpy(dtype="float64"), df["Price"])

onx = to_onnx(model, df[FEATURES].to_numpy(dtype="float32")[:1], target_opset={"": 17, "ai.onnx.ml": 3})
out = os.path.join(ROOT, "api", "rent_model.onnx")
with open(out, "wb") as f:
    f.write(onx.SerializeToString())
print("wrote", out, os.path.getsize(out) // 1024, "KB")
