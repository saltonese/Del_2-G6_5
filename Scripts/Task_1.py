
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
