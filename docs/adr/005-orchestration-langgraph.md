# ADR-005: LangGraph как оркестратор агента

## Status

Accepted

## Context

Линейные скрипты **не принимаются**. Нужен stateful pipeline: guardrails → retrieve → graph expand → RBAC → rerank → generate → output guardrails с возможностью ветвления (blocked / ok).

## Alternatives

### 1. Линейный Python-скрипт

- Плюсы: минимум зависимостей
- Минусы: не сдаётся; нет явного state

### 2. LangGraph

- Плюсы: state machine, checkpointing, экосистема LangChain; соответствует курсу
- Минусы: learning curve; версионность API

### 3. LlamaIndex Workflows / custom asyncio FSM

- Плюсы: гибкость
- Минусы: больше boilerplate; слабее alignment с рекомендацией курса

## Decision

Использовать **LangGraph** с явным `State` и узлами: `input_guardrails`, `classify_intent`, `vector_retrieve`, `graph_expand`, `rbac_filter`, `rerank`, `generate_answer`, `output_guardrails`.

## Consequences

**Плюсы:** sequence diagram 1:1 с кодом; тестируемые узлы.

**Минусы:** зависимость от LangGraph releases.

**Риски:** сложный debug — mitigated trace_id и последующим OTel (MVP).

## Compliance & Security

Узел `rbac_filter` обязателен в графе, не «опциональный middleware».
