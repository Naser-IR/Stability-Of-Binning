import time
import numpy as np
import pandas as pd

from par import (

    build_count_prefix_table,

    stability_check_naive,

    stability_check_prefix,
    

    find_maximum_stable_epsilon_naive,

    find_maximum_stable_epsilon_prefix,

    find_maximum_stable_epsilon_prefix_monitonic,  # <--- NEW: Import the monotonic function

)
# ============================================================
# Configuration
# ============================================================

original_cuts = [4.0, 8.0, 14.0]

min_value = 0.0
max_value = 24.0

step_size = 1.0

C_values = range(
    200_000,
    1_000_001,
    100_000
)

output_file = "algorithm3_C_runtime_monotonic.csv"


# ============================================================
# Prepare the data
# ============================================================
df = pd.read_csv("Accidents_rounded.csv")
time_data = pd.to_numeric(
    df["Time"],
    errors="coerce"
).dropna().to_numpy(dtype=float)

# clean_time_data = pd.to_numeric(
#     time_data,
#     errors="coerce"
# ).dropna()

# clean_time_data = clean_time_data[
#     (clean_time_data >= min_value)
#     & (clean_time_data <= max_value)
# ]


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


# ============================================================
# Run Algorithm 3 for every C value
# ============================================================

results = []

for threshold_C in C_values:

    # --------------------------------------------------------
    # Algorithm 3A: naive maximum epsilon
    # --------------------------------------------------------

    naive_start = time.perf_counter()

    naive_maximum_epsilon = (
        find_maximum_stable_epsilon_naive(
            data=time_data,
            original_cuts=original_cuts,
            step_size=step_size,
            threshold_C=threshold_C,
            min_value=min_value,
            max_value=max_value,
            verbose=False
        )
    )

    naive_runtime = (
        time.perf_counter()
        - naive_start
    )

    # --------------------------------------------------------
    # Algorithm 3B: prefix maximum epsilon
    # --------------------------------------------------------

    prefix_start = time.perf_counter()

    prefix_maximum_epsilon = (
        find_maximum_stable_epsilon_prefix(
            prefix_table=prefix_table,
            original_cuts=original_cuts,
            step_size=step_size,
            threshold_C=threshold_C,
            verbose=False
        )
    )


    prefix_runtime = (
        time.perf_counter()
        - prefix_start
    )

    prefix_runtime_with_preprocessing = (
        preprocessing_time
        + prefix_runtime
    )
    prefix_monotonic_start = time.perf_counter()
    prefix_maximum_epsilon_monotonic = (
        find_maximum_stable_epsilon_prefix_monitonic(
            prefix_table=prefix_table,
            original_cuts=original_cuts,
            step_size=step_size,
            threshold_C=threshold_C,
            verbose=False
        )
    )
    prefix_monotonic_runtime = (
        time.perf_counter()
        - prefix_monotonic_start
    )

    prefix_runtime_with_preprocessing_monotonic = (
        preprocessing_time
        + prefix_monotonic_runtime
    )
    # maximum_epsilon_match = np.isclose(
    #     naive_maximum_epsilon,
    #     prefix_maximum_epsilon,
    #     prefix_maximum_epsilon_monotonic
    # )
    match_1 = np.isclose(naive_maximum_epsilon, prefix_maximum_epsilon)
    match_2 = np.isclose(prefix_maximum_epsilon, prefix_maximum_epsilon_monotonic)
    maximum_epsilon_match = bool(match_1 and match_2)

    results.append({
        "C": threshold_C,

        "naive_maximum_epsilon":
            naive_maximum_epsilon,

        "naive_runtime_seconds":
            naive_runtime,

        "prefix_maximum_epsilon":
            prefix_maximum_epsilon,

        "prefix_maximum_epsilon_monotonic":
            prefix_maximum_epsilon_monotonic,

        "prefix_runtime_excluding_preprocessing_seconds":
            prefix_runtime,

        "prefix_preprocessing_seconds":
            preprocessing_time,

        "prefix_runtime_including_preprocessing_seconds":
            prefix_runtime_with_preprocessing,

        "prefix_monotonic_runtime_excluding_preprocessing_seconds":
            prefix_monotonic_runtime,

        "prefix_monotonic_runtime_including_preprocessing_seconds":
            prefix_runtime_with_preprocessing_monotonic,

        "maximum_epsilon_match":
            maximum_epsilon_match
    })

    print(
        f"C={threshold_C:,} | "
        f"naive epsilon={naive_maximum_epsilon}, "
        f"time={naive_runtime:.8f}s | "
        f"prefix epsilon={prefix_maximum_epsilon}, "
        f"time={prefix_runtime:.8f}s | "
        f"monotonic epsilon={prefix_maximum_epsilon_monotonic}, "
        f"time={prefix_monotonic_runtime:.8f}s | "
        f"match={maximum_epsilon_match}"
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
