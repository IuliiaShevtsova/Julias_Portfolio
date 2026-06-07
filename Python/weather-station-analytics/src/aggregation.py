from __future__ import annotations

import math
import numpy as np
import pandas as pd

AGG_RULES = {
    "temp": ["mean", "median"],
    "temp_min": ["min"],
    "temp_max": ["max"],
    "rh": ["mean", "median", "min", "max"],
    "dew_point": ["mean", "median", "min", "max"],
    "precip": ["sum", "mean", "median", "max"],
    "wind_speed": ["mean", "median", "max"],
    "station_pressure": ["mean", "median", "min", "max"],
    "wind_gust_max": ["max", "mean"],
}

BASE_REQUIRED_COLUMNS = [
    "datetime",
    "station_id",
    "temp",
    "temp_min",
    "temp_max",
    "rh",
    "dew_point",
    "precip",
    "wind_speed",
    "wind_dir",
    "station_pressure",
    "wind_gust_max",
]


def circular_mean_degrees(series: pd.Series) -> float:
    values = pd.to_numeric(series, errors="coerce").dropna()

    if values.empty:
        return np.nan

    radians = np.deg2rad(values)
    sin_mean = np.mean(np.sin(radians))
    cos_mean = np.mean(np.cos(radians))

    angle = math.degrees(math.atan2(sin_mean, cos_mean))
    return angle % 360


def count_non_null(series: pd.Series) -> int:
    return int(series.notna().sum())


def missing_ratio(series: pd.Series) -> float:
    if len(series) == 0:
        return np.nan
    return float(series.isna().mean())


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        f"{col}_{stat}" if isinstance(col, str) else "_".join(col).strip("_")
        for col, stat in df.columns
    ]
    return df


def _rename_temperature_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rename_map = {
        "temp_min_min": "temp_min",
        "temp_max_max": "temp_max",
    }
    return df.rename(columns=rename_map)


def build_aggregated_table(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    missing = [col for col in BASE_REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for aggregation: {missing}")

    data = df.copy()
    data["datetime"] = pd.to_datetime(data["datetime"], errors="coerce")
    data = data[data["datetime"].notna()].copy()
    data = data.sort_values(["station_id", "datetime"])

    # keep station metadata columns if present
    metadata_cols = [
        c for c in data.columns
        if c not in BASE_REQUIRED_COLUMNS
        and not c.startswith("is_")
        and c not in ["source_file", "load_timestamp"]
    ]

    grouped = data.set_index("datetime").groupby("station_id").resample(freq)

    aggregated = grouped.agg(AGG_RULES)
    aggregated = _flatten_columns(aggregated)

    # circular mean for wind direction
    wind_dir = grouped["wind_dir"].apply(circular_mean_degrees)
    aggregated["wind_dir_circular_mean"] = wind_dir

    # counts / missingness
    value_cols = [c for c in BASE_REQUIRED_COLUMNS if c not in ["datetime", "station_id"]]
    for col in value_cols:
        aggregated[f"{col}_count"] = grouped[col].apply(count_non_null)
        aggregated[f"{col}_missing_ratio"] = grouped[col].apply(missing_ratio)

    aggregated = aggregated.reset_index()
    aggregated = _rename_temperature_columns(aggregated)

    # bring back station metadata
    if metadata_cols:
        station_metadata = data[["station_id"] + metadata_cols].drop_duplicates(subset=["station_id"])
        aggregated = aggregated.merge(station_metadata, on="station_id", how="left")

    aggregated["resolution"] = freq

    return aggregated


def build_gold_10min(df: pd.DataFrame) -> pd.DataFrame:
    gold_10min = df.copy()
    gold_10min["datetime"] = pd.to_datetime(gold_10min["datetime"], errors="coerce")
    gold_10min = gold_10min[gold_10min["datetime"].notna()].copy()
    gold_10min = gold_10min.sort_values(["station_id", "datetime"]).reset_index(drop=True)
    gold_10min["resolution"] = "10min"
    return gold_10min


def build_gold_1h(df: pd.DataFrame) -> pd.DataFrame:
    return build_aggregated_table(df, freq="1h")


def build_gold_1d(df: pd.DataFrame) -> pd.DataFrame:
    return build_aggregated_table(df, freq="1D")