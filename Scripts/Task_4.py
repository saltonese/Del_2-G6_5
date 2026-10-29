from pathlib import Path
from Task_3 import compute_refund_ratio

import numpy as np
import pandas as pd

DATA_DIR = Path.cwd() / "Data"
OUTPUT_DIR = Path("output")

EPSILON = 1e-6          # keeps the refund ratio finite when sales_count == 0
NOK_CORRECTION = 10.0   # NOK prices were registered on the EUR scale
OUTLIER_N_STD = 3.0     # |x - mean| > 3 * std  ->  hardware glitch


TRANSACTION_COLUMNS = ["timestamp", "register_id", "item", "price", "currency", "status"]
STATUS_ORDER = ["SUCCESS", "REFUND", "CANCELLED"]

#task 4.1
def build_dataframe(records: list[dict]) -> pd.DataFrame:
    """List of transaction dicts -> DataFrame indexed by (sorted) datetime timestamp."""
    
    df = pd.DataFrame(records, columns=TRANSACTION_COLUMNS)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    return df.set_index("timestamp").sort_index()

#task_4.2
def resample_hourly_revenue(df: pd.DataFrame) -> pd.Series:
    """Total price per item in 1-hour windows."""
    
    return df.groupby("item")["price"].resample("1h").sum().rename("revenue")

#task 4.3
def create_status_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Total revenue per item (rows) across the status categories (columns)."""
    
    pivot = df.pivot_table(values="price", index="item", columns="status",
                           aggfunc="sum", fill_value=0.0)
    
    return pivot.reindex(columns=STATUS_ORDER, fill_value=0.0)    # always all three columns

#task 4.4
def item_refund_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Refund ratio per item = refunds / (successful sales + epsilon)."""
    
    counts = df.groupby(["item", "status"]).size().unstack(fill_value=0)
    counts = counts.reindex(columns=["SUCCESS", "REFUND"], fill_value=0)

    ratio = compute_refund_ratio(counts["SUCCESS"].to_numpy(), counts["REFUND"].to_numpy())
    
    return pd.DataFrame(
        {"sales_count": counts["SUCCESS"], "refund_count": counts["REFUND"], "refund_ratio": ratio},
        index=counts.index,
    )

# function test on made up data
demo_records = [
    {"timestamp": "2026-10-15 08:30:00", "register_id": "POS_01", "item": "Latte",  "price": 4.5, "currency": "EUR", "status": "SUCCESS"},
    {"timestamp": "2026-10-15 07:10:00", "register_id": "POS_01", "item": "Latte",  "price": 4.0, "currency": "EUR", "status": "SUCCESS"},
    {"timestamp": "2026-10-15 09:05:00", "register_id": "POS_02", "item": "Latte",  "price": 4.5, "currency": "NOK", "status": "REFUND"},
    {"timestamp": "2026-10-15 07:40:00", "register_id": "POS_02", "item": "Muffin", "price": 3.5, "currency": "USD", "status": "SUCCESS"},
]

demo_df = build_dataframe(demo_records)

assert isinstance(demo_df.index, pd.DatetimeIndex) and demo_df.index.is_monotonic_increasing

demo_hourly = resample_hourly_revenue(demo_df)

assert demo_hourly[("Latte", pd.Timestamp("2026-10-15 08:00"))] == 4.5
assert demo_hourly[("Muffin", pd.Timestamp("2026-10-15 07:00"))] == 3.5

demo_pivot = create_status_pivot(demo_df)

assert list(demo_pivot.columns) == STATUS_ORDER
assert demo_pivot.loc["Latte", "SUCCESS"] == 8.5 and demo_pivot.loc["Latte", "REFUND"] == 4.5
assert demo_pivot.loc["Muffin", "REFUND"] == 0.0

demo_ratios = item_refund_ratios(demo_df)

assert np.isclose(
    demo_ratios.loc[["Latte"], "refund_ratio"].to_numpy(dtype=np.float64),
    0.5,
).all()    # 1 / (2 + eps)

assert demo_ratios.loc["Muffin", "refund_ratio"] == 0.0
print("Task 4 functions OK")
print(demo_pivot)