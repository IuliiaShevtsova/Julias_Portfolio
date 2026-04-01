from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.info_notes import PAGE_NOTES, format_note

st.set_page_config(page_title="Data Quality", layout="wide", initial_sidebar_state="collapsed")

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

st.title("Data Quality")

st.info(PAGE_NOTES["data_quality_intro"])

LAYER_PATHS = {
    "silver": Path("data/silver/silver_weather.parquet"),
    "gold_1h": Path("data/gold/weather_1h.parquet"),
    "gold_1d": Path("data/gold/weather_1d.parquet"),
}

layer = st.selectbox("Layer", list(LAYER_PATHS.keys()))
path = LAYER_PATHS[layer]

if not path.exists():
    st.warning(format_note("no_data_found_resolution", resolution=layer))
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
    st.caption(
    "Quality flags indicate rows that deserve closer inspection. "
    "They are not always errors, but they represent conditions that may affect interpretation or downstream modeling."
)

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

with st.expander("How data quality is assessed"):
    st.markdown("""
    Quality assessment includes:
    - missing value counts
    - duplicate station/timestamp observations
    - invalid datetime values
    - physically implausible ranges (for example negative wind speed or humidity above 100%)
    - internal inconsistencies such as temperature outside its interval min/max
    - whether station metadata could be matched successfully
    """)