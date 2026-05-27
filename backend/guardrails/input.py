from __future__ import annotations

import re

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|above)\s+instructions", re.I),
    re.compile(r"disregard\s+(your\s+)?(system\s+)?prompt", re.I),
    re.compile(r"you\s+are\s+now\s+(in\s+)?(\w+\s+)?mode", re.I),
    re.compile(r"system\s*:\s*", re.I),
    re.compile(r"<\s*/?\s*system\s*>", re.I),
    re.compile(r"jailbreak", re.I),
    re.compile(r"выведи\s+системный\s+промпт", re.I),
    re.compile(r"игнорируй\s+предыдущ", re.I),
]

STOP_PATTERNS = [
    re.compile(r"\bpassword\b", re.I),
    re.compile(r"\bsecret\s*key\b", re.I),
]


def check_input(query: str) -> tuple[bool, str | None]:
    text = (query or "").strip()
    if not text:
        return False, "empty_query"
    if len(text) > 4000:
        return False, "query_too_long"
    for pattern in INJECTION_PATTERNS + STOP_PATTERNS:
        if pattern.search(text):
            return False, f"blocked_pattern:{pattern.pattern}"
    return True, None
