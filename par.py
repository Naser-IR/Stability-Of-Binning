# import numpy as np
# import pandas as pd
# import itertools
# import matplotlib.pyplot as plt

# ########################################
# # === Load your data ===
# ########################################

# df = pd.read_csv("Accidents_rounded.csv")
# time_data = df['Time'].values

# ########################################
# # === Generate perturbations ===
# ########################################

# def generate_perturbations(original_cuts, epsilon, step_size):
#     k = len(original_cuts)
#     num_steps = int(np.floor(epsilon / step_size))
#     possible_steps = range(-num_steps, num_steps + 1)

#     perturbed_cuts_list = []
#     for steps in itertools.product(possible_steps, repeat=k):
#         new_cuts = [tau + s * step_size for tau, s in zip(original_cuts, steps)]

#         # keep only strictly increasing cut-vectors
#         if all(np.diff(new_cuts) > 0):
#             perturbed_cuts_list.append(new_cuts)

#     return perturbed_cuts_list

# # def generate_perturbations(original_cuts, epsilon, step_size):
# #     k = len(original_cuts)
# #     num_steps = int(np.floor(epsilon / step_size))
# #     possible_steps = range(-num_steps, num_steps + 1)

# #     all_step_combinations = list(itertools.product(possible_steps, repeat=k))
# #     perturbed_cuts_list = []
# #     for steps in all_step_combinations:
# #         new_cuts = []
# #         for tau_i, i in zip(original_cuts, steps):
# #             shift = i * step_size
# #             if abs(shift) <= epsilon:
# #                 new_cuts.append(tau_i + shift)
# #         if len(new_cuts) == k:
# #             perturbed_cuts_list.append(new_cuts)

# #     return perturbed_cuts_list

# ########################################
# # === Bin and count ===
# ########################################

# def bin_and_count(data, cuts):
#     """
#     Assign each data point to a bin and count how many points fall into each bin.
#     """
#     bins = np.digitize(data, cuts, right=False)
#     bin_labels = np.arange(len(cuts) + 1)  # for cuts [8,16] -> bins 0,1,2

#     counts = []
#     for label in bin_labels:
#         count = np.sum(bins == label)
#         counts.append(count)

#     return np.array(counts)

# ########################################
# # === Algorithm 1: Stability Check ===
# ########################################

# def stability_check(data, original_cuts, epsilon, step_size, threshold_C):
#     """
#     Pseudo-code: check if any perturbation changes any bin count by >= C.
#     """
#     original_counts = bin_and_count(data, original_cuts)

#     perturbations = generate_perturbations(original_cuts, epsilon, step_size)
#     print(f"Generated {len(perturbations)} perturbations.")

#     for cuts in perturbations:
#         perturbed_counts = bin_and_count(data, cuts)

#         differences = np.abs(original_counts - perturbed_counts)

#         if np.any(differences >= threshold_C):
#             print(f"Unstable! Found diff ≥ {threshold_C} with cuts {cuts}")
#             return "Not Stable"

#     print("All perturbations within threshold.")
#     return "Stable"

# ########################################
# # === Algorithm 2: Evaluate Partition ===
# ########################################

# # def evaluate_partition(data, cuts):
# #     """
# #     Simple evaluation: just return bin counts.
# #     """
# #     counts = bin_and_count(data, cuts)
# #     return counts

# def find_stable_binning(data, k, min_value, max_value, epsilon, step_size, threshold_C):
#     """
#     For each candidate binning f:
#       - Use Algorithm 1 to check stability
#       - If stable, return that binning
#     If none is stable, return None.
#     """
#     candidate_binnings = generate_candidate_binnings(k,min_value,max_value, step_size)
#     for idx, cuts in enumerate(candidate_binnings):
#         print(f"Checking candidate binning {idx + 1}: cuts = {cuts}")
#         result = stability_check(data, cuts, epsilon, step_size, threshold_C)
#         if result == "Stable":
#             print(f"Found stable binning: cuts = {cuts}")
#             return cuts
#     print("No stable binning found.")
#     return None



