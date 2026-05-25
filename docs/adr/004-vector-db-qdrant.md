# ADR-004: Qdrant как векторная БД

## Status

Proposed

## Context

Нужна self-hosted vector DB для эмбеддингов чанков с фильтрацией по метаданным (роль, document_id). Код загрузки в Qdrant — следующий шаг после data prep; решение нужно зафиксировать до backend.

## Alternatives

### 1. Qdrant

- Плюсы: зрелый Docker-образ; хорошая фильтрация payload; популярен в RU enterprise PoC
- Минусы: отдельный кластер в MVP

### 2. Milvus

- Плюсы: масштабирование, зрелый OSS
- Минусы: тяжелее эксплуатация на solo-PoC

### 3. pgvector в PostgreSQL

- Плюсы: один storage на PoC
- Минусы: слабее story про разделение Data Plane; нагрузка на OLTP-контур

## Decision

**Предлагается:** **Qdrant** (local Docker на PoC, cluster на MVP). Эмбеддинги — отдельный self-hosted embedding service (sentence-transformers / bge-m3).

## Consequences

**Плюсы:** alignment с методичкой и шаблоном FastAPI+LangGraph.

**Минусы:** ещё один сервис в compose.

**Риски:** рассинхрон id чанков PG ↔ Qdrant — mitigated единым `chunk_id` / external_id в metadata.

## Compliance & Security

Payload не должен содержать секреты вне RBAC-фильтра; роли дублируются в payload для pre-filter.
