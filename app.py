
from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from src.services.ocr_service import extract_text_from_image, extract_text_from_pdf
from src.services.redaction_service import redact_text, redact_file
from src.utils.logger import logger

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
REDACTED_FOLDER = "redacted"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REDACTED_FOLDER, exist_ok=True)

# --- FRONTEND ROUTE ---
@app.route("/")
def home_page():
    logger.info("Home route accessed (frontend)")
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            logger.warning("Upload attempt with no file")
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            logger.warning("Upload attempt with empty filename")
            return jsonify({"error": "Empty filename"}), 400

        # Get use case + redaction style
        use_case = request.form.get("use_case", "default").lower()
        if use_case == "general":
            use_case = "default"  # Map frontend "general" to backend "default"

        redaction_style = request.form.get("redaction_style", "black_box").lower()
        logger.info(f"File upload started: {file.filename}, use_case={use_case}, style={redaction_style}")

        # Save uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Prepare redacted output path
        redacted_filename = f"redacted_{file.filename}"
        redacted_path = os.path.join(REDACTED_FOLDER, redacted_filename)

        # OCR + Redaction
        if file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            text = extract_text_from_image(file_path)
            redacted_text = redact_text(text, use_case, redaction_style)
            redact_file(file_path, redacted_path, use_case, redaction_style)

        elif file.filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
            redacted_text = redact_text(text, use_case, redaction_style)
            redact_file(file_path, redacted_path, use_case, redaction_style)

        else:
            logger.error(f"Unsupported file type: {file.filename}")
            return jsonify({"error": "Unsupported file type"}), 400

        logger.info(f"File successfully processed: {file.filename}")

        return jsonify({
            "original_text": text,
            "redacted_text": redacted_text,
            "redacted_file_url": f"/download/{redacted_filename}",
            "preview_url": f"/preview/{redacted_filename}",
            "use_case": use_case,
            "redaction_style": redaction_style
        })

    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/redact", methods=["POST"])
def redact_endpoint():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            logger.warning("Redact endpoint called with no text")
            return jsonify({"error": "No text provided"}), 400

        use_case = data.get("use_case", "default").lower()
        redaction_style = data.get("redaction_style", "black_box").lower()
        redacted_text = redact_text(data["text"], use_case, redaction_style)

        logger.info(f"Redaction completed for use_case={use_case}, style={redaction_style}")

        return jsonify({
            "redacted_text": redacted_text,
            "use_case": use_case,
            "redaction_style": redaction_style
        })

    except Exception as e:
        logger.error(f"Error in redact_endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    logger.info(f"Download requested: {filename}")
    return send_from_directory(REDACTED_FOLDER, filename, as_attachment=True)


@app.route("/preview/<filename>", methods=["GET"])
def preview_file(filename):
    logger.info(f"Preview requested: {filename}")
    return send_from_directory(REDACTED_FOLDER, filename, as_attachment=False)


if __name__ == "__main__":
    logger.info("Starting SealDoc AI+ Flask server...")
    app.run(debug=True, host="0.0.0.0", port=5000)