# def generate_candidate_binnings(k, min_value, max_value, step_size):
#     """
#     Generate all possible binning functions with k bins
#     (i.e., k-1 cut points) within [min_value, max_value],
#     using step_size as the granularity.
#     """
#     possible_cuts = np.arange(min_value, max_value, step_size)
#     cut_combinations = itertools.combinations(possible_cuts, k - 1)

#     candidate_binnings = []
#     for cuts in cut_combinations:
#         cuts_sorted = sorted(cuts)
#         candidate_binnings.append(cuts_sorted)

#     return candidate_binnings

# ########################################
# # === Algorithm 3: Find Worst-Case ===
# ########################################

# ########################################
# # === Algorithm 3: Find Minimal ε for Stability ===
# ########################################

# def find_minimal_epsilon(data, original_cuts, step_size, threshold_C, max_epsilon):
#     """
#     Incrementally increase ε from 0 up to max_epsilon.
#     For each ε:
#       - Use Algorithm 1 (stability check)
#       - If stable, return ε
#     If none is stable up to max_epsilon, return None.
#     """
#     epsilon = 1

#     while epsilon <= max_epsilon:
#         print(f"Checking ε = {epsilon}")
#         result = stability_check(data, original_cuts, epsilon, step_size, threshold_C)

#         if result == "Stable":
#             print(f"✅ Found minimal ε for stability: {epsilon}")
#             return epsilon
#         else:
#             epsilon += step_size  # You can adjust step increment here if needed

#     print(f"❌ No stable ε found up to {max_epsilon}")
#     return None

# ########################################
# # === Example cost function ===
# ########################################

# def example_cost_function(original_counts, perturbed_counts):
#     """
#     Example: the maximum single bin difference.
#     """
#     differences = np.abs(original_counts - perturbed_counts)
#     return np.max(differences)

# ########################################
# # === PLOT ===
# ########################################

# # def plot_histogram(data, cuts, title, filename=None):
# #     plt.figure(figsize=(8, 4))
# #     plt.hist(data, bins=30, alpha=0.5, edgecolor='black')

# #     for cut in cuts:
# #         plt.axvline(x=cut, color='red', linestyle='--')

# #     plt.title(title)
# #     plt.xlabel('Rounded Time')
# #     plt.ylabel('Frequency')
# #     plt.tight_layout()

# #     if filename:
# #         plt.savefig(filename)
# #         print(f"Saved plot: {filename}")

# #     plt.show()

# ########################################
# # === Run everything ===
# ########################################

# if __name__ == "__main__":
#     original_cuts = [2.0]
#     epsilon = 1.0
#     step_size = 1.0
#     threshold_C = 30000
#     k=7
#     min_value = 0
#     max_value = 24
#     max_epsilon= 3

#     # print("\n=== Running Algorithm 1: Stability Check ===")
#     # stability = stability_check(time_data, original_cuts, epsilon, step_size, threshold_C)
#     # print(f"Stability check result: {stability}")

#     print("\n=== Running Algorithm 2: Evaluate Partition ===")
#     original_counts = find_stable_binning(time_data,k, min_value, max_value, epsilon, step_size, threshold_C)
#     print(f"Bin counts for original cuts: {original_counts}")

#     # print("\n=== Running Algorithm 3: Worst-case Search ===")
#     # min_epsilon = find_minimal_epsilon(time_data, original_cuts, step_size, threshold_C, max_epsilon)
#     # === Plots ===
#     # plot_histogram(time_data, original_cuts, "Original Cuts", "original_cuts.png")



import itertools
import time
from dataclasses import dataclass
from typing import List, Optional, Sequence

import numpy as np
import pandas as pd


# ============================================================
# Data loading
# ============================================================

df = pd.read_csv("Accidents_rounded.csv")

time_data = pd.to_numeric(
    df["Time"],
    errors="coerce"
).dropna().to_numpy(dtype=float)


# ============================================================
# General validation helpers
# ============================================================

