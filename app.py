from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return {"status": "Backend is running"}

@app.route("/ocr", methods=["POST"])
def ocr():
    return {"items": ["Test Item 1", "Test Item 2"]}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)