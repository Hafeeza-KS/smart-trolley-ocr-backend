from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import easyocr
import cv2
import numpy as np
import io
from PIL import Image

app = FastAPI()

# Allow frontend (Netlify) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later if needed
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OCR reader once (important for performance)
reader = easyocr.Reader(['en'], gpu=False)

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    # Read image bytes
    image_bytes = await file.read()

    # Convert bytes → OpenCV image
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "Invalid image"}

    # Convert to grayscale (better OCR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # OCR
    results = reader.readtext(gray)

    # Extract confident text only
    items = []
    for (_, text, confidence) in results:
        if confidence > 0.4:
            items.append(text.strip())

    return {
        "items": items
    }
