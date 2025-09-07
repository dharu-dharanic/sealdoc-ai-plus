from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from src.services.redaction_service import redact_text

upload_bp = Blueprint("upload", __name__)

UPLOAD_FOLDER = "uploads"
REDACTED_FOLDER = "redacted"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    use_case = request.form.get("use_case", "general")

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)

        # Perform redaction (example service call)
        redacted_filename = f"redacted_{filename}"
        redacted_path = os.path.join(REDACTED_FOLDER, redacted_filename)

        with open(upload_path, "r", errors="ignore") as f:
            text = f.read()

        redacted_text = redact_text(text)

        with open(redacted_path, "w") as f:
            f.write(redacted_text)

        return jsonify({
            "original_file": filename,
            "redacted_file": redacted_filename,
            "download_url": f"/download/{redacted_filename}",
            "preview_url": f"/preview/{redacted_filename}",
            "use_case": use_case
        })

    return jsonify({"error": "File type not allowed"}), 400
