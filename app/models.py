#!/usr/bin/env python3
"""
G1 DE IDEIAS — models.py
Dataclass profissional para Notícia/Ideia + helpers
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import json

@dataclass
class Noticia:
    id: str
    titulo: str
    texto_completo: str
    resumo: str
    fonte_arroba: str = "@auto"
    plataforma: str = "screenshot"
    coletor_login: str = "fabio"
    data: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    hora: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    categorias: List[str] = field(default_factory=list)
    editoria: str = "IA"
    link_original: str = ""
    link_github: str = ""
    imagem: str = ""
    imagem_original: str = ""
    perfil_escrita: str = "tecnico"
    # Metadados JEV
    jev_score: Optional[float] = None
    jev_util: Optional[float] = None
    jev_editoria_conf: Optional[float] = None
    jev_model: str = "jev-1.13.0"
    atualizado_em: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict):
        # tolerante a campos extras
        known = {k for k in cls.__dataclass_fields__}
        filtered = {k: v for k, v in d.items() if k in known}
        return cls(**filtered)

    def validate(self):
        assert self.id, "id obrigatório"
        assert self.titulo and len(self.titulo) >= 10, "título muito curto"
        assert len(self.texto_completo) >= 40, "texto muito curto"

def load_noticias(json_path: Path) -> List[Noticia]:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    raw = data.get("noticias") or data.get("ideias") or []
    return [Noticia.from_dict(x) for x in raw]

def save_noticias(json_path: Path, noticias: List[Noticia], meta: dict = None):
    meta = meta or {}
    payload = {
        "projeto": "G1 de Ideias",
        "versao": "2.0-profissional",
        "data": datetime.now().strftime("%Y-%m-%d"),
        "pasta_prints": meta.get("pasta_prints", "/storage/emulated/0/Pictures/Screenshots"),
        "total_prints": meta.get("total_prints", len(noticias)),
        "status": meta.get("status", f"Atualizado {datetime.now().isoformat()} - JEV {len(noticias)} ideias"),
        "editorias": ["IA","Seguranca","Hacking","Automacao","WhatsApp","VPS"],
        "perfis": ["tecnico","provocador","didatico"],
        "total_ideias": len(noticias),
        "ultima_atualizacao": datetime.now().isoformat(),
        "ideias": [n.to_dict() for n in sorted(noticias, key=lambda x: x.id, reverse=True)]
    }
    Path(json_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
