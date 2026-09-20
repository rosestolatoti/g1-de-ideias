#!/usr/bin/env python3
"""
G1 DE IDEIAS — app.py (shim profissional)
Mantém compatibilidade: `python3 app.py` e `gunicorn app:app`
Delega para factory em app/__init__.py

Uso:
  python3 app.py                    # dev 0.0.0.0:5000
  gunicorn -w 2 -b 0.0.0.0:5000 app:app  # prod
  FLASK_ENV=development python3 app.py
"""
import os
from pathlib import Path

# Garante que pacote `app` é encontrado quando rodado como `python app.py`
BASE = Path(__file__).resolve().parent
import sys
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from app import create_app, app as flask_app

# Export para gunicorn/vercel: `app` é Flask instance
app = flask_app

if __name__ == "__main__":
    import json
    from app.config import config_by_name

    env = os.getenv("FLASK_ENV", "production")
    cfg = config_by_name.get(env, config_by_name["production"])
    # Load JSON info
    json_path = BASE / "data" / "noticias.json"
    total = 0
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            total = len(data.get("ideias") or data.get("noticias") or [])
        except: pass

    print("="*60)
    print("G1 DE IDEIAS — Flask Profissional v2.0")
    print(f"  Env: {env} | Port: {cfg.PORT} | Host: {cfg.HOST}")
    print(f"  JSON: {json_path} ({total} notícias)")
    print(f"  DB: {BASE/'data/noticias.db'}")
    print(f"  Prints cropped: {BASE/'prints/cropped'}")
    print("="*60)
    print("Rotas:")
    print("  /                        → index.html (Globo)")
    print("  /health /ready           → health check")
    print("  /api/noticias?categoria=github → filtrado")
    print("  /api/categorias          → contagem por categoria")
    print("  /search?q=phone /api/busca?q=phone")
    print("  /prints/cropped/xxx.jpg  → imagem padrão")
    print("  /detalhe/<id>            → página detalhe")
    print("  /api/jev/health          → JEV status")
    print("="*60)

    # host/port da config
    debug = os.getenv("FLASK_ENV") in ("development","dev")
    app.run(host=cfg.HOST, port=cfg.PORT, debug=debug, use_reloader=debug)
