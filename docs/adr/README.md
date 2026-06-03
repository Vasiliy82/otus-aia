# Architecture Decision Log (ADL)

Журнал архитектурных решений проекта «AI-ассистент кредитного аналитика».

Шаблон: [template.md](template.md).

| ID | Документ | Статус | Дата |
|----|----------|--------|------|
| 000 | [project-kickoff](000-project-kickoff.md) | Accepted | 2026-05-26 |
| 001 | [domain-bank-compliance](001-domain-bank-compliance.md) | Accepted | 2026-05-26 |
| 002 | [graphrag-vs-vector-rag](002-graphrag-vs-vector-rag.md) | Accepted | 2026-05-26 |
| 003 | [self-hosted-llm](003-self-hosted-llm.md) | Accepted | 2026-05-26 |
| 004 | [vector-db-pgvector-to-qdrant](004-vector-db-qdrant.md) | Accepted | 2026-05-26 |
| 005 | [orchestration-langgraph](005-orchestration-langgraph.md) | Accepted | 2026-05-26 |
| 006 | [rbac-chunk-level](006-rbac-chunk-level.md) | Accepted | 2026-05-26 |
| 007 | [poc-mocks-and-mvp-replacement](007-poc-mocks-and-mvp-replacement.md) | Accepted | 2026-05-26 |
| 008 | [inference-isolation-grpc](008-inference-isolation-grpc.md) | Accepted | 2026-06-03 |
| 009 | [context-ranking-rrf-crossencoder](009-context-ranking-rrf-crossencoder.md) | Accepted | 2026-06-03 |
| 010 | [platform-subsystem-decomposition](010-platform-subsystem-decomposition.md) | Accepted | 2026-06-03 |
| 011 | [deployment-topology-k8s-vms](011-deployment-topology-k8s-vms.md) | Accepted | 2026-06-03 |

## Запланировано (MVP)

- ADR: LLM Serving — выбор конкретного движка (vLLM / SGLang / TGI) и квантизации после закупки GPU
- ADR: Graph DB — операционные процедуры Neo4j cluster
- ADR: IdP Integration — подключение Active Directory для RBAC через корпоративную IAM/SSO
