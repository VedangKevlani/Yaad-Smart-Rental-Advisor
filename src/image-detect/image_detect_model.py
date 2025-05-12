from flask import Flask, request, jsonify
import cv2
import numpy as np
from PIL import Image
import io
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

@app.route('/check-image', methods=['POST'])
def check_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Read file into OpenCV-compatible format
        file_bytes = file.read()
        np_arr = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"error": "Invalid image data"}), 400

        # 🧠 Your AI detection logic here
        # For now, let's simulate a result:
        result = {
            "message": "Image appears to be real",
            "confidence": 92.5
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
