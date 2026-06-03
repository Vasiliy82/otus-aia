# Целевая архитектура MVP

Раздел описывает production-архитектуру системы после успешного GO-решения по PoC. Код MVP **не реализуется** до завершения PoC-валидации и принятия инвестиционного решения. Архитектура спроектирована как almost-production: единая платформа с подсистемами, изолированный inference-слой и корректное ранжирование контекста.

## Целевая система

**AI-платформа кредитного анализа** (`creditPlatform`) — единая Secure GraphRAG платформа банка. Внутри выделены подсистемы с разными жизненными циклами, владельцами и SLA. Решение о декомпозиции зафиксировано в [ADR-010](../adr/010-platform-subsystem-decomposition.md).

### Подсистемы платформы

| Подсистема | Назначение | Ключевые контейнеры |
|------------|-----------|---------------------|
| Secure GraphRAG Runtime | Production online-контур запроса | FastAPI (I/O-bound), vLLM, Triton Inference Server |
| Knowledge Ingestion Pipeline | Offline/batch пополнение базы знаний | Airflow/ETL, парсеры, chunker, batch embeddings, graph enrichment |
| AI Quality & MLOps | Качество, эксперименты, реестр моделей | Evaluation Runner (RAGAS/DeepEval/promptfoo), MLflow, Prompt Registry, Golden Set |
| Security & Access Control | Секреты, политики доступа, аудит | HashiCorp Vault, OPA, Audit Log |
| Observability & Reliability | Метрики, трассировки, алерты, бэкапы | OTel Collector, Jaeger, Prometheus/Grafana, Alertmanager, Backup |

Платформенными/governance-системами ландшафта остаются **Delivery & Release Platform** (CI/CD) и **Architecture as Code**. Внешние системы: нормативная база банка, источники финансовой отчётности, корпоративная IAM/SSO.

## Ключевые архитектурные решения MVP

### Изоляция inference-слоя (ADR-008)

Тяжёлый инференс полностью вынесен из API-шлюза:

- **vLLM** (GPU) — генерация LLM (Qwen), OpenAI-compatible API.
- **Triton Inference Server** (GPU) — embeddings и cross-encoder reranker, динамический батчинг, конкурентные инстансы моделей.
- **FastAPI** остаётся строго **I/O-bound**: тонкие gRPC-клиенты, без загрузки PyTorch-весов в lifespan. Это снимает блокирующий прогрев и GIL-боттлнек, обеспечивая стабильную latency под параллельной нагрузкой и независимое масштабирование API и моделей.

### Ранжирование контекста: RRF + Cross-Encoder (ADR-009)

Эвристика `vector_score + 0.5·graph_score` заменена на двухступенчатое ранжирование:

1. **RRF (Reciprocal Rank Fusion)** сливает dense- (Qdrant) и graph- (Neo4j) списки по относительным позициям (`score = Σ 1/(k + rank_i)`, k ≈ 60), нивелируя разницу шкал.
2. **Cross-Encoder** переранжирует top-N пар `(query, chunk)` на основе глубокого внимания (инференс в Triton).

Ранжирование выполняется **после** RBAC-фильтрации (ADR-006).

### Deployment-топология (ADR-011)

Production MVP — **один on-prem product Kubernetes-кластер** + **Data VMs** для stateful:

| Слой | Размещение | Компоненты |
|------|------------|------------|
| `credit-ai-app` | K8s namespace | FastAPI, OPA, Vault Agent |
| `credit-ai-gpu` | K8s namespace (GPU node pool) | vLLM, Triton |
| `credit-ai-ingestion` | K8s namespace | Airflow, ETL, batch jobs |
| `credit-ai-observability` | K8s namespace | OTel, Jaeger, Prometheus, Velero |
| DB Tier | VM (bank infra / DBA) | PostgreSQL, Neo4j, Qdrant |
| Object Storage | VM | MinIO, backup storage |

