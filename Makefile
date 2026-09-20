# Makefile — G1 DE IDEIAS
.PHONY: help install dev prod pipeline crop generate sync test lint docker vercel

help:
	@echo "G1 DE IDEIAS — comandos:"
	@echo "  make install   - pip install -r requirements.txt"
	@echo "  make dev       - flask dev 127.0.0.1:5000"
	@echo "  make prod      - gunicorn 0.0.0.0:5000"
	@echo "  make pipeline  - OCR+JEV+JSON+crop+HTML+SQLite (10 pendentes)"
	@echo "  make pipeline-all - tudo pendente (--all)"
	@echo "  make generate  - só gera index+detalhe"
	@echo "  make sync      - só sync JSON->DB"
	@echo "  make test      - pytest"
	@echo "  make docker    - docker compose up --build"
	@echo "  make vercel    - deploy vercel --prod"

install:
	pip install -r requirements.txt

dev:
	FLASK_ENV=development python app.py

prod:
	gunicorn -c gunicorn.conf.py app:app

pipeline:
	python scripts/pipeline.py

pipeline-all:
	python scripts/pipeline.py --all

crop:
	python scripts/crop_prints.py --all

generate:
	python scripts/generate_site.py

sync:
	python scripts/sync_sqlite.py

test:
	pytest -v

lint:
	ruff check . || true

docker:
	docker compose up --build -d && docker compose logs -f

vercel:
	vercel --prod
