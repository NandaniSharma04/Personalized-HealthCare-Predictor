"""
Health System & Symptoms Vocabulary Routes
"""
from flask import Blueprint, jsonify
from pathlib import Path
import json

health_bp = Blueprint("health_bp", __name__, url_prefix="/api")

@health_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "success": True, "server": "HealthAI Flask API"}), 200

@health_bp.route("/symptoms", methods=["GET"])
def get_symptoms():
    sym_path = Path(__file__).resolve().parents[1] / "ml" / "symptom_list.json"
    if not sym_path.exists():
        return jsonify({"success": False, "error": "Symptoms file not found"}), 404
    symptoms = json.loads(sym_path.read_text(encoding="utf-8"))
    return jsonify({"success": True, "count": len(symptoms), "symptoms": sorted(symptoms)}), 200
