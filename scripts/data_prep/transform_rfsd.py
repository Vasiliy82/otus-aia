from __future__ import annotations

import logging
from pathlib import Path

import polars as pl

from scripts.data_prep.config import (
    BASE_YEAR,
    COLUMN_RENAME,
    COMPANY_COLUMNS,
    FINANCIAL_COLUMNS,
    FLAG_COLUMNS,
    ID_COLUMNS,
    META_COLUMNS,
    OKVED_SECTIONS,
    RANDOM_SEED,
    REGION_TAXCODES,
    RENAMED_FINANCIAL_COLUMNS,
    REPORT_COLUMNS,
    REQUIRED_YEARS,
    RISK_COLUMNS,
    SAMPLE_BUCKET_SIZES,
    TARGET_YEAR,
    YearPaths,
)

logger = logging.getLogger(__name__)


def col_exists(df: pl.DataFrame, col: str) -> bool:
    return col in df.columns


def read_rfsd_year_local(year: int, path: Path) -> pl.LazyFrame:
    lf = pl.scan_parquet(path)
    schema_names = lf.collect_schema().names()

    wanted_columns = [c for c in (META_COLUMNS + FINANCIAL_COLUMNS) if c != "year"]
    existing_columns = [c for c in wanted_columns if c in schema_names]
    missing_columns = [c for c in wanted_columns if c not in schema_names]
    if missing_columns:
        logger.warning("year=%s: missing columns: %s", year, missing_columns)

    lf = lf.select(existing_columns).with_columns(pl.lit(year).cast(pl.Int32).alias("year"))

    rename_map = {old: new for old, new in COLUMN_RENAME.items() if old in existing_columns}
    lf = lf.rename(rename_map)
    current_cols = lf.collect_schema().names()

    string_cols = [c for c in ID_COLUMNS if c in current_cols]
    lf = lf.with_columns(
        [
            pl.col(c).cast(pl.Utf8, strict=False).str.strip_chars().alias(c)
            for c in string_cols
        ]
    )

    flag_cols = [c for c in FLAG_COLUMNS if c in current_cols]
    lf = lf.with_columns([pl.col(c).cast(pl.Float64, strict=False).alias(c) for c in flag_cols])

    financial_cols = [c for c in RENAMED_FINANCIAL_COLUMNS if c in lf.collect_schema().names()]
    lf = lf.with_columns([pl.col(c).cast(pl.Float64, strict=False).alias(c) for c in financial_cols])

    if "inn" in current_cols:
        lf = lf.filter(pl.col("inn").is_not_null())
    if "ogrn" in current_cols:
        lf = lf.filter(pl.col("ogrn").is_not_null())
    if "region_taxcode" in current_cols and REGION_TAXCODES:
        lf = lf.filter(pl.col("region_taxcode").is_in(REGION_TAXCODES))
    if "okved_section" in current_cols and OKVED_SECTIONS:
        lf = lf.filter(pl.col("okved_section").is_in(OKVED_SECTIONS))

    return lf


def load_raw_rfsd(year_paths: YearPaths) -> pl.DataFrame:
    frames = [read_rfsd_year_local(year, path) for year, path in year_paths.paths.items()]
    return pl.concat(frames, how="diagonal_relaxed").collect()


def build_financial_reports(raw: pl.DataFrame) -> pl.DataFrame:
    existing_report_cols = [c for c in REPORT_COLUMNS if c in raw.columns]
    return (
        raw.select(existing_report_cols)
        .unique(subset=["inn", "year"], keep="first")
        .sort(["inn", "year"])
    )


def filter_reports_two_years(financial_reports: pl.DataFrame) -> pl.DataFrame:
    companies_with_required_years = (
        financial_reports.filter(pl.col("year").is_in(REQUIRED_YEARS))
        .group_by("inn")
        .agg(pl.col("year").n_unique().alias("years_count"))
        .filter(pl.col("years_count") == len(REQUIRED_YEARS))
        .select("inn")
    )
    return financial_reports.join(companies_with_required_years, on="inn", how="inner")


def build_company_dim(reports_2y: pl.DataFrame) -> pl.DataFrame:
    return (
        reports_2y.sort(["inn", "year"])
        .group_by("inn")
        .agg(
            [
                pl.col("ogrn").drop_nulls().last().alias("ogrn"),
                pl.col("region").drop_nulls().last().alias("region"),
                pl.col("region_taxcode").drop_nulls().last().alias("region_taxcode"),
                pl.col("okved").drop_nulls().last().alias("okved"),
                pl.col("okved_section").drop_nulls().last().alias("okved_section"),
                pl.col("creation_date").drop_nulls().last().alias("creation_date"),
                pl.col("dissolution_date").drop_nulls().last().alias("dissolution_date"),
                pl.col("age").drop_nulls().last().alias("age"),
            ]
        )
        .with_columns((pl.lit("Компания ИНН ") + pl.col("inn")).alias("company_label"))
    )


