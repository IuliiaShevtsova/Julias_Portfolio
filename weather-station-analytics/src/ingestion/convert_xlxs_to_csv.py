from pathlib import Path
import pandas as pd


INPUT_DIR = Path("data/raw/xlsx")


def load_all_xlsx():
    files = list(INPUT_DIR.glob("*.xlsx"))

    if not files:
        print("No XLSX files found.")
        return []

    data = []
    for file_path in files:
        df = pd.read_excel(file_path, engine="openpyxl")
        data.append((file_path, df))

    return data