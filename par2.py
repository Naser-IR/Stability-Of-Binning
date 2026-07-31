import itertools
import time
from dataclasses import dataclass
from typing import List, Optional, Sequence
import math

import numpy as np
import pandas as pd


# ============================================================
# Configuration and Data Loading
# ============================================================

CSV_PATH = "/Users/naserihab/Desktop/dataset-search/useddata/adult_reconstruction.csv"
X_COL = "age"
Y_COL = "income"
AGGREGATION = "AVG"  # Options: 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'

print(f"Loading data from {CSV_PATH}...")
try:
    df = pd.read_csv(CSV_PATH, low_memory=False, skiprows=1)
    df.columns = df.columns.str.strip()
    
    x_data = pd.to_numeric(df[X_COL], errors="coerce").dropna().to_numpy(dtype=float)
    
    if AGGREGATION.upper() == "COUNT":
        y_data = None
    else:
        if Y_COL not in df.columns:
            print(f"WARNING: Target column '{Y_COL}' not found. Defaulting to 1s.")
            y_data = np.ones_like(x_data)
        else:
            y_data = pd.to_numeric(df[Y_COL], errors="coerce").dropna().to_numpy(dtype=float)
            
            # Align lengths in case of NaNs
            min_len = min(len(x_data), len(y_data))
            x_data = x_data[:min_len]
            y_data = y_data[:min_len]
            
except FileNotFoundError:
    print(f"ERROR: File {CSV_PATH} not found. Using dummy data for testing.")
    x_data = np.random.uniform(17, 90, 1000)
    y_data = np.random.uniform(20000, 150000, 1000)


# ============================================================
# General validation helpers
# ============================================================

def validate_cuts(cuts: Sequence[float], min_value: float, max_value: float) -> np.ndarray:
    cuts_array = np.asarray(cuts, dtype=float)
    if cuts_array.ndim != 1: raise ValueError("cuts must be a one-dimensional sequence")
    if len(cuts_array) == 0: raise ValueError("cuts cannot be empty")
    if not np.all(np.isfinite(cuts_array)): raise ValueError("cuts must contain only finite values")
    if np.any(np.diff(cuts_array) <= 0): raise ValueError("cuts must be strictly increasing")
    if np.any(cuts_array < min_value): raise ValueError(f"All cuts must be at least {min_value}")
    if np.any(cuts_array > max_value): raise ValueError(f"All cuts must be at most {max_value}")
    return cuts_array

def calculate_saturation_epsilon(original_cuts: Sequence[float], min_value: float, max_value: float, step_size: float) -> float:
    cuts = validate_cuts(original_cuts, min_value, max_value)
    if step_size <= 0: raise ValueError("step_size must be greater than 0")
    maximum_possible_displacement = max(np.max(cuts - min_value), np.max(max_value - cuts))
    number_of_steps = int(np.ceil(maximum_possible_displacement / step_size - 1e-12))
    return number_of_steps * step_size


# ============================================================
# Perturbation generation
# ============================================================

def generate_perturbations(original_cuts: Sequence[float], epsilon: float, step_size: float, min_value: float, max_value: float) -> List[np.ndarray]:
    if epsilon < 0: raise ValueError("epsilon must be non-negative")
    if step_size <= 0: raise ValueError("step_size must be greater than 0")

    original_cuts_array = validate_cuts(original_cuts, min_value, max_value)
    number_of_steps = int(np.floor(epsilon / step_size + 1e-12))
    possible_step_shifts = range(-number_of_steps, number_of_steps + 1)
    
    perturbations = []
    for shift_tuple in itertools.product(possible_step_shifts, repeat=len(original_cuts_array)):
        shifts = np.asarray(shift_tuple, dtype=float)
        perturbed_cuts = original_cuts_array + shifts * step_size

        if np.any(perturbed_cuts < min_value - 1e-12): continue
        if np.any(perturbed_cuts > max_value + 1e-12): continue
        if np.any(np.diff(perturbed_cuts) <= 0): continue
        
        perturbations.append(perturbed_cuts)

    return perturbations


# ============================================================
# Naive Dynamic Aggregation Query
# ============================================================

