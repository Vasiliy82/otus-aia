.PHONY: help install install-backend db-up db-down db-wait db-migrate data-download data-prepare data-load data-all data-clean embed-chunks api test-data test-backend test-all

PYTHON ?= python
ENV_FILE := $(if $(wildcard .env),.env,.env.example)
COMPOSE ?= docker compose -f infra/docker-compose.yml --env-file $(ENV_FILE)

help:
	@echo "Targets:"
	@echo "  install          Install data pipeline dependencies"
	@echo "  install-backend  Install backend (FastAPI, LangGraph, embeddings)"
	@echo "  db-up            Start PostgreSQL (pgvector)"
	@echo "  db-down          Stop PostgreSQL"
	@echo "  db-wait          Wait for PostgreSQL health"
	@echo "  db-migrate       Apply infra/sql migrations"
	@echo "  data-download    Download RFSD from HuggingFace"
	@echo "  data-prepare     Transform RFSD + seed legal/graph + export"
	@echo "  data-load        Load prepared data into PostgreSQL"
	@echo "  data-all         db-up + db-wait + db-migrate + data-prepare + data-load"
	@echo "  embed-chunks     Index chunk embeddings (after data-load)"
	@echo "  api              Run FastAPI on :8000"
	@echo "  data-clean       Remove data/processed/"
	@echo "  test-data        Run data pipeline tests"
	@echo "  test-backend     Run backend unit tests"
	@echo "  test-all         test-data + test-backend"

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

embed-chunks:
	$(PYTHON) -m backend embed

api:
	$(PYTHON) -m backend serve

test-data:
	$(PYTHON) -m pytest tests/data_prep -q

test-backend:
	$(PYTHON) -m pytest tests/backend -q

test-all: test-data test-backend
