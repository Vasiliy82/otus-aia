.PHONY: help install install-backend db-up db-down db-wait db-migrate data-download data-prepare data-load data-all data-clean embed-chunks api test-data test-backend test-all arch-build arch-poc-site arch-poc-export arch-mvp-site arch-mvp-export arch-poc arch-mvp arch-all arch-dev-poc arch-dev-mvp

PYTHON ?= python
ENV_FILE := $(if $(wildcard .env),.env,.env.example)
COMPOSE      ?= docker compose -f infra/docker-compose.yml --env-file $(ENV_FILE)
COMPOSE_ARCH ?= docker compose -f infra/docker-compose.arch.yml
ARCH_RUN     = $(COMPOSE_ARCH) run --rm

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
	@echo "  test-data         Run data pipeline tests"
	@echo "  test-backend      Run backend unit tests"
	@echo "  test-all          test-data + test-backend"
	@echo ""
	@echo "Architecture (LikeC4, custom image otus-aia/likec4:local):"
	@echo "  arch-build        Build LikeC4 Docker image (required once)"
	@echo "  arch-poc-site     Build static website for PoC  → dist/arch/poc/"
	@echo "  arch-poc-export   Export PoC diagrams to PNG    → docs/diagrams/poc/"
	@echo "  arch-mvp-site     Build static website for MVP  → dist/arch/mvp/"
	@echo "  arch-mvp-export   Export MVP diagrams to PNG    → docs/diagrams/mvp/"
	@echo "  arch-poc          arch-poc-site + arch-poc-export"
	@echo "  arch-mvp          arch-mvp-site + arch-mvp-export"
	@echo "  arch-all          arch-poc + arch-mvp"
	@echo "  arch-dev-poc      Live preview PoC on :5173"
	@echo "  arch-dev-mvp      Live preview MVP on :5174"

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

# ─── Architecture Diagrams (LikeC4) ──────────────────────────────────────────

arch-build:
	$(COMPOSE_ARCH) build likec4

arch-poc-site: arch-build
	$(ARCH_RUN) -v $(CURDIR)/architecture/poc:/data \
	  -v $(CURDIR)/dist/arch/poc:/data/dist \
	  likec4 build -o dist --base "./"

arch-poc-export: arch-build
	$(ARCH_RUN) -v $(CURDIR)/architecture/poc:/data \
	  -v $(CURDIR)/docs/diagrams/poc:/data/assets \
	  likec4 export png --output assets

arch-mvp-site: arch-build
	$(ARCH_RUN) -v $(CURDIR)/architecture/mvp:/data \
	  -v $(CURDIR)/dist/arch/mvp:/data/dist \
	  likec4 build -o dist --base "./"

arch-mvp-export: arch-build
	$(ARCH_RUN) -v $(CURDIR)/architecture/mvp:/data \
	  -v $(CURDIR)/docs/diagrams/mvp:/data/assets \
	  likec4 export png --output assets

arch-poc: arch-poc-site arch-poc-export

arch-mvp: arch-mvp-site arch-mvp-export

arch-all: arch-poc arch-mvp

arch-dev-poc: arch-build
	$(COMPOSE_ARCH) --profile arch-dev up likec4-dev-poc

arch-dev-mvp: arch-build
	$(COMPOSE_ARCH) --profile arch-dev up likec4-dev-mvp
