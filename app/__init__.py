#!/usr/bin/env python3
"""
G1 DE IDEIAS — app/__init__.py
Factory profissional (create_app) — pronto para gunicorn, vercel, docker
"""
import os
import logging
from flask import Flask
from pathlib import Path

def create_app(config_name: str = None):
    # config
    env = config_name or os.getenv("FLASK_ENV", "production")
    # corrige: development/production vs dev/prod
    if env == "prod": env = "production"
    if env == "dev": env = "development"

    from app.config import config_by_name
    cfg = config_by_name.get(env, config_by_name["production"])

    base = Path(__file__).resolve().parent.parent
    app = Flask(__name__,
                static_folder=str(base / "static"),
                template_folder=str(base / "templates"))

    app.config.from_object(cfg)
    app.config["BASE_DIR"] = base

    # Logging profissional
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )
    app.logger.setLevel(logging.INFO)

    # Blueprints
    from app.routes.health import health_bp
    from app.routes.api import api_bp
    from app.routes.views import views_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    # CORS simples para API
    @app.after_request
    def cors(resp):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp

    # Error handlers profissionais
    @app.errorhandler(404)
    def not_found(e):
        return {"error":"nao_encontrado","path": str(e)}, 404

    @app.errorhandler(500)
    def internal(e):
        app.logger.exception("500")
        return {"error":"erro_interno"}, 500

    app.logger.info(f"G1 DE IDEIAS iniciado env={env} base={base} port={cfg.PORT}")
    return app

# Para `flask run` e gunicorn `app:create_app()`
app = create_app()
