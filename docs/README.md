# Документация курсовой работы

Монорепозиторий объединяет архитектуру, PoC-код и материалы для защиты.

## Оглавление по главам

| Глава | Содержание | Папка / артефакты |
|-------|------------|-------------------|
| 1. Постановка задачи | Заказчик, пользователи, границы PoC/MVP | [poc/scope.md](poc/scope.md), [requirements.md](requirements.md) |
| 2. Архитектура PoC | C4, sequence, data flow, ER | [diagrams/](diagrams/) (в работе) |
| 3. Реализация PoC | Ingestion, GraphRAG, LangGraph, RBAC | [../backend/](../backend/), [../scripts/data_prep/](../scripts/data_prep/) |
| 4. Production MVP | Целевая архитектура без кода | [mvp/README.md](mvp/README.md) |
| 5. ADR | Обоснование решений | [adr/](adr/) |
| 6. Риски и roadmap | Остаточные риски, план развития | [adr/007-poc-mocks-and-mvp-replacement.md](adr/007-poc-mocks-and-mvp-replacement.md) |

## Навигация

- [poc/scope.md](poc/scope.md) — цели и границы PoC-прототипа
- [requirements.md](requirements.md) — чеклист сдачи по методичке
- [adr/README.md](adr/README.md) — журнал архитектурных решений (ADL)
- [lectures-index.md](lectures-index.md) — индекс лекций курса (когда читать)

## Локальные черновики

Папки `Наработки/` и `local-docs/` в `.gitignore` — рабочие заметки и конспекты лекций. В git попадает дистиллированная версия из этих материалов.