def bin_and_aggregate_naive(
    x_data: Sequence[float], y_data: Optional[Sequence[float]], cuts: Sequence[float], agg_func: str = "COUNT"
) -> np.ndarray:
    agg = agg_func.upper()
    x_arr = np.asarray(x_data, dtype=float)
    valid_mask = np.isfinite(x_arr)
    x_arr = x_arr[valid_mask]
    
    y_arr = np.asarray(y_data, dtype=float)[valid_mask] if y_data is not None else np.ones_like(x_arr)
    cuts_array = np.asarray(cuts, dtype=float)
    bin_indices = np.digitize(x_arr, cuts_array, right=False)
    
    df_temp = pd.DataFrame({'bin': bin_indices, 'y': y_arr})
    grouped = df_temp.groupby('bin')['y']
    num_bins = len(cuts_array) + 1
    
    if agg == 'COUNT': res = grouped.count().reindex(range(num_bins), fill_value=0).values
    elif agg == 'SUM': res = grouped.sum().reindex(range(num_bins), fill_value=0.0).values
    elif agg == 'AVG': res = grouped.mean().reindex(range(num_bins), fill_value=0.0).values
    elif agg == 'MIN': res = grouped.min().reindex(range(num_bins), fill_value=np.inf).values
    elif agg == 'MAX': res = grouped.max().reindex(range(num_bins), fill_value=-np.inf).values
    else: raise ValueError(f"Unknown aggregation: {agg}")
        
    return res


# ============================================================
# Optimized Preprocessing (Sparse Table & Prefix Arrays)
# ============================================================

@dataclass
class AggregationTable:
    min_value: float
    max_value: float
    step_size: float
    agg_func: str
    
    # Prefix arrays for SUM, COUNT, and AVG
    pref_counts: np.ndarray
    pref_sums: np.ndarray
    
    # Sparse Tables for MIN and MAX
    st_min: np.ndarray
    st_max: np.ndarray

def build_aggregation_table(
    x_data: Sequence[float], y_data: Optional[Sequence[float]], min_value: float, max_value: float, step_size: float, agg_func: str = "COUNT"
) -> AggregationTable:
    
    agg = agg_func.upper()
    x_arr = np.asarray(x_data, dtype=float)
    valid_mask = np.isfinite(x_arr)
    x_arr = x_arr[valid_mask]
    y_arr = np.asarray(y_data, dtype=float)[valid_mask] if y_data is not None else np.ones_like(x_arr)
        
    # m is the number of internal grid cells
    m = int(round((max_value - min_value) / step_size))
    
    # Map each data point to its corresponding cell (0 to m-1)
    cell_indices = np.floor((x_arr - min_value) / step_size).astype(int)
    
    # Filter out data strictly outside the domain
    inside_mask = (cell_indices >= 0) & (cell_indices < m)
    valid_cells = cell_indices[inside_mask]
    valid_y = y_arr[inside_mask]
    
    df_cells = pd.DataFrame({'cell': valid_cells, 'y': valid_y})
    grouped = df_cells.groupby('cell')['y']
    
    # Atomic aggregates per cell
    cell_counts = grouped.count().reindex(range(m), fill_value=0).values
    cell_sums = grouped.sum().reindex(range(m), fill_value=0.0).values
    cell_mins = grouped.min().reindex(range(m), fill_value=np.inf).values
    cell_maxs = grouped.max().reindex(range(m), fill_value=-np.inf).values
    
    # 1. Build Prefix Arrays (1-indexed for easy range queries)
    pref_counts = np.zeros(m + 1, dtype=int)
    pref_sums = np.zeros(m + 1, dtype=float)
    
    pref_counts[1:] = np.cumsum(cell_counts)
    pref_sums[1:] = np.cumsum(cell_sums)
    
    # 2. Build Sparse Tables (for MIN/MAX)
    LOG = int(math.log2(m)) + 1 if m > 0 else 1
    st_min = np.full((m, LOG), np.inf)
    st_max = np.full((m, LOG), -np.inf)
    
    if m > 0:
        for i in range(m):
            st_min[i][0] = cell_mins[i]
            st_max[i][0] = cell_maxs[i]
            
        for j in range(1, LOG):
            for i in range(m - (1 << j) + 1):
                st_min[i][j] = min(st_min[i][j-1], st_min[i + (1 << (j-1))][j-1])
                st_max[i][j] = max(st_max[i][j-1], st_max[i + (1 << (j-1))][j-1])
                
    return AggregationTable(
        min_value=float(min_value), max_value=float(max_value), step_size=float(step_size),
        agg_func=agg, pref_counts=pref_counts, pref_sums=pref_sums, st_min=st_min, st_max=st_max
    )

def cut_to_index(table: AggregationTable, cut: float) -> int:
    rel = (float(cut) - table.min_value) / table.step_size
    idx = int(round(rel))
    return idx

def query_sparse_table(st: np.ndarray, L: int, R: int, agg_type: str) -> float:
    if L > R: return np.inf if agg_type == 'MIN' else -np.inf
    j = int(math.log2(R - L + 1))
    if agg_type == 'MIN': return min(st[L][j], st[R - (1 << j) + 1][j])
    else: return max(st[L][j], st[R - (1 << j) + 1][j])

