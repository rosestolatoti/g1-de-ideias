#!/usr/bin/env python3
"""
G1 DE IDEIAS — storage_service.py
Gestão profissional de JSON/SQLite (fonte da verdade)
"""
import json
import sqlite3
from pathlib import Path
import logging
from typing import List
from app.models import Noticia

log = logging.getLogger("g1.storage")

def load_noticias(json_path: Path) -> List[Noticia]:
    p = Path(json_path)
    if not p.exists():
        log.warning(f"JSON não existe {p}, retornando vazio")
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    raw = data.get("noticias") or data.get("ideias") or []
    return [Noticia.from_dict(x) for x in raw]

def save_noticias(json_path: Path, noticias: List[Noticia]):
    from app.models import save_noticias as _save
    _save(Path(json_path), noticias)

def sync_sqlite(json_path: Path, db_path: Path) -> int:
    noticias = load_noticias(json_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS noticias")
    cur.execute("""
        CREATE TABLE noticias (
            id TEXT PRIMARY KEY,
            titulo TEXT,
            resumo TEXT,
            texto_completo TEXT,
            fonte_arroba TEXT,
            plataforma TEXT,
            categorias TEXT,
            editoria TEXT,
            data TEXT,
            hora TEXT,
            link_original TEXT,
            link_github TEXT,
            imagem TEXT,
            imagem_original TEXT,
            perfil_escrita TEXT,
            jev_score REAL,
            jev_util REAL
        )
    """)
    cur.execute("CREATE INDEX idx_categorias ON noticias(categorias)")
    cur.execute("CREATE INDEX idx_plataforma ON noticias(plataforma)")
    cur.execute("CREATE INDEX idx_data ON noticias(data)")
    for n in noticias:
        cur.execute("""
            INSERT OR REPLACE INTO noticias
            (id,titulo,resumo,texto_completo,fonte_arroba,plataforma,categorias,editoria,data,hora,link_original,link_github,imagem,imagem_original,perfil_escrita,jev_score,jev_util)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (n.id, n.titulo, n.resumo, n.texto_completo, n.fonte_arroba, n.plataforma, ",".join(n.categorias), n.editoria, n.data, n.hora, n.link_original, n.link_github, n.imagem, n.imagem_original, n.perfil_escrita, n.jev_score or 0, n.jev_util or 0))
    conn.commit()
    total = cur.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
    conn.close()
    log.info(f"SQLite sync {total} em {db_path}")
    return total

def search_sqlite(db_path: Path, q: str, categoria: str = "", limit=20):
    if not Path(db_path).exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if categoria:
        cur.execute("SELECT * FROM noticias WHERE categorias LIKE ? LIMIT ?", (f"%{categoria}%", limit))
    elif q:
        like = f"%{q}%"
        cur.execute("SELECT * FROM noticias WHERE titulo LIKE ? OR resumo LIKE ? OR texto_completo LIKE ? OR categorias LIKE ? LIMIT ?", (like, like, like, like, limit))
    else:
        cur.execute("SELECT * FROM noticias ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
