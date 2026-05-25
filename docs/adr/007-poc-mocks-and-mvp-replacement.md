# ADR-007: Моки в PoC и план замены в MVP

## Status

Accepted

## Context

PoC проверяет гипотезу архитектуры за ограниченное время. Часть стека (GPU LLM, Neo4j cluster, Vault, OTel, reranker model) дорога в setup. Нужен явный реестр моков, чтобы защита не выглядела как «сделали вид».

## Alternatives

### 1. Реализовать всё production-сразу

- Плюсы: нет «обмана»
- Минусы: высокий риск срыва; отвлечение от ADR/диаграмм

### 2. Честные моки + ADR + MVP-архитектура (выбрано)

- Плюсы: соответствует лекции 03 (PoC = GO/NO-GO); фокус на GraphRAG/RBAC/LangGraph
- Минусы: нужно чётко описать замену

### 3. Только документация без кода

- Плюсы: меньше работ
- Минусы: слабее implementation criteria

## Decision

| Компонент | PoC | MVP / Production |
|-----------|-----|------------------|
| LLM | MockLLMClient | vLLM + Qwen AWQ |
| Reranker | score formula | cross-encoder service |
| Graph store | PostgreSQL tables | Neo4j cluster |
| Vector DB | Qdrant docker | Qdrant cluster |
| OCR | готовые чанки | layout parser → MinIO |
| Secrets | `.env` | Vault |
| Observability | trace_id logs | OTel + Jaeger + Prometheus |
| Legal corpus | synthetic 3 docs | RusLawOD slice |
| Streaming | нет | SSE/WebSocket |

## Consequences

**Плюсы:** прозрачный техдолг; roadmap для главы 6.

**Минусы:** защита требует акцента на «что реально работает» (RBAC, graph, pipeline).

**Риски:** оценщик путает PoC с prod — mitigated ADR и диаграммами MVP.

## Compliance & Security

Моки не отключают RBAC и guardrails — они остаются «настоящими».
