# AI-ассистент кредитного аналитика — Secure GraphRAG PoC

Защищённый on-prem GraphRAG-ассистент для нормативно-финансового анализа контрагентов в корпоративном банке.

## Текущий этап: PoC

- Подготовка данных: финансовая отчётность + синтетический юридический срез + граф знаний
- ADR-пакет (000–007) и архитектурная документация
- Backend: LangGraph + FastAPI `/ask` + pgvector + MockLLM

## Быстрый старт

```bash
cp .env.example .env
make install-backend
make data-all
make embed-chunks
make api
```

`make data-all` поднимает PostgreSQL (pgvector), применяет миграции, готовит демо-датасет и загружает его в БД.

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

## Структура репозитория

```
infra/          Docker Compose (pgvector), SQL-схемы
scripts/        Пайплайн подготовки данных
backend/        LangGraph, FastAPI, pgvector retrieval
docs/           ADR, scope PoC, архитектурная документация
data/raw/       Сырые данные (gitignore)
data/poc/       Экспорт артефактов после prepare
```

## Документация

- [docs/README.md](docs/README.md) — Project Charter, бизнес-кейс
- [docs/poc/scope.md](docs/poc/scope.md) — границы PoC и ограничения этапа
- [docs/acceptance-criteria.md](docs/acceptance-criteria.md) — критерии приёмки GO/NO-GO
- [docs/adr/](docs/adr/) — журнал архитектурных решений
- [docs/technology-radar.md](docs/technology-radar.md) — стек PoC vs MVP
