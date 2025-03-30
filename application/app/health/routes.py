from flask import jsonify
from app.health import bp

@bp.route("/health")
def health():
    """Egészségügyi ellenőrzés"""
    return jsonify({"status": "ok"}), 200
