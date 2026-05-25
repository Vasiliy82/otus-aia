# ADR-006: RBAC на уровне чанков

## Status

Accepted

## Context

Критичное требование: пользователь без прав **не получает** ответ по секретному документу. Фильтрация только на уровне документа груба (весь doc виден или скрыт); внутренние политики могут иметь разные роли на разделы/чанки.

## Alternatives

### 1. RBAC только на document

- Плюсы: проще ACL
- Минусы: не покрывает смешанные роли; слабее для демо `ch_003`

### 2. RBAC на chunk (выбрано)

- Плюсы: гранулярность; соответствует методичке; поле `allowed_roles text[]`
- Минусы: нужно поддерживать при ingestion

### 3. ABAC / policy engine (OPA)

- Плюсы: гибкость enterprise
- Минусы: избыточно для PoC

## Decision

Хранить `allowed_roles` на каждом **chunk**. При retrieval и graph expansion применять фильтр по роли пользователя (`analyst`, `risk_manager`). Демо: `ch_003` только для `risk_manager`.

## Consequences

**Плюсы:** прямые pytest-кейсы из scope PoC.

**Минусы:** дублирование ролей в Qdrant payload.

**Риски:** утечка через graph expansion — mitigated фильтром после expand.

## Compliance & Security

Тест: analyst + запрос про секретную методику → `ch_003` отсутствует в контексте.
