from ingestion import load_all_xlsx_to_bronze_df
from transformation import clean_bronze_df
from aggregation import build_gold_10min, build_gold_1h, build_gold_1d
from export import (
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
    save_parquet(gold_1h, GOLD_1H_PATH)

    print("Step 5: Building gold 1-day table...")
    gold_1d = build_gold_1d(silver_df)
    save_parquet(gold_1d, GOLD_1D_PATH)

    print("Pipeline finished successfully.")


if __name__ == "__main__":
    main()