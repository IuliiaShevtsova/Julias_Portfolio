from __future__ import annotations

from pathlib import Path
import pandas as pd

STATION_METADATA_PATH = Path("data/raw/stations/station_metadata.csv")

EXPECTED_COLUMNS = [
    "datetime",
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
    "station_id",
    "source_file",
    "load_timestamp",
]

NUMERIC_COLUMNS = [
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


def validate_required_columns(df: pd.DataFrame) -> None:
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def parse_datetime_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    return df


def parse_load_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["load_timestamp"] = pd.to_datetime(df["load_timestamp"], errors="coerce")
    return df


def coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def remove_duplicates_and_sort(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # duplicate observations for same station and timestamp
    df = df.drop_duplicates(subset=["station_id", "datetime"], keep="last")

    df = df.sort_values(["station_id", "datetime"]).reset_index(drop=True)
    return df


def apply_basic_range_checks(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # relative humidity [%]
    df.loc[(df["rh"] < 0) | (df["rh"] > 100), "rh"] = pd.NA

    # precipitation should not be negative
    df.loc[df["precip"] < 0, "precip"] = pd.NA

    # wind direction [degrees]
    df.loc[(df["wind_dir"] < 0) | (df["wind_dir"] > 360), "wind_dir"] = pd.NA

    # wind speed / gust should not be negative
    df.loc[df["wind_speed"] < 0, "wind_speed"] = pd.NA
    df.loc[df["wind_gust_max"] < 0, "wind_gust_max"] = pd.NA

    # broad physical sanity checks
    df.loc[(df["temp"] < -80) | (df["temp"] > 60), "temp"] = pd.NA
    df.loc[(df["temp_min"] < -80) | (df["temp_min"] > 60), "temp_min"] = pd.NA
    df.loc[(df["temp_max"] < -80) | (df["temp_max"] > 60), "temp_max"] = pd.NA
    df.loc[(df["dew_point"] < -100) | (df["dew_point"] > 60), "dew_point"] = pd.NA

    # station pressure [hPa]
    df.loc[
        (df["station_pressure"] < 850) | (df["station_pressure"] > 1100),
        "station_pressure"
    ] = pd.NA

    return df


def add_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["is_datetime_missing"] = df["datetime"].isna()

    df["is_temp_inconsistent"] = (
        df["temp_min"].notna()
        & df["temp_max"].notna()
        & (df["temp_min"] > df["temp_max"])
    )

    df["is_temp_outside_interval_bounds"] = (
        df["temp"].notna()
        & df["temp_min"].notna()
        & df["temp_max"].notna()
        & ((df["temp"] < df["temp_min"]) | (df["temp"] > df["temp_max"]))
    )

    df["is_wind_gust_below_speed"] = (
        df["wind_gust_max"].notna()
        & df["wind_speed"].notna()
        & (df["wind_gust_max"] < df["wind_speed"])
    )

    df["is_station_id_missing"] = df["station_id"].isna()

    return df


def load_station_metadata() -> pd.DataFrame:
    if not STATION_METADATA_PATH.exists():
        return pd.DataFrame(columns=["station_id"])

    stations = pd.read_csv(STATION_METADATA_PATH, dtype={"station_id": str})
    stations = standardize_columns(stations)

    if "station_id" not in stations.columns:
        raise ValueError("station_metadata.csv must contain a 'station_id' column.")

    stations["station_id"] = stations["station_id"].astype(str).str.zfill(5)
    return stations


def join_station_metadata(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["station_id"] = df["station_id"].astype(str).str.zfill(5)

    stations = load_station_metadata()

    if stations.empty:
        df["station_metadata_matched"] = False
        return df

    joined = df.merge(stations, on="station_id", how="left", suffixes=("", "_station"))
    station_cols = [c for c in stations.columns if c != "station_id"]

    if station_cols:
        joined["station_metadata_matched"] = joined[station_cols].notna().any(axis=1)
    else:
        joined["station_metadata_matched"] = True

    return joined


def clean_bronze_df(bronze_df: pd.DataFrame) -> pd.DataFrame:
    df = bronze_df.copy()

    df = standardize_columns(df)
    validate_required_columns(df)
    df = parse_datetime_column(df)
    df = parse_load_timestamp(df)
    df = coerce_numeric_columns(df)
    df = remove_duplicates_and_sort(df)
    df = apply_basic_range_checks(df)
    df = add_quality_flags(df)
    df = join_station_metadata(df)

    return df