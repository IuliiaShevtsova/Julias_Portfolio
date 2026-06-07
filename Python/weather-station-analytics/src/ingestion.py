from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re
import pandas as pd

RAW_DIR = Path("data/raw/xlsx")
STATION_PATTERN = re.compile(r"station_(\d+)", re.IGNORECASE)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w_]", "", regex=True)
    )
    return df


def extract_station_id(filename: str) -> str | None:
    match = STATION_PATTERN.search(filename)
    if not match:
        return None
    return match.group(1).zfill(5)


def load_all_xlsx_to_bronze_df() -> pd.DataFrame:
    files = sorted(RAW_DIR.glob("*.xlsx"))

    if not files:
        return pd.DataFrame()

    frames = []

    for file_path in files:
        df = pd.read_excel(file_path, engine="openpyxl")
        df = standardize_columns(df)

        df["station_id"] = extract_station_id(file_path.name)
        df["source_file"] = file_path.name
        df["load_timestamp"] = datetime.utcnow()

        frames.append(df)

    bronze_df = pd.concat(frames, ignore_index=True)
    return bronze_df