def validate_cuts(
    cuts: Sequence[float],
    min_value: float,
    max_value: float
) -> np.ndarray:
    """
    Validate and return the cut vector as a NumPy array.
    """
    cuts_array = np.asarray(cuts, dtype=float)

    if cuts_array.ndim != 1:
        raise ValueError("cuts must be a one-dimensional sequence")

    if len(cuts_array) == 0:
        raise ValueError("cuts cannot be empty")

    if not np.all(np.isfinite(cuts_array)):
        raise ValueError("cuts must contain only finite values")

    if np.any(np.diff(cuts_array) <= 0):
        raise ValueError("cuts must be strictly increasing")

    if np.any(cuts_array < min_value):
        raise ValueError(
            f"All cuts must be at least {min_value}"
        )

    if np.any(cuts_array > max_value):
        raise ValueError(
            f"All cuts must be at most {max_value}"
        )

    return cuts_array


def calculate_saturation_epsilon(
    original_cuts: Sequence[float],
    min_value: float,
    max_value: float,
    step_size: float
) -> float:
    """
    Calculate the epsilon after which no new valid grid-aligned
    perturbations can be generated.

    This is not a user-selected max_epsilon. It is calculated
    automatically from the domain and the original cuts.
    """
    cuts = validate_cuts(
        original_cuts,
        min_value,
        max_value
    )

    if step_size <= 0:
        raise ValueError("step_size must be greater than 0")

    maximum_possible_displacement = max(
        np.max(cuts - min_value),
        np.max(max_value - cuts)
    )

    number_of_steps = int(
        np.ceil(
            maximum_possible_displacement / step_size
            - 1e-12
        )
    )

    return number_of_steps * step_size


# ============================================================
# Perturbation generation
# ============================================================

def generate_perturbations(
    original_cuts: Sequence[float],
    epsilon: float,
    step_size: float,
    min_value: float,
    max_value: float
) -> List[np.ndarray]:
    """
    Generate all valid perturbations of the original cuts.

    Each cut may move by:

        -epsilon, -epsilon + step_size, ..., +epsilon

    A perturbation is kept only when:

    1. Every cut remains inside [min_value, max_value].
    2. The cuts remain strictly increasing.
    """
    if epsilon < 0:
        raise ValueError("epsilon must be non-negative")

    if step_size <= 0:
        raise ValueError("step_size must be greater than 0")

    original_cuts_array = validate_cuts(
        original_cuts,
        min_value,
        max_value
    )

    number_of_steps = int(
        np.floor(epsilon / step_size + 1e-12)
    )

    possible_step_shifts = range(
        -number_of_steps,
        number_of_steps + 1
    )

    perturbations = []

    for shift_tuple in itertools.product(
        possible_step_shifts,
        repeat=len(original_cuts_array)
    ):
        shifts = np.asarray(
            shift_tuple,
            dtype=float
        )

        perturbed_cuts = (
            original_cuts_array
            + shifts * step_size
        )

        # Reject cuts outside the domain.
        if np.any(perturbed_cuts < min_value - 1e-12):
            continue

        if np.any(perturbed_cuts > max_value + 1e-12):
            continue

        # Reject non-increasing partitions.
        if np.any(np.diff(perturbed_cuts) <= 0):
            continue

        perturbations.append(perturbed_cuts)

    return perturbations


# ============================================================
# Naive count query
# ============================================================

def bin_and_count(
    data: Sequence[float],
    cuts: Sequence[float]
) -> np.ndarray:
    """
    Calculate the count in every bin by scanning the raw data.

    For cuts [c1, c2], the bins are:

        bin 0: x < c1
        bin 1: c1 <= x < c2
        bin 2: x >= c2
    """
    data_array = np.asarray(data, dtype=float)
    cuts_array = np.asarray(cuts, dtype=float)

    data_array = data_array[
        np.isfinite(data_array)
    ]

    bin_indices = np.digitize(
        data_array,
        cuts_array,
        right=False
    )

    counts = np.bincount(
        bin_indices,
        minlength=len(cuts_array) + 1
    )

    return counts.astype(np.int64)


# ============================================================
# Prefix-count preprocessing
# ============================================================

@dataclass
class CountPrefixTable:
    """
    Prefix table for count aggregation.

    prefix_counts[i] stores the number of values smaller than:

        min_value + i * step_size
    """

    min_value: float
    max_value: float
    step_size: float
    prefix_counts: np.ndarray
    total_count: int

    @property
    def number_of_cells(self) -> int:
        return len(self.prefix_counts) - 1


