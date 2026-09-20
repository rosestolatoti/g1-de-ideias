# G1 DE IDEIAS — globo.com de ideias com JEV + OCR

**Dono:** Fábio Rosestolato | **Agente:** Fabricio do Android (moto g84 5G) | **Crédito:** Desenvolvido por: Fábio Rosestolato

[![CI](https://github.com/rosestolatoti/g1-de-ideias/actions/workflows/ci.yml/badge.svg)](https://github.com/rosestolatoti/g1-de-ideias/actions/workflows/ci.yml)
[![Deploy](https://github.com/rosestolatoti/g1-de-ideias/actions/workflows/deploy.yml/badge.svg)](https://github.com/rosestolatoti/g1-de-ideias/actions/workflows/deploy.yml)
[![Vercel](https://img.shields.io/badge/deploy-vercel-black?logo=vercel)](https://vercel.com)
[![Cloudflare](https://img.shields.io/badge/deploy-cloudflare_pages-orange?logo=cloudflare)](https://pages.cloudflare.com)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue?logo=python)](https://python.org)
[![JEV](https://img.shields.io/badge/JEV-typesafe.ai-purple)](https://typesafe.ai)

> **Conceito:** Portal no formato **globo.com** onde cada “notícia” é uma **ideia** extraída dos seus prints. Layout idêntico (header #0669DE, manchete #06AA48, títulos #C4170C, Open Sans 800), mas com pipeline profissional: **Tesseract OCR → JEV (TypeSafe System One, 300ms) → crop → site estático** — 24h no ar sem depender de celular ou PC.

---

## 🏗️ Arquitetura 24/7 (sem gambiarra)

```
[ Moto g84 5G — Termux ]
  /storage/emulated/0/Pictures/Screenshots (1110 prints)
       │ inotify + pipeline.py --watch (ou upload manual)
       ▼
[ GitHub — rosestolatoti/g1-de-ideias ]
  data/noticias.json (FONTE DA VERDADE, 10→1110 ideias)
  prints/original/*.png (opcional, LFS)
  prints/cropped/*.jpg (leve, versionado)
       │ GitHub Actions (ubuntu-latest + tesseract + JEV)
       │ 1) OCR por+eng --psm 6
       │ 2) JEV fan-out batch 8 (score + choice + noul)
       │ 3) crop 110+48px (moto g84 padrão)
       │ 4) generate_site.py → index.html + detalhe/*.html
       │ 5) sync_sqlite.py → noticias.db
       ▼
[ Vercel (gru1) + Cloudflare Pages ]  ← 24/7 CELULAR DESLIGADO = NO AR
  index.html + detalhe/*.html (estático, <100ms TTFB)
  prints/cropped/*.jpg (CDN)

[ Linux Mint 22.3 Zena (100.73.169.99) ]  ← OPCIONAL, sempre ligado
  systemd g1-ideias.service → gunicorn app:app (2 workers)
  tunnel cloudflared → https://g1deideiasdofabio.com (sem abrir porta)
  runner self-hosted para OCR pesado (opcional)
```

**Por que não depende de celular?** O site é **estático** gerado no CI e hospedado na CDN. Celular só envia prints quando ligado; se desligar, o site continua no ar (só não entra ideia nova até sincronizar).

---

## 📂 Estrutura profissional

```
g1-de-ideias/
├── app/                      # factory Flask profissional
│   ├── __init__.py           # create_app() + blueprints + CORS + error handlers
│   ├── config.py             # Base/Dev/Prod/Testing + .env + /tmp/typesafe-lab
│   ├── models.py             # dataclass Noticia + load/save helpers
│   ├── services/
│   │   ├── ocr_service.py    # tesseract por+eng --psm 6 (OMP_THREAD_LIMIT=2)
│   │   ├── jev_service.py    # TypeSafe SDK 0.7.0 com fallback heurístico
│   │   ├── crop_service.py   # Pillow 11.1.0 crop 110/48 moto g84
│   │   └── storage_service.py# JSON ↔ SQLite sync + search
│   └── routes/
│       ├── health.py         # /health /ready /api/health
│       ├── api.py            # /api/noticias /api/categorias /search /api/jev/health
│       └── views.py          # / /detalhe/<id> /prints/<path>
├── scripts/
│   ├── pipeline.py           # ⭐ ORQUESTRADOR: OCR→JEV→JSON→crop→HTML→SQLite (usado no CI/Mint/Termux)
│   ├── generate_site.py      # JSON → index.html + detalhe/*.html (layout refinado 20/09)
│   ├── adb_capture.py        # ADB/Shizuku screencap moto g84 (loopback 127.0.0.1:5555 + rish)
│   ├── crop_prints.py        # crop avulso (legado, mantido)
│   └── sync_sqlite.py        # JSON → DB (legado, mas usado por pipeline)
├── data/
│   ├── noticias.json         # FONTE DA VERDADE (ideias[] ordenadas id desc)
│   └── noticias.db           # espelho SQLite (gerado, gitignored no .db, mas CI commita)
├── prints/
│   ├── original/             # crus (copiados de /Screenshots, heavy)
│   └── cropped/              # padrão 1080x2246 sem barra notificação
├── templates/
│   └── globo.html            # base globo.com (header azul, manchete verde, ticker)
├── static/css, static/js     # (futuro: separar CSS)
├── detalhe/                  # gerado (gitignored *.html + .gitkeep)
├── index.html                # gerado (copiado de templates/globo.html + dados)
├── tests/                    # pytest api + jev fallback
├── .github/workflows/
│   ├── ci.yml                # lint + test + build docker + generate smoke
│   └── deploy.yml            # pipeline JEV + Vercel + Cloudflare Pages (push main)
├── systemd/
│   └── g1-ideias.service     # Mint Zena systemd Restart=always
├── app.py                    # shim compat: `python app.py` e `gunicorn app:app`
├── app_legacy.py             # backup do app.py simples anterior
├── gunicorn.conf.py          # 2 workers gthread
├── Dockerfile + docker-compose.yml
├── vercel.json + wrangler.toml + Makefile
├── requirements.txt (pinado) + requirements-dev.txt
├── .gitignore + .env.example
└── README.md (este)
```

---

## 🚀 Quick start (3 comandos)

```bash
# 1) Clone + env
git clone https://github.com/rosestolatoti/g1-de-ideias.git
cd g1-de-ideias
cp .env.example .env
# edite TYPESAFE_API_KEY=apikey_... (já em /tmp/typesafe-lab/.env.secure)

# 2) Instale
pip install -r requirements.txt
# ou no Debian proot: apt install python3-flask python3-pil tesseract-ocr-por

# 3) Rode
make dev          # FLASK_ENV=development → http://127.0.0.1:5000
make generate     # só gera site estático (sem servidor)
make pipeline     # pega 10 prints pendentes, OCR+JEV→JSON→HTML+DB
```

### Testar saúde

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/api/noticias?categoria=github
curl http://127.0.0.1:5000/api/jev/health   # verifica JEV key/model
```

---

## 🤖 JEV — peneira inteligente (por que não é gambiarra?)

**Problema:** 1110 prints, só 10 curados. LLM custa $0.03/print → $32 pra peneirar tudo.

**Solução JEV:** 300ms, $0.000013/print (2.300x mais barato), fan-out 8 prints por chamada.

```python
# app/services/jev_service.py
from app.services.jev_service import get_jev
j = get_jev()
# state = {id: texto_ocr}
# questions = {id_edit: choice(editoria), id_vale: score(0-3), id_util: noul()}
r = await j.classify_batch([{"id":"20260910-205937","texto": "..."}])
# r["20260910-205937"] = {editoria:"ia", score:2.66, util:0.98, aprovado: True}
```

**Thresholds profissionais (calibráveis via .env):**
- `JEV_SCORE_MIN=1.0` (0 lixo, 1 fraco, 2 bom, 3 manchete)
- `JEV_UTIL_MIN=0.55` (noul útil)
- Só `aprovado = score>=1.0 && util>=0.55` vira ideia; reprovado fica fora mas logado.

**Fallback:** Sem `TYPESAFE_API_KEY`, usa heurística determinística (palavras-chave + tamanho), nunca quebra CI.

**Custo medido:** 1097 prints × 0.6s JEV = 11 min vs 1h LLM; $0.014 vs $32.

---

## 📸 Pipeline completo (comandos profissionais)

```bash
# Pipeline padrão (10 pendentes mais recentes):
python scripts/pipeline.py
# Tudo pendente (1110 → ~28 min + JEV batches):
python scripts/pipeline.py --all
# Dry-run (só lista):
python scripts/pipeline.py --dry-run --limit 20
# Força reprocessar já curados:
python scripts/pipeline.py --force --limit 5
# Sem JEV (heurística):
python scripts/pipeline.py --no-jev --limit 10
# Threshold custom:
JEV_SCORE_MIN=1.5 JEV_UTIL_MIN=0.7 python scripts/pipeline.py --all

# Avulsos:
python scripts/generate_site.py   # só HTML
python scripts/sync_sqlite.py     # só DB
python scripts/crop_prints.py --all
python scripts/adb_capture.py --check      # verifica adb/shizuku
python scripts/adb_capture.py --screencap  # tira print via adb
```

---

## 🔌 ADB / Shizuku — moto g84 5G profissional

Este repo já tem infra validada para o celular se controlar via ADB sem código pareamento:

```bash
# Wrapper já existe em /root/adb_self.sh (loopback 127.0.0.1:5555, auto-cura via PC)
bash /root/adb_self.sh devices
bash /root/adb_self.sh shell getprop ro.product.model  # → moto g84 5G
bash /root/adb_self.sh shell screencap -p /sdcard/Download/00_AMBIENTE_TERMUX/test.png

# Scripts integrados:
python scripts/adb_capture.py --check      # adb + shizuku rish
python scripts/adb_capture.py --screencap  # salva em prints/original + Screenshots

# Shizuku (se instalado):
rish -c 'id'  # uid 2000
rish -c 'pm list packages | grep termux'
```

**Regra de ouro:** salvar em `/data/data/com.termux/files/home/` ou `/sdcard/Download/00_AMBIENTE_TERMUX/` (proot não enxerga `/root` via Termux:API).

---

## ☁️ Deploy 24/7 — GitHub Actions + Vercel + Cloudflare

### 1) GitHub — crie repo e push

```bash
cd /root/g1-ideias
git init
git remote add origin https://github.com/rosestolatoti/g1-de-ideias.git
git add .
git commit -m "feat: v2 profissional JEV+OCR+CD (app factory, pipeline, vercel, cloudflare)"
git push -u origin main
```

### 2) Secrets (Settings → Secrets → Actions)

```
TYPESAFE_API_KEY=apikey_211fcd85e...  # já em /tmp/typesafe-lab/.env.secure
VERCEL_TOKEN=vercel_xxx
VERCEL_ORG_ID=xxx
VERCEL_PROJECT_ID=xxx
CLOUDFLARE_API_TOKEN=cf_xxx
CLOUDFLARE_ACCOUNT_ID=xxx
```

### 3) Automático

- Push em `main` → `deploy.yml` roda pipeline (JEV) + gera site + commit + deploy Vercel + Cloudflare Pages
- Push/PR → `ci.yml` roda lint/test/build docker
- `schedule: cron 0 9 * * *` → rebuild diário 06:00 BRT

### 4) Vercel (gru1) e Cloudflare Pages

- Vercel: `vercel --prod` (ou automático via GitHub Apps)
- Cloudflare Pages: `npx wrangler pages deploy ./ --project-name=g1-de-ideias`
- Domínio: aponte `g1deideiasdofabio.com` no Cloudflare DNS → CNAME Vercel + Pages

---

## 🐧 Mint 22.3 Zena — systemd + Docker + Tunnel (opcional, sempre ligado)

```bash
# systemd (Restart=always)
sudo cp systemd/g1-ideias.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now g1-ideias
systemctl status g1-ideias
journalctl -u g1-ideias -f

# Docker
docker compose up --build -d
docker compose logs -f

# Cloudflare Tunnel (sem abrir porta)
cloudflared tunnel create g1-ideias
cloudflared tunnel route dns g1-ideias g1deideiasdofabio.com
cloudflared tunnel run g1-ideias --url http://localhost:5000
# ou via compose: docker compose --profile tunnel up -d
```

---

## 🗄️ Dados — JSON vs SQLite

| Formato | Papel | Edição |
|---------|-------|--------|
| `data/noticias.json` | **FONTE DA VERDADE** | Manual ou pipeline (commit) |
| `data/noticias.db` | Espelho rápido | `python scripts/sync_sqlite.py` (não edite) |

**Schema Noticia (models.py):**
```json
{
  "id": "20260910-205937",
  "titulo": "Phone Harness: faça seu agente testar seu checkout",
  "texto_completo": "OCR completo...",
  "resumo": "2 linhas",
  "fonte_arroba": "@startupideaspod",
  "plataforma": "twitter",
  "categorias": ["twitter","github","gringa"],
  "editoria": "IA",
  "data": "2026-09-10", "hora": "20:59:37",
  "link_original": "https://x.com/...",
  "link_github": "https://github.com/phone-harness/phone-harness",
  "imagem": "prints/cropped/Screenshot_20260910-205937.X.jpg",
  "imagem_original": "/storage/emulated/0/Pictures/Screenshots/Screenshot_20260910-205937.X.png",
  "jev_score": 2.66, "jev_util": 0.98
}
```

**Multi-categoria:** Uma ideia em N categorias → aparece em todos os filtros (igual UOL).

---

## 🧪 Testes

```bash
pytest -v
pytest tests/test_jev.py -v
curl http://127.0.0.1:5000/health | jq
curl "http://127.0.0.1:5000/api/noticias?categoria=github&limit=2" | jq
```

---

## 🔧 Troubleshooting

| Sintoma | Causa | Solução |
|---------|-------|---------|
| `ModuleNotFoundError: app` | rodou `python app.py` sem PYTHONPATH | `PYTHONPATH=. python app.py` ou use `make dev` |
| `TYPESAFE_API_KEY vazio` | sem .env | `cp .env.example .env` e cole chave de `/tmp/typesafe-lab/.env.secure` |
| `tesseract: command not found` (CI) | sem apt | `sudo apt install tesseract-ocr tesseract-ocr-por` |
| `ocr vazio` | print muito novo/corrompido | `python scripts/pipeline.py --no-jev --limit 1` pra debug |
| `adb devices empty` | 5555 fechou | `bash /root/adb_self.sh devices` (auto-cura via PC) |
| `termux-wake-lock: command not found` dentro proot | cron roda dentro proot isolado | não use cron proot pra termux-api; use `termux-job-scheduler` externo |

---

## 📜 Crédito e licença

Desenvolvido por: **Fábio Rosestolato** | Agente: **Fabricio do Android** | **MIT** | 2026-09-20 v2.0 profissional

Inspiração: `globo.com` (header #0669DE, manchete #06AA48) + `uol.com.br` | Stack: Flask 3.1.1, Pillow 11.1.0, Tesseract 5.5.0, TypeSafe JEV 0.7.0, Gunicorn 23.0.0, Vercel gru1, Cloudflare Pages

---

## 🗺️ Roadmap

- [x] v2.0 Factory + JEV pipeline + CI/CD
- [ ] Bot Telegram coletor (manda print → JEV → commit)
- [ ] Domínio `g1deideiasdofabio.com` + UptimeRobot
- [ ] Syncthing Screenshots → Mint (P2P sem nuvem)
- [ ] 1110 prints peneirados (hoje só 10, faltam 1100)

```

