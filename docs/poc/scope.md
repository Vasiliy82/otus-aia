# PoC: границы и минимальный сценарий

## Цель

Демонстрация защищённого GraphRAG-ассистента для анализа нормативных и финансовых данных контрагентов в корпоративном банке: LangGraph-оркестрация, векторный поиск, графовое расширение контекста, RBAC на уровне чанков, input/output guardrails, мок локального LLM.

## Сценарий

Ассистент кредитного/комплаенс-аналитика отвечает на вопрос по контрагенту и нормативным ограничениям.

Пример запроса:

> Можно ли использовать документы по компании Ромашка для предварительного анализа риска? Покажи финансовые признаки и нормативные основания.

Ожидаемый ответ: краткий вывод, нормативные и финансовые фрагменты, ссылки на чанки, отказ при отсутствии прав.

## Что реализуем в коде (PoC)

| Компонент | Реализация |
|-----------|------------|
| Backend API | FastAPI, 2–3 endpoint (следующий шаг) |
| LangGraph | Граф 5–7 узлов (следующий шаг) |
| GraphRAG | Qdrant + расширение по графу (следующий шаг) |
| Knowledge Graph | PostgreSQL `graph_node` / `graph_edge` |
| Guardrails | regexp + списки паттернов |
| RBAC | фильтрация чанков по `allowed_roles` |
| Ingestion / data prep | `make data-all` — RFSD + синтетический legal slice |
| Unit tests | pytest на RBAC, guardrails, graph expansion |

## Что мокаем

- LLM Serving → `MockLLMClient`
- Reranker → детерминированная формула score
- OCR → подготовленные тексты чанков
- Vault → `.env` на PoC
- OpenTelemetry → `trace_id` в JSON-логах

## Что нельзя мокать

- GraphRAG (не только vector top-k)
- RBAC (User B не видит секретный документ)
- LangGraph / state machine
- Deployment / Data Flow диаграммы в документации
- Внешние облачные API (OpenAI/Anthropic)

## Данные PoC

- **RFSD** (HuggingFace): стратифицированная выборка компаний с отчётами 2023–2024
- **Синтетический legal slice**: 3 документа, 3 чанка, демо RBAC на `ch_003`
- **Граф**: Document, Chunk, Company, LegalAct, RiskFactor; рёбра BELONGS_TO, MENTIONS, LINKED_TO

Подготовка: `make data-all` (см. корневой [README.md](../../README.md)).

## Критические тесты (план)

1. `analyst` не получает `ch_003` в контексте
2. `risk_manager` получает `ch_003`
3. Prompt injection блокируется на входе
4. Ответ без источников блокируется на выходе
5. Graph expansion добавляет связанный документ/узел