def build_count_prefix_table(
    data: Sequence[float],
    min_value: float,
    max_value: float,
    step_size: float
) -> CountPrefixTable:
    """
    Preprocess the data into grid-cell counts and prefix counts.

    Preprocessing complexity:

        O(n + m)

    where:
        n = number of data points
        m = number of grid cells
    """
    if step_size <= 0:
        raise ValueError("step_size must be greater than 0")

    if max_value <= min_value:
        raise ValueError(
            "max_value must be greater than min_value"
        )

    number_of_cells_float = (
        max_value - min_value
    ) / step_size

    number_of_cells = int(
        round(number_of_cells_float)
    )

    if not np.isclose(
        number_of_cells_float,
        number_of_cells
    ):
        raise ValueError(
            "The domain length must be divisible by step_size"
        )

    data_array = np.asarray(data, dtype=float)
    data_array = data_array[
        np.isfinite(data_array)
    ]

    cell_counts = np.zeros(
        number_of_cells,
        dtype=np.int64
    )

    # Values smaller than the domain minimum belong to the first
    # histogram bin for every valid cut vector.
    number_below_minimum = int(
        np.sum(data_array < min_value)
    )

    inside_domain_mask = (
        (data_array >= min_value)
        & (data_array < max_value)
    )

    inside_domain_data = data_array[
        inside_domain_mask
    ]

    if len(inside_domain_data) > 0:
        cell_indices = np.floor(
            (
                inside_domain_data
                - min_value
            ) / step_size
        ).astype(np.int64)

        cell_indices = np.clip(
            cell_indices,
            0,
            number_of_cells - 1
        )

        cell_counts += np.bincount(
            cell_indices,
            minlength=number_of_cells
        )

    prefix_counts = np.empty(
        number_of_cells + 1,
        dtype=np.int64
    )

    prefix_counts[0] = number_below_minimum

    prefix_counts[1:] = (
        number_below_minimum
        + np.cumsum(cell_counts)
    )

    return CountPrefixTable(
        min_value=float(min_value),
        max_value=float(max_value),
        step_size=float(step_size),
        prefix_counts=prefix_counts,
        total_count=len(data_array)
    )


def cut_to_prefix_index(
    prefix_table: CountPrefixTable,
    cut: float
) -> int:
    """
    Convert a cut value into its prefix-table index.

    The cut must be aligned with the prefix grid.
    """
    relative_position = (
        float(cut)
        - prefix_table.min_value
    ) / prefix_table.step_size

    index = int(round(relative_position))

    if not np.isclose(
        relative_position,
        index,
        atol=1e-9
    ):
        raise ValueError(
            f"Cut {cut} is not aligned with the prefix grid"
        )

    if index < 0 or index > prefix_table.number_of_cells:
        raise ValueError(
            f"Cut {cut} is outside "
            f"[{prefix_table.min_value}, "
            f"{prefix_table.max_value}]"
        )

    return index


def count_below_cut_prefix(
    prefix_table: CountPrefixTable,
    cut: float
) -> int:
    """
    Return the number of data points x satisfying x < cut.

    Complexity: O(1)
    """
    index = cut_to_prefix_index(
        prefix_table,
        cut
    )

    return int(
        prefix_table.prefix_counts[index]
    )


def bin_and_count_prefix(
    prefix_table: CountPrefixTable,
    cuts: Sequence[float]
) -> np.ndarray:
    """
    Calculate all bin counts from the prefix table.

    Each interval count is calculated using:

        prefix[right] - prefix[left]

    A single interval query is O(1).

    For k cuts, calculating all k+1 bins takes O(k).
    """
    cuts_array = np.asarray(
        cuts,
        dtype=float
    )

    if len(cuts_array) == 0:
        return np.asarray(
            [prefix_table.total_count],
            dtype=np.int64
        )

    if np.any(np.diff(cuts_array) <= 0):
        raise ValueError(
            "cuts must be strictly increasing"
        )

    cumulative_counts = np.asarray(
        [
            count_below_cut_prefix(
                prefix_table,
                cut
            )
            for cut in cuts_array
        ],
        dtype=np.int64
    )

    bin_counts = np.empty(
        len(cuts_array) + 1,
        dtype=np.int64
    )

    # First bin: x < first cut
    bin_counts[0] = cumulative_counts[0]

    # Middle bins
    if len(cuts_array) > 1:
        bin_counts[1:-1] = np.diff(
            cumulative_counts
        )

    # Final bin: x >= final cut
    bin_counts[-1] = (
        prefix_table.total_count
        - cumulative_counts[-1]
    )

    return bin_counts


