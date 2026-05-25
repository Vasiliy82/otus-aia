# Secure GraphRAG PoC — курсовая OTUS AI-Архитектор

Защищённый on-prem GraphRAG-ассистент для нормативно-финансового анализа контрагентов в корпоративном банке.

## Этап PoC (текущий)

- Подготовка данных: RFSD (HuggingFace) + синтетический юридический срез и граф знаний
- ADR-пакет и навигация по документации курсовой
- Backend (LangGraph, FastAPI, Qdrant) — следующий шаг

## Быстрый старт

```bash
cp .env.example .env
make install
make data-all
```

`make data-all` поднимает PostgreSQL, применяет миграции, готовит демо-датасет и загружает его в БД.

Отдельные шаги:

```bash
make db-up
make data-download    # требует HF_TOKEN в .env для приватных зеркал; публичный RFSD часто без токена
make data-prepare
make data-load
make test-data
```

## Структура репозитория

```
infra/          Docker Compose, SQL-схемы
scripts/        Пайплайн подготовки данных
docs/           ADR, scope PoC, индекс лекций
backend/        (заготовка) приложение PoC
data/raw/       Сырые данные (gitignore)
data/poc/       Экспорт артефактов после prepare
```

## Документация

- [docs/README.md](docs/README.md) — оглавление курсовой
- [docs/poc/scope.md](docs/poc/scope.md) — границы PoC
- [docs/adr/](docs/adr/) — Architecture Decision Records

## Лицензия

См. [LICENSE](LICENSE).
