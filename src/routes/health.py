from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "app": "SealDoc AI+",
        "message": "✅ SealDoc AI+ backend is running fine!"
    }), 200
