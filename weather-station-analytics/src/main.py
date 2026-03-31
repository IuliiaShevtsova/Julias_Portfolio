import sys
from pathlib import Path

# Add src directory to path to enable imports
sys.path.insert(0, str(Path(__file__).parent))

from ingestion import load_all_xlsx
from transformation import transform
from utils import save_csv


def main():
    datasets = load_all_xlsx()

    if not datasets:
        return

    for file_path, df in datasets:
        df_transformed = transform(df)
        save_csv(df_transformed, file_path)


if __name__ == "__main__":
    main()