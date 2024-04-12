import pandas as pd


def get_df() -> pd.DataFrame:
    df = pd.read_excel("sample.xlsx")
    return df