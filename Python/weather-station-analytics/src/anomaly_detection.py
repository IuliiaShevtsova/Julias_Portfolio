from __future__ import annotations

from typing import Iterable
import numpy as np
import pandas as pd


DEFAULT_VARIABLES = [
    "temp_mean",
    "rh_mean",
    "dew_point_mean",
    "precip_sum",
    "wind_speed_mean",
    "station_pressure_mean",
]


def median_abs_deviation(series: pd.Series) -> float:
    values = pd.to_numeric(series, errors="coerce").dropna()

    if values.empty:
        return np.nan

    median = np.median(values)
    mad = np.median(np.abs(values - median))
    return mad


def add_rolling_robust_anomalies(
    df: pd.DataFrame,
    variables: Iterable[str] | None = None,
    group_col: str = "station_id",
    time_col: str = "datetime",
    window: int = 24,
    threshold: float = 3.5,
    min_periods: int = 12,
) -> pd.DataFrame:
    """
    Add anomaly columns using rolling median + MAD.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe, usually hourly gold table.
    variables : iterable of str
        Numeric variables to evaluate.
    group_col : str
        Grouping column, e.g. station_id.
    time_col : str
        Datetime column.
    window : int
        Rolling window size in rows (for hourly data, 24 = 24 hours).
    threshold : float
        Robust score threshold for anomaly detection.
    min_periods : int
        Minimum required observations in rolling window.
    """
    data = df.copy()

    if variables is None:
        variables = [v for v in DEFAULT_VARIABLES if v in data.columns]
    else:
        variables = [v for v in variables if v in data.columns]

    if time_col not in data.columns:
        raise ValueError(f"Missing required time column: {time_col}")
    if group_col not in data.columns:
        raise ValueError(f"Missing required group column: {group_col}")

    data[time_col] = pd.to_datetime(data[time_col], errors="coerce")
    data = data[data[time_col].notna()].copy()
    data = data.sort_values([group_col, time_col]).reset_index(drop=True)

    for variable in variables:
        data[variable] = pd.to_numeric(data[variable], errors="coerce")

        baseline_col = f"{variable}_rolling_median"
        mad_col = f"{variable}_rolling_mad"
        score_col = f"{variable}_anomaly_score"
        flag_col = f"{variable}_is_anomaly"
        reason_col = f"{variable}_anomaly_reason"

        data[baseline_col] = (
            data.groupby(group_col)[variable]
            .transform(
                lambda s: s.rolling(window=window, min_periods=min_periods).median()
            )
        )

        data[mad_col] = (
            data.groupby(group_col)[variable]
            .transform(
                lambda s: s.rolling(window=window, min_periods=min_periods)
                .apply(median_abs_deviation, raw=False)
            )
        )

        scale = 1.4826 * data[mad_col]
        deviation = (data[variable] - data[baseline_col]).abs()

        # avoid division by zero
        score = deviation / scale.replace(0, np.nan)
        data[score_col] = score

        data[flag_col] = data[score_col] > threshold

        data[reason_col] = np.where(
            data[flag_col],
            (
                "Value deviates strongly from rolling median baseline "
                f"(threshold={threshold}, window={window})"
            ),
            pd.NA,
        )

    anomaly_flag_cols = [f"{v}_is_anomaly" for v in variables if f"{v}_is_anomaly" in data.columns]
    if anomaly_flag_cols:
        data["is_anomaly"] = data[anomaly_flag_cols].fillna(False).any(axis=1)
    else:
        data["is_anomaly"] = False

    score_cols = [f"{v}_anomaly_score" for v in variables if f"{v}_anomaly_score" in data.columns]
    if score_cols:
        data["max_anomaly_score"] = data[score_cols].max(axis=1, skipna=True)
    else:
        data["max_anomaly_score"] = np.nan

    return data