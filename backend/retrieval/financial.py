from __future__ import annotations

DEFAULT_DEMO_INN = "7700000001"


def lookup_financial_facts(inn: str | None) -> dict:
    """PoC: deterministic financial facts for demo company (future: SQL from financial_report)."""
    effective_inn = inn or DEFAULT_DEMO_INN
    return {
        "inn": effective_inn,
        "company_name": "ООО Ромашка",
        "revenue_2023": 100_000_000,
        "revenue_2024": 62_000_000,
        "revenue_drop_pct": 38,
        "profit_2024": -3_000_000,
        "risk_flags": [
            "revenue_drop_gt_30",
            "negative_profit",
        ],
    }
