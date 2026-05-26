# Требования к системе

Полный чеклист приёмки PoC — в [acceptance-criteria.md](acceptance-criteria.md).

## Нефункциональные требования (зафиксированы Службой ИБ и ЦБ РФ)

- On-prem / закрытый контур — без облачных AI API.
- GraphRAG: не только векторный поиск, но и расширение по графу знаний (требование Дирекции ИТ, ADR-002).
- LangGraph / state machine — оркестратор с явным состоянием и аудитом шагов.
- RBAC на уровне фрагментов — пользователь без прав не получает закрытый контент.

## Архитектурные артефакты для GO-решения

- Deployment Diagram и Data Flow.
- C4 Level 1–2.
- Sequence Diagram полного запроса.
- ER-диаграмма.
- Разделение Control Plane / Data Plane в архитектуре MVP.

## Минимальный набор ADR

- [x] ADR-000 … ADR-007 (домен, GraphRAG, LLM, векторный поиск, LangGraph, RBAC, моки)
- [ ] ADR: LLM Serving (vLLM / SGLang) — при переходе к MVP
- [ ] ADR: Graph DB (Neo4j) — при переходе к MVP
