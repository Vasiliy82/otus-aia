from __future__ import annotations

from typing import Protocol

from backend.state import AskState


class LLMClient(Protocol):
    def generate(self, state: AskState) -> str:
        """Produce an answer from filtered context chunks."""
