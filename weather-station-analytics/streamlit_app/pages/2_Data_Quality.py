from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Data Quality")

LAYER_PATHS = {
    "silver": Path("data/silver/silver_weather.parquet"),
    "gold_1h": Path("data/gold/weather_1h.parquet"),
    "gold_1d": Path("data/gold/weather_1d.parquet"),
}

layer = st.selectbox("Layer", list(LAYER_PATHS.keys()))
path = LAYER_PATHS[layer]

if not path.exists():
    st.warning(f"{layer} dataset not found.")
    st.stop()

df = pd.read_parquet(path)

if "datetime" in df.columns:
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

summary = pd.DataFrame({
    "column": df.columns,
    "missing_count": df.isna().sum().values,
    "missing_ratio": df.isna().mean().round(4).values,
    "dtype": df.dtypes.astype(str).values,
})

st.subheader("Missing values summary")
st.dataframe(summary, use_container_width=True)

fig = px.bar(
    summary.sort_values("missing_count", ascending=False),
    x="column",
    y="missing_count",
    title="Missing values by column"
)
st.plotly_chart(fig, use_container_width=True)

if "station_metadata_matched" in df.columns:
    match_rate = df["station_metadata_matched"].mean() * 100
    st.metric("Metadata matched", f"{match_rate:.1f}%")

flag_columns = [c for c in df.columns if c.startswith("is_")]
if flag_columns:
    st.subheader("Quality flags")
    flag_summary = pd.DataFrame({
        "flag": flag_columns,
        "true_count": [int(df[c].fillna(False).astype(bool).sum()) for c in flag_columns]
    })
    st.dataframe(flag_summary, use_container_width=True)

    fig_flags = px.bar(flag_summary, x="flag", y="true_count", title="Triggered quality flags")
    st.plotly_chart(fig_flags, use_container_width=True)

if {"station_id", "datetime"}.issubset(df.columns):
    duplicate_count = int(df.duplicated(subset=["station_id", "datetime"]).sum())
    st.metric("Duplicate station/timestamp rows", duplicate_count)

if "station_id" in df.columns:
    per_station = (
        df.groupby("station_id")
        .size()
        .reset_index(name="row_count")
        .sort_values("row_count", ascending=False)
    )
    st.subheader("Rows by station")
    st.dataframe(per_station, use_container_width=True)