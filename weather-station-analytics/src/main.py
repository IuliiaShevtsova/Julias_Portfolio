from .ingestion import load_all_xlsx_to_bronze_df
from .transformation import clean_bronze_df
from .aggregation import build_gold_10min, build_gold_1h, build_gold_1d
from .anomaly_detection import add_rolling_robust_anomalies
from .export import (
    BRONZE_PATH,
    SILVER_PATH,
    GOLD_10MIN_PATH,
    GOLD_1H_PATH,
    GOLD_1D_PATH,
    save_parquet,
)


def main() -> None:
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


if __name__ == "__main__":
    main()