# ============================================================
# Algorithm 1A: Naive stability check
# ============================================================

def stability_check_naive(
    data: Sequence[float],
    original_cuts: Sequence[float],
    epsilon: float,
    step_size: float,
    threshold_C: float,
    min_value: float,
    max_value: float,
    verbose: bool = False
) -> str:
    """
    Algorithm 1 using the naive count query.

    The original query is compared separately with every valid
    perturbation.
    """
    if threshold_C <= 0:
        raise ValueError(
            "threshold_C must be greater than 0"
        )

    original_cuts_array = validate_cuts(
        original_cuts,
        min_value,
        max_value
    )

    original_counts = bin_and_count(
        data,
        original_cuts_array
    )

    perturbations = generate_perturbations(
        original_cuts=original_cuts_array,
        epsilon=epsilon,
        step_size=step_size,
        min_value=min_value,
        max_value=max_value
    )

    if verbose:
        print(
            f"ε = {epsilon}: "
            f"{len(perturbations)} valid perturbations"
        )

    for perturbed_cuts in perturbations:
        perturbed_counts = bin_and_count(
            data,
            perturbed_cuts
        )

        differences = np.abs(
            original_counts
            - perturbed_counts
        )

        if np.any(differences >= threshold_C):
            if verbose:
                print("Not stable")
                print(
                    "Failing cuts:",
                    perturbed_cuts.tolist()
                )
                print(
                    "Original counts:",
                    original_counts
                )
                print(
                    "Perturbed counts:",
                    perturbed_counts
                )
                print(
                    "Differences:",
                    differences
                )

            return "Not Stable"

    if verbose:
        print("Stable")

    return "Stable"


# ============================================================
# Algorithm 1B: Prefix-optimized stability check
# ============================================================

def stability_check_prefix(
    prefix_table: CountPrefixTable,
    original_cuts: Sequence[float],
    epsilon: float,
    step_size: float,
    threshold_C: float,
    verbose: bool = False
) -> str:
    """
    Algorithm 1 using prefix-count queries.

    It uses the same stability definition as the naive version.
    """
    if threshold_C <= 0:
        raise ValueError(
            "threshold_C must be greater than 0"
        )

    original_cuts_array = validate_cuts(
        original_cuts,
        prefix_table.min_value,
        prefix_table.max_value
    )

    original_counts = bin_and_count_prefix(
        prefix_table,
        original_cuts_array
    )

    perturbations = generate_perturbations(
        original_cuts=original_cuts_array,
        epsilon=epsilon,
        step_size=step_size,
        min_value=prefix_table.min_value,
        max_value=prefix_table.max_value
    )

    if verbose:
        print(
            f"ε = {epsilon}: "
            f"{len(perturbations)} valid perturbations"
        )

    for perturbed_cuts in perturbations:
        perturbed_counts = bin_and_count_prefix(
            prefix_table,
            perturbed_cuts
        )

        differences = np.abs(
            original_counts
            - perturbed_counts
        )

        if np.any(differences >= threshold_C):
            if verbose:
                print("Not stable")
                print(
                    "Failing cuts:",
                    perturbed_cuts.tolist()
                )
                print(
                    "Original counts:",
                    original_counts
                )
                print(
                    "Perturbed counts:",
                    perturbed_counts
                )
                print(
                    "Differences:",
                    differences
                )

            return "Not Stable"

    if verbose:
        print("Stable")

    return "Stable"


# ============================================================
# Algorithm 1C: Prefix-optimized with Extreme-First Heuristic
# ============================================================

