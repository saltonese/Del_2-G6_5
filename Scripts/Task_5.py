import json
import pandas as pd

from pathlib import Path #used to easyely path between files and directories
from typing import cast

from Task_1 import read_log_file
from Task_1 import parse_log_text
from Task_2 import find_log_files
from Task_2 import get_active_registers
from Task_3 import remove_price_outliers
from Task_4 import build_dataframe 
from Task_4 import resample_hourly_revenue
from Task_4 import create_status_pivot
from Task_4 import item_refund_ratios


print(Path.cwd())
DATA_DIR = Path.cwd().parent / "Data"
OUTPUT_DIR = Path("output")

EPSILON = 1e-6          # keeps the refund ratio finite when sales_count == 0
NOK_CORRECTION = 10.0   # NOK prices were registered on the EUR scale
OUTLIER_N_STD = 3.0     # |x - mean| > 3 * std  ->  hardware glitch


def hourly_to_nested_dict(hourly: pd.Series) -> dict[str, dict[str, float]]:
    """(item, hour) Series -> {item: {"YYYY-MM-DD HH:MM:SS": revenue}} (JSON needs string keys)."""
    
    result: dict[str, dict[str, float]] = {}
    
    for index, revenue in hourly.items():
        item, hour = cast(tuple[str, pd.Timestamp], index)
        result.setdefault(item, {})[hour.strftime("%Y-%m-%d %H:%M:%S")] = round(
            float(revenue), 2
        )
    
    return result


def run_pipeline(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Discover log files and active registers
    log_files = sorted(find_log_files(data_dir))
    
    with open(data_dir / "store_config.json", encoding="utf-8") as f:
        active_registers = get_active_registers(json.load(f))
    print(f"[1/7] {len(log_files)} log files found, active registers: {sorted(active_registers)}")

    # 2. Ingest + parse
    records: list[dict] = []
    encodings: dict[str, str] = {}
    
    for path in log_files:
        text, encoding = read_log_file(path)
        encodings[path.relative_to(data_dir).as_posix()] = encoding
        records.extend(parse_log_text(text))
    n_parsed = len(records)
    records = [r for r in records if r["register_id"] in active_registers]
    print(f"[2/7] {n_parsed} records parsed, {n_parsed - len(records)} dropped (inactive register)")

    # 3. DataFrame
    raw_df = build_dataframe(records)
    print(f"[3/7] DataFrame built: {raw_df.shape[0]} rows, index {raw_df.index.min()} -> {raw_df.index.max()}")

    # 4. Outlier cleaning (NumPy)
    df = raw_df.copy()
    cleaned_prices = remove_price_outliers(df["price"].to_numpy())
    n_outliers = int((cleaned_prices != df["price"].to_numpy()).sum())
    df["price"] = cleaned_prices
    print(f"[4/7] {n_outliers} outlier prices replaced by the median of the valid prices")

    # 5. NOK correction
    is_nok = df["currency"] == "NOK"
    df.loc[is_nok, "price"] = df.loc[is_nok, "price"] * NOK_CORRECTION
    df["price"] = df["price"].round(2)
    print(f"[5/7] {int(is_nok.sum())} NOK prices multiplied by {NOK_CORRECTION}")

    # 6. Reports
    hourly = resample_hourly_revenue(df)
    pivot = create_status_pivot(df)
    ratios = item_refund_ratios(df)
    print(f"[6/7] hourly revenue ({len(hourly)} item-hour rows), pivot {pivot.shape}, refund ratios {ratios.shape}")

    # 7. Save
    df.to_csv(output_dir / "cleaned_transactions.csv", index_label="timestamp")
    with open(output_dir / "hourly_revenue.json", "w", encoding="utf-8") as f:
        json.dump(hourly_to_nested_dict(hourly), f, indent=2)
    pivot.to_csv(output_dir / "status_pivot_table.csv")
    ratios.to_csv(output_dir / "item_refund_ratios.csv")
    print(f"[7/7] 4 output files written to {output_dir.resolve()}")

    return {
        "log_files": log_files, "active_registers": active_registers, "encodings": encodings,
        "raw_df": raw_df, "clean_df": df, "n_outliers": n_outliers,
        "hourly": hourly, "pivot": pivot, "ratios": ratios,
    }

results = run_pipeline()