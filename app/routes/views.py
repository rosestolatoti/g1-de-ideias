from flask import Blueprint, send_from_directory, current_app
from pathlib import Path

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def index():
    base = Path(current_app.root_path).parent
    # index.html é gerado por scripts/generate_site.py e copiado de templates/globo.html
    idx = base / "index.html"
    if idx.exists():
        return send_from_directory(str(base), "index.html")
    # fallback template
    tpl = base / "templates" / "globo.html"
    if tpl.exists():
        return send_from_directory(str(base / "templates"), "globo.html")
    return "G1 DE IDEIAS — gere o site com: python3 scripts/generate_site.py", 200

@views_bp.route("/detalhe/<id>")
def detalhe(id):
    base = Path(current_app.root_path).parent
    return send_from_directory(str(base / "detalhe"), f"{id}.html")

@views_bp.route("/prints/<path:filename>")
def prints_file(filename):
    base = Path(current_app.root_path).parent
    return send_from_directory(str(base / "prints"), filename)

@views_bp.route("/static/<path:filename>")
def static_files(filename):
    base = Path(current_app.root_path).parent
    return send_from_directory(str(base / "static"), filename)
