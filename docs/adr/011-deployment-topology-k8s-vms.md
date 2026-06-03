# ADR-011: Deployment-топология MVP — Kubernetes + VM

## Status

Accepted

## Context

Целевая архитектура MVP — on-prem платформа банка с десятками контейнеров (FastAPI, vLLM, Triton, ETL, observability) и stateful-хранилищами (PostgreSQL, Neo4j, Qdrant, MinIO). Нужно явно зафиксировать:

- **где** работает оркестратор (Kubernetes vs VM vs bare metal);
- **один** product-кластер или **несколько** изолированных K8s;
- как текущие «зоны» deployment-диаграммы (runtime, GPU, ingestion, data) соотносятся с реальной инфраструктурой.

Ограничения банка:

- DBA-команда эксплуатирует **PostgreSQL** на выделенной инфраструктуре, не внутри произвольных pod'ов приложений.
- GPU для vLLM и Triton закупается отдельно; inference должен быть изолирован от API (ADR-008).
- CI/CD (Git, Argo CD, Container Registry) — **корпоративная платформа** (`deliveryPlatform`), не часть product-кластера.
- PoC/staging — Docker Compose; production MVP — после ИБ-аудита (см. technology-radar).

## Alternatives

### 1. Несколько изолированных Kubernetes-кластеров (app / ML / data)

- Плюсы: жёсткий blast-radius; независимые циклы апгрейда control plane; проще для ИБ при hard isolation inference
- Минусы: кратно выше операционные затраты; избыточно для одного продукта и одной команды на MVP; сложнее GitOps и сквозная observability

### 2. Один product Kubernetes + namespaces + node pools; stateful — на VM (выбрано)

- Плюсы: операционная простота; GitOps в один кластер; логические зоны через namespace и NetworkPolicy; GPU — отдельный node pool в том же K8s; БД на VM — в зоне компетенции DBA
- Минусы: общий control plane — при компромете кластера blast-radius шире, чем у multi-cluster (снижается NetworkPolicy, RBAC, bank ingress)

### 3. Всё на VM / bare metal без Kubernetes

- Плюсы: минимум абстракций
- Минусы: нет стандартного масштабирования и GitOps; противоречит целевому radar (K8s после ИБ-аудита) и модели CI/CD (Argo CD)

## Decision

Production MVP разворачивается **on-prem в одном product Kubernetes-кластере** для **stateless**-нагрузки:

| Namespace | Назначение | Контейнеры |
|-----------|------------|------------|
| `credit-ai-app` | Online runtime | FastAPI, OPA, Vault Agent |
| `credit-ai-gpu` | Inference (GPU node pool) | vLLM, Triton |
| `credit-ai-ingestion` | Batch/offline | Airflow, parsers, chunker, batch embeddings, graph enrichment |
| `credit-ai-observability` | Метрики, трейсы, алерты, backup jobs | OTel, Jaeger, Prometheus/Grafana, Alertmanager, Velero/CronJob |

**Stateful**-хранилища — **на VM** (предпочтительно; bare metal — если виртуализация даёт явный минус для конкретного сервиса):

| Компонент | Размещение | Владелец |
|-----------|------------|----------|
| PostgreSQL | VM | Bank DBA |
| Neo4j | VM | Bank infra / MLOps |
| Qdrant | VM | Bank infra / MLOps |
| MinIO | VM | Bank infra |
| Backup Storage | VM / offsite object storage | SRE |

**GPU worker nodes** — физические GPU-серверы или GPU-VM, **вступающие в тот же K8s-кластер** как отдельный node pool (`nodeSelector` / taints `nvidia.com/gpu`). General worker nodes и control plane — на VM (VMware/OpenStack).

**CI/CD** — внешняя `deliveryPlatform`; Argo CD деплоит манифесты в product K8s.

**Multi-cluster** на MVP **не используем**. Второй K8s (отдельный ML/inference-кластер) рассматривается только при явном требовании ИБ к hard isolation между app и inference tier.

## Consequences

**Плюсы:** согласованность с DBA-практикой банка; один GitOps-контур; namespaces отделяют online/batch/GPU/observability; deployment-диаграмма читается как «K8s + Data VMs».

**Минусы:** нужны NetworkPolicy и дисциплина namespace; cross-namespace gRPC (app → gpu) и подключения к VM-БД требуют явной сетевой матрицы.

**Риски:** перегрузка GPU node pool — мониторинг GPU utilization и алерты (ADR-007). Latency app → Triton — gRPC внутри кластера + colocation GPU nodes.

**Дополнительно:** обновлены [`architecture/mvp/deployment.c4`](../architecture/mvp/deployment.c4), descriptions в `model.c4`, technology-radar, `docs/mvp/README.md`.

## Compliance & Security

Трафик app ↔ gpu namespace — внутри закрытого контура, mTLS; секреты из Vault. Данные на VM-БД не покидают периметр банка. Ingress/mTLS для `/ask` — через корпоративный bank ingress controller в namespace `credit-ai-app`.
