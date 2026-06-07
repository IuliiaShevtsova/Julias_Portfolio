from pathlib import Path
import pandas as pd

BRONZE_PATH = Path("data/bronze/bronze_weather.parquet")
SILVER_PATH = Path("data/silver/silver_weather.parquet")
GOLD_10MIN_PATH = Path("data/gold/weather_10min.parquet")
GOLD_1H_PATH = Path("data/gold/weather_1h.parquet")
GOLD_1D_PATH = Path("data/gold/weather_1d.parquet")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_parquet(df: pd.DataFrame, path: Path) -> Path:
    ensure_parent(path)
    df.to_parquet(path, index=False)
    print(f"Saved: {path}")
    return path