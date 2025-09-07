from flask import Blueprint, send_from_directory, jsonify, request
import os
from src.services.redaction_service import redact_text

download_bp = Blueprint("download", __name__)

REDACTED_FOLDER = "redacted"

@download_bp.route("/redact", methods=["POST"])
def redact_endpoint():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    return jsonify({"redacted_text": redact_text(data["text"])})


@download_bp.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(REDACTED_FOLDER, filename, as_attachment=True)


@download_bp.route("/preview/<filename>", methods=["GET"])
def preview_file(filename):
    """
    Serve the redacted file inline (for browser preview).
    Works for images and PDFs.
    """
    return send_from_directory(REDACTED_FOLDER, filename, as_attachment=False)
