#!/usr/bin/env python3
"""
Plot the runtime comparison results from timings_epsilon_sweep.csv
with the same colors as the k-sweep plot:
  - Yellow for Alg2 (naive)
  - Blue for Alg4 (DP)
  - Green for Alg5 (edge-consistent)
"""

# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np

# # Read the CSV file
# df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/algorithm_runtimes_count_epsilon_car.csv")
# # df = df[df["k"] == 4.0].copy()
# df = df.sort_values("Epsilon")
# # Create figure and axis
# fig, ax = plt.subplots(figsize=(10, 6))

# # Plot Alg2 (yellow)
# ax.plot(df['Epsilon'], df['Alg2_Time_sec'], 'o-', color='#FFC900', linewidth=2, 
#         markersize=6, label='naive', zorder=6)

# # Plot Alg4 (blue)
# ax.plot(df['Epsilon'], df['Alg4_Time_sec'], 's-', color='#1F77B4', linewidth=2, 
#         markersize=6, label='DP', zorder=6)

# # Plot Alg5_EC (green)
# ax.plot(df['Epsilon'], df['Alg5_Time_sec'], '^-', color='#2CA02C', linewidth=2, 
#         markersize=6, label='Graph-Based', zorder=6)

# # Set y-axis to log scale
# ax.set_yscale('log')


# ax.set_xlim(0,6)
# ax.set_xticks(np.arange(0, 7, 1))
# # Labels and title
# ax.set_xlabel('Epsilon', fontsize=28)
# ax.set_ylabel('time (s, log scale)', fontsize=28)
# # ax.set_title('Runtime vs ε — Alg2, Alg4, Alg5(EC)', fontsize=14, fontweight='bold')

# # Grid
# ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
# ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)

# # Legend
# ax.legend(loc='best', fontsize=20, framealpha=0.9)


# plt.xticks(fontsize=20)
# plt.tick_params(axis='y', which='major', labelsize=20)
# plt.tick_params(axis='y', which='minor', labelsize=20)
# # plt.yticks(fontsize=20)
# # Tight layout
# plt.tight_layout()

# # Save the figure
# plt.savefig("epsilon_comparison.png", dpi=300, bbox_inches='tight')
# print("✓ Plot saved as epsilon_comparison.png")

# # Display the plot
# plt.show()




from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import pandas as pd
import matplotlib.pyplot as plt

# CSV files
files = {
    "Dataset 1": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimes_average_epsilon_income.csv",
    "Dataset 2": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimes_max_income_epsilon.csv",
    "Dataset 3": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimes_Min_epsiln_income.csv",
}

# Same color + marker for the same algorithm
algorithms = {
    "naive": {
        "column": "Alg2_Time_sec",
        "color": "#FFC900",
        "marker": "o",
    },
    "DP": {
        "column": "Alg4_Time_sec",
        "color": "#1F77B4",
        "marker": "s",
    },
    "Graph-Based": {
        "column": "Alg5_Time_sec",
        "color": "#2CA02C",
        "marker": "^",
    },
}

# Different line style for each dataset
dataset_styles = {
    "Dataset 1": "-",
    "Dataset 2": "--",
    "Dataset 3": ":",
}

fig, ax = plt.subplots(figsize=(10, 6))

for dataset_name, file_path in files.items():

    # Read CSV
    df = pd.read_csv(file_path)

    # Sort by Epsilon
    df = df.sort_values("Epsilon")

    # Convert runtime columns to numeric
    for alg_info in algorithms.values():
        column = alg_info["column"]

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Plot each algorithm
    for alg_name, alg_info in algorithms.items():

        ax.plot(
            df["Epsilon"],
            df[alg_info["column"]],
            color=alg_info["color"],          # same color for algorithm
            marker=alg_info["marker"],        # same marker for algorithm
            linestyle=dataset_styles[dataset_name],  # dataset changes line style
            linewidth=4,
            markersize=8,
            zorder=6,
        )


# Log scale
ax.set_yscale("log")
ax.set_ylim(1e-2, 2e2)

# Axis labels
ax.set_xlabel("Epsilon", fontsize=28)
ax.set_ylabel("time (s, log scale)", fontsize=28)

# Limits
ax.set_xlim(0, 6)

# Grid
ax.grid(
    True,
    which="both",
    alpha=0.3,
    linestyle="-",
    linewidth=1
)

ax.grid(
    True,
    which="minor",
    alpha=0.15,
    linestyle=":",
    linewidth=0.6
)

# Legend


# Custom legend: only dataset line styles
# from matplotlib.patches import Patch
# from matplotlib.lines import Line2D

# dataset_legend = [
#     Patch(facecolor='#FFC900', edgecolor='black', label='Naive'),
#     Patch(facecolor='#1F77B4', edgecolor='black', label='DP'),
#     Patch(facecolor='#2CA02C', edgecolor='black', label='Graph based'),

#     Line2D([0], [0], color='black', linewidth=3, linestyle='-',
#            label='AVG Query'),
#     Line2D([0], [0], color='black', linewidth=3, linestyle='--',
#            label='MAX Query'),
#     Line2D([0], [0], color='black', linewidth=3, linestyle=':',
#            label='MIN Query'),
# ]

# ax.legend(
#     handles=dataset_legend,
#     loc='lower center',
#     bbox_to_anchor=(0.5, 1.02),
#     ncol=6,
#     fontsize=20,
#     handlelength=2.5,
#     handleheight=1.6,
#     handletextpad=0.7,
#     columnspacing=1.4,
#     borderpad=0.7
# )

# ax.legend(
#     handles=dataset_legend,
#     loc='best',
#     fontsize=20,
#     framealpha=0.9
# )

plt.xticks(fontsize=20)
plt.yticks(fontsize=20)

plt.tight_layout()

plt.savefig(
    "runtime_comparison_three_datasets_epsilon.png",
    dpi=300,
    bbox_inches="tight"
)

print("✓ Plot saved as runtime_comparison_three_datasets_epsilon.png")

plt.show()

