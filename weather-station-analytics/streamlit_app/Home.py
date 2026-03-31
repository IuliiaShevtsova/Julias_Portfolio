from pathlib import Path
import streamlit as st
import pandas as pd

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #E5E7EB;
    padding: 1rem;
    border-radius: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Weather Pipeline Dashboard", layout="wide")

st.title("Weather Pipeline Dashboard")
st.write("Interactive reporting for weather data processing, aggregation, and anomaly analysis.")

silver_path = Path("data/silver/silver_weather.parquet")
gold_1h_path = Path("data/gold/weather_1h.parquet")
gold_1d_path = Path("data/gold/weather_1d.parquet")

if not silver_path.exists():
    st.warning("Silver dataset not found. Run the pipeline first.")
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
col3.metric("Start", str(min_dt)[:16] if pd.notna(min_dt) else "n/a")
col4.metric("End", str(max_dt)[:16] if pd.notna(max_dt) else "n/a")

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