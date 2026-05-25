# Architecture Decision Log (ADL)

Журнал архитектурных решений курсовой «Защищённая платформа GraphRAG для корпоративного банка».

Шаблон: [template.md](template.md). Формат по лекции 08 (OTUS AI-Архитектор).

| ID | Документ | Статус | Дата |
|----|----------|--------|------|
| 000 | [project-kickoff](000-project-kickoff.md) | Accepted | 2026-05-26 |
| 001 | [domain-bank-compliance](001-domain-bank-compliance.md) | Accepted | 2026-05-26 |
| 002 | [graphrag-vs-vector-rag](002-graphrag-vs-vector-rag.md) | Accepted | 2026-05-26 |
| 003 | [self-hosted-llm](003-self-hosted-llm.md) | Accepted | 2026-05-26 |
| 004 | [vector-db-qdrant](004-vector-db-qdrant.md) | Proposed | 2026-05-26 |
| 005 | [orchestration-langgraph](005-orchestration-langgraph.md) | Accepted | 2026-05-26 |
| 006 | [rbac-chunk-level](006-rbac-chunk-level.md) | Accepted | 2026-05-26 |
| 007 | [poc-mocks-and-mvp-replacement](007-poc-mocks-and-mvp-replacement.md) | Accepted | 2026-05-26 |

## Запланировано (MVP / backend)

- ADR: LLM Serving (vLLM / SGLang / TGI)
- ADR: Graph DB (Neo4j vs SQLite/PostgreSQL для PoC)
- ADR: Observability stack (OpenTelemetry + Jaeger)
