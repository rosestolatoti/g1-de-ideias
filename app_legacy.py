#!/usr/bin/env python3
"""
G1 DE IDEIAS — app.py (Flask)
Servidor com busca e filtro por categoria (GitHub etc) + JSON/SQLite

Uso:
  pip install Flask  # ou apt install python3-flask
  python3 app.py
  # abre http://127.0.0.1:5000
  # busca: http://127.0.0.1:5000/search?q=github
  # filtro: http://127.0.0.1:5000/api/noticias?categoria=github
"""
from flask import Flask, jsonify, request, send_from_directory, render_template_string
import json
import sqlite3
from pathlib import Path

base = Path(__file__).parent
json_path = base / "data" / "noticias.json"
db_path = base / "data" / "noticias.db"

app = Flask(__name__, static_folder="prints", template_folder="templates")

def load_json():
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return data.get("noticias") or data.get("ideias") or []

@app.route("/")
def index():
    # serve index.html gerado
    return send_from_directory(base, "index.html")

@app.route("/api/noticias")
def api_noticias():
    q = request.args.get("q", "").lower().strip()
    cat = request.args.get("categoria", "").lower().strip()
    noticias = load_json()
    if cat:
        noticias = [n for n in noticias if cat in [c.lower() for c in n.get("categorias",[])]]
        # ex: ?categoria=github → só noticias com github
    if q:
        noticias = [n for n in noticias if q in n.get("titulo","").lower() or q in n.get("resumo","").lower() or q in n.get("texto_completo","").lower() or q in n.get("fonte_arroba","").lower()]
    return jsonify({"total": len(noticias), "filtro": cat or q, "noticias": noticias})

@app.route("/api/busca")
@app.route("/search")
def search():
    q = request.args.get("q","")
    # tenta SQLite primeiro
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        like = f"%{q}%"
        cur.execute("""
            SELECT * FROM noticias 
            WHERE titulo LIKE ? OR resumo LIKE ? OR texto_completo LIKE ? OR categorias LIKE ?
            LIMIT 20
        """, (like, like, like, like))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return jsonify({"fonte":"sqlite","q":q,"total":len(rows),"resultados":rows})
    # fallback JSON
    noticias = [n for n in load_json() if q.lower() in n.get("titulo","").lower()]
    return jsonify({"fonte":"json","q":q,"total":len(noticias),"resultados":noticias})

@app.route("/prints/<path:filename>")
def prints_file(filename):
    return send_from_directory(base / "prints", filename)

@app.route("/detalhe/<id>")
def detalhe(id):
    return send_from_directory(base / "detalhe", f"{id}.html")

if __name__ == "__main__":
    print("G1 DE IDEIAS — Flask")
    print(f"JSON: {json_path} ({len(load_json())} notícias)")
    print(f"DB: {db_path} {'existe' if db_path.exists() else 'rode sync_sqlite.py'}")
    print("Rotas:")
    print("  /              → index.html (Globo)")
    print("  /api/noticias?categoria=github  → só GitHub")
    print("  /search?q=phone  → busca")
    print("  /prints/cropped/xxx.jpg → imagem padrão")
    app.run(host="0.0.0.0", port=5000, debug=True)
