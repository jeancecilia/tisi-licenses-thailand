"""Feature engineering pipeline for TISI license datasets."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATASETS_DIR = PROJECT_ROOT / "datasets"
MERGED_FILE = PROCESSED_DIR / "tisi_licenses_merged.csv"

CLEAN_DATASET = DATASETS_DIR / "tisi_licenses_clean_2024_2025.csv"
TRENDS_DATASET = DATASETS_DIR / "tisi_trends_by_standard.csv"
IMPORT_DEPENDENCY_DATASET = DATASETS_DIR / "tisi_import_dependency.csv"
RISK_DATASET = DATASETS_DIR / "tisi_risk_index.csv"
LATEST_SNAPSHOT_DATASET = DATASETS_DIR / "tisi_latest_snapshot_summary.csv"

LICENSE_COLUMNS: List[str] = [
    "num_manufacturing_licenses",
    "num_import_licenses",
    "num_display_licenses",
]

ENTREPRENEUR_COLUMNS: List[str] = [
    "num_manufacturing_entrepreneurs",
    "num_import_entrepreneurs",
    "num_display_entrepreneurs",
]


def _ensure_numeric(df: pd.DataFrame, columns: Iterable[str]) -> None:
    """Convert selected columns to numeric, filling NaN with zeros."""
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)


def _min_max_normalize(series: pd.Series) -> pd.Series:
    """Apply min-max normalization that always returns values between 0 and 1."""
    if series.empty:
        return series
    min_value = series.min()
    max_value = series.max()
    if pd.isna(min_value) or pd.isna(max_value) or max_value == min_value:
        return pd.Series(0.0, index=series.index)
    normalized = (series - min_value) / (max_value - min_value)
    return normalized.clip(0, 1)


def load_base_dataframe() -> pd.DataFrame:
    """Load merged dataset and ensure schema readiness for feature engineering."""
    if not MERGED_FILE.exists():
        raise FileNotFoundError(
            f"Required merged file not found at {MERGED_FILE}. "
            "Run scripts/merge_raw.py first."
        )

    df = pd.read_csv(MERGED_FILE)
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    _ensure_numeric(df, LICENSE_COLUMNS + ENTREPRENEUR_COLUMNS)

    if "total_licenses" not in df.columns:
        df["total_licenses"] = 0
    df["total_licenses"] = pd.to_numeric(df["total_licenses"], errors="coerce").fillna(
        0
    )

    recomputed_total = (
        df["num_manufacturing_licenses"]
        + df["num_import_licenses"]
        + df["num_display_licenses"]
    )
    missing_totals = df["total_licenses"] == 0
    df.loc[missing_totals, "total_licenses"] = recomputed_total[missing_totals]

    df["num_total_entrepreneurs"] = (
        df["num_manufacturing_entrepreneurs"]
        + df["num_import_entrepreneurs"]
        + df["num_display_entrepreneurs"]
    )

    df["import_to_manufacturing_ratio"] = df["num_import_licenses"] / (
        df["num_manufacturing_licenses"] + 1e-6
    )
    total_import_manufacturing = (
        df["num_import_licenses"] + df["num_manufacturing_licenses"] + 1e-6
    )
    df["import_dependency_ratio"] = df["num_import_licenses"] / total_import_manufacturing
    df["domestic_share_ratio"] = df["num_manufacturing_licenses"] / (
        df["num_import_licenses"] + df["num_manufacturing_licenses"] + 1e-6
    )
    df["display_to_total_ratio"] = df["num_display_licenses"] / (
        df["total_licenses"] + 1e-6
    )

    df = df.sort_values(["tis_number", "snapshot_date"]).reset_index(drop=True)
    return df


def build_clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Return the clean, feature-enriched dataset."""
    return df.copy()


