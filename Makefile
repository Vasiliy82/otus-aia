.PHONY: help install install-backend db-up db-down db-wait db-migrate data-download data-prepare data-load data-all data-clean clean embed-chunks api test-data test-backend test-all arch-build arch-dev arch-dev-poc arch-dev-mvp arch-dev-down arch-poc-export arch-mvp-export arch-export

PYTHON ?= python
ENV_FILE := $(if $(wildcard .env),.env,.env.example)
COMPOSE      ?= docker compose -f infra/docker-compose.yml --env-file $(ENV_FILE)
COMPOSE_ARCH ?= docker compose -f infra/docker-compose.arch.yml

help:
	@echo "Targets:"
	@echo "  install           Install data pipeline dependencies"
	@echo "  install-backend   Install backend (FastAPI, LangGraph, embeddings)"
	@echo "  db-up             Start PostgreSQL (pgvector)"
	@echo "  db-down           Stop PostgreSQL"
	@echo "  db-wait           Wait for PostgreSQL health"
	@echo "  db-migrate        Apply infra/sql migrations"
	@echo "  data-download     Download RFSD from HuggingFace"
	@echo "  data-prepare      Transform RFSD + seed legal/graph + export"
	@echo "  data-load         Load prepared data into PostgreSQL"
	@echo "  data-all          db-up + db-wait + db-migrate + data-prepare + data-load"
	@echo "  embed-chunks      Index chunk embeddings (after data-load)"
	@echo "  api               Run FastAPI on :8000"
	@echo "  data-clean        Remove data/processed/"
	@echo "  clean             Full cleanup (containers, volumes, generated artifacts)"
	@echo "  test-data         Run data pipeline tests"
	@echo "  test-backend      Run backend unit tests"
	@echo "  test-all          test-data + test-backend"
	@echo ""
	@echo "Architecture (LikeC4, image otus-aia/likec4:local):"
	@echo "  arch-build        Build LikeC4 Docker image (first time)"
	@echo "  arch-dev          Start PoC :5173 + MVP :5174 dev servers (background)"
	@echo "  arch-dev-poc      Start PoC dev server only"
	@echo "  arch-dev-mvp      Start MVP dev server only"
	@echo "  arch-dev-down     Stop LikeC4 dev containers"
	@echo "  arch-poc-export   Export PoC PNG (requires arch-dev-poc running)"
	@echo "  arch-mvp-export   Export MVP PNG (requires arch-dev-mvp running)"
	@echo "  arch-export       arch-poc-export + arch-mvp-export"

install:
	$(PYTHON) -m pip install -r requirements.txt

install-backend: install
	$(PYTHON) -m pip install -r requirements-backend.txt

db-up:
	$(COMPOSE) up -d postgres

db-down:
	$(COMPOSE) down

db-wait:
	@echo "Waiting for PostgreSQL..."
	@$(COMPOSE) exec -T postgres sh -c 'until pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB; do sleep 1; done'

db-migrate:
	$(PYTHON) -m scripts.data_prep migrate

data-download:
	$(PYTHON) -m scripts.data_prep download

data-prepare:
	$(PYTHON) -m scripts.data_prep prepare

data-load:
	$(PYTHON) -m scripts.data_prep load

data-all: db-up db-wait db-migrate data-prepare data-load

data-clean:
	rm -rf data/processed/*

clean:
# Останавливаем и удаляем все ресурсы основного compose-проекта (включая тома) и orphan-контейнеры.
	$(COMPOSE) down --volumes --remove-orphans || true
# Останавливаем и удаляем все ресурсы compose-проекта архитектурных диаграмм (включая тома) и orphan-контейнеры.
	$(COMPOSE_ARCH) down --volumes --remove-orphans || true
# Удаляем экспортированные PNG-диаграммы PoC.
	rm -f docs/diagrams/poc/*.png
# Удаляем экспортированные PNG-диаграммы MVP.
	rm -f docs/diagrams/mvp/*.png
# Удаляем подготовленные датасеты/артефакты пайплайна.
	rm -rf data/processed/* data/poc/*
# Удаляем скачанные сырьевые данные, полученные командой make data-download.
	rm -rf data/raw/*
# Удаляем временные кэши тестов и анализаторов.
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
# Удаляем локальные Python-кэши и артефакты сборки пакета.
	rm -rf __pycache__/ build/ *.egg-info/

embed-chunks:
	$(PYTHON) -m backend embed

api:
	$(PYTHON) -m backend serve

test-data:
	$(PYTHON) -m pytest tests/data_prep -q

test-backend:
	$(PYTHON) -m pytest tests/backend -q

test-all: test-data test-backend

# ─── Architecture Diagrams (LikeC4) ──────────────────────────────────────────

arch-build:
	$(COMPOSE_ARCH) build likec4-dev-poc

arch-dev: arch-build
	$(COMPOSE_ARCH) up -d likec4-dev-poc likec4-dev-mvp

arch-dev-poc: arch-build
	$(COMPOSE_ARCH) up -d likec4-dev-poc

arch-dev-mvp: arch-build
	$(COMPOSE_ARCH) up -d likec4-dev-mvp

arch-dev-down:
	$(COMPOSE_ARCH) down

arch-poc-export:
	@if [ -z "$$($(COMPOSE_ARCH) ps -q likec4-dev-poc 2>/dev/null)" ]; then \
	  echo "likec4-dev-poc is not running. Start: make arch-dev-poc (or make arch-dev)"; exit 1; \
	fi
	$(COMPOSE_ARCH) exec -T likec4-dev-poc \
	  likec4 export png --output assets \
	  --server-url http://127.0.0.1:5173/ --timeout 60

arch-mvp-export:
	@if [ -z "$$($(COMPOSE_ARCH) ps -q likec4-dev-mvp 2>/dev/null)" ]; then \
	  echo "likec4-dev-mvp is not running. Start: make arch-dev-mvp (or make arch-dev)"; exit 1; \
	fi
	$(COMPOSE_ARCH) exec -T likec4-dev-mvp \
	  likec4 export png --output assets \
	  --server-url http://127.0.0.1:5173/ --timeout 60

arch-export: arch-poc-export arch-mvp-export
