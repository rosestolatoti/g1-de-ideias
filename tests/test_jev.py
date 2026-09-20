import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

def test_jev_fallback():
    from app.services.jev_service import JevService
    j = JevService(api_key="fake")
    j.client = None  # força fallback
    r = j.fallback_classify("Tutorial de IA com github.com/meu-repo e automação LLM")
    assert r["editoria"] in ["ia","automacao","outro","github","vps"]
    assert 0 <= r["score"] <= 3
    assert 0 <= r["util"] <= 1

def test_jev_health():
    from app.services.jev_service import get_jev
    h = get_jev().health()
    assert "has_sdk" in h
    assert "model" in h
