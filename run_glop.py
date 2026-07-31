# import time
# import threading
# import pandas as pd

# from glopal import (
#     algorithm2_independent_naive,
#     algorithm4_independent_dp,
#     algorithm5_independent_graph,
# )



import time
import threading
import pandas as pd

from glopal import (
    algorithm2_independent_naive,
    algorithm4_independent_dp,
    algorithm5_independent_graph,
)

# ============================================================
# Tunables
# ============================================================
CSV_PATH = "" #path to the CSV file containing the data (found in used data)
OUTPUT_CSV_FILE = "" #path to the output CSV file where execution times will be saved

X_COL = "age"        # The column used for binning 
Y_COL = "income"     # The column used for aggregating 

AGGREGATION = "AVG"  # Options: 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'

L, U, STEP = 17.0, 90.0, 1.0

# --- NEW: Dynamic Parameter Lists ---
K_VALUES = [7]             # List of k values to test
EPS_VALUES = [3.0]         # List of epsilon values to test
C_VALUES = [500,1000,1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]            # <--- NEW: List of C thresholds to test

USE_PREFILTER = True

# --- Constraints ---
MIN_WIDTH = 0.0               
MAX_WIDTH = 90.0              
EXCLUDED_BOUNDARIES = None    
REQUIRED_BOUNDARIES = None    

# Alg 2 knobs
CANDIDATE_STRIDE = 1          
MAX_COMBINATIONS = None       
# ============================================================


def _timed_call(fn, *args, **kwargs):
    """Run a function and return (result, seconds)."""
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    dt = time.perf_counter() - t0
    return out, dt


