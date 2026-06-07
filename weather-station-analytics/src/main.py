import sys
import argparse
import socket
import subprocess
import time
import webbrowser
import urllib.request
from pathlib import Path
from typing import Optional

# When running `python src/main.py` ensure the package root is on sys.path
if __package__ is None and __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))

from src.ingestion import load_all_xlsx_to_bronze_df
from src.transformation import clean_bronze_df
from src.aggregation import build_gold_10min, build_gold_1h, build_gold_1d
from src.anomaly_detection import add_rolling_robust_anomalies
from src.export import (
    BRONZE_PATH,
    SILVER_PATH,
    GOLD_10MIN_PATH,
    GOLD_1H_PATH,
    GOLD_1D_PATH,
    save_parquet,
)


def run_pipeline() -> None:
    print("Step 1: Loading all XLSX files into one bronze table...")
    bronze_df = load_all_xlsx_to_bronze_df()

    if bronze_df.empty:
        print("No raw XLSX files found. Pipeline stopped.")
        return

    save_parquet(bronze_df, BRONZE_PATH)

    print("Step 2: Cleaning and enriching bronze into silver...")
    silver_df = clean_bronze_df(bronze_df)
    save_parquet(silver_df, SILVER_PATH)

    print("Step 3: Building gold 10-minute table...")
    gold_10min = build_gold_10min(silver_df)
    save_parquet(gold_10min, GOLD_10MIN_PATH)

    print("Step 4: Building gold 1-hour table...")
    gold_1h = build_gold_1h(silver_df)
    gold_1h = add_rolling_robust_anomalies(
        gold_1h,
        variables=[
            "temp_mean",
            "rh_mean",
            "dew_point_mean",
            "precip_sum",
            "wind_speed_mean",
            "station_pressure_mean",
        ],
        window=24,
        threshold=3.5,
        min_periods=12,
    )
    save_parquet(gold_1h, GOLD_1H_PATH)

    print("Step 5: Building gold 1-day table...")
    gold_1d = build_gold_1d(silver_df)
    gold_1d = add_rolling_robust_anomalies(
        gold_1d,
        variables=[
            "temp_mean",
            "rh_mean",
            "dew_point_mean",
            "precip_sum",
            "wind_speed_mean",
            "station_pressure_mean",
        ],
        window=7,
        threshold=3.5,
        min_periods=3,
    )
    save_parquet(gold_1d, GOLD_1D_PATH)

    print("Pipeline finished successfully.")


def _is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(0.5)
            s.connect((host, port))
            return True
        except Exception:
            return False


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def serve_streamlit(project_root: Path, port: Optional[int] = None, open_browser: bool = True) -> None:
    port_to_use = port if port is not None else 8501
    if _is_port_in_use(port_to_use):
        free = _find_free_port()
        print(f"Port {port_to_use} is in use — switching to free port {free}.")
        port_to_use = free
    cmd = [sys.executable, "-m", "streamlit", "run", "streamlit_app/Home.py", "--server.port", str(port_to_use)]
    print(f"Starting Streamlit on port {port_to_use}...")
    proc = subprocess.Popen(cmd, cwd=str(project_root))

    url = f"http://localhost:{port_to_use}"
    browser_lock = project_root / ".streamlit_browser_open"

    # wait until the server responds, then open browser once
    if open_browser and not browser_lock.exists():
        ready = False
        for _ in range(60):
            try:
                with urllib.request.urlopen(url, timeout=1) as resp:
                    if resp.status == 200:
                        ready = True
                        break
            except Exception:
                time.sleep(0.5)
        if ready:
            try:
                webbrowser.open(url)
                browser_lock.write_text(str(time.time()))
            except Exception:
                print(f"Failed to open browser automatically — open {url} manually.")

    print(f"Streamlit running (pid={proc.pid}) — open {url} in your browser.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run pipeline and optionally serve Streamlit dashboard")
    parser.add_argument("--serve-dashboard", action="store_true", help="Start streamlit dashboard after pipeline")
    parser.add_argument("--port", type=int, default=8501, help="Preferred port for Streamlit (will pick a free port if in use)")
    parser.add_argument("--no-open", dest="open_browser", action="store_false", help="Do not open the browser automatically")
    args = parser.parse_args()

    # Run pipeline
    run_pipeline()

    # Optionally serve Streamlit
    if args.serve_dashboard:
        project_root = Path(__file__).resolve().parents[1]
        serve_streamlit(project_root, port=args.port, open_browser=args.open_browser)


if __name__ == "__main__":
    main()