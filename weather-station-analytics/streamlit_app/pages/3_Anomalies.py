from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.info_notes import PAGE_NOTES, format_note

st.set_page_config(page_title="Anomalies", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

/* Hide sidebar completely */
[data-testid="stSidebar"] {
    display: none;
}

.header-nav {
    background-color: #0b372e;
    padding: 1.25rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    color: #ecfbf9;
    border-bottom: 3px solid #374151;
}

.header-title {
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 1rem 0;
    letter-spacing: -0.5px;
}

h1 {
    color: #111827;
    font-weight: 700;
    margin-top: 0;
}
</style>

<div class="header-nav">
    <div class="header-title">Weather Analytics Dashboard</div>
</div>
""", unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("HOME", use_container_width=True, key="nav_home"):
        st.switch_page("Home.py")

with col2:
    if st.button("DATA EXPLORER", use_container_width=True, key="nav_explorer"):
        st.switch_page("pages/1_Data_Explorer.py")

with col3:
    if st.button("DATA QUALITY", use_container_width=True, key="nav_quality"):
        st.switch_page("pages/2_Data_Quality.py")

with col4:
    if st.button("ANOMALIES", use_container_width=True, key="nav_anomalies"):
        st.switch_page("pages/3_Anomalies.py")

st.title("Anomalies")

st.info(PAGE_NOTES["anomaly_intro"])

METRIC_LABELS = {
    "temp_mean": "Temperature Mean (°C)",
    "temp_median": "Temperature Median (°C)",
    "temp_min": "Min Temperature (°C)",
    "temp_max": "Max Temperature (°C)",
    "rh_mean": "Relative Humidity Mean (%)",
    "rh_median": "Relative Humidity Median (%)",
    "rh_min": "Relative Humidity Min (%)",
    "rh_max": "Relative Humidity Max (%)",
    "dew_point_mean": "Dew Point Mean (°C)",
    "dew_point_median": "Dew Point Median (°C)",
    "dew_point_min": "Dew Point Min (°C)",
    "dew_point_max": "Dew Point Max (°C)",
    "precip_sum": "Precipitation Sum (mm)",
    "precip_mean": "Precipitation Mean (mm)",
    "precip_median": "Precipitation Median (mm)",
    "precip_max": "Precipitation Max (mm)",
    "wind_speed_mean": "Wind Speed Mean (m/s)",
    "wind_speed_median": "Wind Speed Median (m/s)",
    "wind_speed_max": "Wind Speed Max (m/s)",
    "station_pressure_mean": "Station Pressure Mean (hPa)",
    "station_pressure_median": "Station Pressure Median (hPa)",
    "station_pressure_min": "Station Pressure Min (hPa)",
    "station_pressure_max": "Station Pressure Max (hPa)",
}


def get_metric_label(metric_name: str) -> str:
    return METRIC_LABELS.get(metric_name.lower(), metric_name.replace("_", " ").title())


RESOLUTION_PATHS = {
    "1h": Path("data/gold/weather_1h.parquet"),
    "1d": Path("data/gold/weather_1d.parquet"),
    "10min": Path("data/gold/weather_10min.parquet"),
}


def load_data(resolution: str) -> pd.DataFrame:
    path = RESOLUTION_PATHS[resolution]
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    return df


def get_available_anomaly_metrics(df: pd.DataFrame) -> list[str]:
    metrics = []
    for col in df.columns:
        if col.endswith("_is_anomaly"):
            metrics.append(col[:-11])  # remove "_is_anomaly"
    return sorted(metrics)


resolution = st.selectbox("Resolution", ["1h", "1d", "10min"])
df = load_data(resolution)

if df.empty:
    st.warning(format_note("no_data_found_resolution", resolution=resolution))
    st.stop()

available_anomaly_metrics = get_available_anomaly_metrics(df)

if not available_anomaly_metrics and "is_anomaly" not in df.columns:
    st.info(PAGE_NOTES["no_anomaly_columns"])
    st.stop()

station_label_col = "station_name" if "station_name" in df.columns else "station_id"

station_options = sorted(df[station_label_col].dropna().astype(str).unique().tolist())
selected_stations = st.multiselect(
    "Stations",
    station_options,
    default=station_options[:1] if station_options else []
)

if selected_stations:
    df = df[df[station_label_col].astype(str).isin(selected_stations)]

df = df[df["datetime"].notna()].copy()

if df.empty:
    st.warning(PAGE_NOTES["no_data_after_station_filter"])
    st.stop()

min_date = df["datetime"].min().date()
max_date = df["datetime"].max().date()

date_range = st.date_input(
    "Time period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    df = df[
        (df["datetime"].dt.date >= start_date) &
        (df["datetime"].dt.date <= end_date)
    ]

if df.empty:
    st.warning(PAGE_NOTES["no_data_in_time_period"])
    st.stop()

if available_anomaly_metrics:
    selected_metric = st.selectbox(
        "Metric",
        available_anomaly_metrics,
        format_func=get_metric_label
    )
    anomaly_flag_col = f"{selected_metric}_is_anomaly"
    anomaly_score_col = f"{selected_metric}_anomaly_score" if f"{selected_metric}_anomaly_score" in df.columns else None
    anomaly_reason_col = f"{selected_metric}_anomaly_reason" if f"{selected_metric}_anomaly_reason" in df.columns else None
else:
    selected_metric = None
    anomaly_flag_col = "is_anomaly"
    anomaly_score_col = "max_anomaly_score" if "max_anomaly_score" in df.columns else None
    anomaly_reason_col = None

metric_to_plot = selected_metric if selected_metric in df.columns else None
anomalies_df = df[df[anomaly_flag_col].fillna(False).astype(bool)].copy()

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows", len(df))
col2.metric("Stations", df["station_id"].nunique() if "station_id" in df.columns else 0)
col3.metric("Anomalies", len(anomalies_df))
if anomaly_score_col and anomalies_df.shape[0] > 0 and anomalies_df[anomaly_score_col].notna().any():
    col4.metric("Max anomaly score", f"{anomalies_df[anomaly_score_col].max():.2f}")
else:
    col4.metric("Max anomaly score", "n/a")

# Counts by station
if not anomalies_df.empty:
    st.subheader("Anomalies by station")
    station_counts = (
        anomalies_df.groupby(station_label_col)
        .size()
        .reset_index(name="anomaly_count")
        .sort_values("anomaly_count", ascending=False)
    )

    fig_station = px.bar(
        station_counts,
        x=station_label_col,
        y="anomaly_count",
        title="Anomaly count by station"
    )
    st.plotly_chart(fig_station, use_container_width=True)
else:
    st.info(PAGE_NOTES["no_anomalies_found"])

# Timeline plot
if metric_to_plot and metric_to_plot in df.columns:
    st.subheader(f"{get_metric_label(metric_to_plot)} with anomalies")

    fig = go.Figure()
    group_col = station_label_col if station_label_col in df.columns else "station_id"

    for station_value, station_df in df.groupby(group_col):
        fig.add_trace(
            go.Scatter(
                x=station_df["datetime"],
                y=station_df[metric_to_plot],
                mode="lines",
                name=str(station_value),
            )
        )

        station_anomalies = station_df[station_df[anomaly_flag_col].fillna(False).astype(bool)].copy()
        if not station_anomalies.empty:
            fig.add_trace(
                go.Scatter(
                    x=station_anomalies["datetime"],
                    y=station_anomalies[metric_to_plot],
                    mode="markers",
                    name=f"Anomalies - {station_value}",
                    marker=dict(color="red", size=8),
                )
            )

    fig.update_layout(
        template="plotly_white",
        height=480,
        xaxis_title="Datetime",
        yaxis_title=get_metric_label(metric_to_plot),
        legend_title="Station",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
    "Red markers show observations flagged as anomalous for the selected variable. "
    "These may indicate sensor problems, abrupt local changes, unusual meteorological conditions, or data issues."
)

# Score distribution
if anomaly_score_col and anomaly_score_col in df.columns:
    st.subheader("Anomaly score distribution")
    score_df = df[[anomaly_score_col]].dropna().copy()
    if not score_df.empty:
        fig_score = px.histogram(
            score_df,
            x=anomaly_score_col,
            nbins=40,
            title="Distribution of anomaly scores"
        )
        st.plotly_chart(fig_score, use_container_width=True)

# Daily anomaly counts
if not anomalies_df.empty:
    st.subheader("Anomaly counts over time")
    timeline_counts = (
        anomalies_df.assign(day=anomalies_df["datetime"].dt.date)
        .groupby("day")
        .size()
        .reset_index(name="anomaly_count")
    )

    fig_timeline = px.line(
        timeline_counts,
        x="day",
        y="anomaly_count",
        markers=True,
        title="Daily anomaly counts"
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

# Table
st.subheader("Anomaly table")

table_cols = ["datetime"]
if station_label_col in anomalies_df.columns:
    table_cols.append(station_label_col)
elif "station_id" in anomalies_df.columns:
    table_cols.append("station_id")

if metric_to_plot and metric_to_plot in anomalies_df.columns:
    table_cols.append(metric_to_plot)

if anomaly_score_col and anomaly_score_col in anomalies_df.columns:
    table_cols.append(anomaly_score_col)

if anomaly_reason_col and anomaly_reason_col in anomalies_df.columns:
    table_cols.append(anomaly_reason_col)

table_cols = [c for c in table_cols if c in anomalies_df.columns]

if anomalies_df.empty:
    st.info(PAGE_NOTES["no_anomalies_found"])
else:
    st.dataframe(
        anomalies_df[table_cols].sort_values("datetime"),
        use_container_width=True
    )

with st.expander("How anomalies are calculated", expanded=False):
    st.markdown("""
    **Method:** rolling median + median absolute deviation (MAD)

    For each station and variable:
    1. A rolling median is used as a local baseline.
    2. A rolling MAD is used as a robust measure of variability.
    3. The anomaly score is the absolute deviation from the rolling median, scaled by the MAD.

    In simplified form:

    `anomaly_score = |value - rolling_median| / (1.4826 × rolling_MAD)`

    A value is flagged as anomalous when this score exceeds a defined threshold.

    **Why this method?**
    - It is robust to outliers.
    - It is more stable than a plain z-score for environmental data.
    - It is easy to interpret and visualize.

    **Limitations**
    - Real weather events can also be flagged.
    - Sparse or zero-inflated variables such as precipitation may behave differently.
    - Results depend on the rolling window size and threshold.
    """)

with st.expander("How to interpret anomalies scientifically"):
    st.markdown("""
    Useful follow-up checks include:
    - comparing whether the same anomaly appears at nearby stations
    - checking whether anomalies co-occur across related variables
    - distinguishing isolated spikes from sustained shifts
    - reviewing missingness and data quality flags around anomaly periods
    - considering whether the anomaly may reflect a genuine weather event
    """)