def stability_check_prefix_extreme_first(
    prefix_table: CountPrefixTable,
    original_cuts: Sequence[float],
    epsilon: float,
    step_size: float,
    threshold_C: float,
    verbose: bool = False
) -> str:
    """
    Algorithm 1 using prefix-count queries with a fail-fast optimization.
    
    It sorts the generated perturbations so that the most extreme shifts 
    (maximum epsilon distances) are evaluated first. If a cut is unstable, 
    this guarantees we find the failure almost immediately.
    """
    if threshold_C <= 0:
        raise ValueError("threshold_C must be greater than 0")

    original_cuts_array = validate_cuts(
        original_cuts,
        prefix_table.min_value,
        prefix_table.max_value
    )

    original_counts = bin_and_count_prefix(
        prefix_table,
        original_cuts_array
    )

    perturbations = generate_perturbations(
        original_cuts=original_cuts_array,
        epsilon=epsilon,
        step_size=step_size,
        min_value=prefix_table.min_value,
        max_value=prefix_table.max_value
    )

    # --- THE OPTIMIZATION ---
    # Sort perturbations descending based on their total absolute distance 
    # from the original cuts. This puts extreme shifts (e.g., ±5) at index 0.
    perturbations.sort(
        key=lambda p: np.sum(np.abs(p - original_cuts_array)),
        reverse=True
    )

    if verbose:
        print(f"ε = {epsilon}: {len(perturbations)} valid perturbations (Extreme First)")

    for perturbed_cuts in perturbations:
        perturbed_counts = bin_and_count_prefix(
            prefix_table,
            perturbed_cuts
        )

        differences = np.abs(original_counts - perturbed_counts)

        if np.any(differences >= threshold_C):
            if verbose:
                print("Not stable")
                print("Failing cuts:", perturbed_cuts.tolist())
                print("Original counts:", original_counts)
                print("Perturbed counts:", perturbed_counts)
                print("Differences:", differences)

            return "Not Stable"

    if verbose:
        print("Stable")

    return "Stable"



# ============================================================
# Algorithm 1D: Prefix-optimized (Count-Only Extremes)
# ============================================================

def stability_check_prefix_count_optimized(
    prefix_table: CountPrefixTable,
    original_cuts: Sequence[float],
    epsilon: float,
    step_size: float,
    threshold_C: float,
    verbose: bool = False
) -> str:
    """
    Algorithm 1 highly optimized strictly for COUNT aggregation.
    Exploits the monotonic nature of counts by evaluating ONLY the absolute 
    maximum extreme shifts. If the extremes are stable, the inner shifts 
    are mathematically guaranteed to be stable.
    """
    if threshold_C <= 0:
        raise ValueError("threshold_C must be greater than 0")

    original_cuts_array = validate_cuts(
        original_cuts,
        prefix_table.min_value,
        prefix_table.max_value
    )

    original_counts = bin_and_count_prefix(
        prefix_table,
        original_cuts_array
    )

    # Calculate the maximum allowed shift
    number_of_steps = int(np.floor(epsilon / step_size + 1e-12))
    
    if number_of_steps == 0:
        extreme_shifts = [0]
    else:
        # ONLY check the extreme negative and positive limits
        extreme_shifts = [-number_of_steps, number_of_steps]

    perturbations = []
    import itertools
    for shift_tuple in itertools.product(extreme_shifts, repeat=len(original_cuts_array)):
        shifts = np.asarray(shift_tuple, dtype=float)
        perturbed_cuts = original_cuts_array + shifts * step_size

        # Reject cuts outside the domain or crossing cuts
        if np.any(perturbed_cuts < prefix_table.min_value - 1e-12):
            continue
        if np.any(perturbed_cuts > prefix_table.max_value + 1e-12):
            continue
        if np.any(np.diff(perturbed_cuts) <= 0):
            continue

        perturbations.append(perturbed_cuts)

    if verbose:
        print(f"ε = {epsilon}: {len(perturbations)} extreme combinations checked (Count Optimized)")

    for perturbed_cuts in perturbations:
        perturbed_counts = bin_and_count_prefix(
            prefix_table,
            perturbed_cuts
        )

        differences = np.abs(original_counts - perturbed_counts)

        if np.any(differences >= threshold_C):
            if verbose:
                print("Not stable")
            return "Not Stable"

    if verbose:
        print("Stable")

    return "Stable"
# ============================================================
# Algorithm 3A: Naive maximum stable epsilon
# ============================================================

