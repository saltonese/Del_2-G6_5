from pathlib import Path

import numpy as np

DATA_DIR = Path.cwd() / "Data"
OUTPUT_DIR = Path("output")

EPSILON = 1e-6          # keeps the refund ratio finite when sales_count == 0
NOK_CORRECTION = 10.0   # NOK prices were registered on the EUR scale
OUTLIER_N_STD = 3.0     # |x - mean| > 3 * std  ->  hardware glitch


#Task_3.1

def remove_price_outliers(prices, n_std: float = OUTLIER_N_STD) -> np.ndarray:
    """Replace values with |x - mean| > n_std * std by the median of the remaining valid values."""
    
    values = np.asarray(prices, dtype=float).ravel()

    if values.size == 0:
        return values.copy()

    mean, std = values.mean(), values.std()          # ddof=0 (population std)
    is_outlier = np.abs(values - mean) > n_std * std

    cleaned = values.copy()
    
    if is_outlier.any():
        cleaned[is_outlier] = np.median(values[~is_outlier])
    return cleaned

rng = np.random.default_rng(0)
prices = np.append(rng.normal(5, 1, 200), [999.0, 999.0, 999.0])

cleaned = remove_price_outliers(prices)
assert cleaned.shape == prices.shape and cleaned.ndim == 1
assert not (cleaned == 999.0).any()
assert np.allclose(cleaned[-3:], np.median(prices[prices < 999]))
assert np.array_equal(cleaned[:-3], prices[:-3])      # valid values untouched
assert prices[-1] == 999.0                           # input not modified
assert remove_price_outliers(list(prices)).shape == prices.shape   # also accepts lists
print("remove_price_outliers OK")


# Known limitation of the 3-sigma rule: with n <= 10 values it can never flag anything,
# because the largest possible z-score is (n-1)/sqrt(n) < 3.
print("n=4 :", remove_price_outliers([3.0, 4.0, 5.0, 999.0]))


#Task_3.2
def compute_refund_ratio(sales_count: np.ndarray, refund_count: np.ndarray) -> np.ndarray:
    """Element-wise refund ratio: refund_count / (sales_count + EPSILON)."""
    
    sales = np.asarray(sales_count, dtype=float)
    refunds = np.asarray(refund_count, dtype=float)
    return refunds / (sales + EPSILON)

ratio = compute_refund_ratio(np.array([10, 0, 5, 4]), np.array([1, 0, 5, 0]))
assert np.allclose(ratio, [0.1, 0.0, 1.0, 0.0])
assert np.isfinite(ratio).all()                      # no division-by-zero problems
print("compute_refund_ratio OK ->", ratio.round(4))