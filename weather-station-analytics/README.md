# Weather Station Pipeline

Project scaffold for end-to-end weather station data pipeline with ingestion, validation, processing, features, modeling, reporting, dashboard and containerization.

## Setup

The project includes a pre-configured virtual environment with all dependencies installed.

To run the pipeline:
```bash
./run.sh
```

Or manually:
```bash
source .venv/bin/activate
python src/main.py
```

## Structure

- `data/` : raw, processed, sample [ADD this, because it is gitignored and is not in the repository]
- `db/weather.duckdb` : analytical database file
- `src/` : code modules
- `dashboards/streamlit_app.py` : web dashboard
- `tests/` : test suite

