

import numpy as np


def clean_prices(prices):
    unchanged_prices = np.asarray(prices, dtype=float)   

    valid_prices = [] 
    mean_of_unchanged_prices = np.mean(unchanged_prices)
    standard_deviation_of_unchanged_prices = np.std(unchanged_prices)
    
    
    for x in unchanged_prices:
        if abs(x - mean_of_unchanged_prices) > 3 * standard_deviation_of_unchanged_prices:
           pass
        else:
            valid_prices.append(x)

    median_of_valid_prices = np.median(valid_prices)

    
    mask = abs(unchanged_prices - mean_of_unchanged_prices) > 3 * standard_deviation_of_unchanged_prices
    unchanged_prices[mask] = median_of_valid_prices

    final_prices = np.asarray(unchanged_prices, dtype=float)

    return final_prices






def compute_refund_ratio(sales_count: np.ndarray, refund_count: np.ndarray) -> np.ndarray:

    