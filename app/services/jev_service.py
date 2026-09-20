#!/usr/bin/env python3
"""
G1 DE IDEIAS — app/services/jev_service.py
Serviço JEV (TypeSafe System One) profissional.
SDK: typesafe-sdk 0.7.0 | Model: jev-1.13.0
Uso correto:
  from typesafe_sdk import TypeSafeClient, Choice, Score, Noul
  with TypeSafeClient() as client:
      r = client.system_one(state="texto", questions={"q": Choice(criteria={...})})
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

log = logging.getLogger("g1.jev")

try:
    from typesafe_sdk import TypeSafeClient, Choice, Score, Noul
    HAS_JEV = True
except Exception as e:
    HAS_JEV = False
    log.warning(f"typesafe-sdk não disponível: {e}")
    Choice = Score = Noul = None  # type: ignore

def _load_key() -> str:
    for p in ["/tmp/typesafe-lab/.env.secure", "/root/.hermes/.env", Path(".env")]:
        try:
            txt = Path(p).read_text(encoding="utf-8")
            for line in txt.splitlines():
                if line.strip().startswith("TYPESAFE_API_KEY="):
                    return line.split("=",1)[1].strip().strip('"').strip("'")
        except: pass
    return os.getenv("TYPESAFE_API_KEY","")

class JevService:
    def __init__(self, api_key: Optional[str] = None, model: str = "jev-1.13.0"):
        self.api_key = api_key or _load_key()
        self.model = model
        self.client = None
        if HAS_JEV and self.api_key:
            try:
                os.environ["TYPESAFE_API_KEY"] = self.api_key
                # TypeSafeClient lê env; podemos também passar explicit
                self.client = TypeSafeClient(api_key=self.api_key, model=self.model)
            except Exception as e:
                log.warning(f"JEV client init falhou: {e}")
                self.client = None
        if not self.api_key:
            log.warning("TYPESAFE_API_KEY vazio — JEV vai usar fallback heurístico")

    def health(self) -> dict:
        return {
            "has_sdk": HAS_JEV,
            "has_key": bool(self.api_key),
            "key_prefix": (self.api_key[:12]+"...") if self.api_key else None,
            "model": self.model,
            "client_ok": self.client is not None
        }

    def fallback_classify(self, texto: str) -> dict:
        t = texto.lower()
        if any(k in t for k in ["ia","gpt","llm","agent","claude","codex","gemini"]): ed="ia"
        elif any(k in t for k in ["hack","exploit","vuln","cve","pentest"]): ed="hacking"
        elif any(k in t for k in ["seguran","privacid","cripto","lgpd"]): ed="seguranca"
        elif any(k in t for k in ["whatsapp","telegram","zap"]): ed="whatsapp"
        elif any(k in t for k in ["vps","servidor","adb","android","deploy","docker"]): ed="vps"
        elif any(k in t for k in ["automa","workflow","n8n","zapier","make"]): ed="automacao"
        else: ed="outro"
        score = 1.0
        if len(texto) > 300: score += 0.5
        if any(k in t for k in ["github.com","reposit","open source","tool"]): score += 0.5
        if "http" in t: score += 0.3
        score = min(3.0, round(score,2))
        util = 0.7 if len(texto)>80 else 0.4
        # penaliza se parece barra de notificação
        if texto.strip().startswith("20:") and len(texto)<120:
            util = 0.2
        return {"editoria": ed, "score": score, "util": util, "confidence": 0.55, "fallback": True}

    def classify_batch(self, items: List[Dict[str,str]]) -> Dict[str, dict]:
        """
        items = [{"id":"20260910-205937","texto":"..."}, ...]
        Retorna {id: {editoria, score, util, confidence, aprovado?, fallback}}
        Fan-out: 1 chamada JEV com N prints.
        """
        if not items:
            return {}
        if not self.client or not HAS_JEV:
            return {x["id"]: self.fallback_classify(x["texto"]) for x in items}

        # Monta state único: objeto com cada id -> texto curto
        # JEV aceita state como JSONContent (str, dict, list). Usamos dict.
        state = {it["id"]: it["texto"][:1200] for it in items}

        questions: Dict[str, Any] = {}
        for it in items:
            k = it["id"]
            txt = it["texto"][:1200]
            # Choice editoria
            questions[f"{k}_edit"] = Choice(
                instructions=f"Qual editoria do G1 esta ideia pertence? Texto curto: {txt[:90]}",
                criteria={
                    "ia": "IA, agentes, LLM, automação",
                    "seguranca": "Segurança, privacidade",
                    "hacking": "Hacking, exploit, pentest",
                    "automacao": "Automação, workflow, scripts",
                    "whatsapp": "WhatsApp, Telegram",
                    "vps": "VPS, servidor, ADB, Android",
                    "outro": "Outro ou indefinido"
                }
            )
            # Score vale
            questions[f"{k}_vale"] = Score(
                instructions=f"Vale virar matéria G1? Texto: {txt[:120]}",
                criteria=[
                    "0 lixo/sujeira, não publica",
                    "1 fraco, curiosidade mas não vira matéria",
                    "2 bom, vira matéria normal, útil",
                    "3 manchete, capa, história forte"
                ]
            )
            # Noul útil
            questions[f"{k}_util"] = Noul(
                instructions="Este conteúdo é útil e aproveitável (não é sujeira ou vazia)?"
            )

        try:
            # Chamada sync correta
            with self.client as client:
                # Re-instancia com api_key para garantir
                pass
            # Na prática, TypeSafeClient pode ser usado como context ou direto
            # Usamos client temporário para garantir close
            from typesafe_sdk import TypeSafeClient as TSC
            with TSC(api_key=self.api_key, model=self.model) as cli:
                resp = cli.system_one(state=state, questions=questions)

            # resp tem .choices, .scores, .nouls e .answers?
            # SDK 0.7.0 retorna SystemOneResponse com .choices/.scores/.nouls
            out: Dict[str, dict] = {}
            for it in items:
                k = it["id"]
                # Tenta pegar de .choices / .scores / .nouls primeiro
                edit_ans = None
                vale_ans = None
                util_ans = None
                try:
                    edit_ans = resp.choices.get(f"{k}_edit") if hasattr(resp, "choices") else None
                    vale_ans = resp.scores.get(f"{k}_vale") if hasattr(resp, "scores") else None
                    util_ans = resp.nouls.get(f"{k}_util") if hasattr(resp, "nouls") else None
                except: pass
                # fallback para .answers dict
                if not edit_ans and hasattr(resp, "answers"):
                    edit_ans = resp.answers.get(f"{k}_edit")
                    vale_ans = resp.answers.get(f"{k}_vale")
                    util_ans = resp.answers.get(f"{k}_util")

                # Normaliza
                if edit_ans is not None:
                    editoria = getattr(edit_ans, "choice", None) or (edit_ans.get("choice") if isinstance(edit_ans, dict) else "outro")
                    conf = getattr(edit_ans, "confidence", None) or (edit_ans.get("confidence") if isinstance(edit_ans, dict) else 0.6) or 0.6
                else:
                    editoria, conf = "outro", 0.5

                if vale_ans is not None:
                    score_val = getattr(vale_ans, "score", None) or (vale_ans.get("score") if isinstance(vale_ans, dict) else 1.0) or 1.0
                    # score pode ser float 0-3
                    try: score_val = float(score_val)
                    except: score_val = 1.0
                else:
                    score_val = 1.0

                if util_ans is not None:
                    util_val = getattr(util_ans, "noul", None) or (util_ans.get("noul") if isinstance(util_ans, dict) else 0.5) or 0.5
                    try: util_val = float(util_val)
                    except: util_val = 0.5
                else:
                    util_val = 0.5

                out[k] = {
                    "editoria": editoria or "outro",
                    "confidence": float(conf) if conf else 0.6,
                    "score": float(score_val),
                    "util": float(util_val),
                    "fallback": False,
                }
            return out

        except Exception as e:
            log.warning(f"JEV batch falhou, fallback heurístico: {e}")
            return {x["id"]: self.fallback_classify(x["texto"]) for x in items}

    async def classify_batch_async(self, items: List[Dict[str,str]]) -> Dict[str, dict]:
        """Wrapper async para compat com pipeline async legacy"""
        return self.classify_batch(items)

_jev = None
def get_jev() -> JevService:
    global _jev
    if _jev is None:
        _jev = JevService()
    return _jev