def _timed_call_with_timeout(fn, timeout_secs, *args, **kwargs):
    """Run a function with a timeout. Returns (result, seconds) or (None, None) if timeout."""
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = fn(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    t0 = time.perf_counter()
    thread = threading.Thread(target=target, daemon=False)
    thread.start()
    thread.join(timeout=timeout_secs)
    dt = time.perf_counter() - t0
    
    if thread.is_alive():
        return None, None
    if exception[0] is not None:
        raise exception[0]
    return result[0], dt


def main():
    print(f"Loading data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH, low_memory=False, skiprows=1)
    
    print("Columns Pandas actually sees:", df.columns.tolist())
    df.columns = df.columns.str.strip() 
    
    # Extract X (the domain)
    x_series = pd.to_numeric(df[X_COL], errors="coerce").dropna()
    
    # Extract Y (the target variable) - only needed if not COUNT
    if AGGREGATION.upper() == 'COUNT':
        y_series = None
    else:
        if Y_COL not in df.columns:
            print(f"WARNING: Target column '{Y_COL}' not found. Check your CSV!")
            y_series = pd.Series([1] * len(x_series))
        else:
            y_series = pd.to_numeric(df[Y_COL], errors="coerce").dropna()
            # Align x and y series by index to ensure data integrity
            common_index = x_series.index.intersection(y_series.index)
            x_series = x_series.loc[common_index]
            y_series = y_series.loc[common_index]

    print(f"\n{'='*50}")
    print(f"Global Constraints Active | Aggregation: {AGGREGATION}")
    print(f"  - Min Width: {MIN_WIDTH}")
    print(f"  - Max Width: {MAX_WIDTH}")
    print(f"  - Forbidden: {EXCLUDED_BOUNDARIES}")
    print(f"  - Required:  {REQUIRED_BOUNDARIES} (Alg 5 only)")
    print(f"{'='*50}")

    # List to store results for the final CSV
    results_list = []

    # Loop through all combinations of K, EPS, and C
    for k in K_VALUES:
        for eps in EPS_VALUES:
            for current_c in C_VALUES:  # <--- NEW: Added the loop for C
                
                print(f"\n\n{'#'*60}")
                print(f"Evaluating algorithms for EXACTLY k = {k} | EPSILON = {eps} | C = {current_c}")
                print(f"{'#'*60}\n")
                
                # Variables to store execution times for this loop
                time_alg2 = None
                time_alg4 = None
                time_alg5 = None
                best_dev_alg4 = None

                # ---------- Algorithm 2 (naive) ----------
                print("--- Algorithm 2 (Independent Naive) ---")
                try:
                    cuts2, t2 = _timed_call_with_timeout(
                        algorithm2_independent_naive,
                        600, 
                        x_series, y_series, L, U, STEP, k, eps, current_c,
                        agg_func=AGGREGATION,
                        candidate_stride=CANDIDATE_STRIDE,
                        max_combinations=MAX_COMBINATIONS,
                        min_width=MIN_WIDTH,
                        max_width=MAX_WIDTH,
                        excluded_boundaries=EXCLUDED_BOUNDARIES,
                    )
                    if cuts2 is None and t2 is None:
                        print("Status: TIMEOUT (Exceeded 120 seconds)")
                        time_alg2 = "TIMEOUT"
                    else:
                        print(f"Time Taken: {t2:.6f} seconds")
                        print(f"Stable Cuts Found: {cuts2}")
                        time_alg2 = round(t2, 6)
                except Exception as e:
                    print(f"Error: {repr(e)}")
                    time_alg2 = "ERROR"

                print("\n" + "-"*50 + "\n")

                # ---------- Algorithm 4 (DP) ----------
                print("--- Algorithm 4 (Independent DP) ---")
                try:
                    ((cuts4, best4), t4) = _timed_call(
                        algorithm4_independent_dp,
                        x_series, y_series, L, U, STEP, k, eps, current_c,
                        agg_func=AGGREGATION,
                        min_width=MIN_WIDTH,
                        max_width=MAX_WIDTH,
                        excluded_boundaries=EXCLUDED_BOUNDARIES,
                    )
                    print(f"Time Taken: {t4:.6f} seconds")
                    best_dev_alg4 = int(best4) if best4 is not None else 'None'
                    print(f"Best Worst-Case Dev: {best_dev_alg4}")
                    print(f"Stable Cuts Found: {cuts4}")
                    time_alg4 = round(t4, 6)
                except Exception as e:
                    print(f"Error: {repr(e)}")
                    time_alg4 = "ERROR"

                print("\n" + "-"*50 + "\n")

                # ---------- Algorithm 5 (Graph/DFS) ----------
                print("--- Algorithm 5 (Independent Graph/DFS) ---")
                try:
                    (cuts5, t5) = _timed_call(
                        algorithm5_independent_graph,
                        x_series, y_series, L, U, STEP, k, eps, current_c,
                        agg_func=AGGREGATION,
                        use_boundary_prefilter=USE_PREFILTER,
                        min_width=MIN_WIDTH,
                        max_width=MAX_WIDTH,
                        excluded_boundaries=EXCLUDED_BOUNDARIES,
                        required_boundaries=REQUIRED_BOUNDARIES,
                    )
                    print(f"Time Taken: {t5:.6f} seconds")
                    print(f"Stable Cuts Found: {cuts5}")
                    time_alg5 = round(t5, 6)
                except Exception as e:
                    print(f"Error: {repr(e)}")
                    time_alg5 = "ERROR"
                
                # Append this loop's results to the tracking list
                results_list.append({
                    "k": k,
                    "Epsilon": eps,
                    "C_Threshold": current_c,
                    "DP_Best_Dev": best_dev_alg4,
                    "Alg2_Time_sec": time_alg2,
                    "Alg4_Time_sec": time_alg4,
                    "Alg5_Time_sec": time_alg5
                })
                    
    # Save the tracked execution times to a CSV file
    print(f"\n{'='*50}")
    print("Finished evaluating all combinations.")
    
    results_df = pd.DataFrame(results_list)
    results_df.to_csv(OUTPUT_CSV_FILE, index=False)
    print(f"Execution times saved successfully to '{OUTPUT_CSV_FILE}'")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()

# import time
# import threading
# import pandas as pd

# from glopal import (
#     algorithm2_independent_naive,
#     algorithm4_independent_dp,
#     algorithm5_independent_graph,
# )

# # ============================================================
# # Tunables
# # ============================================================
# CSV_PATH = "/Users/naserihab/Desktop/dataset-search/adult_reconstruction.csv"
# OUTPUT_CSV_FILE = "/Users/naserihab/Desktop/adult_reconstruction_runtimes.csv"

# X_COL = "age"        # The column used for binning 
# Y_COL = "income"     # The column used for aggregating 

# AGGREGATION = "MAX"  # Options: 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'

# L, U, STEP = 17.0, 90.0, 1.0

# # --- NEW: Dynamic Parameter Lists ---
# K_VALUES = [7]               # List of k values to test
# EPS_VALUES = [1,2,3.0,4,5]        # List of epsilon values to test

# # Base C value. For MIN income, C will be calculated as (eps * C_BASE)
# # Since you wanted C=2300 for EPS=2.0, we set C_BASE to 1150.
# C_BASE = 6500 
# USE_PREFILTER = True

# # --- Constraints ---
# MIN_WIDTH = 0.0               
# MAX_WIDTH = 90.0              
# EXCLUDED_BOUNDARIES = None    
# REQUIRED_BOUNDARIES = None    

# # Alg 2 knobs
# CANDIDATE_STRIDE = 1          
# MAX_COMBINATIONS = None       
# # ============================================================


# def _timed_call(fn, *args, **kwargs):
#     """Run a function and return (result, seconds)."""
#     t0 = time.perf_counter()
#     out = fn(*args, **kwargs)
#     dt = time.perf_counter() - t0
#     return out, dt


# def _timed_call_with_timeout(fn, timeout_secs, *args, **kwargs):
#     """Run a function with a timeout. Returns (result, seconds) or (None, None) if timeout."""
#     result = [None]
#     exception = [None]
    
#     def target():
#         try:
#             result[0] = fn(*args, **kwargs)
#         except Exception as e:
#             exception[0] = e
    
#     t0 = time.perf_counter()
#     thread = threading.Thread(target=target, daemon=False)
#     thread.start()
#     thread.join(timeout=timeout_secs)
#     dt = time.perf_counter() - t0
    
#     if thread.is_alive():
#         return None, None
#     if exception[0] is not None:
#         raise exception[0]
#     return result[0], dt


# def main():
#     print(f"Loading data from {CSV_PATH}...")
#     df = pd.read_csv(CSV_PATH, low_memory=False, skiprows=1)
    
#     print("Columns Pandas actually sees:", df.columns.tolist())
#     df.columns = df.columns.str.strip() 
    
#     # Extract X (the domain)
#     x_series = pd.to_numeric(df[X_COL], errors="coerce").dropna()
    
#     # Extract Y (the target variable) - only needed if not COUNT
#     if AGGREGATION.upper() == 'COUNT':
#         y_series = None
#     else:
#         if Y_COL not in df.columns:
#             print(f"WARNING: Target column '{Y_COL}' not found. Check your CSV!")
#             y_series = pd.Series([1] * len(x_series))
#         else:
#             y_series = pd.to_numeric(df[Y_COL], errors="coerce").dropna()
#             # Align x and y series by index to ensure data integrity
#             common_index = x_series.index.intersection(y_series.index)
#             x_series = x_series.loc[common_index]
#             y_series = y_series.loc[common_index]

#     print(f"\n{'='*50}")
#     print(f"Global Constraints Active | Aggregation: {AGGREGATION}")
#     print(f"  - Min Width: {MIN_WIDTH}")
#     print(f"  - Max Width: {MAX_WIDTH}")
#     print(f"  - Forbidden: {EXCLUDED_BOUNDARIES}")
#     print(f"  - Required:  {REQUIRED_BOUNDARIES} (Alg 5 only)")
#     print(f"{'='*50}")

#     # List to store results for the final CSV
#     results_list = []

#     # Loop through all combinations of K and EPS
#     for k in K_VALUES:
#         for eps in EPS_VALUES:
#             current_c = C_BASE
            
#             print(f"\n\n{'#'*60}")
#             print(f"Evaluating algorithms for EXACTLY k = {k} | EPSILON = {eps} | C = {current_c}")
#             print(f"{'#'*60}\n")
            
#             # Variables to store execution times for this loop
#             time_alg2 = None
#             time_alg4 = None
#             time_alg5 = None
#             best_dev_alg4 = None

#             # ---------- Algorithm 2 (naive) ----------
#             print("--- Algorithm 2 (Independent Naive) ---")
#             try:
#                 # Updated to pass y_series and agg_func for the new universal builder
#                 cuts2, t2 = _timed_call_with_timeout(
#                     algorithm2_independent_naive,
#                     120, 
#                     x_series, y_series, L, U, STEP, k, eps, current_c,
#                     agg_func=AGGREGATION,
#                     candidate_stride=CANDIDATE_STRIDE,
#                     max_combinations=MAX_COMBINATIONS,
#                     min_width=MIN_WIDTH,
#                     max_width=MAX_WIDTH,
#                     excluded_boundaries=EXCLUDED_BOUNDARIES,
#                 )
#                 if cuts2 is None and t2 is None:
#                     print("Status: TIMEOUT (Exceeded 120 seconds)")
#                     time_alg2 = "TIMEOUT"
#                 else:
#                     print(f"Time Taken: {t2:.6f} seconds")
#                     print(f"Stable Cuts Found: {cuts2}")
#                     time_alg2 = round(t2, 6)
#             except Exception as e:
#                 print(f"Error: {repr(e)}")
#                 time_alg2 = "ERROR"

#             print("\n" + "-"*50 + "\n")

#             # ---------- Algorithm 4 (DP) ----------
#             print("--- Algorithm 4 (Independent DP) ---")
#             try:
#                 ((cuts4, best4), t4) = _timed_call(
#                     algorithm4_independent_dp,
#                     x_series, y_series, L, U, STEP, k, eps, current_c,
#                     agg_func=AGGREGATION,
#                     min_width=MIN_WIDTH,
#                     max_width=MAX_WIDTH,
#                     excluded_boundaries=EXCLUDED_BOUNDARIES,
#                 )
#                 print(f"Time Taken: {t4:.6f} seconds")
#                 best_dev_alg4 = int(best4) if best4 is not None else 'None'
#                 print(f"Best Worst-Case Dev: {best_dev_alg4}")
#                 print(f"Stable Cuts Found: {cuts4}")
#                 time_alg4 = round(t4, 6)
#             except Exception as e:
#                 print(f"Error: {repr(e)}")
#                 time_alg4 = "ERROR"

#             print("\n" + "-"*50 + "\n")

#             # ---------- Algorithm 5 (Graph/DFS) ----------
#             print("--- Algorithm 5 (Independent Graph/DFS) ---")
#             try:
#                 (cuts5, t5) = _timed_call(
#                     algorithm5_independent_graph,
#                     x_series, y_series, L, U, STEP, k, eps, current_c,
#                     agg_func=AGGREGATION,
#                     use_boundary_prefilter=USE_PREFILTER,
#                     min_width=MIN_WIDTH,
#                     max_width=MAX_WIDTH,
#                     excluded_boundaries=EXCLUDED_BOUNDARIES,
#                     required_boundaries=REQUIRED_BOUNDARIES,
#                 )
#                 print(f"Time Taken: {t5:.6f} seconds")
#                 print(f"Stable Cuts Found: {cuts5}")
#                 time_alg5 = round(t5, 6)
#             except Exception as e:
#                 print(f"Error: {repr(e)}")
#                 time_alg5 = "ERROR"
            
#             # Append this loop's results to the tracking list
#             results_list.append({
#                 "k": k,
#                 "Epsilon": eps,
#                 "C_Threshold": current_c,
#                 "DP_Best_Dev": best_dev_alg4,
#                 "Alg2_Time_sec": time_alg2,
#                 "Alg4_Time_sec": time_alg4,
#                 "Alg5_Time_sec": time_alg5
#             })
                
#     # Save the tracked execution times to a CSV file
#     print(f"\n{'='*50}")
#     print("Finished evaluating all combinations.")
    
#     results_df = pd.DataFrame(results_list)
#     results_df.to_csv(OUTPUT_CSV_FILE, index=False)
#     print(f"Execution times saved successfully to '{OUTPUT_CSV_FILE}'")
#     print(f"{'='*50}\n")


# if __name__ == "__main__":
#     main()


# # ============================================================
# # Tunables
# # ============================================================

# CSV_PATH = "Accidents_rounded.csv"
# CSV_PATH = "/Users/naserihab/Desktop/adult_reconstruction.csv"
# X_COL = "age"        # The column used for binning (e.g., Time)
# Y_COL = "income"    # The column used for aggregating (e.g., Severity, Speed)

# AGGREGATION = "MIN"   # Options: 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'

# L, U, STEP = 17.0, 90.0, 1.0
# EPS = 2.0
# K = 7  

# # NOTE: You will need to adjust C based on your AGGREGATION!
# # For MAX Severity, a change of 1 or 2 is massive.
# C = 2300  
# #6500 the max 2300 the min
# USE_PREFILTER = True

# # --- Constraints ---
# MIN_WIDTH = 0.0               # Bins must be at least this wide
# MAX_WIDTH = 90.0              # Bins cannot be wider than this
# EXCLUDED_BOUNDARIES = None    # e.g., [12.0]
# REQUIRED_BOUNDARIES = None    # e.g., [6.0] (Alg 5 only)

# # Alg 2 knobs
# CANDIDATE_STRIDE = 1          
# MAX_COMBINATIONS = None       
# # ============================================================


# def _timed_call(fn, *args, **kwargs):
#     """Run a function and return (result, seconds)."""
#     t0 = time.perf_counter()
#     out = fn(*args, **kwargs)
#     dt = time.perf_counter() - t0
#     return out, dt


# def _timed_call_with_timeout(fn, timeout_secs, *args, **kwargs):
#     """Run a function with a timeout. Returns (result, seconds) or (None, None) if timeout."""
#     result = [None]
#     exception = [None]
    
#     def target():
#         try:
#             result[0] = fn(*args, **kwargs)
#         except Exception as e:
#             exception[0] = e
    
#     t0 = time.perf_counter()
#     thread = threading.Thread(target=target, daemon=False)
#     thread.start()
#     thread.join(timeout=timeout_secs)
#     dt = time.perf_counter() - t0
    
#     if thread.is_alive():
#         return None, None
#     if exception[0] is not None:
#         raise exception[0]
#     return result[0], dt


# def main():
#     print(f"Loading data from {CSV_PATH}...")
#     df = pd.read_csv(CSV_PATH, low_memory=False,skiprows=1)
#         # df = pd.read_csv(CSV_PATH, low_memory=False)
#     print("Columns Pandas actually sees:", df.columns.tolist())
#     df.columns = df.columns.str.strip() 
#     # Extract X (the domain)
#     x_series = pd.to_numeric(df[X_COL], errors="coerce").dropna()
    
#     # Extract Y (the target variable) - only needed if not COUNT
#     if AGGREGATION.upper() == 'COUNT':
#         y_series = None
#     else:
#         # Fallback to a dummy series if Y_COL doesn't exist to prevent immediate crashes,
#         # but warn the user.
#         if Y_COL not in df.columns:
#             print(f"WARNING: Target column '{Y_COL}' not found. Check your CSV!")
#             y_series = pd.Series([1] * len(x_series))
#         else:
#             y_series = pd.to_numeric(df[Y_COL], errors="coerce").dropna()
            
#             # Align x and y series by index to ensure data integrity
#             common_index = x_series.index.intersection(y_series.index)
#             x_series = x_series.loc[common_index]
#             y_series = y_series.loc[common_index]

#     print(f"\n{'='*50}")
#     print(f"Evaluating exactly k = {K} cuts | Aggregation: {AGGREGATION}")
#     print(f"Threshold (C): {C}")
#     print(f"Constraints Active:")
#     print(f"  - Min Width: {MIN_WIDTH}")
#     print(f"  - Max Width: {MAX_WIDTH}")
#     print(f"  - Forbidden: {EXCLUDED_BOUNDARIES}")
#     print(f"  - Required:  {REQUIRED_BOUNDARIES} (Alg 5 only)")
#     print(f"{'='*50}\n")

#     # ---------- Algorithm 2 (naive) ----------
#     if AGGREGATION.upper() == 'COUNT':
#         print("--- Algorithm 2 (Independent Naive) ---")
#         try:
#             # Alg 2 (as currently written in your file) only takes 'series' and does COUNT
#             cuts2, t2 = _timed_call_with_timeout(
#                 algorithm2_independent_naive,
#                 120, 
#                 x_series, L, U, STEP, K, EPS, C,
#                 candidate_stride=CANDIDATE_STRIDE,
#                 max_combinations=MAX_COMBINATIONS,
#                 min_width=MIN_WIDTH,
#                 max_width=MAX_WIDTH,
#                 excluded_boundaries=EXCLUDED_BOUNDARIES,
#             )
#             if cuts2 is None and t2 is None:
#                 print("Status: TIMEOUT (Exceeded 120 seconds)")
#             else:
#                 print(f"Time Taken: {t2:.6f} seconds")
#                 print(f"Stable Cuts Found: {cuts2}")
#         except Exception as e:
#             print(f"Error: {repr(e)}")
#     else:
#         print("--- Algorithm 2 (Independent Naive) ---")
#         print(f"Skipped: Current Algorithm 2 code only supports 'COUNT'. You are running '{AGGREGATION}'.")

#     print("\n" + "-"*50 + "\n")

#     # ---------- Algorithm 4 (DP) ----------
#     print("--- Algorithm 4 (Independent DP) ---")
#     try:
#         ((cuts4, best4), t4) = _timed_call(
#             algorithm4_independent_dp,
#             x_series, y_series, L, U, STEP, K, EPS, C,
#             agg_func=AGGREGATION,
#             min_width=MIN_WIDTH,
#             max_width=MAX_WIDTH,
#             excluded_boundaries=EXCLUDED_BOUNDARIES,
#         )
#         print(f"Time Taken: {t4:.6f} seconds")
#         print(f"Best Worst-Case Dev: {best4 if best4 is not None else 'None'}")
#         print(f"Stable Cuts Found: {cuts4}")
#     except Exception as e:
#         print(f"Error: {repr(e)}")

#     print("\n" + "-"*50 + "\n")

#     # ---------- Algorithm 5 (Graph/DFS) ----------
#     print("--- Algorithm 5 (Independent Graph/DFS) ---")
#     try:
#         (cuts5, t5) = _timed_call(
#             algorithm5_independent_graph,
#             x_series, y_series, L, U, STEP, K, EPS, C,
#             agg_func=AGGREGATION,
#             use_boundary_prefilter=USE_PREFILTER,
#             min_width=MIN_WIDTH,
#             max_width=MAX_WIDTH,
#             excluded_boundaries=EXCLUDED_BOUNDARIES,
#             required_boundaries=REQUIRED_BOUNDARIES,
#         )
#         print(f"Time Taken: {t5:.6f} seconds")
#         print(f"Stable Cuts Found: {cuts5}")
#     except Exception as e:
#         print(f"Error: {repr(e)}")
        
#     print(f"\n{'='*50}")


# if __name__ == "__main__":
#     main()
