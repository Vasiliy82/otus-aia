# Целевая архитектура MVP

Раздел описывает production-архитектуру системы после успешного GO-решения по PoC. Код MVP **не реализуется** до завершения PoC-валидации и принятия инвестиционного решения.

## Состав архитектурных артефактов (в разработке)

- C4 Level 1–3: Context, Container, Component
- Deployment Diagram: DMZ / Control Plane / Data Plane / GPU Zone / Observability
- Sequence Diagram: полный запрос от пользователя до ответа
- ER-диаграмма production: Neo4j cluster, Qdrant cluster, PostgreSQL, MinIO
- Capacity planning: CPU / RAM / VRAM / дисковое пространство
- Roadmap: PoC → MVP → Production с зависимостями от найма и закупок

## Ключевые отличия MVP от PoC

| Компонент | PoC | MVP |
|-----------|-----|-----|
| LLM | MockLLMClient | self-hosted Qwen (vLLM, 24+ ГБ VRAM) |
| Graph store | PostgreSQL | Neo4j cluster |
| Векторная БД | pgvector | Qdrant cluster |
| Secrets | `.env` | HashiCorp Vault |
| Observability | JSON-логи с `trace_id` | OpenTelemetry + Jaeger + Prometheus |
| Юридический корпус | синтетика | реальная нормативная база |

## Условия перехода к MVP

1. GO-решение Технического комитета по итогам PoC.
2. Закупка GPU-сервера (бюджет Q1 2027).
3. Найм MLOps-инженера (запланирован Q3 2026).
4. Прохождение ИБ-аудита архитектуры.
5. Согласование юридического корпуса с Дирекцией права.

Связанный ADR: [007-poc-mocks-and-mvp-replacement.md](../adr/007-poc-mocks-and-mvp-replacement.md).
