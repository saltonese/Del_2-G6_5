
import json
import re
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path.cwd() / "Data"
OUTPUT_DIR = Path("output")

EPSILON = 1e-6          # keeps the refund ratio finite when sales_count == 0
NOK_CORRECTION = 10.0   # NOK prices were registered on the EUR scale
OUTLIER_N_STD = 3.0     # |x - mean| > 3 * std  ->  hardware glitch

print(f"pandas {pd.__version__} | numpy {np.__version__}")
assert DATA_DIR.exists(), "Run `python generate_data_for_d2.py` first to create the Data/ folder."


def read_log_file(path: str | Path) -> tuple[str, str]:
    """Read a text file whose encoding is either UTF-8 or ISO-8859-1.

    Returns
    -------
    (file_text_content, encoding_used)
    """
    path = Path(path)
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("iso-8859-1"), "iso-8859-1"


# Test: the same text saved with two different encodings
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    (tmp / "utf8.log").write_bytes("Café ølbar\n".encode("utf-8"))
    (tmp / "latin1.log").write_bytes("Café ølbar\n".encode("iso-8859-1"))

    text_utf8, enc_utf8 = read_log_file(tmp / "utf8.log")
    text_latin1, enc_latin1 = read_log_file(tmp / "latin1.log")

assert (enc_utf8, enc_latin1) == ("utf-8", "iso-8859-1")
assert text_utf8 == text_latin1 == "Café ølbar\n"
print("read_log_file OK:", enc_utf8, "/", enc_latin1)


LOG_PATTERN = re.compile(
    r"""
    ^\[(?P<timestamp>\d{4}-\d{2}-\d{2}\ \d{2}:\d{2}:\d{2})\]\s+   # [2026-10-15 08:30:00]
    \[(?P<register_id>[A-Za-z0-9_]+)\]\s+                       # [POS_01]
    item=(?P<item>.+?)\s+                                       # item=Latte
    price=(?P<price>\d+(?:\.\d+)?)\s+                           # price=4.50
    (?P<currency>[A-Z]{3})\s+                                   # EUR / NOK / USD
    \((?P<status>SUCCESS|REFUND|CANCELLED)\)$                   # (SUCCESS)
    """,
    re.VERBOSE,
)

# Only used for the validation at the end (the parser itself ignores everything that does not match)
NOISE_PATTERN = re.compile(r"^(---.*---|===.*===|\[DEBUG\].*)$")


def parse_log_text(text: str) -> list[dict]:
    """Extract all valid sales lines from log text, ignoring system noise.

    Each record has the keys: timestamp (str), register_id (str), item (str),
    price (float), currency (str), status (str).
    """
    records = []
    for line in text.splitlines():
        match = LOG_PATTERN.match(line.strip())
        if match is None:
            continue  # noise or malformed line
        record = match.groupdict()
        record["price"] = float(record["price"])
        records.append(record)
    return records


sample = """--- PRINTER PAPER LOW ---
[2026-10-15 08:30:00] [POS_01] item=Latte price=4.50 EUR (SUCCESS)
[DEBUG] BARCODE SCANNER REBOOTED
=== NETWORK SYNC OK ===
[2026-10-15 08:31:12] [POS_02] item=Muffin price=999.00 NOK (REFUND)
[2026-10-15 08:32:00] [POS_02] item=Muffin price=abc NOK (REFUND)
[2026-10-15 08:33:00] [POS_02] item=Muffin price=3.50 NOK (UNKNOWN)
"""

parsed = parse_log_text(sample)
assert len(parsed) == 2
assert parsed[0] == {
    "timestamp": "2026-10-15 08:30:00",
    "register_id": "POS_01",
    "item": "Latte",
    "price": 4.5,
    "currency": "EUR",
    "status": "SUCCESS",
}
assert parsed[1]["price"] == 999.0 and parsed[1]["status"] == "REFUND"
print("parse_log_text OK ->", len(parsed), "of 7 lines are valid")




