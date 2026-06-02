# ADR-005: LangGraph как оркестратор агента

## Status

Accepted

## Context

Служба безопасности банка требует аудируемости каждого шага обработки запроса: система должна фиксировать, через какие этапы прошёл запрос, где была применена фильтрация RBAC и где сработали guardrails. Линейный скрипт не обеспечивает ни явного состояния, ни структурированного аудитного следа, ни управляемого ветвления (blocked / ok).

Требования к оркестратору:
- явный `State` — текущий контекст обработки запроса;
- ветвление: guardrails → blocked (отказ) или ok (продолжение);
- возможность воспроизвести последовательность шагов по `trace_id`;
- тестируемость каждого узла в изоляции.

## Alternatives

### 1. Линейный Python-скрипт

- Плюсы: минимум зависимостей, прост в понимании
- Минусы: нет явного состояния; невозможен аудит шагов, требуемый СБ; нет управляемого ветвления; сложно тестировать отдельные этапы

### 2. LangGraph

- Плюсы: state machine с явным `State`; checkpointing; узлы независимо тестируемы; sequence diagram 1:1 с кодом
- Минусы: зависимость от releases LangGraph; learning curve для команды

### 3. LlamaIndex Workflows / custom asyncio FSM

- Плюсы: независимость от LangGraph-экосистемы
- Минусы: значительно больше boilerplate; нет готового checkpointing; сложнее onboarding новых разработчиков

## Decision

Использовать **LangGraph** с явным `State` и узлами:

- `input_guardrails` → (blocked → `blocked_end` | ok → `classify_intent`)
- `classify_intent` → маршрутизация по `intent`:
  - `risk_analysis` → `financial_lookup` → `vector_retrieve`
  - `compliance` / `general` → `vector_retrieve` (для compliance в state задаётся `search_scope=compliance`)
- общая цепочка: `vector_retrieve` → `graph_expand` → `rrf_fusion` → `rbac_filter` → `rerank` → `generate_answer` → `output_guardrails`

Узел `rrf_fusion` сливает dense- и graph-списки через Reciprocal Rank Fusion; узел `rerank` выполняет cross-encoder reranking top-N (ADR-009). На MVP инференс embeddings и cross-encoder вынесен из процесса FastAPI в Triton по gRPC (ADR-008) — узлы графа остаются I/O-bound.

Каждый узел логирует свой результат с `trace_id`. Ветвление реализовано через conditional edges LangGraph (`_blocked_route`, `_intent_route`).

## Consequences

**Плюсы:** аудитный след удовлетворяет требованиям СБ; sequence diagram читается прямо из кода; узлы покрываются unit-тестами; checkpointing позволяет воспроизвести запрос по `trace_id`.

**Минусы:** зависимость от конкретного релиза LangGraph; потребует актуализации при обновлениях API.

**Риски:** сложный debug при ошибках в middle-узлах — снижается `trace_id` в JSON-логах и последующим OTel в MVP.

## Compliance & Security

Узел `rbac_filter` — обязательный элемент графа, не опциональный middleware. Его отсутствие или bypass делают систему несоответствующей требованиям ИБ.
