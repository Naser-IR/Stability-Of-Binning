# import time
# import numpy as np
# import pandas as pd
# from par import (

#     build_count_prefix_table,

#     stability_check_naive,

#     stability_check_prefix,

#     find_maximum_stable_epsilon_naive,

#     find_maximum_stable_epsilon_prefix,

# )

# # ============================================================
# # Configuration
# # ============================================================

# original_cuts = [4.0, 8.0, 14.0]

# min_value = 0.0
# max_value = 24.0

# step_size = 1.0
# threshold_C = 1_000_000

# epsilon_values = range(1, 8)

# output_file = "algorithm1_epsilon_runtime.csv"

# # preprocessing_start = time.perf_counter()
# # ============================================================
# # Prepare the data
# # ============================================================
# df = pd.read_csv("Accidents_rounded.csv")
# time_data = pd.to_numeric(
#     df["Time"],
#     errors="coerce"
# ).dropna().to_numpy(dtype=float)

# # clean_time_data = pd.to_numeric(
# #     time_data,
# #     errors="coerce"
# # ).dropna()

# # clean_time_data = clean_time_data[
# #     (clean_time_data >= min_value)
# #     & (clean_time_data <= max_value)
# # ]


# # ============================================================
# # Prefix preprocessing
# # ============================================================

# preprocessing_start = time.perf_counter()

# prefix_table = build_count_prefix_table(
#     data=time_data,
#     min_value=min_value,
#     max_value=max_value,
#     step_size=step_size
# )

# preprocessing_time = (
#     time.perf_counter()
#     - preprocessing_start
# )

# print(preprocessing_time)
# # ============================================================
# # Run Algorithm 1 for epsilon = 1, ..., 7
# # ============================================================

# results = []

# for epsilon in epsilon_values:

#     # --------------------------------------------------------
#     # Algorithm 1A: naive
#     # --------------------------------------------------------

#     naive_start = time.perf_counter()

#     naive_result = stability_check_naive(
#         data=time_data,
#         original_cuts=original_cuts,
#         epsilon=float(epsilon),
#         step_size=step_size,
#         threshold_C=threshold_C,
#         min_value=min_value,
#         max_value=max_value,
#         verbose=False
#     )

#     naive_runtime = (
#         time.perf_counter()
#         - naive_start
#     )

#     # --------------------------------------------------------
#     # Algorithm 1B: prefix
#     # --------------------------------------------------------

#     prefix_start = time.perf_counter()

#     prefix_result = stability_check_prefix(
#         prefix_table=prefix_table,
#         original_cuts=original_cuts,
#         epsilon=float(epsilon),
#         step_size=step_size,
#         threshold_C=threshold_C,
#         verbose=False
#     )

#     prefix_runtime = (
#         time.perf_counter()
#         - prefix_start
#     )

#     prefix_runtime_with_preprocessing = (
#         preprocessing_time
#         + prefix_runtime
#     )

#     results_match = (
#         naive_result == prefix_result
#     )

#     results.append({
#         "epsilon": float(epsilon),
#         "C": threshold_C,

#         "naive_result": naive_result,
#         "naive_runtime_seconds": naive_runtime,

#         "prefix_result": prefix_result,
#         "prefix_runtime_excluding_preprocessing_seconds":
#             prefix_runtime,

#         "prefix_preprocessing_seconds":
#             preprocessing_time,

#         "prefix_runtime_including_preprocessing_seconds":
#             prefix_runtime_with_preprocessing,

#         "results_match": results_match
#     })

#     print(
#         f"epsilon={epsilon} | "
#         f"naive={naive_result}, "
#         f"time={naive_runtime:.8f}s | "
#         f"prefix={prefix_result}, "
#         f"time={prefix_runtime:.8f}s | "
#         f"match={results_match}"
#     )


# # ============================================================
# # Save results
# # ============================================================

# results_df = pd.DataFrame(results)

# results_df.to_csv(
#     output_file,
#     index=False
# )

# print("\nExperiment completed.")
# print(f"Results saved to: {output_file}")

# print("\nResults:")
# print(results_df.to_string(index=False))


import time
import numpy as np
import pandas as pd
from par import (
    build_count_prefix_table,
    stability_check_naive,
    stability_check_prefix,
    stability_check_prefix_extreme_first,  # <--- NEW: Import the extreme-first function
    stability_check_prefix_count_optimized,  # <--- NEW: Import the count-optimized function
    find_maximum_stable_epsilon_naive,
    find_maximum_stable_epsilon_prefix,
)

