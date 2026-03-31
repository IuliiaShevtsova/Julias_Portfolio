import pandas as pd


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w_]", "", regex=True)
    )
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    return df