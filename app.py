from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import cv2
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# IMPORTANT: initialize reader lazily (saves memory)
reader = None

def get_reader():
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'], gpu=False)
    return reader

@app.route("/", methods=["GET"])
def health():
    return {"status": "OCR backend running"}

@app.route("/ocr", methods=["POST"])
def ocr_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    img_bytes = file.read()

    np_img = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    reader = get_reader()
    results = reader.readtext(gray)

    items = [text.strip() for (_, text, conf) in results if conf > 0.4]

    return jsonify({"items": items})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
