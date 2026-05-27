from __future__ import annotations

from backend.llm.base import LLMClient
from backend.state import AskState, Citation


class MockLLMClient:
    """Template answer for PoC — no external API (ADR-003)."""

    def generate(self, state: AskState) -> str:
        chunks = state.get("context_chunks") or []
        role = state.get("role", "analyst")
        query = state.get("query", "")
        intent = state.get("intent") or "general"

        if not chunks:
            return (
                "По запросу не найдено фрагментов, доступных для вашей роли. "
                "Уточните запрос или обратитесь к риск-менеджеру."
            )

        lines = [
            f"**PoC GraphRAG (MockLLM)** — роль `{role}`, intent `{intent}`.",
            f"Запрос: {query}",
            "",
            "**Вывод:** на основании доступных фрагментов и связей графа знаний "
            "предварительный анализ возможен с учётом нормативных и политических оснований.",
            "",
            "**Источники:**",
        ]
        for idx, ch in enumerate(chunks, start=1):
            ext = ch.get("external_id") or ch.get("chunk_id")
            title = ch.get("document_title") or "—"
            snippet = (ch.get("chunk_text") or "")[:120]
            lines.append(f"{idx}. [{ext}] {title}: {snippet}…")

        return "\n".join(lines)

    def build_citations(self, state: AskState) -> list[Citation]:
        citations: list[Citation] = []
        for ch in state.get("context_chunks") or []:
            citations.append(
                {
                    "chunk_id": ch.get("chunk_id"),
                    "external_id": ch.get("external_id"),
                    "document_title": ch.get("document_title"),
                }
            )
        for node in state.get("expanded_nodes") or []:
            if node.get("node_type") in ("Document", "LegalAct", "RiskFactor", "Company"):
                citations.append(
                    {
                        "node_id": node.get("node_id"),
                        "node_type": node.get("node_type"),
                        "label": node.get("label"),
                    }
                )
        return citations
