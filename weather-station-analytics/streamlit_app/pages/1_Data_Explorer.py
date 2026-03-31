from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("Data Explorer")

RESOLUTION_PATHS = {
    "10min": Path("data/silver/silver_weather.parquet"),
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

resolution = st.selectbox("Resolution", ["10min", "1h", "1d"])
df = load_data(resolution)

if df.empty:
    st.warning(f"No data found for resolution: {resolution}")
    st.stop()

# station filter
if "station_name" in df.columns:
    station_label_col = "station_name"
else:
    station_label_col = "station_id"

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

# metric filter
excluded = {
    "datetime", "station_id", "source_file", "load_timestamp",
    "station_metadata_matched", "resolution"
}
metrics = [
    c for c in df.columns
    if c not in excluded
    and not c.startswith("is_")
    and pd.api.types.is_numeric_dtype(df[c])
]

selected_metrics = st.multiselect(
    "Metrics",
    metrics,
    default=metrics[:2] if len(metrics) >= 2 else metrics
)

show_mean = st.checkbox("Show mean", value=True)
show_std = st.checkbox("Show ±1 std", value=True)
show_anomalies = st.checkbox("Show anomalies", value=True)

if not selected_metrics:
    st.info("Select at least one metric.")
    st.stop()

plot_metric = st.selectbox("Metric to plot", selected_metrics)

# KPI row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows", len(df))
col2.metric("Stations", df["station_id"].nunique() if "station_id" in df.columns else 0)
col3.metric("Mean", f"{df[plot_metric].mean():.2f}" if df[plot_metric].notna().any() else "n/a")
col4.metric("Std", f"{df[plot_metric].std():.2f}" if df[plot_metric].notna().any() else "n/a")

# plot
plot_df = df.sort_values("datetime").copy()

fig = go.Figure()

# split by station for cleaner legend
group_col = station_label_col if station_label_col in plot_df.columns else "station_id"

for station_value, station_df in plot_df.groupby(group_col):
    fig.add_trace(
        go.Scatter(
            x=station_df["datetime"],
            y=station_df[plot_metric],
            mode="lines",
            name=str(station_value),
        )
    )

if show_mean and pd.api.types.is_numeric_dtype(plot_df[plot_metric]):
    mean_val = plot_df[plot_metric].mean()
    fig.add_hline(y=mean_val, line_dash="dash", annotation_text="mean")

if show_std and pd.api.types.is_numeric_dtype(plot_df[plot_metric]):
    mean_val = plot_df[plot_metric].mean()
    std_val = plot_df[plot_metric].std()
    fig.add_hline(y=mean_val + std_val, line_dash="dot")
    fig.add_hline(y=mean_val - std_val, line_dash="dot")

if show_anomalies and "is_anomaly" in plot_df.columns:
    anomalies = plot_df[plot_df["is_anomaly"] == True]
    if not anomalies.empty:
        fig.add_trace(
            go.Scatter(
                x=anomalies["datetime"],
                y=anomalies[plot_metric],
                mode="markers",
                name="Anomalies",
                marker=dict(color="red", size=8),
            )
        )

fig.update_layout(
    title=f"{plot_metric} over time",
    xaxis_title="Datetime",
    yaxis_title=plot_metric,
    legend_title="Station",
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)

# stats table
st.subheader("Summary statistics")
stats_df = df[selected_metrics].describe().T.reset_index().rename(columns={"index": "metric"})
st.dataframe(stats_df, use_container_width=True)

# data preview
st.subheader("Filtered data preview")
preview_cols = ["datetime", group_col] + selected_metrics
preview_cols = [c for c in preview_cols if c in df.columns]
st.dataframe(df[preview_cols].sort_values("datetime"), use_container_width=True)