def first_value_for_year(col: str, year: int) -> pl.Expr:
    return (
        pl.col(col)
        .filter(pl.col("year") == year)
        .drop_nulls()
        .first()
        .alias(f"{col}_{year}")
    )


def build_features(company_dim: pl.DataFrame, reports_2y: pl.DataFrame) -> pl.DataFrame:
    wide_exprs = []
    for year in REQUIRED_YEARS:
        for col in RENAMED_FINANCIAL_COLUMNS + FLAG_COLUMNS:
            if col in reports_2y.columns:
                wide_exprs.append(first_value_for_year(col, year))

    wide = reports_2y.group_by("inn").agg(wide_exprs)
    features = company_dim.join(wide, on="inn", how="inner")

    exprs = []
    revenue_base_col = f"revenue_{BASE_YEAR}"
    revenue_target_col = f"revenue_{TARGET_YEAR}"
    assets_base_col = f"assets_{BASE_YEAR}"
    assets_target_col = f"assets_{TARGET_YEAR}"

    if col_exists(features, revenue_base_col) and col_exists(features, revenue_target_col):
        exprs.append(
            pl.when(pl.col(revenue_base_col) > 0)
            .then(
                (pl.col(revenue_base_col) - pl.col(revenue_target_col))
                / pl.col(revenue_base_col)
                * 100
            )
            .otherwise(None)
            .alias(f"revenue_drop_{TARGET_YEAR}_pct")
        )

    if col_exists(features, assets_base_col) and col_exists(features, assets_target_col):
        exprs.append(
            pl.when(pl.col(assets_base_col) > 0)
            .then(
                (pl.col(assets_base_col) - pl.col(assets_target_col))
                / pl.col(assets_base_col)
                * 100
            )
            .otherwise(None)
            .alias(f"assets_drop_{TARGET_YEAR}_pct")
        )

    if exprs:
        features = features.with_columns(exprs)

    risk_exprs = []
    revenue_drop_col = f"revenue_drop_{TARGET_YEAR}_pct"
    assets_drop_col = f"assets_drop_{TARGET_YEAR}_pct"
    net_profit_target_col = f"net_profit_{TARGET_YEAR}"
    equity_target_col = f"equity_{TARGET_YEAR}"

    if col_exists(features, revenue_drop_col):
        risk_exprs.append(
            (pl.col(revenue_drop_col) >= 30).fill_null(False).alias("risk_revenue_drop_gt_30")
        )
    if col_exists(features, net_profit_target_col):
        risk_exprs.append(
            (pl.col(net_profit_target_col) < 0).fill_null(False).alias("risk_negative_profit")
        )
    if col_exists(features, assets_drop_col):
        risk_exprs.append(
            (pl.col(assets_drop_col) >= 25).fill_null(False).alias("risk_assets_drop_gt_25")
        )
    if col_exists(features, equity_target_col):
        risk_exprs.append(
            (pl.col(equity_target_col) < 0).fill_null(False).alias("risk_negative_equity")
        )

    if risk_exprs:
        features = features.with_columns(risk_exprs)

    data_quality_conditions = []
    filed_target_col = f"filed_{TARGET_YEAR}"
    imputed_target_col = f"imputed_{TARGET_YEAR}"
    outlier_target_col = f"outlier_{TARGET_YEAR}"

    if col_exists(features, filed_target_col):
        data_quality_conditions.append((pl.col(filed_target_col) == 0.0).fill_null(False))
    if col_exists(features, imputed_target_col):
        data_quality_conditions.append((pl.col(imputed_target_col) == 1.0).fill_null(False))
    if col_exists(features, outlier_target_col):
        data_quality_conditions.append((pl.col(outlier_target_col) == 1.0).fill_null(False))

    if data_quality_conditions:
        data_quality_expr = data_quality_conditions[0]
        for condition in data_quality_conditions[1:]:
            data_quality_expr = data_quality_expr | condition
        features = features.with_columns(data_quality_expr.alias("risk_data_quality_issue"))
    else:
        features = features.with_columns(pl.lit(False).alias("risk_data_quality_issue"))

    present_risk_cols = [c for c in RISK_COLUMNS if c in features.columns]
    if present_risk_cols:
        features = features.with_columns(
            pl.sum_horizontal([pl.col(c).cast(pl.Int8) for c in present_risk_cols]).alias("risk_count")
        )

    return features


def safe_sample(df: pl.DataFrame, n: int, seed: int) -> pl.DataFrame:
    if df.height == 0:
        return df
    return df.sample(n=min(n, df.height), seed=seed, shuffle=True)


