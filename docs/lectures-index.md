# Индекс лекций `local-docs/`

Краткий указатель: **когда читать** файл на этапах PoC → MVP → сдача. Полные конспекты — в `local-docs/` (локально, в gitignore).

| № | Файл | Когда | Суть для проекта |
|---|------|-------|------------------|
| 01 | Пресейл, контракты и работа с требованиями | MVP doc | PoC как оплачиваемый этап, GO/NO-GO, ROI |
| 02 | Проектирование и оценка | MVP doc | WBS, риски, смета, план работ |
| 03 | Стратегия поставки PoC → Production | **PoC** | Границы PoC, техдолг, критерии выхода |
| 04 | HLD, C4 Model | **PoC diagrams** | Context + Container для PoC |
| 05 | LLD | MVP | Компоненты агента, интерфейсы |
| 06 | RAG и продвинутые вариации | **PoC backend** | GraphRAG, chunking, hybrid search |
| 07 | AI-агенты и Multi-Agent | **PoC backend** | LangGraph, ReAct, state |
| 08 | ADR | **сейчас** | Формат ADR, ADL, trade-off |
| 09 | CTO Challenge | сдача | Защита решений, ответы на «почему не X» |
| 10 | Техдолг и архнадзор | MVP | Связь с ADR-007, эволюция |
| 11 | Интеграции | MVP | API Gateway, события, контракты |
| 12 | Архитектура данных | **сейчас** | Ingestion, OLTP/OLAP, качество данных |
| 13 | Качество и тестирование GenAI | PoC tests | eval, regression, judge (опционально) |
| 14 | Security by Design | **PoC** | Guardrails, RBAC, zero trust |
| 15 | Observability | MVP | OTel, метрики, trace на агента |
| 16 | Sizing приложений и данных | MVP doc | CPU/RAM/диски |
| 17 | Sizing и оптимизация LLM | MVP doc | VRAM, квантование AWQ/GGUF |
| 18 | IaC и CI/CD | MVP | compose → pipeline deploy |
| 19 | MLOps-конвейеры | MVP | версии моделей, drift |
| 20 | Стратегии deployment | MVP | canary, shadow, A/B |
| 21 | HA и DR | MVP | кластеры, RPO/RTO |
| 22 | Serverless vs Kubernetes | опционально | выбор для AI workloads |
| 23 | EDA для AI | опционально | асинхронный ingestion |
| 24 | High-Load inference | опционально | latency, батчинг |
| 25 | Гибрид и мультиоблако | опционально | не для air-gapped MVP |
| 26 | Multi-tenancy SaaS | опционально | если SaaS-угл |
| 27 | Federated Learning | опционально | privacy-preserving |
| 28 | FinOps | MVP | TCO self-hosted vs cloud |
| 29 | Технологический радар | roadmap | эволюция стека |
| 30 | Ethical AI / Governance | ADR | этика, bias, политики |
| 31 | API as product | PoC API | контракт FastAPI, версии |
| 32–33 | Методические указания | **всегда** | Критерии сдачи, monorepo, чеклист |

## Рекомендуемый порядок чтения (PoC)

1. 32–33, 08 — критерии и ADR  
2. 03, 12, 14 — границы PoC, данные, безопасность  
3. 06, 07 — RAG и LangGraph перед кодом backend  
4. 04 — диаграммы после фиксации data model (`infra/sql/`)

## Следующий пакет (backend)

- 06, 07, 14, 31 — реализация агента и API  
- 04, 05 — обновить диаграммы под код  
- 15, 17 — observability и sizing для MVP-главы
