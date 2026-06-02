# AI-ассистент кредитного аналитика — Secure GraphRAG PoC

Защищённый on-prem GraphRAG-ассистент для нормативно-финансового анализа контрагентов в корпоративном банке.

## Текущий этап: PoC

- Подготовка данных: финансовая отчётность + синтетический юридический срез + граф знаний
- ADR-пакет (000–007) и архитектурная документация
- Backend: LangGraph + FastAPI `/ask` + pgvector + MockLLM

## Быстрый старт

```bash
python3 -m venv .venv
source .venv/bin/activate

cp .env.example .env
make install-backend
make obs-up
make data-all
make embed-chunks
make api
```

`make obs-up` поднимает PostgreSQL (pgvector), Jaeger UI (:16686) и otel-collector (:4317).
`make data-all` применяет миграции, готовит демо-датасет и загружает его в БД.
`make api` загружает embedding-модель сразу при старте (warmup), без ожидания первого `/ask`.

Демо GraphRAG:

```bash
curl -s http://localhost:8000/health

curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"Снижение выручки и политика банка","role":"analyst"}'

curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"Секретная методика оценки риска","role":"risk_manager"}'
```

Observability:

- JSON-логи каждого шага RAG (`rag_step`) в stdout API
- Jaeger UI: http://localhost:16686 — трассировка `POST /ask` и узлов LangGraph
- `trace_id` в ответе `/ask` совпадает с trace ID в Jaeger

Отдельные шаги:

```bash
make db-up
make data-download
make data-prepare
make data-load
make embed-chunks
make test-data
make test-backend
```

Интеграционные тесты backend (живой PostgreSQL + эмбеддинги):

```bash
RUN_INTEGRATION=1 make test-backend
```

## Архитектурные диаграммы (LikeC4)

Исходники: `architecture/poc/` (реализованный PoC), `architecture/mvp/` (целевая архитектура).

```bash
make arch-build       # первый раз: образ с Playwright
make arch-dev         # dev-серверы в фоне: PoC :5173, MVP :5174
make arch-export      # PNG → docs/diagrams/poc|mvp/ (нужны запущенные dev-контейнеры)
make arch-dev-down    # остановить dev-контейнеры
```

Только одна модель:

```bash
make arch-dev-poc
make arch-poc-export  # после arch-dev-poc

make arch-dev-mvp
make arch-mvp-export
```

Просмотр в браузере: http://localhost:5173 (PoC), http://localhost:5174 (MVP).

Экспортированные PNG (после `make arch-export`). MVP — единая платформа `creditPlatform` с подсистемами; 8 целевых представлений + детализирующие:

| View | PoC | MVP |
|------|-----|-----|
| System Landscape (C1) | `docs/diagrams/poc/poc_context.png` | `docs/diagrams/mvp/mvp_landscape.png` |
| Containers / Subsystems (C2) | `docs/diagrams/poc/poc_container.png` | `docs/diagrams/mvp/mvp_container.png` |
| Components (L3) | `docs/diagrams/poc/poc_component.png` | `docs/diagrams/mvp/mvp_component.png` |
| Secure GraphRAG Runtime | — | `docs/diagrams/mvp/mvp_runtime.png` |
| Knowledge Ingestion | — | `docs/diagrams/mvp/mvp_ingestion.png` |
| AI Quality & MLOps | — | `docs/diagrams/mvp/mvp_quality_mlops.png` |
| Delivery & Release (CI/CD) | — | `docs/diagrams/mvp/mvp_cicd.png` |
| Observability & Reliability | — | `docs/diagrams/mvp/mvp_observability.png` |
| Security & Access Control | — | `docs/diagrams/mvp/mvp_security.png` |
| Architecture as Code | — | `docs/diagrams/mvp/mvp_arch_as_code.png` |
| Sequence POST /ask | `docs/diagrams/poc/poc_ask_sequence.png` | `docs/diagrams/mvp/mvp_ask_sequence.png` |
| ER PostgreSQL | `docs/diagrams/poc/poc_er.png` | `docs/diagrams/mvp/mvp_er_postgres.png` |
| ER Qdrant/Neo4j | — | `docs/diagrams/mvp/mvp_er_datastores.png` |
| Deployment | `docs/diagrams/poc/poc_deployment.png` | `docs/diagrams/mvp/mvp_deployment.png` |

## Структура репозитория

```
architecture/   LikeC4-модели PoC и MVP
infra/          Docker Compose (pgvector, Jaeger, otel-collector, LikeC4), SQL-схемы
scripts/        Пайплайн подготовки данных
backend/        LangGraph, FastAPI, pgvector retrieval
docs/           ADR, scope PoC, diagrams/ (PNG из LikeC4)
data/raw/       Сырые данные (gitignore)
data/poc/       Экспорт артефактов после prepare
```

## Документация

- [docs/README.md](docs/README.md) — Project Charter, бизнес-кейс
- [docs/poc/scope.md](docs/poc/scope.md) — границы PoC и ограничения этапа
- [docs/acceptance-criteria.md](docs/acceptance-criteria.md) — критерии приёмки GO/NO-GO
- [docs/adr/](docs/adr/) — журнал архитектурных решений
- [docs/technology-radar.md](docs/technology-radar.md) — стек PoC vs MVP