def build_trends_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Create month-over-month change metrics per TIS standard."""
    trends = df[
        [
            "tis_number",
            "tis_name_th",
            "snapshot_date",
            *LICENSE_COLUMNS,
            "total_licenses",
        ]
    ].copy()

    metric_columns = LICENSE_COLUMNS + ["total_licenses"]
    grouped = trends.groupby("tis_number", group_keys=False)
    for column in metric_columns:
        trends[f"{column}_diff"] = grouped[column].diff()
        trends[f"{column}_pct_change"] = grouped[column].pct_change() * 100
    return trends


def build_import_dependency_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Generate dataset focused on import vs manufacturing exposure."""
    return df[
        [
            "tis_number",
            "tis_name_th",
            "snapshot_date",
            "num_manufacturing_licenses",
            "num_import_licenses",
            "import_dependency_ratio",
            "domestic_share_ratio",
        ]
    ].copy()


def build_risk_index_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Compute simple supply-chain risk indicators."""
    risk_df = df[
        [
            "tis_number",
            "tis_name_th",
            "snapshot_date",
            "num_total_entrepreneurs",
            "import_dependency_ratio",
        ]
    ].copy()

    risk_df["entrepreneur_risk_raw"] = 1 / (risk_df["num_total_entrepreneurs"] + 1)
    risk_df["entrepreneur_risk_norm"] = _min_max_normalize(
        risk_df["entrepreneur_risk_raw"]
    )
    risk_df["import_dependency_norm"] = _min_max_normalize(
        risk_df["import_dependency_ratio"]
    )
    risk_df["risk_score"] = (
        50 * risk_df["entrepreneur_risk_norm"]
        + 50 * risk_df["import_dependency_norm"]
    )

    def classify(score: float) -> str:
        if score >= 70:
            return "high"
        if score >= 40:
            return "medium"
        return "low"

    risk_df["risk_label"] = risk_df["risk_score"].apply(classify)
    return risk_df


def build_latest_snapshot_summary(df: pd.DataFrame, risk_df: pd.DataFrame) -> pd.DataFrame:
    """Capture the most recent month with enriched metrics."""
    latest_date = df["snapshot_date"].max()
    latest_df = df[df["snapshot_date"] == latest_date].copy()
    risk_latest = risk_df[risk_df["snapshot_date"] == latest_date][
        ["tis_number", "risk_score", "risk_label"]
    ]
    latest_df = latest_df.merge(risk_latest, on="tis_number", how="left")
    selected_columns = [
        "tis_number",
        "tis_name_th",
        "snapshot_date",
        *LICENSE_COLUMNS,
        *ENTREPRENEUR_COLUMNS,
        "num_total_entrepreneurs",
        "total_licenses",
        "import_to_manufacturing_ratio",
        "import_dependency_ratio",
        "domestic_share_ratio",
        "display_to_total_ratio",
        "risk_score",
        "risk_label",
    ]
    return latest_df[selected_columns]


def write_dataset(df: pd.DataFrame, path: Path) -> None:
    """Persist a dataframe as CSV with ISO date formatting."""
    df_to_save = df.copy()
    if "snapshot_date" in df_to_save.columns:
        df_to_save["snapshot_date"] = df_to_save["snapshot_date"].dt.strftime("%Y-%m-%d")
    df_to_save.to_csv(path, index=False)


def main() -> None:
    """Execute the feature engineering workflow."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Loading merged dataset from %s", MERGED_FILE)
    base_df = load_base_dataframe()

    logging.info("Building clean dataset.")
    clean_df = build_clean_dataset(base_df)
    write_dataset(clean_df, CLEAN_DATASET)

    logging.info("Building trends dataset.")
    trends_df = build_trends_dataset(base_df)
    write_dataset(trends_df, TRENDS_DATASET)

    logging.info("Building import dependency dataset.")
    import_dep_df = build_import_dependency_dataset(base_df)
    write_dataset(import_dep_df, IMPORT_DEPENDENCY_DATASET)

    logging.info("Building risk index dataset.")
    risk_df = build_risk_index_dataset(base_df)
    write_dataset(risk_df, RISK_DATASET)

    logging.info("Building latest snapshot summary.")
    latest_df = build_latest_snapshot_summary(base_df, risk_df)
    write_dataset(latest_df, LATEST_SNAPSHOT_DATASET)

    logging.info("All datasets written to %s", DATASETS_DIR)


if __name__ == "__main__":
    main()
