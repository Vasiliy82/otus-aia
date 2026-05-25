-- Financial domain (RFSD / counterparty analysis)
CREATE TABLE IF NOT EXISTS company (
    company_id SERIAL PRIMARY KEY,
    inn TEXT NOT NULL UNIQUE,
    ogrn TEXT,
    name TEXT,
    region TEXT,
    okved TEXT,
    okved_section TEXT,
    creation_date DATE,
    dissolution_date DATE
);

CREATE TABLE IF NOT EXISTS financial_report (
    report_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES company(company_id),
    report_year INT NOT NULL,
    revenue NUMERIC,
    profit NUMERIC,
    assets NUMERIC,
    filed BOOLEAN,
    imputed BOOLEAN,
    outlier BOOLEAN,
    UNIQUE (company_id, report_year)
);

CREATE TABLE IF NOT EXISTS financial_fact (
    fact_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES company(company_id),
    fact_type TEXT NOT NULL,
    report_year INT,
    value NUMERIC,
    unit TEXT,
    description TEXT,
    source_report_id INT REFERENCES financial_report(report_id)
);

CREATE TABLE IF NOT EXISTS risk_factor (
    risk_factor_id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT
);

CREATE TABLE IF NOT EXISTS company_risk (
    company_risk_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES company(company_id),
    risk_factor_id INT NOT NULL REFERENCES risk_factor(risk_factor_id),
    fact_id INT REFERENCES financial_fact(fact_id),
    confidence NUMERIC NOT NULL DEFAULT 1.0,
    explanation TEXT
);