def find_maximum_stable_epsilon_naive(
    data: Sequence[float],
    original_cuts: Sequence[float],
    step_size: float,
    threshold_C: float,
    min_value: float,
    max_value: float,
    verbose: bool = True
) -> float:
    """
    Increase epsilon until the first unstable epsilon is found.

    No max_epsilon is supplied by the user.

    The function stops when:

    1. The first unstable epsilon is found, or
    2. Every possible valid perturbation has already been included.
    """
    if step_size <= 0:
        raise ValueError(
            "step_size must be greater than 0"
        )

    saturation_epsilon = calculate_saturation_epsilon(
        original_cuts=original_cuts,
        min_value=min_value,
        max_value=max_value,
        step_size=step_size
    )

    epsilon = 0.0
    maximum_stable_epsilon: Optional[float] = None

    while epsilon <= saturation_epsilon + 1e-12:
        if verbose:
            print(
                f"\nNaive stability check for ε = {epsilon}"
            )

        result = stability_check_naive(
            data=data,
            original_cuts=original_cuts,
            epsilon=epsilon,
            step_size=step_size,
            threshold_C=threshold_C,
            min_value=min_value,
            max_value=max_value,
            verbose=verbose
        )

        if result == "Not Stable":
            break

        maximum_stable_epsilon = epsilon
        epsilon += step_size

    if maximum_stable_epsilon is None:
        # Normally epsilon = 0 is stable when C > 0.
        maximum_stable_epsilon = 0.0

    if verbose:
        if epsilon <= saturation_epsilon + 1e-12:
            print(
                f"\nFirst unstable epsilon: {epsilon}"
            )
        else:
            print(
                "\nAll possible valid perturbations are stable."
            )

        print(
            "Maximum stable epsilon:",
            maximum_stable_epsilon
        )

    return maximum_stable_epsilon


# ============================================================
# Algorithm 3B: Prefix maximum stable epsilon
# ============================================================

def find_maximum_stable_epsilon_prefix(
    prefix_table: CountPrefixTable,
    original_cuts: Sequence[float],
    step_size: float,
    threshold_C: float,
    verbose: bool = True
) -> float:
    """
    Increase epsilon until the first unstable epsilon is found,
    using the prefix-count stability check.

    No max_epsilon is supplied by the user.
    """
    if step_size <= 0:
        raise ValueError(
            "step_size must be greater than 0"
        )

    saturation_epsilon = calculate_saturation_epsilon(
        original_cuts=original_cuts,
        min_value=prefix_table.min_value,
        max_value=prefix_table.max_value,
        step_size=step_size
    )

    epsilon = 0.0
    maximum_stable_epsilon: Optional[float] = None

    while epsilon <= saturation_epsilon + 1e-12:
        if verbose:
            print(
                f"\nPrefix stability check for ε = {epsilon}"
            )

        result = stability_check_prefix(
            prefix_table=prefix_table,
            original_cuts=original_cuts,
            epsilon=epsilon,
            step_size=step_size,
            threshold_C=threshold_C,
            verbose=verbose
        )

        if result == "Not Stable":
            break

        maximum_stable_epsilon = epsilon
        epsilon += step_size

    if maximum_stable_epsilon is None:
        maximum_stable_epsilon = 0.0

    if verbose:
        if epsilon <= saturation_epsilon + 1e-12:
            print(
                f"\nFirst unstable epsilon: {epsilon}"
            )
        else:
            print(
                "\nAll possible valid perturbations are stable."
            )

        print(
            "Maximum stable epsilon:",
            maximum_stable_epsilon
        )

    return maximum_stable_epsilon


# ============================================================
# Algorithm 3c: Prefix maximum stable epsilon count (Optimized)
# ============================================================

