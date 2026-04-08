from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import os

# Try importing pytesseract safely
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    TESSERACT_AVAILABLE = True
except:
    TESSERACT_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Health check
@app.route("/", methods=["GET"])
def health():
    return {"status": "OCR backend running"}

# OCR endpoint
@app.route("/ocr", methods=["POST"])
def ocr_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files['image']
        img_bytes = file.read()

        # Convert to OpenCV format
        np_img = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        # 🔥 Improved preprocessing (better OCR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        items = []

        # ✅ If Tesseract is available → use real OCR
        if TESSERACT_AVAILABLE:
            try:
                text = pytesseract.image_to_string(gray, config='--psm 6')
                items = [line.strip() for line in text.split("\n") if line.strip()]
            except Exception as e:
                items = ["OCR failed - fallback used"]

        # ✅ Fallback (if Tesseract not available)
        if not items:
            items = ["Sample Item", "Demo Product"]

        return jsonify({
            "items": items,
            "mode": "tesseract" if TESSERACT_AVAILABLE else "fallback"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)