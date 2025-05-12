from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image as PilImage
from flask_cors import CORS
import io

app = Flask(__name__)
CORS(app)  # This allows cross-origin requests from any origin
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit, adjust if needed

# Load the model once when the server starts
model = tf.keras.models.load_model('property_classifier_model.h5')

@app.route('/check-image', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['image']
    app.logger.info(f"Received file: {file.filename}")
    print("Received files:", request.files)
    print(request.files)

    try:
        img = PilImage.open(file.stream).convert("RGB")
        img = img.resize((128, 128))

        # Convert the image to a numpy array and preprocess it
        img_array = np.array(img)  # Convert to numpy array
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        img_array = img_array / 255.0  # Normalize the image (same as during training)

        # Make the prediction
        prediction = model.predict(img_array)[0][0]
        label = "Real" if prediction >= 0.5 else "Fake"
        confidence = float(prediction if prediction >= 0.5 else 1 - prediction)

        # Send back the result to the frontend
        return jsonify({
            "label": label,
            "confidence": round(confidence * 100, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port = 3000)
