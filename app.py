from flask import Flask, request, jsonify
from ocr.py import extract_text_from_image, extract_text_from_pdf
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Hello, SealDoc AI+ is running locally!"

@app.route("/health")
def health():
    return jsonify({"status": "OK", "service": "SealDoc AI+"})

# OCR route
@app.route("/extract-text", methods=["POST"])
def extract_text():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(filepath)
    else:
        text = extract_text_from_image(filepath)

    return jsonify({"extracted_text": text})

if __name__ == "__main__":
    app.run(debug=True)
