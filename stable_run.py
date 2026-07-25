# import time
# import threading
# import pandas as pd

# from stable_construction import (
#     algorithm2_independent_naive,
#     algorithm4_independent_dp,
#     algorithm5_independent_graph,
# )

# # ----------------- Tunables -----------------
# # CSV_PATH = "Crimes_rounded.csv"
# CSV_PATH = "Accidents_rounded.csv"
# ATTR_COL = "Time"

# L, U, STEP = 0.0, 24.0, 1.0
# EPS = 1.0
# # C = EPS * 47000
# C = EPS * 67000
# USE_PREFILTER = True

# # --- NEW: Set your specific k here ---
# K = 4  

# # Alg2 knobs (to avoid runaway runtimes for larger k)
# CANDIDATE_STRIDE = 1          # try 2 or 3 to speed up
# MAX_COMBINATIONS = None       # e.g., 200_000 to cap work; None = no cap
# # -------------------------------------------


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
#         # Timeout occurred
#         return None, None
    
#     if exception[0] is not None:
#         raise exception[0]
    
#     return result[0], dt


# def main():
#     # Load series once
#     print(f"Loading data from {CSV_PATH}...")
#     df = pd.read_csv(CSV_PATH, low_memory=False)
#     series = pd.to_numeric(df[ATTR_COL], errors="coerce").dropna()
    
#     print(f"\n{'='*50}")
#     print(f"Evaluating algorithms for exactly k = {K} cuts")
#     print(f"{'='*50}\n")

#     # ---------- Algorithm 2 (naive) ----------
#     print("--- Algorithm 2 (Independent Naive) ---")
#     try:
#         cuts2, t2 = _timed_call_with_timeout(
#             algorithm2_independent_naive,
#             120,  # 2 minutes timeout
#             series, L, U, STEP, K, EPS, C,
#             candidate_stride=CANDIDATE_STRIDE,
#             max_combinations=MAX_COMBINATIONS,
#         )
#         if cuts2 is None and t2 is None:
#             print("Status: TIMEOUT (Exceeded 120 seconds)")
#         else:
#             print(f"Time Taken: {t2:.6f} seconds")
#             print(f"Stable Cuts Found: {cuts2}")
#     except Exception as e:
#         print(f"Error: {repr(e)}")

#     print("\n" + "-"*50 + "\n")

#     # ---------- Algorithm 4 (DP) ----------
#     print("--- Algorithm 4 (Independent DP) ---")
#     try:
#         ((cuts4, best4), t4) = _timed_call(
#             algorithm4_independent_dp,
#             series, L, U, STEP, K, EPS, C
#         )
#         print(f"Time Taken: {t4:.6f} seconds")
#         print(f"Best Worst-Case Dev: {int(best4) if best4 is not None else 'None'}")
#         print(f"Stable Cuts Found: {cuts4}")
#     except Exception as e:
#         print(f"Error: {repr(e)}")

#     print("\n" + "-"*50 + "\n")

#     # ---------- Algorithm 5 (Graph/DFS) ----------
#     print("--- Algorithm 5 (Independent Graph/DFS) ---")
#     try:
#         (cuts5, t5) = _timed_call(
#             algorithm5_independent_graph,
#             series, L, U, STEP, K, EPS, C,
#             use_boundary_prefilter=USE_PREFILTER,
#         )
#         print(f"Time Taken: {t5:.6f} seconds")
#         print(f"Stable Cuts Found: {cuts5}")
#     except Exception as e:
#         print(f"Error: {repr(e)}")
        
#     print(f"\n{'='*50}")


# if __name__ == "__main__":
#     main()


import time
import threading
import pandas as pd

from stable_constrain import (
    algorithm2_independent_naive,
    algorithm4_independent_dp,
    algorithm5_independent_graph,
)

# ----------------- Tunables -----------------
# CSV_PATH = "Crimes_rounded.csv"
CSV_PATH = "Accidents_rounded.csv"
ATTR_COL = "Time"

L, U, STEP = 0.0, 24.0, 1.0
EPS = 1.0
# C = EPS * 47000
C = EPS * 160000
USE_PREFILTER = True

