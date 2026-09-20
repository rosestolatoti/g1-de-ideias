from flask import Blueprint, jsonify
from pathlib import Path
import time
import os

health_bp = Blueprint("health", __name__)
START = time.time()

@health_bp.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "g1-de-ideias",
        "uptime_s": int(time.time() - START),
        "version": "2.0-profissional",
        "owner": "Fábio Rosestolato"
    })

@health_bp.route("/ready")
def ready():
    json_path = Path(os.getenv("DATA_JSON", "data/noticias.json"))
    db_path = Path(os.getenv("DB_PATH", "data/noticias.db"))
    checks = {
        "json_exists": json_path.exists(),
        "db_exists": db_path.exists(),
        "tesseract": Path("/usr/bin/tesseract").exists(),
    }
    # Tenta contar noticias
    try:
        import json
        if json_path.exists():
            data = json.loads(json_path.read_text(encoding="utf-8"))
            checks["total_ideias"] = len(data.get("ideias") or data.get("noticias") or [])
        else:
            checks["total_ideias"] = 0
    except Exception as e:
        checks["error"] = str(e)
    ok = checks["json_exists"]
    return jsonify({"ready": ok, "checks": checks}), (200 if ok else 503)

@health_bp.route("/api/health")
def api_health():
    return health()
