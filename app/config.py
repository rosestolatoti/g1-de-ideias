#!/usr/bin/env python3
"""
G1 DE IDEIAS — config.py
Configuração profissional por ambiente (dev / production / testing)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)
# também tenta carregar da lab isolada (robustez)
lab_env = Path("/tmp/typesafe-lab/.env.secure")
if lab_env.exists():
    load_dotenv(lab_env, override=False)
hermes_env = Path("/root/.hermes/.env")
if hermes_env.exists():
    load_dotenv(hermes_env, override=False)

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-g1-de-ideias-troque-em-prod")
    JSON_PATH = Path(os.getenv("DATA_JSON", str(BASE_DIR / "data" / "noticias.json")))
    DB_PATH = Path(os.getenv("DB_PATH", str(BASE_DIR / "data" / "noticias.db")))
    PRINTS_CROPPED = Path(os.getenv("PRINTS_CROPPED", str(BASE_DIR / "prints" / "cropped")))
    PRINTS_ORIGINAL = Path(os.getenv("PRINTS_ORIGINAL", str(BASE_DIR / "prints" / "original")))
    SCREENSHOTS_DIR = Path(os.getenv("SCREENSHOTS_DIR", "/storage/emulated/0/Pictures/Screenshots"))
    CROP_TOP = int(os.getenv("CROP_TOP", "110"))
    CROP_BOTTOM = int(os.getenv("CROP_BOTTOM", "48"))
    TYPESAFE_API_KEY = os.getenv("TYPESAFE_API_KEY", "")
    JEV_SCORE_MIN = float(os.getenv("JEV_SCORE_MIN", "1.0"))
    JEV_UTIL_MIN = float(os.getenv("JEV_UTIL_MIN", "0.55"))
    JEV_BATCH_SIZE = int(os.getenv("JEV_BATCH_SIZE", "8"))
    PORT = int(os.getenv("PORT", "5000"))
    HOST = os.getenv("HOST", "0.0.0.0")
    JSON_SORT_KEYS = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    # Em produção usa gunicorn, não debug

class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    JSON_PATH = BASE_DIR / "data" / "noticias.test.json"

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