def bin_and_aggregate_optimized(table: AggregationTable, cuts: Sequence[float]) -> np.ndarray:
    cuts_array = np.asarray(cuts, dtype=float)
    num_bins = len(cuts_array) + 1
    res = np.empty(num_bins, dtype=float)
    m = int(round((table.max_value - table.min_value) / table.step_size))
    
    # Boundary indices [0, cut1, cut2, ... m]
    indices = [0]
    for c in cuts_array:
        indices.append(cut_to_index(table, c))
    indices.append(m)
    
    for i in range(num_bins):
        L = indices[i]       # Left boundary index
        R = indices[i+1] - 1 # Rightmost cell index included in this bin
        
        if L > R:
            if table.agg_func in ['COUNT', 'SUM']: res[i] = 0.0
            elif table.agg_func == 'MIN': res[i] = np.inf
            elif table.agg_func == 'MAX': res[i] = -np.inf
            else: res[i] = 0.0
            continue
            
        # O(1) Queries based on aggregation type
        if table.agg_func == 'COUNT': res[i] = table.pref_counts[R + 1] - table.pref_counts[L]
        elif table.agg_func == 'SUM': res[i] = table.pref_sums[R + 1] - table.pref_sums[L]
        elif table.agg_func == 'AVG':
            c_count = table.pref_counts[R + 1] - table.pref_counts[L]
            c_sum = table.pref_sums[R + 1] - table.pref_sums[L]
            res[i] = c_sum / c_count if c_count > 0 else 0.0
        elif table.agg_func == 'MIN': res[i] = query_sparse_table(table.st_min, L, R, 'MIN')
        elif table.agg_func == 'MAX': res[i] = query_sparse_table(table.st_max, L, R, 'MAX')
            
    return res


# ============================================================
# Helpers for checking stability differences safely
# ============================================================

def calculate_deviations(original: np.ndarray, perturbed: np.ndarray) -> np.ndarray:
    valid = np.isfinite(original) & np.isfinite(perturbed)
    diffs = np.full_like(original, np.inf)
    diffs[valid] = np.abs(original[valid] - perturbed[valid])
    
    both_inf = np.isposinf(original) & np.isposinf(perturbed)
    both_ninf = np.isneginf(original) & np.isneginf(perturbed)
    diffs[both_inf | both_ninf] = 0.0
    return diffs


# ============================================================
# Algorithm 1A: Naive stability check
# ============================================================

def stability_check_naive(
    x_data: Sequence[float], y_data: Optional[Sequence[float]], original_cuts: Sequence[float], 
    epsilon: float, step_size: float, threshold_C: float, min_value: float, max_value: float, 
    agg_func: str = "COUNT", verbose: bool = False
) -> str:
    if threshold_C <= 0: raise ValueError("threshold_C must be greater than 0")
    original_cuts_array = validate_cuts(original_cuts, min_value, max_value)
    original_counts = bin_and_aggregate_naive(x_data, y_data, original_cuts_array, agg_func)
    
    perturbations = generate_perturbations(original_cuts=original_cuts_array, epsilon=epsilon, step_size=step_size, min_value=min_value, max_value=max_value)
    
    for perturbed_cuts in perturbations:
        perturbed_counts = bin_and_aggregate_naive(x_data, y_data, perturbed_cuts, agg_func)
        differences = calculate_deviations(original_counts, perturbed_counts)

        if np.any(differences >= threshold_C):
            return "Not Stable"
    return "Stable"


# ============================================================
# Algorithm 1C: Optimized with Conditional Extreme-First
# ============================================================

def stability_check_optimized_extreme_first(
    table: AggregationTable, original_cuts: Sequence[float], epsilon: float, step_size: float, threshold_C: float, verbose: bool = False
) -> str:
    if threshold_C <= 0: raise ValueError("threshold_C must be greater than 0")
    original_cuts_array = validate_cuts(original_cuts, table.min_value, table.max_value)
    original_counts = bin_and_aggregate_optimized(table, original_cuts_array)
    
    perturbations = generate_perturbations(original_cuts=original_cuts_array, epsilon=epsilon, step_size=step_size, min_value=table.min_value, max_value=table.max_value)
    
    # ONLY apply Extreme-First sorting for monotonic aggregations
    if table.agg_func in ['COUNT', 'SUM']:
        perturbations.sort(key=lambda p: np.sum(np.abs(p - original_cuts_array)), reverse=True)

    for perturbed_cuts in perturbations:
        perturbed_counts = bin_and_aggregate_optimized(table, perturbed_cuts)
        differences = calculate_deviations(original_counts, perturbed_counts)

        if np.any(differences >= threshold_C):
            return "Not Stable"
            
    return "Stable"


