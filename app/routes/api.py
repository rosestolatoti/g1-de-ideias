from flask import Blueprint, jsonify, request
from pathlib import Path
import json
import os

api_bp = Blueprint("api", __name__)

def _load():
    from flask import current_app
    # tenta config(BASE_DIR) primeiro, depois env, depois relativo ao CWD
    base = None
    try:
        base = Path(current_app.config.get("BASE_DIR", Path.cwd()))
    except:
        base = Path.cwd()
    p = Path(os.getenv("DATA_JSON", str(base / "data" / "noticias.json")))
    if not p.is_absolute():
        p = base / p
    if not p.exists():
        # fallback absoluto no BASE
        p = base / "data" / "noticias.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    return data.get("noticias") or data.get("ideias") or []

@api_bp.route("/api/noticias")
def api_noticias():
    q = request.args.get("q","").lower().strip()
    cat = request.args.get("categoria","").lower().strip()
    try:
        limit = min(int(request.args.get("limit","50")), 100)
        offset = int(request.args.get("offset","0"))
    except:
        limit, offset = 50, 0
    noticias = _load()
    total_antes = len(noticias)
    if cat:
        noticias = [n for n in noticias if cat in [c.lower() for c in n.get("categorias",[])]]
    if q:
        noticias = [n for n in noticias if q in n.get("titulo","").lower() or q in n.get("resumo","").lower() or q in n.get("texto_completo","").lower() or q in n.get("fonte_arroba","").lower()]
    total = len(noticias)
    pag = noticias[offset:offset+limit]
    return jsonify({
        "total": total,
        "total_antes": total_antes,
        "filtro": cat or q or None,
        "limit": limit,
        "offset": offset,
        "noticias": pag
    })

@api_bp.route("/api/busca")
@api_bp.route("/search")
def search():
    from flask import current_app
    from app.services.storage_service import search_sqlite
    q = request.args.get("q","")
    base = Path(current_app.config.get("BASE_DIR", Path.cwd()))
    db_path = Path(os.getenv("DB_PATH", str(base / "data" / "noticias.db")))
    if not db_path.is_absolute():
        db_path = base / db_path
    if db_path.exists():
        rows = search_sqlite(db_path, q, limit=20)
        return jsonify({"fonte":"sqlite","q":q,"total":len(rows),"resultados":rows})
    noticias = [n for n in _load() if q.lower() in n.get("titulo","").lower()]
    return jsonify({"fonte":"json","q":q,"total":len(noticias),"resultados":noticias})

@api_bp.route("/api/categorias")
def categorias():
    noticias = _load()
    from collections import Counter
    c = Counter()
    for n in noticias:
        for cat in n.get("categorias",[]):
            c[cat.lower()] += 1
    return jsonify({"total": len(noticias), "categorias": dict(c)})

@api_bp.route("/api/jev/health")
def jev_health():
    try:
        from app.services.jev_service import get_jev
        j = get_jev()
        return jsonify(j.health())
    except Exception as e:
        return jsonify({"error": str(e), "has_sdk": False}), 500
