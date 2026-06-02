from backend.retrieval.financial import DEFAULT_DEMO_INN, lookup_financial_facts


def test_lookup_financial_facts_defaults_inn():
    facts = lookup_financial_facts(None)
    assert facts["inn"] == DEFAULT_DEMO_INN
    assert facts["company_name"] == "ООО Ромашка"
    assert "revenue_drop_gt_30" in facts["risk_flags"]


def test_lookup_financial_facts_uses_provided_inn():
    facts = lookup_financial_facts("1234567890")
    assert facts["inn"] == "1234567890"
