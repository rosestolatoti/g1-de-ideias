#!/usr/bin/env python3
"""
G1 DE IDEIAS — scripts/pipeline.py
Pipeline profissional: Screenshots -> OCR -> JEV -> JSON -> Crop -> HTML -> SQLite
Orquestrador único (usado por GitHub Actions, Mint systemd e Termux).

Uso:
  python3 scripts/pipeline.py --all          # processa todos pendentes
  python3 scripts/pipeline.py --dry-run      # só mostra o que faria
  python3 scripts/pipeline.py --limit 20     # limita N prints
  python3 scripts/pipeline.py --force        # reprocessa mesmo já curados
  JEV_SCORE_MIN=1.2 python3 scripts/pipeline.py

Env:
  TYPESAFE_API_KEY (obrigatório pra JEV real, senão fallback)
"""
import argparse, json, os, re, sys, time, subprocess
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from app.services.ocr_service import ocr_image
from app.services.crop_service import crop_image
from app.models import Noticia
from app.services.storage_service import load_noticias, save_noticias, sync_sqlite

# JEV é async mas pipeline é sync — usamos wrapper
try:
    import asyncio
    from app.services.jev_service import get_jev
    HAS_JEV = True
except:
    HAS_JEV = False

def parse_args():
    p = argparse.ArgumentParser(description="Pipeline G1 DE IDEIAS")
    p.add_argument("--all", action="store_true", help="processa todos pendentes")
    p.add_argument("--limit", type=int, default=0, help="limite de prints")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true", help="reprocessa já curados")
    p.add_argument("--no-jev", action="store_true", help="pula JEV, só OCR + heurística")
    p.add_argument("--score-min", type=float, default=float(os.getenv("JEV_SCORE_MIN","1.0")))
    p.add_argument("--util-min", type=float, default=float(os.getenv("JEV_UTIL_MIN","0.55")))
    return p.parse_args()

def list_screenshots(screenshots_dir: Path, json_path: Path, force=False):
    raw = json.loads(json_path.read_text(encoding="utf-8")) if json_path.exists() else {"ideias":[]}
    existing = set(x["id"] for x in (raw.get("ideias") or raw.get("noticias") or []))
    files = []
    if screenshots_dir.exists():
        files = sorted(screenshots_dir.glob("Screenshot_*.png")) + sorted(screenshots_dir.glob("Screenshot_*.jpg"))
        # ordena por mtime desc (mais recente primeiro)
        files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)
    else:
        print(f"⚠️  Screenshots dir não existe: {screenshots_dir}")
        return [], existing
    pending = []
    for f in files:
        m = re.search(r"(\d{8}-\d{6})", f.name)
        id_ = m.group(1) if m else f.stem[:16]
        if force or id_ not in existing:
            pending.append((f, id_))
    return pending, existing

def ocr_text(image_path: Path) -> str:
    return ocr_image(image_path)

def jev_classify_batch(batch_texts, score_min, util_min, use_jev=True):
    """batch_texts = [(file, id, texto)] -> dict id-> {editoria,score,util,aprovado}"""
    if not use_jev or not HAS_JEV:
        from app.services.jev_service import JevService
        j = JevService()
        out = {}
        for _, id_, txt in batch_texts:
            r = j.fallback_classify(txt)
            out[id_] = {
                "editoria": r["editoria"],
                "score": r["score"],
                "util": r["util"],
                "confidence": r["confidence"],
                "aprovado": (r["util"] >= util_min and r["score"] >= score_min),
                "fallback": True
            }
        return out
    # JEV real — sync (SDK 0.7.0 é síncrono)
    from app.services.jev_service import get_jev
    j = get_jev()
    items = [{"id": id_, "texto": txt[:1200]} for _, id_, txt in batch_texts]
    res = j.classify_batch(items)  # sync, já trata fallback interno
    out = {}
    for _, id_, _ in batch_texts:
        r = res.get(id_, {"editoria":"outro","score":0,"util":0,"confidence":0.5,"fallback":True})
        out[id_] = {
            "editoria": r.get("editoria","outro"),
            "score": float(r.get("score",0)),
            "util": float(r.get("util",0)),
            "confidence": float(r.get("confidence",0.6)),
            "aprovado": (float(r.get("util",0)) >= util_min and float(r.get("score",0)) >= score_min),
            "fallback": bool(r.get("fallback", False))
        }
    return out

