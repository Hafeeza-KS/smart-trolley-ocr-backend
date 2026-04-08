from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
import cv2
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# Health check
@app.route("/", methods=["GET"])
def health():
    return {"status": "OCR backend running"}

# OCR endpoint
@app.route("/ocr", methods=["POST"])
def ocr_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    img_bytes = file.read()

    # Convert to OpenCV format
    np_img = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    # Preprocess image (important for accuracy)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    # OCR extraction
    text = pytesseract.image_to_string(gray, config='--psm 6')

    # Clean output
    items = [line.strip() for line in text.split("\n") if line.strip()]

    return jsonify({"items": items})


# Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)