# ADR-003: Self-hosted LLM вместо облачных API

## Status

Accepted

## Context

Система должна работать on-prem / air-gapped без OpenAI, Anthropic и аналогов. Курс фокусируется на архитектуре и RAG, не на обучении моделей. Для PoC допустимы моки при сохранении интерфейса production.

## Alternatives

### 1. Публичные облачные API

- Плюсы: лучшее качество ответов, быстрый старт
- Минусы: дисквалификация по методичке; риски утечки данных

### 2. Self-hosted OSS (Qwen, DeepSeek, Saiga) + vLLM/SGLang

- Плюсы: контроль данных; соответствие ФЗ-152 narrative
- Минусы: нужен GPU, MLOps, ниже качество малых моделей

### 3. Deterministic mock composer на PoC, vLLM на MVP

- Плюсы: PoC двигается без GPU; контракт `LLMClient` готов к замене
- Минусы: демо не показывает «настоящие» формулировки LLM на PoC

## Decision

**PoC:** интерфейс `LLMClient` + `MockLLMClient` (шаблонный ответ по чанкам). **MVP:** self-hosted **Qwen 2.5/3** (или аналог) через **vLLM** с AWQ/GGUF под 24GB VRAM.

## Consequences

**Плюсы:** соблюдение суверенитета; единый API для оркестратора.

**Минусы:** на PoC качество формулировок ограничено шаблоном.

**Риски:** галлюцинации — mitigated GraphRAG, guardrails, обязательные ссылки на источники.

## Compliance & Security

Запрет вывода без источников (output guardrails). Логирование trace_id для аудита.