# --- Set your specific k here ---
K = 4  

# --- NEW: Set your Constraints here ---
# Set to None if you do not want to use them
MIN_WIDTH = 0              # Bins must be at least this wide
MAX_WIDTH = 24              # Bins cannot be wider than this
EXCLUDED_BOUNDARIES = None  # Boundaries that are strictly forbidden
REQUIRED_BOUNDARIES = [6.0, 18.0]   # Boundaries that MUST be selected (Algorithm 5 only)

# Alg2 knobs (to avoid runaway runtimes for larger k)
CANDIDATE_STRIDE = 1          # try 2 or 3 to speed up
MAX_COMBINATIONS = None       # e.g., 200_000 to cap work; None = no cap
# -------------------------------------------


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
        # Timeout occurred
        return None, None
    
    if exception[0] is not None:
        raise exception[0]
    
    return result[0], dt


def main():
    # Load series once
    print(f"Loading data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH, low_memory=False)
    series = pd.to_numeric(df[ATTR_COL], errors="coerce").dropna()
    
    print(f"\n{'='*50}")
    print(f"Evaluating algorithms for exactly k = {K} cuts")
    print(f"Constraints Active:")
    print(f"  - Min Width: {MIN_WIDTH}")
    print(f"  - Max Width: {MAX_WIDTH}")
    print(f"  - Forbidden: {EXCLUDED_BOUNDARIES}")
    print(f"  - Required:  {REQUIRED_BOUNDARIES} (Alg 5 only)")
    print(f"{'='*50}\n")

    # ---------- Algorithm 2 (naive) ----------
    print("--- Algorithm 2 (Independent Naive) ---")
    try:
        cuts2, t2 = _timed_call_with_timeout(
            algorithm2_independent_naive,
            120,  # 2 minutes timeout
            series, L, U, STEP, K, EPS, C,
            candidate_stride=CANDIDATE_STRIDE,
            max_combinations=MAX_COMBINATIONS,
            min_width=MIN_WIDTH,
            max_width=MAX_WIDTH,
            excluded_boundaries=EXCLUDED_BOUNDARIES,
        )
        if cuts2 is None and t2 is None:
            print("Status: TIMEOUT (Exceeded 120 seconds)")
        else:
            print(f"Time Taken: {t2:.6f} seconds")
            print(f"Stable Cuts Found: {cuts2}")
    except Exception as e:
        print(f"Error: {repr(e)}")

    print("\n" + "-"*50 + "\n")

    # ---------- Algorithm 4 (DP) ----------
    print("--- Algorithm 4 (Independent DP) ---")
    try:
        ((cuts4, best4), t4) = _timed_call(
            algorithm4_independent_dp,
            series, L, U, STEP, K, EPS, C,
            min_width=MIN_WIDTH,
            max_width=MAX_WIDTH,
            excluded_boundaries=EXCLUDED_BOUNDARIES,
        )
        print(f"Time Taken: {t4:.6f} seconds")
        print(f"Best Worst-Case Dev: {int(best4) if best4 is not None else 'None'}")
        print(f"Stable Cuts Found: {cuts4}")
    except Exception as e:
        print(f"Error: {repr(e)}")

    print("\n" + "-"*50 + "\n")

    # ---------- Algorithm 5 (Graph/DFS) ----------
    print("--- Algorithm 5 (Independent Graph/DFS) ---")
    try:
        (cuts5, t5) = _timed_call(
            algorithm5_independent_graph,
            series, L, U, STEP, K, EPS, C,
            use_boundary_prefilter=USE_PREFILTER,
            min_width=MIN_WIDTH,
            max_width=MAX_WIDTH,
            excluded_boundaries=EXCLUDED_BOUNDARIES,
            required_boundaries=REQUIRED_BOUNDARIES,
        )
        print(f"Time Taken: {t5:.6f} seconds")
        print(f"Stable Cuts Found: {cuts5}")
    except Exception as e:
        print(f"Error: {repr(e)}")
        
    print(f"\n{'='*50}")


if __name__ == "__main__":
    main()