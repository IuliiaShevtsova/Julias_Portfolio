# Weather Station Analytics

This repository contains an end-to-end pipeline for processing weather station data and a small Streamlit dashboard to preview the results.

What it does
- Ingests raw XLSX files into a bronze table.
- Cleans and enriches observations into a silver dataset.
- Builds aggregated gold tables at multiple resolutions (10min, 1h, 1d).
- Provides a Streamlit dashboard for quick exploration and monitoring.

Quick start
1. Activate the project virtual environment:
```bash
source .venv/bin/activate
```
2. Install (if needed) dependencies:
```bash
pip install -r requirements.txt
```
3. Run the pipeline (recommended - run as a module):
```bash
# from the project root
python -m src.main
# or use the helper script
./run.sh
```

Preview dashboard (manual)
```bash
# in the same activated venv
streamlit run streamlit_app/Home.py --server.port 8501
# open http://localhost:8501
```

Preview dashboard (automated from pipeline)
The pipeline can optionally start the dashboard after it finishes. Useful CLI options:

```bash
# start pipeline and the dashboard (preferred port 8501)
python -m src.main --serve-dashboard --port 8501

# don't open the browser automatically
python -m src.main --serve-dashboard --no-open

# do not open the browser automatically
python -m src.main --serve-dashboard --no-open
```

Stopping the dashboard (manual)

- To stop the dashboard that was started via the pipeline or `streamlit run`, switch to the terminal that is running Streamlit and press `Ctrl+C`.
- Or stop it from another shell:
```bash
pkill -f "streamlit run"
# or find the PID and kill it:
lsof -iTCP:8501 -sTCP:LISTEN -n -P
kill <PID>
```

Notes
- The pipeline prints a short hint after completion with the dashboard command and URL.

Project structure (important files)
- `src/` : pipeline modules (ingestion, transformation, aggregation, export, main)
- `streamlit_app/` : Streamlit dashboard pages and utilities
- `data/` : output parquet files created by the pipeline (`data/bronze`, `data/silver`, `data/gold`)
- `requirements.txt` : Python dependencies

If you want, I can also add a single-command Makefile or update `run.sh` to include `--serve-dashboard` options for convenience.

