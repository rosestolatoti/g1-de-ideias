# G1 DE IDEIAS — Dockerfile profissional
FROM python:3.13-slim

LABEL maintainer="Fábio Rosestolato <rosestolatoti@gmail.com>"
LABEL description="G1 DE IDEIAS - globo.com de ideias com JEV + OCR"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=5000

WORKDIR /app

# Sistema: tesseract + por + eng + fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-por tesseract-ocr-eng \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . .

# Gera site estático no build (se JSON existir)
RUN python scripts/generate_site.py || echo "generate_site skip (sem JSON)"
RUN python scripts/sync_sqlite.py || echo "sync skip"

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health').read()" || exit 1

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
