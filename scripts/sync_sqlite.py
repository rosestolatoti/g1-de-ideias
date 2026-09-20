#!/usr/bin/env python3
"""
G1 DE IDEIAS — sync_sqlite.py
Sincroniza data/noticias.json (fonte da verdade) → data/noticias.db (espelho para busca/filtro)

Uso:
  python3 scripts/sync_sqlite.py
  sqlite3 data/noticias.db "SELECT COUNT(*) FROM noticias;"
  sqlite3 data/noticias.db "SELECT titulo FROM noticias WHERE categorias LIKE '%github%'"
"""
import json
import sqlite3
from pathlib import Path

def sync():
    base = Path(__file__).resolve().parent.parent
    json_path = base / "data" / "noticias.json"
    db_path = base / "data" / "noticias.db"

    if not json_path.exists():
        print(f"JSON não encontrado: {json_path}")
        return

    data = json.loads(json_path.read_text(encoding="utf-8"))
    noticias = data.get("noticias") or data.get("ideias") or []
    if not noticias:
        print("Nenhuma notícia no JSON (chaves ideias/noticias vazias)")
        return

    # Conecta (cria se não existe)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Recria tabela (idempotente)
    cur.execute("DROP TABLE IF EXISTS noticias")
    cur.execute("""
        CREATE TABLE noticias (
            id TEXT PRIMARY KEY,
            titulo TEXT,
            resumo TEXT,
            texto_completo TEXT,
            fonte_arroba TEXT,
            plataforma TEXT,
            categorias TEXT,  -- CSV: twitter,github,gringa
            editoria TEXT,
            data TEXT,
            hora TEXT,
            link_original TEXT,
            link_github TEXT,
            imagem TEXT,
            imagem_original TEXT,
            perfil_escrita TEXT
        )
    """)
    # Índice para busca rápida por categoria
    cur.execute("CREATE INDEX idx_categorias ON noticias(categorias)")
    cur.execute("CREATE INDEX idx_plataforma ON noticias(plataforma)")
    cur.execute("CREATE INDEX idx_data ON noticias(data)")

    # Insere
    for n in noticias:
        categorias = ",".join(n.get("categorias", []))
        cur.execute("""
            INSERT OR REPLACE INTO noticias
            (id,titulo,resumo,texto_completo,fonte_arroba,plataforma,categorias,editoria,data,hora,link_original,link_github,imagem,imagem_original,perfil_escrita)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            n.get("id"),
            n.get("titulo"),
            n.get("resumo"),
            n.get("texto_completo"),
            n.get("fonte_arroba"),
            n.get("plataforma"),
            categorias,
            n.get("editoria",""),
            n.get("data"),
            n.get("hora"),
            n.get("link_original",""),
            n.get("link_github",""),
            n.get("imagem",""),
            n.get("imagem_original",""),
            n.get("perfil_escrita",""),
        ))

    conn.commit()

    # Teste
    total = cur.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
    print(f"✓ SQLite sincronizado: {total} notícias em {db_path}")
    # Exemplos
    for cat in ["github","twitter","gringa","ia"]:
        cnt = cur.execute("SELECT COUNT(*) FROM noticias WHERE categorias LIKE ?", (f"%{cat}%",)).fetchone()[0]
        print(f"  - {cat}: {cnt}")

    # Busca exemplo
    print("\nExemplo busca 'github':")
    for row in cur.execute("SELECT id, titulo FROM noticias WHERE categorias LIKE '%github%' LIMIT 3"):
        print(f"  {row[0]}: {row[1][:60]}")

    conn.close()

if __name__ == "__main__":
    sync()
