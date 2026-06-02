# Технологический радар

Стек проекта по этапам: что используется в PoC, что запланировано для MVP, и когда происходит переход.

## Хранилища данных

| Технология | PoC | MVP | Условие перехода |
|-----------|-----|-----|-----------------|
| PostgreSQL | Основная СУБД (данные, граф, векторы) | OLTP-контур | Остаётся |
| pgvector | Векторный поиск | Заменяется | Найм MLOps-инженера (Q3 2026) |
| Qdrant | — | Векторная БД (cluster) | После найма MLOps + ИБ-аудит |
| Neo4j | — | Graph DB (cluster) | После найма MLOps + обучения DBA |
| MinIO | — | Объектное хранилище (исходные документы) | При внедрении OCR-pipeline |

## AI / ML компоненты

| Технология | PoC | MVP | Условие перехода |
|-----------|-----|-----|-----------------|
| LLM | MockLLMClient | self-hosted Qwen AWQ (vLLM) | После закупки GPU |
| Embedding | bge-m3 / sentence-transformers (CPU, in-process) | модель на Triton Inference Server (GPU) | После закупки GPU + найма MLOps |
| Reranker | Детерминированная формула `vector + 0.5·graph` | RRF + cross-encoder на Triton (GPU) | После найма MLOps |
| Inference serving | in-process (FastAPI) | vLLM (генерация) + Triton (embeddings/reranker), gRPC — ADR-008 | После закупки GPU |
| Слияние результатов | взвешенная сумма скоров | Reciprocal Rank Fusion (RRF) — ADR-009 | После найма MLOps |

## Оркестрация и API

| Технология | PoC | MVP | Условие перехода |
|-----------|-----|-----|-----------------|
| LangGraph | State machine (5–8 узлов) | Расширенный граф | Остаётся |
| FastAPI | 2–3 эндпоинта | Полный I/O-bound API с версионированием | Наращивается |
| Протокол к моделям | in-process вызовы | gRPC к vLLM и Triton — ADR-008 | После закупки GPU |
| Streaming | — | SSE / WebSocket | При разработке UI |

## Безопасность и управление

| Технология | PoC | MVP | Условие перехода |
|-----------|-----|-----|-----------------|
| Secrets | `.env` | HashiCorp Vault | После ИБ-аудита |
| RBAC | `allowed_roles` на чанках (PostgreSQL) | Остаётся + интеграция с IdP | Наращивается |
| Guardrails | regexp + стоп-листы | ML-классификатор инъекций | После найма MLOps |

## Наблюдаемость

| Технология | PoC | MVP | Условие перехода |
|-----------|-----|-----|-----------------|
| Логирование | `trace_id` в JSON-логах | OpenTelemetry + Jaeger | После найма MLOps |
| Метрики | — | Prometheus + Grafana | После найма MLOps |
| Алертинг | — | PagerDuty / AlertManager | При выходе в production |

## Инфраструктура

| Технология | PoC | MVP | Условие перехода |
|-----------|-----|-----|-----------------|
| Docker Compose | Локальный стенд | CI/CD + staging | Наращивается |
| Kubernetes | — | Целевая среда выполнения | После ИБ-аудита |
| GPU-серверы | — | Минимум 1× A100/H100 (24+ ГБ VRAM) | После закупки (бюджет Q1 2027) |