def find_maximum_stable_epsilon_prefix_monitonic(
    prefix_table: CountPrefixTable,
    original_cuts: Sequence[float],
    step_size: float,
    threshold_C: float,
    verbose: bool = True
) -> float:
    """
    Increase epsilon until the first unstable epsilon is found.
    Uses the count-optimized stability check which ONLY evaluates 
    the absolute extreme shifts, making it incredibly fast for COUNT.
    """
    if step_size <= 0:
        raise ValueError(
            "step_size must be greater than 0"
        )

    saturation_epsilon = calculate_saturation_epsilon(
        original_cuts=original_cuts,
        min_value=prefix_table.min_value,
        max_value=prefix_table.max_value,
        step_size=step_size
    )

    epsilon = 0.0
    maximum_stable_epsilon: Optional[float] = None

    while epsilon <= saturation_epsilon + 1e-12:
        if verbose:
            print(f"\nPrefix stability check for ε = {epsilon}")

        # ---> STRICT COUNT OPTIMIZATION <---
        # We only generate and check the 2^k extreme boundary combinations.
        result = stability_check_prefix_count_optimized(
            prefix_table=prefix_table,
            original_cuts=original_cuts,
            epsilon=epsilon,
            step_size=step_size,
            threshold_C=threshold_C,
            verbose=verbose
        )

        if result == "Not Stable":
            break

        maximum_stable_epsilon = epsilon
        epsilon += step_size

    if maximum_stable_epsilon is None:
        maximum_stable_epsilon = 0.0

    if verbose:
        if epsilon <= saturation_epsilon + 1e-12:
            print(f"\nFirst unstable epsilon: {epsilon}")
        else:
            print("\nAll possible valid perturbations are stable.")

        print("Maximum stable epsilon:", maximum_stable_epsilon)

    return maximum_stable_epsilon
# ============================================================
# Example execution
# ============================================================

if __name__ == "__main__":
    # ========================================================
    # Configuration
    # ========================================================

    original_cuts = [6.0, 12.0, 18.0]

    min_value = 0.0
    max_value = 24.0

    step_size = 1.0
    threshold_C = 1000000

    test_epsilon = 1.0

    # ========================================================
    # Prefix preprocessing
    # ========================================================

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

    # ========================================================
    # Algorithm 1: Stability check
    # ========================================================

    naive_stability_start = time.perf_counter()

    naive_stability_result = stability_check_naive(
        data=time_data,
        original_cuts=original_cuts,
        epsilon=test_epsilon,
        step_size=step_size,
        threshold_C=threshold_C,
        min_value=min_value,
        max_value=max_value,
        verbose=False
    )

    naive_stability_time = (
        time.perf_counter()
        - naive_stability_start
    )

    optimized_stability_start = time.perf_counter()

    optimized_stability_result = stability_check_prefix(
        prefix_table=prefix_table,
        original_cuts=original_cuts,
        epsilon=test_epsilon,
        step_size=step_size,
        threshold_C=threshold_C,
        verbose=False
    )

    optimized_stability_time = (
        time.perf_counter()
        - optimized_stability_start
    )

    # ========================================================
    # Algorithm 3: Maximum stable epsilon
    # ========================================================

    naive_maximum_start = time.perf_counter()

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

    naive_maximum_time = (
        time.perf_counter()
        - naive_maximum_start
    )

    optimized_maximum_start = time.perf_counter()

    optimized_maximum_epsilon = (
        find_maximum_stable_epsilon_prefix(
            prefix_table=prefix_table,
            original_cuts=original_cuts,
            step_size=step_size,
            threshold_C=threshold_C,
            verbose=False
        )
    )

    optimized_maximum_time = (
        time.perf_counter()
        - optimized_maximum_start
    )

    # ========================================================
    # Results
    # ========================================================

    print("\nALGORITHM 1: STABILITY CHECK")
    print("-" * 60)

    print(
        f"Naive:     result={naive_stability_result}, "
        f"runtime={naive_stability_time:.8f} seconds"
    )

    print(
        f"Optimized: result={optimized_stability_result}, "
        f"runtime={optimized_stability_time:.8f} seconds"
    )

    print(
        f"Optimized including preprocessing: "
        f"{preprocessing_time + optimized_stability_time:.8f} seconds"
    )

    print("\nALGORITHM 3: MAXIMUM STABLE EPSILON")
    print("-" * 60)

    print(
        f"Naive:     epsilon={naive_maximum_epsilon}, "
        f"runtime={naive_maximum_time:.8f} seconds"
    )

    print(
        f"Optimized: epsilon={optimized_maximum_epsilon}, "
        f"runtime={optimized_maximum_time:.8f} seconds"
    )

    print(
        f"Optimized including preprocessing: "
        f"{preprocessing_time + optimized_maximum_time:.8f} seconds"
    )