def build_stratified_sample(features: pl.DataFrame, seed: int = RANDOM_SEED) -> pl.DataFrame:
    selected_inns: set[str] = set()

    def exclude_already_selected(df: pl.DataFrame) -> pl.DataFrame:
        if not selected_inns:
            return df
        return df.filter(~pl.col("inn").is_in(list(selected_inns)))

    normal_conditions = []
    if f"revenue_{TARGET_YEAR}" in features.columns:
        normal_conditions.append(pl.col(f"revenue_{TARGET_YEAR}") > 0)
    if f"net_profit_{TARGET_YEAR}" in features.columns:
        normal_conditions.append(pl.col(f"net_profit_{TARGET_YEAR}") > 0)
    for risk_col in RISK_COLUMNS:
        if risk_col in features.columns:
            normal_conditions.append(pl.col(risk_col) == False)

    if normal_conditions:
        normal_filter = normal_conditions[0]
        for condition in normal_conditions[1:]:
            normal_filter = normal_filter & condition
        normal = (
            safe_sample(
                features.filter(normal_filter),
                n=SAMPLE_BUCKET_SIZES.get("normal", 30),
                seed=seed,
            ).with_columns(pl.lit("normal").alias("sample_bucket"))
        )
    else:
        normal = features.head(0).with_columns(pl.lit("normal").alias("sample_bucket"))

    selected_inns.update(normal["inn"].to_list())

    buckets: list[tuple[str, str]] = [
        ("revenue_drop_gt_30", "risk_revenue_drop_gt_30"),
        ("negative_profit", "risk_negative_profit"),
        ("assets_drop_gt_25", "risk_assets_drop_gt_25"),
        ("data_quality_issue", "risk_data_quality_issue"),
    ]

    parts = [normal]
    for idx, (bucket_name, risk_col) in enumerate(buckets):
        if risk_col in features.columns:
            part = (
                safe_sample(
                    exclude_already_selected(features).filter(pl.col(risk_col) == True),
                    n=SAMPLE_BUCKET_SIZES.get(bucket_name, 15),
                    seed=seed + idx + 1,
                ).with_columns(pl.lit(bucket_name).alias("sample_bucket"))
            )
        else:
            part = features.head(0).with_columns(pl.lit(bucket_name).alias("sample_bucket"))
        selected_inns.update(part["inn"].to_list())
        parts.append(part)

    return pl.concat(parts, how="diagonal_relaxed").unique(subset=["inn"], keep="first")


def build_poc_tables(
    sample_companies: pl.DataFrame,
    reports_2y: pl.DataFrame,
) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    sample_inns = sample_companies["inn"].to_list()
    sample_reports = reports_2y.filter(pl.col("inn").is_in(sample_inns)).sort(["inn", "year"])

    poc_company = (
        sample_companies.select(
            [c for c in COMPANY_COLUMNS + ["company_label", "sample_bucket"] if c in sample_companies.columns]
        )
        .unique(subset=["inn"], keep="first")
        .sort("inn")
    )

    poc_financial_report = (
        sample_reports.select([c for c in REPORT_COLUMNS if c in sample_reports.columns]).sort(["inn", "year"])
    )

    derived_cols = (
        [f"revenue_{y}" for y in REQUIRED_YEARS]
        + [f"revenue_drop_{TARGET_YEAR}_pct"]
        + [f"net_profit_{y}" for y in REQUIRED_YEARS]
        + [f"assets_{y}" for y in REQUIRED_YEARS]
        + [f"assets_drop_{TARGET_YEAR}_pct"]
        + [f"equity_{y}" for y in REQUIRED_YEARS]
        + [f"filed_{y}" for y in REQUIRED_YEARS]
        + [f"imputed_{y}" for y in REQUIRED_YEARS]
        + [f"outlier_{y}" for y in REQUIRED_YEARS]
    )

    feature_columns = (
        ["inn", "ogrn", "sample_bucket"]
        + derived_cols
        + RISK_COLUMNS
        + ["risk_count"]
    )
    poc_company_features = (
        sample_companies.select(
            [c for c in feature_columns if c in sample_companies.columns]
        )
        .unique(subset=["inn"], keep="first")
        .sort("inn")
    )

    return poc_company, poc_financial_report, poc_company_features


def transform_rfsd(year_paths: YearPaths) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    raw = load_raw_rfsd(year_paths)
    logger.info("RFSD raw shape: %s", raw.shape)

    financial_reports = build_financial_reports(raw)
    reports_2y = filter_reports_two_years(financial_reports)
    company_dim = build_company_dim(reports_2y)
    features = build_features(company_dim, reports_2y)
    sample_companies = build_stratified_sample(features)
    return build_poc_tables(sample_companies, reports_2y)
