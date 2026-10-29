import pandas as pd

def convert_to_dataframe(dictionaries: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(dictionaries)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    df = df.sort_index()
    return df

def group_and_summarize(df):
    Sum_items_pr_hour = df.groupby("item")["price"].resample("1h").sum()
    return Sum_items_pr_hour

def creating_pivot_table(df):
    pivot_table = pd.pivot_table(
        df,
        index="item",
        columns="status",
        values="price",
        aggfunc="sum",
        fill_value=0
    )
    return pivot_table

def