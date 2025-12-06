"""Pipeline step for merging raw TISI CSV snapshots into a single dataset."""
from __future__ import annotations

import logging
import re
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "tisi_licenses_merged.csv"

SNAPSHOT_PATTERN = re.compile(r"tis_(\d{4})_(\d{2})")
POSSIBLE_ENCODINGS: Sequence[str] = ("cp874", "tis-620", "utf-8-sig", "latin1")

COLUMN_MAP_TH: Dict[str, str] = {
    "ลำดับ": "row_index",
    "เลขที่ มอก.": "tis_number",
    "ชื่อ มอก. ภาษาไทย": "tis_name_th",
    "ชื่อ มอก. ภาษาอังกฤษ": "tis_name_en",
    "ประเภทมาตรฐาน": "standard_type",
    "จำนวนใบอนุญาตทำ": "num_manufacturing_licenses",
    "จำนวนผู้ประกอบการทำ": "num_manufacturing_entrepreneurs",
    "จำนวนใบอนุญาตนำเข้า": "num_import_licenses",
    "จำนวนผู้ประกอบการนำเข้า": "num_import_entrepreneurs",
    "จำนวนใบอนุญาตแสดง": "num_display_licenses",
    "จำนวนผู้ประกอบการแสดง": "num_display_entrepreneurs",
    "จำนวนใบอนุญาตทั้งหมด": "total_licenses",
}

COLUMN_ALIASES: Dict[str, str] = {
    "row_index": "row_index",
    "tis_no": "tis_number",
    "tis_number": "tis_number",
    "tis_standard_number": "tis_number",
    "standard_number": "tis_number",
    "standard_no": "tis_number",
    "tis_name_th": "tis_name_th",
    "thai_standard_name": "tis_name_th",
    "standard_name_th": "tis_name_th",
    "num_manufacturing_licenses": "num_manufacturing_licenses",
    "manufacturing_license_count": "num_manufacturing_licenses",
    "manufacturing_licenses": "num_manufacturing_licenses",
    "num_manufacturing_entrepreneurs": "num_manufacturing_entrepreneurs",
    "manufacturing_entrepreneurs": "num_manufacturing_entrepreneurs",
    "num_import_licenses": "num_import_licenses",
    "import_license_count": "num_import_licenses",
    "num_import_entrepreneurs": "num_import_entrepreneurs",
    "import_entrepreneurs": "num_import_entrepreneurs",
    "num_display_licenses": "num_display_licenses",
    "display_license_count": "num_display_licenses",
    "num_display_entrepreneurs": "num_display_entrepreneurs",
    "display_entrepreneurs": "num_display_entrepreneurs",
    "total_licenses": "total_licenses",
    "total_license_count": "total_licenses",
    "standard_type": "standard_type",
    "tis_name_en": "tis_name_en",
}

REQUIRED_COLUMNS: List[str] = [
    "tis_number",
    "tis_name_th",
    "num_manufacturing_licenses",
    "num_manufacturing_entrepreneurs",
    "num_import_licenses",
    "num_import_entrepreneurs",
    "num_display_licenses",
    "num_display_entrepreneurs",
]


def normalize_column_name(column_name: str) -> str:
    """Convert column names to ASCII snake_case for easier matching."""
    normalized = (
        column_name.strip()
        .lower()
        .encode("ascii", "ignore")
        .decode("ascii")
        .replace("%", "pct")
    )
    normalized_chars = [
        ch if (ch.isalnum() or ch == "_") else "_"
        for ch in normalized.replace(" ", "_")
    ]
    collapsed = re.sub(r"_+", "_", "".join(normalized_chars)).strip("_")
    return collapsed


def canonicalize_column_name(column_name: str, index: int) -> str:
    """Return the canonical column name based on alias mappings."""
    stripped = column_name.strip()
    normalized = normalize_column_name(stripped)
    alias_key_candidates = [stripped, normalized]
    for candidate in alias_key_candidates:
        if candidate in COLUMN_ALIASES:
            return COLUMN_ALIASES[candidate]
    fallback = normalized or f"column_{index}"
    return fallback


def infer_snapshot_date(file_path: Path) -> date:
    """Infer the snapshot date from the file name."""
    match = SNAPSHOT_PATTERN.search(file_path.stem)
    if match:
        year, month = match.groups()
        return date(int(year), int(month), 1)

    modified_dt = datetime.fromtimestamp(file_path.stat().st_mtime)
    logging.warning(
        "File name %s does not match tis_YYYY_MM pattern. "
        "Using file modified month %s-%s as snapshot_date.",
        file_path.name,
        modified_dt.year,
        modified_dt.month,
    )
    return date(modified_dt.year, modified_dt.month, 1)


def read_csv_with_fallback(file_path: Path) -> pd.DataFrame:
    """Load CSV using multiple encodings until one succeeds."""
    last_error: Exception | None = None
    for encoding in POSSIBLE_ENCODINGS:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise UnicodeDecodeError(
        "utf-8", b"", 0, 1, f"Unable to decode {file_path} with known encodings."
    ) from last_error


def prepare_dataframe(file_path: Path) -> pd.DataFrame:
    """Load and standardize a raw CSV file."""
    df = read_csv_with_fallback(file_path)
    df = df.rename(columns=lambda col: COLUMN_MAP_TH.get(col.strip(), col))
    new_columns = [
        canonicalize_column_name(column_name, idx)
        for idx, column_name in enumerate(df.columns)
    ]
    df.columns = new_columns

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise KeyError(
            f"Missing required columns {missing} after normalization in {file_path.name}."
        )

    for numeric_col in REQUIRED_COLUMNS[2:]:
        df[numeric_col] = pd.to_numeric(df[numeric_col], errors="coerce")

    if "total_licenses" in df.columns:
        df["total_licenses"] = pd.to_numeric(df["total_licenses"], errors="coerce")

    snapshot_str = infer_snapshot_date(file_path).isoformat()
    df["snapshot_date"] = snapshot_str
    return df[
        [
            "tis_number",
            "tis_name_th",
            "num_manufacturing_licenses",
            "num_manufacturing_entrepreneurs",
            "num_import_licenses",
            "num_import_entrepreneurs",
            "num_display_licenses",
            "num_display_entrepreneurs",
            *(["total_licenses"] if "total_licenses" in df.columns else []),
            "snapshot_date",
        ]
    ]


def load_all_raw_files(files: Iterable[Path]) -> pd.DataFrame:
    """Read all provided CSV files and concatenate them into one DataFrame."""
    frames = [prepare_dataframe(file_path) for file_path in files]
    merged = pd.concat(frames, ignore_index=True)
    subset_cols = [
        "tis_number",
        "snapshot_date",
        "num_manufacturing_licenses",
        "num_manufacturing_entrepreneurs",
        "num_import_licenses",
        "num_import_entrepreneurs",
        "num_display_licenses",
        "num_display_entrepreneurs",
    ]
    if "total_licenses" in merged.columns:
        subset_cols.append("total_licenses")
    merged = merged.drop_duplicates(subset=subset_cols)
    merged = merged.sort_values(["tis_number", "snapshot_date"]).reset_index(drop=True)
    return merged


def main() -> None:
    """Entry point for merging raw CSV snapshots."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")

    logging.info("Processing %s raw files.", len(csv_files))
    merged_df = load_all_raw_files(csv_files)
    merged_df.to_csv(OUTPUT_FILE, index=False)
    logging.info("Merged dataset written to %s", OUTPUT_FILE)


if __name__ == "__main__":
    main()
