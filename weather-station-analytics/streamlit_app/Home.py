from pathlib import Path
import streamlit as st
import pandas as pd
from utils.info_notes import PAGE_NOTES

st.set_page_config(page_title="Weather Pipeline Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for styling
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

div[data-testid="stMetric"] {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    min-height: 90px;
}

div[data-testid="stMetric"] > div > div {
    font-size: 0.9rem !important;
    line-height: 1.2 !important;
}

div[data-testid="stMetric"] > div > div:first-child {
    font-size: 0.75rem !important;
    color: #6b7280 !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 0.25rem !important;
}

div[data-testid="stMetric"] > div > div:last-child {
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    color: #1f2937 !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}

/* Main content styling */
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

st.info(PAGE_NOTES["dashboard_overview"])

with st.expander("What scientific exploration can be done here"):
    st.markdown(PAGE_NOTES["scientific_exploration"])

st.title("Pipeline Overview")
st.write("Real-time monitoring and analysis of weather data processing pipeline")

silver_path = Path("data/silver/silver_weather.parquet")
gold_1h_path = Path("data/gold/weather_1h.parquet")
gold_1d_path = Path("data/gold/weather_1d.parquet")

if not silver_path.exists():
    st.warning(PAGE_NOTES["silver_dataset_not_found"])
    st.stop()

silver = pd.read_parquet(silver_path)
silver["datetime"] = pd.to_datetime(silver["datetime"], errors="coerce")

n_stations = silver["station_id"].nunique() if "station_id" in silver.columns else 0
min_dt = silver["datetime"].min()
max_dt = silver["datetime"].max()
n_rows = len(silver)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Stations", n_stations)
col2.metric("Rows (silver)", n_rows)
col3.metric("Start", min_dt.strftime("%Y-%m-%d %H:%M") if pd.notna(min_dt) else "n/a")
col4.metric("End", max_dt.strftime("%Y-%m-%d %H:%M") if pd.notna(max_dt) else "n/a")

if "station_metadata_matched" in silver.columns:
    match_rate = silver["station_metadata_matched"].mean() * 100
    st.metric("Metadata matched", f"{match_rate:.1f}%")

st.subheader("Available resolutions")
available = []
if silver_path.exists():
    available.append("10min")
if gold_1h_path.exists():
    available.append("1h")
if gold_1d_path.exists():
    available.append("1d")

st.write(", ".join(available) if available else "No datasets found")

st.subheader("Pipeline layers")
st.markdown("""
- **Bronze**: raw ingested observations from XLSX
- **Silver**: cleaned and validated observations with station metadata
- **Gold**: aggregated observations for dashboarding and anomaly analysis
""")

station_cols = [c for c in ["station_id", "station_name"] if c in silver.columns]
if station_cols:
    st.subheader("Stations preview")
    st.dataframe(
        silver[station_cols].drop_duplicates().sort_values("station_id"),
        use_container_width=True
    )