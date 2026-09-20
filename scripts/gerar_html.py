#!/usr/bin/env python3
"""
G1 DE IDEIAS — gerar_html.py
Gera index.html e detalhe/*.html a partir de data/noticias.json usando templates/globo.html

Uso:
  python3 scripts/gerar_html.py
  python3 -m http.server 8899  # ver em 127.0.0.1:8899
"""
import json
import html
from pathlib import Path

base = Path(__file__).resolve().parent.parent
json_path = base / "data" / "noticias.json"
tpl_path = base / "templates" / "globo.html"
out_index = base / "index.html"
detalhe_dir = base / "detalhe"

# Carrega JSON
data = json.loads(json_path.read_text(encoding="utf-8"))
noticias = data.get("noticias") or data.get("ideias") or []

# Se template globo.html existir, usa como base, senão gera do zero
if tpl_path.exists():
    tpl = tpl_path.read_text(encoding="utf-8")
    print(f"Template: {tpl_path} ({len(tpl)} bytes)")
else:
    print("Template globo.html não encontrado, usando fallback embutido")
    tpl = None

# Gera index com dados (para simplificar, copia globo.html já gerado que tem dados embutidos)
# Neste padrão, o globo.html já é o index final com dados das 10 ideias
# Aqui apenas garante que index.html existe e detalhe/*.html são gerados

# Gera detalhe para cada notícia
detalhe_dir.mkdir(parents=True, exist_ok=True)
for n in noticias:
    detalhe_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(n['titulo'])} — G1 DE IDEIAS</title>
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@700;800&display=swap" rel="stylesheet">
<style>
  *{{margin:0;padding:0;box-sizing:border-box}} body{{font-family:'Open Sans',Arial,sans-serif; background:#fff; color:#111}}
  .hdr{{background:#fff; border-bottom:1px solid #E5E5E5; padding:10px 12px; display:flex; justify-content:space-between; align-items:center; position:sticky; top:0}}
  .logo{{color:#0669DE; font-weight:900; font-size:22px}} .crumb{{padding:10px 12px; font-size:12px; color:#666}} .crumb a{{color:#0669DE; font-weight:700; text-decoration:none}}
  .container{{max-width:640px; margin:0 auto; padding:0 16px}}
  .title{{font-size:26px; font-weight:800; color:#111; line-height:1.2; margin:12px 0}} .meta{{font-size:12px; color:#666; background:#F9F9F9; padding:10px; border:1px solid #E5E5E5; border-radius:6px}}
  .resumo{{font-size:16px; font-weight:600; color:#333; border-left:4px solid #06AA48; padding:10px 12px; background:#F0FDF4; margin:12px 0}}
  .imgwrap{{border:1px solid #E5E5E5; border-radius:8px; overflow:hidden; margin:12px 0}} .imgwrap img{{width:100%; display:block}}
  .ocr{{background:#fff; border:1px solid #E5E5E5; border-radius:8px; padding:12px; margin:12px 0}} .ocr pre{{white-space:pre-wrap; font-family:monospace; font-size:12px; background:#FFFBF5; padding:10px; border:1px dashed #E5E5E5;}}
  .btns{{display:flex; gap:8px; flex-wrap:wrap; margin:12px 0}} .btn{{padding:8px 12px; border-radius:6px; font-weight:800; font-size:12px; text-decoration:none; border:1px solid #0669DE}} .btn-orig{{background:#0669DE; color:white}} .btn-gh{{background:white; color:#0669DE}}
  .footer{{background:#F5F5F5; padding:16px; text-align:center; font-size:11px; color:#666; border-top:1px solid #E5E5E5; margin-top:20px}}
</style>
</head>
<body>
  <div class="hdr"><div class="logo">globo.com <span style="color:#999; font-size:12px; font-weight:700; border-left:1px solid #E5E5E5; padding-left:8px; margin-left:8px">G1 DE IDEIAS</span></div><a href="../index.html" style="color:#0669DE; font-weight:800; text-decoration:none; font-size:12px">✕ Fechar</a></div>
  <div class="crumb"><a href="../index.html">← Voltar</a> • {html.escape(n['data'])} {html.escape(n['hora'])}</div>
  <div class="container">
    <h1 class="title">{html.escape(n['titulo'])}</h1>
    <div class="meta"><strong style="color:#0669DE">{html.escape(n['fonte_arroba'])}</strong> • {html.escape(n['plataforma'])} • por @{n.get('coletor_login','fabio')} • {html.escape(n['data'])} {html.escape(n['hora'])} • {" , ".join(n['categorias'])} • {html.escape(n.get('editoria','IA'))}</div>
    <div style="display:flex; gap:6px; flex-wrap:wrap; margin:10px 0">{''.join([f'<span style="background:#1C1917; color:white; font-size:10px; font-weight:800; padding:3px 6px; border-radius:4px">#{html.escape(c)}</span>' for c in n['categorias']])}</div>
    <div class="resumo">“{html.escape(n['resumo'])}”</div>
    <div class="imgwrap"><img src="../{html.escape(n['imagem'].replace('/root/g1-ideias/','').replace('/storage/emulated/0/Pictures/Screenshots','../prints/original').replace('prints/','prints/cropped/'))}" onerror="this.src='../prints/cropped/{Path(n['imagem']).name.replace('.png','.jpg')}'" alt="print"><div style="font-size:10px; color:#666; padding:6px 8px; background:#F9F9F9; font-family:monospace">📸 {html.escape(Path(n['imagem']).name)} • padrão cropped 1080x2246 • sem barra notificação</div></div>
    <div class="ocr"><div style="font-size:11px; font-weight:800; color:#C4170C; margin-bottom:6px">TEXTO COMPLETO (OCR)</div><pre>{html.escape(n['texto_completo'])}</pre></div>
    <div class="btns">
      <a class="btn btn-orig" href="{html.escape(n['link_original'])}" target="_blank">Ver original ↗</a>
      {'<a class="btn btn-gh" href="'+html.escape(n['link_github'])+'" target="_blank">GitHub ↗</a>' if n.get('link_github') else ''}
      <a class="btn btn-gh" href="../index.html">← Voltar pro G1</a>
    </div>
  </div>
  <div class="footer">G1 DE IDEIAS • <strong>Fábio Rosestolato</strong> • {html.escape(n['id'])} • Tesseract moto g84</div>
</body>
</html>
"""
    out = detalhe_dir / f"{n['id']}.html"
    out.write_text(detalhe_html, encoding="utf-8")

print(f"✓ {len(noticias)} páginas de detalhe em {detalhe_dir}")

# Garante index.html na raiz
if tpl and not out_index.exists():
    out_index.write_text(tpl, encoding="utf-8")
    print(f"✓ index.html criado a partir de templates/globo.html")

# Copia globo.html para index se index não for globo
import shutil
if tpl_path.exists():
    shutil.copy(tpl_path, out_index)
    print(f"✓ index.html atualizado (globo idêntico)")

print("Pronto. Teste: python3 -m http.server 8899 && Chrome 127.0.0.1:8899")