def build_noticia(file_path: Path, id_, texto, jev_res):
    # título: primeiras 12 palavras limpas
    words = re.sub(r"[^\w\s@#/\.]", " ", texto).split()
    titulo = " ".join(words[:12])[:90].strip()
    if len(titulo) < 15:
        titulo = f"Ideia {id_} — {jev_res['editoria'].upper()}"
    # capitaliza
    titulo = titulo[0].upper() + titulo[1:] if titulo else f"Ideia {id_}"
    resumo = " ".join(texto.split()[:30])[:170].strip() + "…"
    # data/hora do id
    try:
        d = id_.split("-")[0]
        data = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
        h = id_.split("-")[1] if "-" in id_ else "120000"
        hora = f"{h[0:2]}:{h[2:4]}:{h[4:6]}"
    except:
        data = datetime.now().strftime("%Y-%m-%d")
        hora = datetime.now().strftime("%H:%M:%S")
    # categorias: plataforma + editoria + gringa/brasil heurística
    categorias = ["screenshot", jev_res["editoria"].lower()]
    t_low = texto.lower()
    if "github.com" in t_low or "reposit" in t_low: categorias.append("github")
    if any(k in t_low for k in ["twitter","x.com","@"]): categorias.append("twitter")
    if any(k in t_low for k in ["instagram"]): categorias.append("instagram")
    # gringa/brasil
    if any(k in t_low for k in [" the ", " and ", " with "]): categorias.append("gringa")
    else: categorias.append("brasil")
    categorias = sorted(set(categorias))
    return Noticia(
        id=id_,
        titulo=titulo,
        texto_completo=texto,
        resumo=resumo,
        fonte_arroba="@auto_jev",
        plataforma="screenshot",
        coletor_login="fabio",
        data=data,
        hora=hora,
        categorias=categorias,
        editoria=jev_res["editoria"].upper() if jev_res["editoria"]!="outro" else "IA",
        link_original="",
        link_github=next((w for w in texto.split() if "github.com" in w), ""),
        imagem=f"prints/cropped/{file_path.name.replace('.png','.jpg').replace('.PNG','.jpg')}",
        imagem_original=str(file_path),
        perfil_escrita="tecnico",
        jev_score=jev_res["score"],
        jev_util=jev_res["util"],
        jev_editoria_conf=jev_res["confidence"],
    )