Stateless — в K8s; stateful БД и object storage — на VM. GPU workers — bare metal или GPU-VM в том же кластере. CI/CD — внешняя `deliveryPlatform` (GitOps в product K8s). Отдельные K8s-кластеры на MVP не используем.

## Состав архитектурных артефактов (LikeC4, `architecture/mvp/`)

8 целевых представлений + детализирующие диаграммы:

| # | View ID | Что показывает |
|---|---------|----------------|
| 1 | `mvp_landscape` | System Landscape (C1): акторы, платформа, внешние и governance-системы |
| 2 | `mvp_container` | Platform Subsystems (C2): подсистемы и общие хранилища |
| 3 | `mvp_runtime` | Container — Secure GraphRAG Runtime (FastAPI + vLLM + Triton) |
| 4 | `mvp_ingestion` | Container — Knowledge Ingestion Pipeline |
| 5 | `mvp_quality_mlops` | AI Quality & MLOps |
| 6 | `mvp_cicd` | Delivery & Release Platform (CI/CD) |
| 7 | `mvp_observability` | Observability & Reliability (+ backup/restore) |
| 8 | `mvp_security` | Security & Access Control (trust boundaries) |
| 9 | `mvp_arch_as_code` | Architecture as Code |
| — | `mvp_component` | L3 — компоненты FastAPI (RRF, gRPC-клиенты) |
| — | `mvp_ask_sequence` | Sequence — `POST /ask` (gRPC к Triton, RRF, cross-encoder, vLLM) |
| — | `mvp_er_postgres` / `mvp_er_datastores` | ER PostgreSQL и логические сущности Qdrant/Neo4j |
| — | `mvp_deployment` | Deployment — K8s (namespaces) + Data VMs (ADR-011) |

## Ключевые отличия MVP от PoC

| Компонент | PoC | MVP |
|-----------|-----|-----|
| LLM | MockLLMClient | self-hosted Qwen (vLLM, 24+ ГБ VRAM), изолированный inference |
| Inference embeddings/reranker | in-process sentence-transformers (CPU) | Triton Inference Server (GPU, gRPC) |
| Ранжирование | `vector + 0.5·graph` (эвристика) | RRF + cross-encoder |
| Graph store | PostgreSQL | Neo4j cluster |
| Векторная БД | pgvector | Qdrant cluster |
| Secrets | `.env` | HashiCorp Vault |
| Observability | JSON-логи с `trace_id` | OpenTelemetry + Jaeger + Prometheus |
| Ingestion | Indexing CLI внутри FastAPI | отдельная подсистема Knowledge Ingestion |
| Deployment | Docker Compose (on-prem) | K8s (stateless) + VM (stateful DB) — ADR-011 |
| Юридический корпус | синтетика | реальная нормативная база |

## Условия перехода к MVP

1. GO-решение Технического комитета по итогам PoC.
2. Закупка GPU-сервера (бюджет Q1 2027) — для vLLM и Triton.
3. Найм MLOps-инженера (запланирован Q3 2026).
4. Прохождение ИБ-аудита архитектуры.
5. Согласование юридического корпуса с Дирекцией права.

## Связанные ADR

- [008-inference-isolation-grpc.md](../adr/008-inference-isolation-grpc.md) — изоляция inference-слоя (Triton, gRPC).
- [009-context-ranking-rrf-crossencoder.md](../adr/009-context-ranking-rrf-crossencoder.md) — RRF + cross-encoder.
- [010-platform-subsystem-decomposition.md](../adr/010-platform-subsystem-decomposition.md) — декомпозиция платформы и набор views.
- [011-deployment-topology-k8s-vms.md](../adr/011-deployment-topology-k8s-vms.md) — K8s + VM, namespaces, node pools.
- [007-poc-mocks-and-mvp-replacement.md](../adr/007-poc-mocks-and-mvp-replacement.md) — реестр замены мок-компонентов.
