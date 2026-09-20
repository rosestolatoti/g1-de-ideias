#!/usr/bin/env python3
"""
G1 DE IDEIAS — scripts/generate_site.py
Gerador profissional estático: data/noticias.json -> index.html + detalhe/*.html
Consolida gerar_html.py + gerar_index_dinamico.py com layout refinado 20/09
"""
import json, html, shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
JSON_PATH = BASE / "data" / "noticias.json"
TPL_PATH = BASE / "templates" / "globo.html"
OUT_INDEX = BASE / "index.html"
DETALHE_DIR = BASE / "detalhe"

def esc(s): return html.escape(s or "")
def format_data_small(data, hora):
    try:
        d = data.split("-")
        return f"{d[2]}/{d[1]} {hora[:5]}"
    except:
        return f"{data} {hora[:5]}"

def img_names(n):
    p = n.get("imagem","")
    name = Path(p).name
    if not name or "." not in name:
        name = f"Screenshot_{n['id']}.png"
    jpg = name.replace(".png",".jpg").replace(".PNG",".jpg")
    return jpg, name

def main():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    noticias = data.get("ideias") or data.get("noticias") or []
    noticias = sorted(noticias, key=lambda x: x.get("id",""), reverse=True)
    # dedup
    seen=set(); dedup=[]
    for n in noticias:
        if n["id"] not in seen:
            dedup.append(n); seen.add(n["id"])
    noticias=dedup
    total=len(noticias)
    print(f"🏗️  Generate site: {total} notícias sequenciais (mais recente primeiro)")

    # template
    if not TPL_PATH.exists():
        print(f"❌ Template não encontrado: {TPL_PATH}")
        return
    tpl = TPL_PATH.read_text(encoding="utf-8")
    pre = tpl.split('<div class="container">')[0]
    if '<div class="container">' not in pre:
        pre += '\n<div class="container">\n'

    if '<div class="info-box">' in tpl:
        footer_html = '<div class="info-box">' + tpl.split('<div class="info-box">')[1]
    elif '<div class="footer">' in tpl:
        footer_html = '<div class="footer">' + tpl.split('<div class="footer">')[1]
    else:
        footer_html = f"""
    <div class="info-box">
      <div style="font-size:12.5px; color:var(--ink-soft); line-height:1.6">Prints originais exibidos como imagem da matéria — toque pra ampliar. <span style="color:var(--green); font-weight:700">OCR tesseract moto g84</span></div>
      <div style="display:flex; gap:8px; margin-top:12px; flex-wrap:wrap">
        <span style="font-size:11px; background:#fff; border:1px solid var(--line-strong); padding:5px 10px; border-radius:999px; font-weight:700"><strong>{total}</strong> notícias</span>
        <span style="font-size:11px; background:var(--green); color:#fff; padding:5px 10px; border-radius:999px; font-weight:800">{total} NO AR</span>
        <span style="font-size:10px; background:#fff; border:1px solid var(--line); padding:5px 10px; border-radius:999px">atualizado {data.get("ultima_atualizacao","")[:16]}</span>
      </div>
    </div>
    <div class="footer">
      <strong>G1 DE IDEIAS DO FABIO.COM</strong> • captura ideias automatica cel Fabio<br>
      Desenvolvido por: <strong>Fábio Rosestolato</strong> • São Paulo
    </div>
  </div>
</body>
</html>
"""

    if total==0:
        body_html = '<div style="padding:32px; text-align:center; color:#6E6E73">Nenhuma ideia ainda — tire um print!</div>'
    else:
        manchete = noticias[0]
        manchete_jpg, manchete_png = img_names(manchete)
        manchete_ds = format_data_small(manchete.get("data",""), manchete.get("hora",""))
        body_html = f"""
    <a data-cat="{esc(' '.join(manchete.get('categorias',[])))}" href="detalhe/{esc(manchete['id'])}.html" style="text-decoration:none">
    <div class="manchete"><h1>{esc(manchete['titulo'])}</h1></div>
    <div style="padding:0 16px">
      <div class="hero-media">
        <img src="prints/cropped/{esc(manchete_jpg)}" alt="print" onerror="imgErro(this)">
        <div class="badge-live">Tempo real</div>
        <div class="badge-photo">📸 {esc(manchete_png)}</div>
      </div>
      <div class="tags">{"".join([f'<span class="tag">#{esc(c)}</span>' for c in manchete.get("categorias",[])])}</div>
      <p class="quote">“{esc(manchete.get("resumo",""))}”</p>
      <div class="meta-line"><span style="color:var(--green)">●</span> <strong>{esc(manchete.get("fonte_arroba","@auto"))}</strong> • {esc(manchete.get("plataforma","screenshot"))} • <span style="font-size:10px; background:var(--bg-soft); border:1px solid var(--line); padding:2px 6px; border-radius:999px">{esc(manchete_ds)}</span> <span style="background:#FFF7ED; padding:2px 7px; border-radius:6px; border:1px solid #FDE68A; font-size:10px; font-weight:800; color:#B45309">PRINT REAL</span> <span style="font-size:10px; color:#8A8D93; margin-left:auto">atualizado {esc(manchete.get("atualizado_em", manchete.get("data",""))[:10])}</span></div>
    </div>
    </a>
    """
        if total>1:
            segunda = noticias[1]
            body_html += f"""
    <div class="siga"><span style="color:var(--green)">●</span> <strong>Siga:</strong> {esc(segunda['titulo'])} — <span style="color:var(--muted)">{esc(segunda.get("resumo","")[:90])}</span> <a href="detalhe/{esc(segunda['id'])}.html">→</a> <span style="font-size:10px; color:#8A8D93; margin-left:6px">{format_data_small(segunda.get("data",""), segunda.get("hora",""))}</span></div>
    <div style="background:#fff">
        """
            for n in noticias[1:5]:
                jpg,_ = img_names(n); ds=format_data_small(n.get("data",""),n.get("hora",""))
                body_html += f"""
    <a data-cat="{esc(' '.join(n.get('categorias',[])))}" href="detalhe/{esc(n['id'])}.html" class="card-sec" style="text-decoration:none; color:inherit">
      <div class="left">
        <div class="kicker">{esc(n.get("editoria","IA"))} <span class="pill">{esc(n.get("perfil_escrita","didatico"))}</span> <span style="font-size:10px; color:#8A8D93; font-weight:600;">{esc(ds)}</span></div>
        <h2>{esc(n['titulo'])}</h2>
        <p>“{esc(n.get("resumo",""))}”</p>
        <div class="foot"><strong>{esc(n.get("fonte_arroba",""))}</strong> • {esc(ds)} • #{", #".join(n.get("categorias",[])[:3])} <span style="margin-left:auto; font-size:10px; color:#8A8D93">atualizado {esc(n.get("atualizado_em", n.get("data",""))[:10])}</span></div>
      </div>
      <img src="prints/cropped/{esc(jpg)}" class="thumb" alt="" onerror="imgErro(this)">
    </a>
            """
            body_html += "\n    </div>"
            if total>5:
                grid = noticias[5:9]
                body_html += '\n    <div class="grid">\n'
                for n in grid:
                    jpg,_=img_names(n); ds=format_data_small(n.get("data",""),n.get("hora",""))
                    body_html += f"""
      <a data-cat="{esc(' '.join(n.get('categorias',[])))}" href="detalhe/{esc(n['id'])}.html" class="grid-card">
        <div class="g-thumb"><img src="prints/cropped/{esc(jpg)}" alt="" onerror="imgErro(this)"></div>
        <div class="kicker">{esc(n.get("editoria","IA"))} <span class="pill">{esc(n.get("perfil_escrita","didatico"))}</span></div>
        <h3>{esc(n['titulo'])}</h3>
        <div class="g-foot">{esc(n.get("fonte_arroba",""))} • {esc(ds)}<br><span style="font-size:10px; color:#8A8D93">atualizado {esc(n.get("atualizado_em", n.get("data",""))[:10])}</span></div>
      </a>
                    """
                body_html += '\n    </div>'
            if total>9:
                rest = noticias[9:]
                body_html += '\n    <div style="background:#fff; margin-top:0">\n'
                for n in rest:
                    jpg,_=img_names(n); ds=format_data_small(n.get("data",""),n.get("hora",""))
                    body_html += f"""
    <a data-cat="{esc(' '.join(n.get('categorias',[])))}" href="detalhe/{esc(n['id'])}.html" class="card-sec" style="text-decoration:none; color:inherit">
      <div class="left">
        <div class="kicker">{esc(n.get("editoria","IA"))} <span class="pill">{esc(n.get("perfil_escrita","didatico"))}</span> <span style="font-size:10px; color:#8A8D93;">{esc(ds)}</span></div>
        <h2>{esc(n['titulo'])}</h2>
        <p>“{esc(n.get("resumo",""))}”</p>
        <div class="foot"><strong>{esc(n.get("fonte_arroba",""))}</strong> • {esc(ds)} • #{", #".join(n.get("categorias",[])[:2])} <span style="margin-left:auto; font-size:10px; color:#8A8D93">atualizado {esc(n.get("atualizado_em", n.get("data",""))[:10])}</span></div>
      </div>
      <img src="prints/cropped/{esc(jpg)}" class="thumb" alt="" onerror="imgErro(this)">
    </a>
                    """
                body_html += '\n    </div>'

    final = pre + body_html + "\n" + footer_html
    OUT_INDEX.write_text(final, encoding="utf-8")
    print(f"✓ index.html {len(final)} bytes -> {OUT_INDEX}")

    # detalhe pages (usa template refinado 20/09)
    DETALHE_DIR.mkdir(parents=True, exist_ok=True)
    for n in noticias:
        jpg, png = img_names(n)
        detalhe_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(n['titulo'])} — G1 DE IDEIAS DO FABIO.COM</title>
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root{{--blue:#0669DE; --green:#06AA48; --red:#C4170C; --ink:#0F1115; --muted:#6E6E73; --line:#EFEFF0; --bg-soft:#F7F8F9}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:'Open Sans', system-ui, sans-serif; background:#fff; color:var(--ink); line-height:1.5}}
  .hdr{{display:flex; justify-content:space-between; align-items:center; padding:13px 16px; background:rgba(255,255,255,0.96); backdrop-filter:blur(10px); position:sticky; top:0; border-bottom:1px solid var(--line); z-index:10}}
  .logo{{font-size:18.5px; font-weight:900; color:var(--blue); letter-spacing:-0.8px}} .logo .com{{color:var(--ink)}} .sub{{font-size:9px; color:var(--muted); font-weight:700; letter-spacing:0.85px; text-transform:uppercase; margin-top:3px}}
  .crumb{{padding:11px 16px; font-size:12px; color:var(--muted); border-bottom:1px solid var(--line); background:var(--bg-soft)}} .crumb a{{color:var(--blue); font-weight:700; text-decoration:none}}
  .ticker-wrap{{background:#111214; color:#E8E8E8; overflow:hidden; white-space:nowrap; font-size:10px; font-weight:600; letter-spacing:0.65px; text-transform:uppercase; padding:8px 0; border-bottom:1px solid #1F1F1F}}
  .ticker{{display:inline-flex; gap:28px; animation:ticker 42s linear infinite}} @keyframes ticker{{0%{{transform:translateX(0)}}100%{{transform:translateX(-50%)}}}} .dot{{width:5px; height:5px; background:var(--green); border-radius:50%; box-shadow:0 0 0 4px rgba(6,170,72,0.12)}}
  .container{{max-width:640px; margin:0 auto; padding:0 16px}}
  .title{{font-size:25px; font-weight:800; color:var(--green); line-height:1.22; letter-spacing:-0.7px; margin:16px 0 12px 0}}
  .meta{{font-size:12px; color:var(--muted); background:var(--bg-soft); padding:11px 12px; border:1px solid var(--line); border-radius:10px; line-height:1.5}}
  .resumo{{font-size:15.5px; font-weight:600; color:#2B2B2B; border-left:3px solid var(--green); padding:12px 14px; background:#F0FDF4; margin:14px 0; border-radius:0 10px 10px 0; line-height:1.48}}
  .imgwrap{{border:1px solid var(--line); border-radius:12px; overflow:hidden; margin:14px 0; box-shadow:0 2px 10px rgba(16,24,40,0.06)}} .imgwrap img{{width:100%; display:block}}
  .ocr{{background:#fff; border:1px solid var(--line); border-radius:12px; padding:14px; margin:14px 0}} .ocr pre{{white-space:pre-wrap; font-family:monospace; font-size:12px; background:#FFFBF5; padding:12px; border:1px dashed #E3E5E8; border-radius:8px; line-height:1.5}}
  .btns{{display:flex; gap:8px; flex-wrap:wrap; margin:16px 0}} .btn{{padding:10px 14px; border-radius:999px; font-weight:800; font-size:12px; text-decoration:none; border:1px solid var(--blue)}} .btn-orig{{background:var(--blue); color:#fff}} .btn-gh{{background:#fff; color:var(--blue)}}
  .footer{{background:var(--bg-soft); padding:20px 16px; text-align:center; font-size:11px; color:var(--muted); border-top:1px solid var(--line); margin-top:24px}}
</style>
<script>
function imgErro(img){{ if(img.dataset.triedOriginal!=='1'){{img.dataset.triedOriginal='1'; img.src='../prints/original/{esc(png)}'; return;}} img.onerror=null; img.src="data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='220'%3E%3Crect width='100%25' height='100%25' fill='%23F7F8F9' rx='10'/%3E%3Ctext x='50%25' y='46%25' text-anchor='middle' fill='%239AA0A6' font-family='Arial' font-size='12.5' font-weight='700'%3E📸 print em processamento%3C/text%3E%3C/svg%3E";}}
</script>
</head>
<body>
  <div class="hdr"><div><div class="logo">G1 DE IDEIAS DO FABIO<span class="com">.COM</span></div><div class="sub">captura ideias automatica cel Fabio</div></div><a href="../index.html" style="color:var(--blue); font-weight:800; text-decoration:none; font-size:12px; border:1px solid var(--line); padding:6px 10px; border-radius:999px; background:#fff">✕ Fechar</a></div>
  <div class="ticker-wrap"><div class="ticker"><span><span class="dot"></span> AO VIVO • {total} NO AR • SÃO PAULO 26° • JEV 0.3s</span><span>• G1 DE IDEIAS DO FABIO.COM • CAPTURA AUTOMÁTICA</span><span><span class="dot"></span> AO VIVO • {total} NO AR • SÃO PAULO 26° • JEV 0.3s</span><span>• G1 DE IDEIAS DO FABIO.COM • CAPTURA AUTOMÁTICA</span></div></div>
  <div class="crumb"><a href="../index.html">← Voltar</a> • {esc(n['data'])} {esc(n['hora'])} • São Paulo</div>
  <div class="container">
    <h1 class="title">{esc(n['titulo'])}</h1>
    <div class="meta"><strong style="color:var(--blue)">{esc(n['fonte_arroba'])}</strong> • {esc(n['plataforma'])} • por @{n.get('coletor_login','fabio')} • {esc(n['data'])} {esc(n['hora'])} • {", ".join(n['categorias'])} • {esc(n.get('editoria','IA'))}</div>
    <div style="display:flex; gap:6px; flex-wrap:wrap; margin:12px 0">{''.join([f'<span style="background:#1A1D23; color:#fff; font-size:10px; font-weight:800; padding:4px 8px; border-radius:999px">#{esc(c)}</span>' for c in n['categorias']])}</div>
    <div class="resumo">“{esc(n['resumo'])}”</div>
    <div class="imgwrap"><img src="../prints/cropped/{esc(jpg)}" onerror="imgErro(this)" alt="print"><div style="font-size:10px; color:var(--muted); padding:8px 10px; background:var(--bg-soft); font-family:monospace; border-top:1px solid var(--line)">📸 {esc(png)} • 1080×2246 • São Paulo</div></div>
    <div class="ocr"><div style="font-size:11px; font-weight:800; color:var(--red); letter-spacing:0.6px; margin-bottom:8px">TEXTO COMPLETO (OCR)</div><pre>{esc(n['texto_completo'])}</pre></div>
    <div class="btns">
      <a class="btn btn-orig" href="{esc(n['link_original'])}" target="_blank">Ver original ↗</a>
      {'<a class="btn btn-gh" href="'+esc(n['link_github'])+'" target="_blank">GitHub ↗</a>' if n.get('link_github') else ''}
      <a class="btn btn-gh" href="../index.html">← Voltar pro G1</a>
    </div>
  </div>
  <div class="footer">G1 DE IDEIAS DO FABIO.COM • <strong>Fábio Rosestolato</strong> • {esc(n['id'])} • São Paulo</div>
</body>
</html>
"""
        (DETALHE_DIR / f"{n['id']}.html").write_text(detalhe_html, encoding="utf-8")
    print(f"✓ {total} páginas detalhe em {DETALHE_DIR}")

if __name__ == "__main__":
    main()