def main():
    args = parse_args()
    json_path = BASE / "data" / "noticias.json"
    screenshots_dir = Path(os.getenv("SCREENSHOTS_DIR", "/storage/emulated/0/Pictures/Screenshots"))
    # fallback para AMBIENTE_TERMUX se não achar
    if not screenshots_dir.exists():
        alt = Path("/sdcard/Download/00_AMBIENTE_TERMUX/G1_DE_IDEIAS/prints/original")
        if alt.exists():
            screenshots_dir = Path("/storage/emulated/0/Pictures/Screenshots")

    pending, existing = list_screenshots(screenshots_dir, json_path, force=args.force)
    if args.limit:
        pending = pending[:args.limit]
    elif not args.all:
        # default: 10 mais recentes (seguro pra não estourar tempo)
        pending = pending[:10]

    print(f"📂 Screenshots dir: {screenshots_dir}")
    print(f"📊 Existentes: {len(existing)} | Pendentes: {len(pending)} (limit={'all' if args.all else args.limit or 10})")
    print(f"🎯 Thresholds: score>={args.score_min} util>={args.util_min} | JEV={'OFF' if args.no_jev else 'ON'}")
    if args.dry_run:
        for f, id_ in pending[:20]:
            print(f"  dry {id_} -> {f.name}")
        print("dry-run, nada executado")
        return

    if not pending:
        print("✅ Nada pendente")
        return

    # OCR
    print(f"\n🔍 OCR {len(pending)} prints (tesseract por+eng, 1-2s cada)...")
    batch_texts = []
    for f, id_ in pending:
        txt = ocr_text(f)
        if txt and len(txt) >= 40:
            batch_texts.append((f, id_, txt))
            print(f"  OCR {id_} {len(txt)}c: {txt[:70].replace(chr(10),' ')}...")
        else:
            print(f"  OCR fraco {id_} len {len(txt) if txt else 0}")

    if not batch_texts:
        print("❌ Nenhum OCR válido")
        return

    # JEV batch (fan-out)
    print(f"\n🤖 JEV peneira {len(batch_texts)} textos em batch...")
    jev_map = jev_classify_batch(batch_texts, args.score_min, args.util_min, use_jev=not args.no_jev)
    for _, id_, _ in batch_texts:
        r = jev_map[id_]
        print(f"  JEV {id_} score={r['score']:.2f} util={r['util']:.2f} ed={r['editoria']} conf={r['confidence']:.2f} {'✅' if r['aprovado'] else '❌'} {'(fallback)' if r['fallback'] else ''}")

    aprovados = [(f,id_,txt) for f,id_,txt in batch_texts if jev_map[id_]["aprovado"]]
    reprovados = len(batch_texts) - len(aprovados)
    print(f"\n📈 Aprovados: {len(aprovados)} | Reprovados: {reprovados}")

    if not aprovados:
        print("❌ Nenhum aprovado pelo JEV (tente --score-min menor ou --no-jev)")
        return

    # Crop
    print(f"\n✂️  Crop {len(aprovados)} prints...")
    from app.services.crop_service import crop_image
    for f, id_, _ in aprovados:
        src = f
        dst = BASE / "prints" / "cropped" / f.name.replace(".png",".jpg").replace(".PNG",".jpg")
        # também salva original
        orig_dst = BASE / "prints" / "original" / f.name
        if not orig_dst.exists():
            try:
                import shutil
                shutil.copy(src, orig_dst)
            except: pass
        try:
            crop_image(src, dst)
        except Exception as e:
            print(f"  crop erro {id_}: {e}")

    # Atualiza JSON
    existing_noticias = load_noticias(json_path)
    novos = []
    for f, id_, txt in aprovados:
        r = jev_map[id_]
        n = build_noticia(f, id_, txt, r)
        novos.append(n)
    todas = existing_noticias + novos
    # dedup por id mantendo mais recente
    dedup = {}
    for n in todas:
        dedup[n.id] = n
    todas = sorted(dedup.values(), key=lambda x: x.id, reverse=True)
    save_noticias(json_path, todas)
    print(f"💾 JSON atualizado: {len(todas)} total ({len(novos)} novos) em {json_path}")

    # Sync SQLite
    db_path = BASE / "data" / "noticias.db"
    total_db = sync_sqlite(json_path, db_path)
    print(f"🗄️  SQLite sync: {total_db}")

    # Gera site
    print(f"\n🏗️  Gerando site estático...")
    gen = BASE / "scripts" / "generate_site.py"
    if gen.exists():
        subprocess.run([sys.executable, str(gen)], check=False)
    else:
        # fallback antigos
        for s in ["gerar_html.py","gerar_index_dinamico.py"]:
            p = BASE / "scripts" / s
            if p.exists():
                subprocess.run([sys.executable, str(p)], check=False)

    print(f"\n✅ Pipeline concluído: {len(novos)} novas ideias no ar")
    print(f"   JSON: {json_path}")
    print(f"   Site: {BASE / 'index.html'}")
    print(f"   Próximo: git add data/noticias.json prints/cropped && git commit -m 'feat: +{len(novos)} ideias JEV' && git push")

if __name__ == "__main__":
    main()