# ============================================================
# Configuration
# ============================================================

original_cuts = [4.0, 8.0, 14.0]

min_value = 0.0
max_value = 24.0

step_size = 1.0
threshold_C = 1_000_000

epsilon_values = range(1, 8)

output_file = "/Users/naserrabah2/Desktop/dataset-search/algorithm1_runtime_3.csv"

# ============================================================
# Prepare the data
# ============================================================
df = pd.read_csv("Accidents_rounded.csv")
time_data = pd.to_numeric(
    df["Time"],
    errors="coerce"
).dropna().to_numpy(dtype=float)

# ============================================================
# Prefix preprocessing
# ============================================================

preprocessing_start = time.perf_counter()

prefix_table = build_count_prefix_table(
    data=time_data,
    min_value=min_value,
    max_value=max_value,
    step_size=step_size
)

preprocessing_time = (
    time.perf_counter()
    - preprocessing_start
)

print(f"Preprocessing time: {preprocessing_time:.8f}s\n")

# ============================================================
# Run Algorithm 1 for epsilon = 1, ..., 7
# ============================================================

results = []

for epsilon in epsilon_values:

    # --------------------------------------------------------
    # Algorithm 1A: naive
    # --------------------------------------------------------
    naive_start = time.perf_counter()

    naive_result = stability_check_naive(
        data=time_data,
        original_cuts=original_cuts,
        epsilon=float(epsilon),
        step_size=step_size,
        threshold_C=threshold_C,
        min_value=min_value,
        max_value=max_value,
        verbose=False
    )

    naive_runtime = (
        time.perf_counter()
        - naive_start
    )

    # --------------------------------------------------------
    # Algorithm 1B: prefix
    # --------------------------------------------------------
    prefix_start = time.perf_counter()

    prefix_result = stability_check_prefix(
        prefix_table=prefix_table,
        original_cuts=original_cuts,
        epsilon=float(epsilon),
        step_size=step_size,
        threshold_C=threshold_C,
        verbose=False
    )

    prefix_runtime = (
        time.perf_counter()
        - prefix_start
    )

    prefix_runtime_with_preprocessing = (
        preprocessing_time
        + prefix_runtime
    )
    
    # --------------------------------------------------------
    # Algorithm 1C: prefix extreme-first (NEW)
    # --------------------------------------------------------
    extreme_start = time.perf_counter()

    extreme_result = stability_check_prefix_count_optimized(
        prefix_table=prefix_table,
        original_cuts=original_cuts,
        epsilon=float(epsilon),
        step_size=step_size,
        threshold_C=threshold_C,
        verbose=False
    )

    extreme_runtime = (
        time.perf_counter()
        - extreme_start
    )

    extreme_runtime_with_preprocessing = (
        preprocessing_time
        + extreme_runtime
    )

    # --------------------------------------------------------
    # Verify and Store Results
    # --------------------------------------------------------
    results_match = (
        naive_result == prefix_result == extreme_result
    )

    results.append({
        "epsilon": float(epsilon),
        "C": threshold_C,

        "naive_result": naive_result,
        "naive_runtime_seconds": naive_runtime,

        "prefix_result": prefix_result,
        "prefix_runtime_excluding_preprocessing_seconds":
            prefix_runtime,
        "prefix_runtime_including_preprocessing_seconds":
            prefix_runtime_with_preprocessing,

        "extreme_result": extreme_result,
        "extreme_runtime_excluding_preprocessing_seconds":
            extreme_runtime,
        "extreme_runtime_including_preprocessing_seconds":
            extreme_runtime_with_preprocessing,

        "prefix_preprocessing_seconds":
            preprocessing_time,

        "results_match": results_match
    })

    print(
        f"epsilon={epsilon} | "
        f"naive={naive_result}, time={naive_runtime:.8f}s | "
        f"prefix={prefix_result}, time={prefix_runtime:.8f}s | "
        f"extreme={extreme_result}, time={extreme_runtime:.8f}s | "
        f"match={results_match}"
    )


# ============================================================
# Save results
# ============================================================

results_df = pd.DataFrame(results)

results_df.to_csv(
    output_file,
    index=False
)

print("\nExperiment completed.")
print(f"Results saved to: {output_file}")

print("\nResults:")
print(results_df.to_string(index=False))