# AI-ассистент кредитного аналитика — Secure GraphRAG PoC

Защищённый on-prem GraphRAG-ассистент для нормативно-финансового анализа контрагентов в корпоративном банке.

## Текущий этап: PoC

- Подготовка данных: финансовая отчётность + синтетический юридический срез + граф знаний
- ADR-пакет (000–007) и архитектурная документация
- Backend (LangGraph, FastAPI, pgvector) — следующий шаг

## Быстрый старт

```bash
cp .env.example .env
make install
make data-all
```

`make data-all` поднимает PostgreSQL, применяет миграции, подготавливает демо-датасет и загружает его в БД.

Отдельные шаги:

```bash
make db-up
make data-download
make data-prepare
make data-load
make test-data
```

## Структура репозитория

```
infra/          Docker Compose, SQL-схемы
scripts/        Пайплайн подготовки данных
docs/           ADR, scope PoC, архитектурная документация
backend/        Приложение PoC (в разработке)
data/raw/       Сырые данные (gitignore)
data/poc/       Экспорт артефактов после prepare
```

## Документация

- [docs/README.md](docs/README.md) — Project Charter, бизнес-кейс
- [docs/poc/scope.md](docs/poc/scope.md) — границы PoC и ограничения этапа
- [docs/acceptance-criteria.md](docs/acceptance-criteria.md) — критерии приёмки GO/NO-GO
- [docs/adr/](docs/adr/) — журнал архитектурных решений
- [docs/technology-radar.md](docs/technology-radar.md) — стек PoC vs MVP
