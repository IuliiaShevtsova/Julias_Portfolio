from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.info_notes import PAGE_NOTES, format_note

st.set_page_config(page_title="Data Explorer", layout="wide", initial_sidebar_state="collapsed")

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

/* Header navigation */
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

.nav-links {
    display: flex;
    gap: 2rem;
    font-size: 0.95rem;
}

h1 {
    color: #111827;
    font-weight: 700;
    margin-top: 0;
}

h2 {
    color: #374151;
    font-weight: 600;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 0.75rem;
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

st.title("Data Explorer")

# Metric name mapping for user-friendly display
METRIC_LABELS = {
    "temp": "Temperature (°C)",
    "temperature": "Temperature (°C)",
    "temp_c": "Temperature (°C)",
    "temp_f": "Temperature (°F)",
    "t": "Temperature (°C)",
    "air_temp": "Air Temperature (°C)",
    "air_temperature": "Air Temperature (°C)",
    "temp_max": "Max Temperature (°C)",
    "temp_min": "Min Temperature (°C)",
    "temp_mean": "Temperature Mean (°C)",
    "temp_median": "Temperature Median (°C)",

    "precip": "Precipitation (mm)",
    "precipitation": "Precipitation (mm)",
    "rain": "Rain (mm)",
    "rainfall": "Rainfall (mm)",
    "precip_mm": "Precipitation (mm)",
    "precipitation_mm": "Precipitation (mm)",
    "precip_sum": "Precipitation Sum (mm)",
    "precip_mean": "Precipitation Mean (mm)",
    "precip_median": "Precipitation Median (mm)",
    "precip_max": "Precipitation Max (mm)",

    "humidity": "Humidity (%)",
    "rh": "Relative Humidity (%)",
    "rel_humidity": "Relative Humidity (%)",
    "humidity_percent": "Humidity (%)",
    "rh_mean": "Relative Humidity Mean (%)",
    "rh_median": "Relative Humidity Median (%)",
    "rh_min": "Relative Humidity Min (%)",
    "rh_max": "Relative Humidity Max (%)",

    "wind_speed": "Wind Speed (m/s)",
    "wind": "Wind Speed (m/s)",
    "ws": "Wind Speed (m/s)",
    "wind_mps": "Wind Speed (m/s)",
    "wind_speed_mean": "Wind Speed Mean (m/s)",
    "wind_speed_median": "Wind Speed Median (m/s)",
    "wind_speed_max": "Wind Speed Max (m/s)",
    "wind_direction": "Wind Direction (°)",
    "wd": "Wind Direction (°)",
    "wind_dir": "Wind Direction (°)",
    "wind_dir_circular_mean": "Wind Direction Circular Mean (°)",
    "wind_gust_max": "Wind Gust Max (m/s)",
    "wind_gust_max_mean": "Wind Gust Mean (m/s)",

    "pressure": "Pressure (hPa)",
    "pres": "Pressure (hPa)",
    "atm_pressure": "Atmospheric Pressure (hPa)",
    "pressure_hpa": "Pressure (hPa)",
    "station_pressure": "Station Pressure (hPa)",
    "station_pressure_mean": "Station Pressure Mean (hPa)",
    "station_pressure_median": "Station Pressure Median (hPa)",
    "station_pressure_min": "Station Pressure Min (hPa)",
    "station_pressure_max": "Station Pressure Max (hPa)",

    "dewpoint": "Dew Point (°C)",
    "dew_point": "Dew Point (°C)",
    "dew_point_mean": "Dew Point Mean (°C)",
    "dew_point_median": "Dew Point Median (°C)",
    "dew_point_min": "Dew Point Min (°C)",
    "dew_point_max": "Dew Point Max (°C)",

    "solar": "Solar Radiation (W/m²)",
    "solar_rad": "Solar Radiation (W/m²)",
    "radiation": "Solar Radiation (W/m²)",
    "ghi": "Global Horizontal Irradiance (W/m²)",

    "soil_temp": "Soil Temperature (°C)",
    "soil_moisture": "Soil Moisture (%)",
    "soil_humidity": "Soil Humidity (%)",

    "visibility": "Visibility (km)",
    "cloud_cover": "Cloud Cover (%)",
    "uv_index": "UV Index",

    "pm25": "PM2.5 (µg/m³)",
    "pm10": "PM10 (µg/m³)",
    "co": "Carbon Monoxide (ppm)",
    "no2": "Nitrogen Dioxide (ppb)",
    "o3": "Ozone (ppb)",
    "so2": "Sulfur Dioxide (ppb)",
}

st.info(PAGE_NOTES["data_explorer_intro"])

def get_metric_label(metric_name: str) -> str:
    return METRIC_LABELS.get(metric_name.lower(), metric_name.replace("_", " ").title())


RESOLUTION_PATHS = {
    "10min": Path("data/gold/weather_10min.parquet"),
    "1h": Path("data/gold/weather_1h.parquet"),
    "1d": Path("data/gold/weather_1d.parquet"),
}


def load_data(resolution: str) -> pd.DataFrame:
    path = RESOLUTION_PATHS[resolution]
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    return df


def get_metric_specific_anomaly_flag(metric: str, df: pd.DataFrame) -> str | None:
    candidate = f"{metric}_is_anomaly"
    if candidate in df.columns:
        return candidate
    if "is_anomaly" in df.columns:
        return "is_anomaly"
    return None


def get_metric_specific_anomaly_score(metric: str, df: pd.DataFrame) -> str | None:
    candidate = f"{metric}_anomaly_score"
    if candidate in df.columns:
        return candidate
    if "max_anomaly_score" in df.columns:
        return "max_anomaly_score"
    return None


def add_anomaly_trace(fig, station_df: pd.DataFrame, metric: str, anomaly_flag_col: str, station_value: str):
    anomalies = station_df[station_df[anomaly_flag_col].fillna(False).astype(bool)].copy()
    if anomalies.empty:
        return

    fig.add_trace(
        go.Scatter(
            x=anomalies["datetime"],
            y=anomalies[metric],
            mode="markers",
            name=f"Anomalies - {station_value}",
            marker=dict(color="red", size=8, symbol="circle"),
        )
    )

st.caption(
    "Resolution changes the level of temporal aggregation. "
    "10-minute data preserves short-term variation, hourly data reduces noise and supports anomaly detection, "
    "and daily data highlights broader patterns."
)

resolution = st.selectbox("Resolution", ["10min", "1h", "1d"])
df = load_data(resolution)

if df.empty:
    st.warning(format_note("no_data_found_resolution", resolution=resolution))
    st.stop()


# station filter
station_label_col = "station_name" if "station_name" in df.columns else "station_id"

station_options = sorted(df[station_label_col].dropna().astype(str).unique().tolist())
selected_stations = st.multiselect(
    "Stations",
    station_options,
    default=station_options[:1] if station_options else []
)

if selected_stations:
    df = df[df[station_label_col].astype(str).isin(selected_stations)]

# time filter
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

# metric filter

with st.expander("Scientifically useful metric combinations"):
    st.markdown("""
    Useful combinations include:
    - **Dew point + relative humidity** to examine moisture conditions
    - **Temperature + precipitation** to inspect rain events and thermal shifts
    - **Pressure + wind speed** to explore changing weather systems
    - **Temperature mean + temperature min/max** to compare central tendency and extremes
    """)

excluded = {
    "datetime", "station_id", "source_file", "load_timestamp",
    "station_metadata_matched", "resolution"
}
metrics = [
    c for c in df.columns
    if c not in excluded
    and not c.startswith("is_")
    and not c.endswith("_anomaly_score")
    and not c.endswith("_anomaly_reason")
    and not c.endswith("_rolling_median")
    and not c.endswith("_rolling_mad")
    and not c.endswith("_count")
    and not c.endswith("_missing_ratio")
    and pd.api.types.is_numeric_dtype(df[c])
]

selected_metrics = st.multiselect(
    "Metrics",
    metrics,
    default=metrics[:2] if len(metrics) >= 2 else metrics,
    format_func=get_metric_label
)

show_mean = st.checkbox("Show mean", value=True)
show_std = st.checkbox("Show ±1 std", value=True)
show_anomalies = st.checkbox("Show anomalies", value=True)

if not selected_metrics:
    st.info(PAGE_NOTES["select_at_least_one_metric"])
    st.stop()

with st.expander("Metric Labels Reference", expanded=False):
    labels_df = pd.DataFrame({
        "Column Name": selected_metrics,
        "Display Label": [get_metric_label(m) for m in selected_metrics]
    })
    st.dataframe(labels_df, use_container_width=True, hide_index=True)

# KPI row
primary_metric = selected_metrics[0]
primary_anomaly_flag = get_metric_specific_anomaly_flag(primary_metric, df)
primary_anomaly_count = int(df[primary_anomaly_flag].fillna(False).astype(bool).sum()) if primary_anomaly_flag else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Rows", len(df))
col2.metric("Stations", df["station_id"].nunique() if "station_id" in df.columns else 0)
col3.metric("Mean", f"{df[primary_metric].mean():.2f}" if df[primary_metric].notna().any() else "n/a")
col4.metric("Std", f"{df[primary_metric].std():.2f}" if df[primary_metric].notna().any() else "n/a")
col5.metric("Anomalies", primary_anomaly_count)

plot_df = df.sort_values("datetime").copy()
group_col = station_label_col if station_label_col in plot_df.columns else "station_id"

plotting_mode = st.radio(
    "Plotting Mode",
    ["Separate plots", "Combined plot", "Custom grouping"],
    help="Choose how to display multiple metrics"
)

if plotting_mode == "Separate plots":
    for metric in selected_metrics:
        metric_label = get_metric_label(metric)
        anomaly_flag_col = get_metric_specific_anomaly_flag(metric, plot_df)

        st.subheader(f"{metric_label} over time")

        fig = go.Figure()

        for station_value, station_df in plot_df.groupby(group_col):
            fig.add_trace(
                go.Scatter(
                    x=station_df["datetime"],
                    y=station_df[metric],
                    mode="lines",
                    name=str(station_value),
                )
            )

            if show_anomalies and anomaly_flag_col:
                add_anomaly_trace(fig, station_df, metric, anomaly_flag_col, str(station_value))

        if show_mean and pd.api.types.is_numeric_dtype(plot_df[metric]):
            mean_val = plot_df[metric].mean()
            fig.add_hline(y=mean_val, line_dash="dash", annotation_text="mean")

        if show_std and pd.api.types.is_numeric_dtype(plot_df[metric]):
            mean_val = plot_df[metric].mean()
            std_val = plot_df[metric].std()
            fig.add_hline(y=mean_val + std_val, line_dash="dot")
            fig.add_hline(y=mean_val - std_val, line_dash="dot")

        fig.update_layout(
            xaxis_title="Datetime",
            yaxis_title=metric_label,
            legend_title="Station",
            template="plotly_white",
            height=420
        )

        st.plotly_chart(fig, use_container_width=True)

        if anomaly_flag_col:
            anomaly_count = int(plot_df[anomaly_flag_col].fillna(False).astype(bool).sum())
            st.caption(f"Detected anomalies for {metric_label}: {anomaly_count}")

        st.caption(
            "Dashed lines show the mean and dotted lines show ±1 standard deviation for the displayed variable. "
            "These help identify unusually high or low values relative to the filtered subset."
        )

elif plotting_mode == "Combined plot":
    st.subheader("Combined Metrics over time")

    fig = go.Figure()

    primary_metric = selected_metrics[0]
    primary_label = get_metric_label(primary_metric)
    primary_anomaly_flag = get_metric_specific_anomaly_flag(primary_metric, plot_df)

    for station_value, station_df in plot_df.groupby(group_col):
        fig.add_trace(
            go.Scatter(
                x=station_df["datetime"],
                y=station_df[primary_metric],
                mode="lines",
                name=f"{primary_label} - {station_value}",
                line=dict(width=2),
            )
        )

        if show_anomalies and primary_anomaly_flag:
            add_anomaly_trace(fig, station_df, primary_metric, primary_anomaly_flag, str(station_value))

    for i, metric in enumerate(selected_metrics[1:], 1):
        metric_label = get_metric_label(metric)

        for station_value, station_df in plot_df.groupby(group_col):
            fig.add_trace(
                go.Scatter(
                    x=station_df["datetime"],
                    y=station_df[metric],
                    mode="lines",
                    name=f"{metric_label} - {station_value}",
                    yaxis=f"y{i+1}",
                    line=dict(dash="dash" if i % 2 == 0 else "solid"),
                )
            )

    layout_kwargs = {
        "xaxis_title": "Datetime",
        "template": "plotly_white",
        "height": 520,
        "legend_title": "Metrics & Stations",
    }

    for i, metric in enumerate(selected_metrics):
        axis_name = "yaxis" if i == 0 else f"yaxis{i+1}"
        axis_title = get_metric_label(metric)
        layout_kwargs[axis_name] = {
            "title": axis_title,
            "overlaying": "y" if i > 0 else None,
            "side": "right" if i > 0 else "left",
            "showgrid": False if i > 0 else True,
        }

    fig.update_layout(**layout_kwargs)

    if show_mean and pd.api.types.is_numeric_dtype(plot_df[primary_metric]):
        mean_val = plot_df[primary_metric].mean()
        fig.add_hline(y=mean_val, line_dash="dash", annotation_text=f"{primary_label} mean")

    if show_std and pd.api.types.is_numeric_dtype(plot_df[primary_metric]):
        mean_val = plot_df[primary_metric].mean()
        std_val = plot_df[primary_metric].std()
        fig.add_hline(y=mean_val + std_val, line_dash="dot", annotation_text=f"{primary_label} +1σ")
        fig.add_hline(y=mean_val - std_val, line_dash="dot", annotation_text=f"{primary_label} -1σ")

    st.plotly_chart(fig, use_container_width=True)

elif plotting_mode == "Custom grouping":
    st.subheader("Custom Metric Grouping")

    if len(selected_metrics) <= 2:
        groups = [selected_metrics]
        st.info(PAGE_NOTES["combined_plot_note"])
    else:
        col1, col2 = st.columns(2)

        with col1:
            group1_metrics = st.multiselect(
                "Group 1 Metrics",
                selected_metrics,
                default=[selected_metrics[0]],
                key="group1"
            )

        with col2:
            remaining_metrics = [m for m in selected_metrics if m not in group1_metrics]
            group2_metrics = st.multiselect(
                "Group 2 Metrics",
                remaining_metrics,
                default=remaining_metrics[:2] if remaining_metrics else [],
                key="group2"
            )

        groups = [group1_metrics, group2_metrics] if group2_metrics else [group1_metrics]

    for i, group_metrics in enumerate(groups):
        if not group_metrics:
            continue

        subplot_title = f"Group {i+1}: {', '.join([get_metric_label(m) for m in group_metrics])}"
        st.subheader(subplot_title)

        fig = go.Figure()

        for j, metric in enumerate(group_metrics):
            metric_label = get_metric_label(metric)
            anomaly_flag_col = get_metric_specific_anomaly_flag(metric, plot_df)

            for station_value, station_df in plot_df.groupby(group_col):
                fig.add_trace(
                    go.Scatter(
                        x=station_df["datetime"],
                        y=station_df[metric],
                        mode="lines",
                        name=f"{metric_label} - {station_value}",
                        yaxis=f"y{j+1}" if j > 0 else "y",
                        line=dict(dash=["solid", "dash", "dot"][j % 3]),
                    )
                )

                if show_anomalies and j == 0 and anomaly_flag_col:
                    add_anomaly_trace(fig, station_df, metric, anomaly_flag_col, str(station_value))

        layout_kwargs = {
            "xaxis_title": "Datetime",
            "template": "plotly_white",
            "height": 420,
            "legend_title": "Metrics & Stations",
        }

        for j, metric in enumerate(group_metrics):
            axis_name = "yaxis" if j == 0 else f"yaxis{j+1}"
            axis_title = get_metric_label(metric)
            layout_kwargs[axis_name] = {
                "title": axis_title,
                "overlaying": "y" if j > 0 else None,
                "side": "right" if j > 0 else "left",
                "showgrid": False if j > 0 else True,
            }

        fig.update_layout(**layout_kwargs)
        st.plotly_chart(fig, use_container_width=True)

    st.caption("Dashed lines show the mean and dotted lines show ±1 standard deviation for the displayed variable. "
            "These help identify unusually high or low values relative to the filtered subset."
        )

# Summary statistics
st.subheader("Summary statistics")
stats_df = df[selected_metrics].describe().T.reset_index().rename(columns={"index": "metric"})
stats_df["metric"] = stats_df["metric"].apply(get_metric_label)
st.dataframe(stats_df, use_container_width=True)

# Anomaly summary
available_anomaly_metrics = [m for m in selected_metrics if get_metric_specific_anomaly_flag(m, df)]
if available_anomaly_metrics:
    st.subheader("Anomaly summary")
    anomaly_summary = []
    for metric in available_anomaly_metrics:
        flag_col = get_metric_specific_anomaly_flag(metric, df)
        score_col = get_metric_specific_anomaly_score(metric, df)

        anomaly_summary.append({
            "metric": get_metric_label(metric),
            "anomaly_count": int(df[flag_col].fillna(False).astype(bool).sum()) if flag_col else 0,
            "max_score": round(float(df[score_col].max()), 3) if score_col and df[score_col].notna().any() else None,
        })

    anomaly_summary_df = pd.DataFrame(anomaly_summary)
    st.dataframe(anomaly_summary_df, use_container_width=True, hide_index=True)

# Data preview
st.subheader("Filtered data preview")
preview_cols = ["datetime", group_col] + selected_metrics
extra_cols = []

for metric in selected_metrics:
    flag_col = get_metric_specific_anomaly_flag(metric, df)
    score_col = get_metric_specific_anomaly_score(metric, df)
    if flag_col and flag_col not in extra_cols:
        extra_cols.append(flag_col)
    if score_col and score_col not in extra_cols:
        extra_cols.append(score_col)

preview_cols = [c for c in preview_cols + extra_cols if c in df.columns]
st.dataframe(df[preview_cols].sort_values("datetime"), use_container_width=True)