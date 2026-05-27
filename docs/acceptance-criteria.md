# Критерии приёмки PoC

Технический комитет принимает решение GO/NO-GO на основании следующего чеклиста. Каждый пункт должен быть подтверждён демонстрацией или артефактом.

## Обязательные технические критерии

### Безопасность и регуляторика

- [ ] Система работает полностью on-prem — ни один запрос не уходит за пределы корпоративного контура
- [ ] Внешние AI API (OpenAI, Anthropic и аналоги) не используются
- [ ] RBAC на уровне фрагментов: пользователь без прав не получает закрытый фрагмент документа в ответе
- [ ] Разграничение ролей `analyst` / `risk_manager` подтверждено автоматическими тестами

### Архитектура GraphRAG

- [ ] Реализован двухшаговый GraphRAG: векторный поиск + расширение по графу знаний
- [ ] Graph expansion подтверждён тестом: связанный узел добавляется к контексту
- [ ] Ответ без источников блокируется на выходе (output guardrail)

### Оркестратор

- [ ] LangGraph state machine реализован с явным `State`
- [ ] Pipeline проходит через узлы: guardrails → retrieve → graph expand → rbac filter → rerank → generate → output guardrails
- [ ] Узлы покрыты unit-тестами

### Защита от инъекций

- [ ] Prompt injection блокируется на входе (input guardrail)
- [ ] Стоп-паттерны настроены и протестированы

## Архитектурные артефакты

- [ ] C4 Level 1–2 (Context + Container) для PoC
- [ ] Sequence Diagram: User → Guardrails → GraphRAG → LLM
- [ ] ER-диаграмма согласована со схемой БД
- [ ] Deployment Diagram: разделение Control Plane и Data Plane
- [ ] ADR зафиксированы для всех ключевых решений

## Целевая архитектура MVP

- [ ] Представлена архитектура MVP с описанием компонентов
- [ ] Реестр мок-компонентов с плановыми датами замены
- [ ] Capacity planning (CPU/RAM/VRAM/диски)
- [ ] Roadmap PoC → MVP с зависимостями от найма/закупок

## Статус реализации

### Выполнено

- [x] Монорепозиторий: `infra/`, `backend/`, `docs/`
- [x] Подготовка данных: `make data-all`
- [x] ADR-000 … ADR-007
- [x] Граф знаний: PostgreSQL `graph_node` / `graph_edge`
- [x] LangGraph pipeline (`backend/graph/workflow.py`)
- [x] FastAPI `POST /ask`, `GET /health`
- [x] pgvector: миграция `004_embeddings.sql`, `make embed-chunks`
- [x] Guardrails + pytest (`tests/backend/`)

### В работе

- [ ] Диаграммы C4, Sequence, ER, Deployment
- [ ] Интеграционные тесты на CI с `RUN_INTEGRATION=1`
