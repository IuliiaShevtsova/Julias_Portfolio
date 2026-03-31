from pathlib import Path


OUTPUT_DIR = Path("data/interim/csv")


def save_csv(df, input_path: Path):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / f"{input_path.stem}.csv"
    df.to_csv(output_file, index=False)

    print(f"Saved: {output_file}")