# ============================================================
# Algorithm 3A: Naive maximum stable epsilon
# ============================================================

def find_maximum_stable_epsilon_naive(
    x_data: Sequence[float], y_data: Optional[Sequence[float]], original_cuts: Sequence[float], 
    step_size: float, threshold_C: float, min_value: float, max_value: float, 
    agg_func: str = "COUNT", verbose: bool = True
) -> float:
    saturation_epsilon = calculate_saturation_epsilon(original_cuts=original_cuts, min_value=min_value, max_value=max_value, step_size=step_size)
    epsilon = 0.0
    maximum_stable_epsilon: Optional[float] = None

    while epsilon <= saturation_epsilon + 1e-12:
        result = stability_check_naive(x_data, y_data, original_cuts, epsilon, step_size, threshold_C, min_value, max_value, agg_func, verbose)
        if result == "Not Stable": break
        maximum_stable_epsilon = epsilon
        epsilon += step_size

    return maximum_stable_epsilon if maximum_stable_epsilon is not None else 0.0


# ============================================================
# Algorithm 3B: Optimized maximum stable epsilon
# ============================================================

def find_maximum_stable_epsilon_optimized(
    table: AggregationTable, original_cuts: Sequence[float], step_size: float, threshold_C: float, verbose: bool = True
) -> float:
    saturation_epsilon = calculate_saturation_epsilon(original_cuts=original_cuts, min_value=table.min_value, max_value=table.max_value, step_size=step_size)
    epsilon = 0.0
    maximum_stable_epsilon: Optional[float] = None

    while epsilon <= saturation_epsilon + 1e-12:
        result = stability_check_optimized_extreme_first(table=table, original_cuts=original_cuts, epsilon=epsilon, step_size=step_size, threshold_C=threshold_C, verbose=verbose)
        if result == "Not Stable": break
        maximum_stable_epsilon = epsilon
        epsilon += step_size

    return maximum_stable_epsilon if maximum_stable_epsilon is not None else 0.0


# ============================================================
# Example execution
# ============================================================

if __name__ == "__main__":
    original_cuts = [30.0, 50.0, 70.0]
    min_value, max_value = 17.0, 90.0
    step_size = 1.0
    threshold_C = 5000  # Adjust according to average income deviations
    test_epsilon = 1.0

    print(f"\nBuilding Data Structures for {AGGREGATION}...")
    preprocessing_start = time.perf_counter()
    table = build_aggregation_table(
        x_data=x_data, y_data=y_data, min_value=min_value, 
        max_value=max_value, step_size=step_size, agg_func=AGGREGATION
    )
    print(f"Preprocessing completed in {time.perf_counter() - preprocessing_start:.6f} seconds.\n")

    print("ALGORITHM 1: STABILITY CHECK")
    print("-" * 60)
    
    # 1. Run Naive Algorithm 1
    t0_naive = time.perf_counter()
    res_naive = stability_check_naive(
        x_data, y_data, original_cuts, test_epsilon, step_size, threshold_C, min_value, max_value, AGGREGATION
    )
    t_naive = time.perf_counter() - t0_naive
    print(f"Naive Result:     {res_naive} | Runtime: {t_naive:.6f} seconds")

    # 2. Run Optimized Algorithm 1
    t0_opt = time.perf_counter()
    res_opt = stability_check_optimized_extreme_first(table, original_cuts, test_epsilon, step_size, threshold_C)
    t_opt = time.perf_counter() - t0_opt
    print(f"Optimized Result: {res_opt} | Runtime: {t_opt:.6f} seconds")


    print("\nALGORITHM 3: MAXIMUM STABLE EPSILON")
    print("-" * 60)
    
    # 1. Run Naive Algorithm 3
    t0_naive_max = time.perf_counter()
    eps_naive = find_maximum_stable_epsilon_naive(
        x_data, y_data, original_cuts, step_size, threshold_C, min_value, max_value, AGGREGATION, verbose=False
    )
    t_naive_max = time.perf_counter() - t0_naive_max
    print(f"Naive Max Eps:     {eps_naive} | Runtime: {t_naive_max:.6f} seconds")
    
    # 2. Run Optimized Algorithm 3
    t0_opt_max = time.perf_counter()
    eps_opt = find_maximum_stable_epsilon_optimized(table, original_cuts, step_size, threshold_C, verbose=False)
    t_opt_max = time.perf_counter() - t0_opt_max
    print(f"Optimized Max Eps: {eps_opt} | Runtime: {t_opt_max:.6f} seconds\n")
