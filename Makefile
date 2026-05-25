.PHONY: help install db-up db-down db-wait db-migrate data-download data-prepare data-load data-all data-clean test-data

PYTHON ?= python
ENV_FILE := $(if $(wildcard .env),.env,.env.example)
COMPOSE ?= docker compose -f infra/docker-compose.yml --env-file $(ENV_FILE)

help:
	@echo "Targets:"
	@echo "  install        Install Python dependencies"
	@echo "  db-up          Start PostgreSQL"
	@echo "  db-down        Stop PostgreSQL"
	@echo "  db-wait        Wait for PostgreSQL health"
	@echo "  db-migrate     Apply infra/sql migrations"
	@echo "  data-download  Download RFSD from HuggingFace"
	@echo "  data-prepare   Transform RFSD + seed legal/graph + export"
	@echo "  data-load      Load prepared data into PostgreSQL"
	@echo "  data-all       db-up + db-wait + db-migrate + data-prepare + data-load"
	@echo "  data-clean     Remove data/processed/"
	@echo "  test-data      Run data pipeline tests"

install:
	$(PYTHON) -m pip install -r requirements.txt

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

test-data:
	$(PYTHON) -m pytest tests/data_prep -q
