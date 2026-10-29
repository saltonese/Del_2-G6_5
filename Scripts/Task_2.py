import json
import re
import tempfile
from pathlib import Path

#from Task_1 import read_log_file 
#from Task_1 import parse_log_text

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path.cwd() / "Data"
OUTPUT_DIR = Path("output")

EPSILON = 1e-6          # keeps the refund ratio finite when sales_count == 0
NOK_CORRECTION = 10.0   # NOK prices were registered on the EUR scale
OUTLIER_N_STD = 3.0     # |x - mean| > 3 * std  ->  hardware glitch


#Task_2.1

def find_log_files(directory: str | Path, extension: str = ".log") -> list[Path]:
    """Recursively collect all files with the given extension below `directory`."""
    directory = Path(directory)
    found: list[Path] = []
    for item in directory.iterdir():
        if item.is_dir():
            found.extend(find_log_files(item, extension))   # recursive case
        elif item.is_file() and item.suffix == extension:
            found.append(item)
    return found

" temporary test with assert, to check if the find_log_files function works as intended"
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    for rel in ["2026/a/POS_01/x.log", "2026/a/POS_02/y.log", "2026/b/POS_01/z.log",
                "2026/b/POS_01/notes.txt", "top.log"]:
        file = tmp / rel
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("test")
    found = find_log_files(tmp)

assert sorted(p.name for p in found) == ["top.log", "x.log", "y.log", "z.log"]
assert all(isinstance(p, Path) for p in found)
print("find_log_files OK ->", sorted(p.name for p in found))

"prints the .log files, so you can verify with the files in Data"
log_files = sorted(find_log_files(DATA_DIR))
print(f"\nFound {len(log_files)} .log files under {DATA_DIR}:")
for log_file in log_files:
    print(log_file.relative_to(DATA_DIR))

#Task_2.2
def get_active_registers(node) -> set[str]:
    """Return the ids of all registers with "active": true anywhere in a nested dict/list structure."""
    active: set[str] = set()
    if isinstance(node, dict):
        if node.get("active") is True and isinstance(node.get("id"), str):
            active.add(node["id"])
        for value in node.values():
            active |= get_active_registers(value)
    elif isinstance(node, list):
        for element in node:
            active |= get_active_registers(element)
    return active    # scalars: base case -> empty set

" example test with assert, to check if the get_active_registers function works as intended"
example_config = {
    "company": "Campus Coffee",
    "regions": [{
        "region_name": "Main Campus",
        "stores": [{
            "name": "Library Cafe",
            "registers": [{"id": "POS_01", "active": True},
                          {"id": "POS_02", "active": False}],
        }],
    }],
}

assert get_active_registers(example_config) == {"POS_01"}

with open(DATA_DIR / "store_config.json", encoding="utf-8") as f:
    store_config = json.load(f)
print("get_active_registers OK -> active in store_config.json:",
        sorted(get_active_registers(store_config)))