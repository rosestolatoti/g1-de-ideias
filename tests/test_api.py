import pytest
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from app import create_app

def test_health():
    app = create_app("testing")
    c = app.test_client()
    rv = c.get("/health")
    assert rv.status_code == 200
    assert rv.json["status"] == "ok"

def test_api_noticias():
    app = create_app("testing")
    # cria json teste mínimo se não existir
    import json
    p = BASE / "data" / "noticias.json"
    assert p.exists(), "noticias.json deve existir"
    c = app.test_client()
    rv = c.get("/api/noticias")
    assert rv.status_code == 200
    assert "total" in rv.json
    assert "noticias" in rv.json

def test_categorias():
    app = create_app("testing")
    c = app.test_client()
    rv = c.get("/api/categorias")
    assert rv.status_code == 200
