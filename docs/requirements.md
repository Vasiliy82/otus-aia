# Требования к сдаче (выжимка)

Полный текст: методичка в `local-docs/32-33. Методические указания...` (локально).

## Три артефакта

1. **Git monorepo** — `infra/`, `backend/`, `docs/`
2. **Architecture Design Document** — диаграммы C4, Deployment, Sequence, ER, capacity planning
3. **Deep-Dive Demo** — видео 5–7 мин, трейсы, визуализация графа, нагрузочный отчёт

## Критично для зачёта

- [ ] On-prem / без облачных API
- [ ] GraphRAG (не только vector search)
- [ ] LangGraph или state machine
- [ ] RBAC на чанках работает
- [ ] Deployment Diagram и Data Flow
- [ ] Control Plane / Data Plane разделены в архитектуре MVP

## ADR (минимум)

- [x] ADR-000 kickoff
- [x] ADR-001 … ADR-007 (домен, GraphRAG, LLM, Qdrant, LangGraph, RBAC, моки)
- [ ] ADR LLM Serving, Graph DB — при переходе к backend/MVP

## PoC implementation (текущий шаг)

- [x] Monorepo scaffold
- [x] Data prep: `make data-all`
- [ ] LangGraph pipeline
- [ ] FastAPI `/ask`
- [ ] Qdrant embeddings load
- [ ] Guardrails + pytest

## Диаграммы (следующие шаги)

- [ ] C4 L1–L2 PoC
- [ ] Sequence: User → Guardrails → GraphRAG → LLM
- [ ] ER (согласована с `infra/sql/`)
