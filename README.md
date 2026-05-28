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

## Структура репозитория

```
architecture/   LikeC4-модели PoC и MVP
infra/          Docker Compose (pgvector, LikeC4), SQL-схемы
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
