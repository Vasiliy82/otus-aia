from __future__ import annotations

from dataclasses import dataclass

import polars as pl
import json


@dataclass(frozen=True)
class LegalSeed:
    documents: pl.DataFrame
    chunks: pl.DataFrame


def build_legal_seed(demo_inn: str, demo_company_name: str = "ООО Ромашка") -> LegalSeed:
    documents = pl.DataFrame(
        {
            "external_id": ["law_001", "policy_001", "risk_001"],
            "source": ["RusLawOD_sample", "synthetic_bank_policy", "synthetic_bank_policy"],
            "doc_type": ["legal_act", "internal_policy", "risk_methodology"],
            "title": [
                "Закон о банковской деятельности",
                "Внутренняя политика оценки контрагентов",
                "Методика оценки финансового риска",
            ],
            "security_level": ["public", "internal", "secret"],
            "metadata": [
                json.dumps({"demo_company_inn": demo_inn, "demo_company_name": demo_company_name}, ensure_ascii=False),
                json.dumps({"demo_company_inn": demo_inn}, ensure_ascii=False),
                json.dumps({"demo_company_inn": demo_inn}, ensure_ascii=False),
            ],
        }
    )

    chunks = pl.DataFrame(
        {
            "external_id": ["ch_001", "ch_002", "ch_003"],
            "document_external_id": ["law_001", "policy_001", "risk_001"],
            "chunk_text": [
                "Кредитная организация обязана идентифицировать клиента и оценивать риски операций.",
                "При снижении выручки более чем на 30% аналитик обязан запросить дополнительные документы.",
                "Секретная методика внутреннего скоринга использует закрытые коэффициенты риска.",
            ],
            "chunk_order": [1, 1, 1],
            "allowed_roles": [
                json.dumps(["analyst", "risk_manager"], ensure_ascii=False),
                json.dumps(["analyst", "risk_manager"], ensure_ascii=False),
                json.dumps(["risk_manager"], ensure_ascii=False),
            ],
            "metadata": [
                json.dumps({"linked_inn": demo_inn}, ensure_ascii=False),
                json.dumps({"linked_inn": demo_inn, "risk_factor": "revenue_drop"}, ensure_ascii=False),
                json.dumps({"linked_inn": demo_inn}, ensure_ascii=False),
            ],
        }
    )

    return LegalSeed(documents=documents, chunks=chunks)
