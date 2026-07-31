# #!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# Read the CSV file
df = pd.read_csv("/Users/naserrabah2/Desktop/dataset-search/algorithm3_C_runtime_monotonic.csv")
# df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/min_sum/aggregates_k_eps_min_stable.csv")
# keep only epsilon = 1
# df = df[df["epsilon"] == 1.0].copy()
# df['Alg2_Time_sec'] = pd.to_numeric(
#     df['Alg2_Time_sec'],
#     errors='coerce'
# )
df = df.sort_values("C")
# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 6))


ax.plot(df['C'], df['naive_runtime_seconds'], 'o-', color='#1f77b4', linewidth=4, 
        markersize=8, label='naive', zorder=6)

# Plot Alg4 (blue)
ax.plot(df['C'], df['prefix_runtime_including_preprocessing_seconds'], 's-', color='#ff7f0e', linewidth=4, 
        markersize=8, label='prefix', zorder=6)

ax.plot(df['C'], df['prefix_monotonic_runtime_including_preprocessing_seconds'], 's-', color='#FFC900', linewidth=4, 
        markersize=8, label='prefix + monotonic', zorder=6)
# Plot Alg2 (yellow)
# ax.plot(df['Epsilon'], df['Alg2_Time_sec'], 'o-', color='#FFC900', linewidth=4, 
#         markersize=8, label='naive', zorder=6)

# # Plot Alg4 (blue)
# ax.plot(df['Epsilon'], df['Alg4_Time_sec'], 's-', color='#1F77B4', linewidth=4, 
#         markersize=8, label='DP', zorder=6)

# # Plot Alg5_EC (green)
# ax.plot(df['Epsilon'], df['Alg5_Time_sec'], '^-', color='#2CA02C', linewidth=4, 
#         markersize=8, label='Graph-Based ', zorder=6)

# Set y-axis to log scale
ax.set_yscale('log')
# ax.set_yticks([0.006, 0.01])
# ax.set_yticklabels(['0.6', '1'], fontsize=20)

# ax.set_ylabel(r'time$\times 10^{-2}$ (s, log scale)', fontsize=28)
# ax.set_yticklabels([
#     r'$6 \times 10^{-3}$',
#     r'$10^{-2}$'
# ], fontsize=20)
# ax.tick_params(axis='y', which='both', labelsize=20)
# ax.set_ylim(1e-2, 2e2)
# def sci_format(x, pos):
#     if x == 0:
#         return "0"
#     exponent = 3
#     value = x / 10**exponent
#     return rf"${value:g}$"

# ax.xaxis.set_major_formatter(FuncFormatter(sci_format))
# Labels and title
ax.set_xlabel(r"C ", fontsize=28)
# ax.set_ylabel('time (s, log scale)', fontsize=28)
# ax.set_title('Runtime vs C — Alg2, Alg4, Alg5(EC)', fontsize=14, fontweight='bold')

# Grid
ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)

# Legend
ax.legend(loc='best', fontsize=20, framealpha=0.9)

# Set x-axis limits
# ax.set_xlim(0, 8)
# ax.set_xticks(np.arange(0, 9, 1))
ax.xaxis.set_major_formatter(
    FuncFormatter(lambda x, pos: f'{x / 1e6:.1f}')
)

ax.set_xlabel(r'C ($\times 10^6$)', fontsize=28)

ax.tick_params(axis='x', labelsize=20)

plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
# Keep logarithmic scale
# ax.set_yscale('log')

# Exact Y tick positions
# yticks = [0.012, 0.013, 0.014, 0.015, 0.016, 0.017, 0.018, 0.019]

# ax.set_yticks(yticks)

# Only change what is displayed
# ax.set_yticklabels(
#     ['1.2', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8', '1.9'],
#     fontsize=20
# )

# # Remove minor tick labels
# ax.tick_params(axis='y', which='minor', labelleft=False)

# ax.set_ylabel(
#     r'time $\times 10^{-2}$ (s, log scale)',
#     fontsize=28
# )
# ax.yaxis.set_major_formatter(
#     FuncFormatter(lambda y, pos: f'{y * 100:g}')
# )

# ax.set_xlabel('C', fontsize=28)
ax.set_ylabel(r'time (s, log scale)', fontsize=28)

# ax.tick_params(axis='both', which='major', labelsize=20)
# plt.yticks(fontsize=20)
# ax.set_yticks([0.006, 0.01])
# ax.set_yticklabels(['0.6', '1'], fontsize=20)
# ax.tick_params(axis='y', which='major', labelsize=20)
# Tight layout
plt.tight_layout()

# Save the figure
plt.savefig("algo3opt.png", dpi=300, bbox_inches='tight')
print("✓ Plot saved as changing_C_car_ount.png")

# Display the plot
plt.show()


# from matplotlib.patches import Patch
# from matplotlib.lines import Line2D
# import pandas as pd
# import matplotlib.pyplot as plt

# # CSV files
# files = {
#     "Dataset 1": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimesAVGincome.csv",
#     "Dataset 2": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimesMaxincome.csv",
#     "Dataset 3": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimes.csv",
# }

# # Same color + marker for the same algorithm
# algorithms = {
#     "naive": {
#         "column": "Alg2_Time_sec",
#         "color": "#FFC900",
#         "marker": "o",
#     },
#     "DP": {
#         "column": "Alg4_Time_sec",
#         "color": "#1F77B4",
#         "marker": "s",
#     },
#     "Graph-Based": {
#         "column": "Alg5_Time_sec",
#         "color": "#2CA02C",
#         "marker": "^",
#     },
# }

# # Different line style for each dataset
# dataset_styles = {
#     "Dataset 1": "-",
#     "Dataset 2": "--",
#     "Dataset 3": ":",
# }

# fig, ax = plt.subplots(figsize=(10, 6))

# for dataset_name, file_path in files.items():

#     # Read CSV
#     df = pd.read_csv(file_path)

#     # Sort by k
#     df = df.sort_values("k")

#     # Convert runtime columns to numeric
#     for alg_info in algorithms.values():
#         column = alg_info["column"]

#         df[column] = pd.to_numeric(
#             df[column],
#             errors="coerce"
#         )

#     # Plot each algorithm
#     for alg_name, alg_info in algorithms.items():

#         ax.plot(
#             df["k"],
#             df[alg_info["column"]],
#             color=alg_info["color"],          # same color for algorithm
#             marker=alg_info["marker"],        # same marker for algorithm
#             linestyle=dataset_styles[dataset_name],  # dataset changes line style
#             linewidth=4,
#             markersize=8,
#             zorder=6,
#         )


# # Log scale
# ax.set_yscale("log")
# ax.set_ylim(1e-2, 2e2)

# # Axis labels
# ax.set_xlabel("k", fontsize=28)
# ax.set_ylabel("time (s, log scale)", fontsize=28)

# # Limits
# ax.set_xlim(2, 11)

# # Grid
# ax.grid(
#     True,
#     which="both",
#     alpha=0.3,
#     linestyle="-",
#     linewidth=1
# )

# ax.grid(
#     True,
#     which="minor",
#     alpha=0.15,
#     linestyle=":",
#     linewidth=0.6
# )

# # Legend


# # Custom legend: only dataset line styles
# # from matplotlib.patches import Patch
# # from matplotlib.lines import Line2D

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

# # ax.legend(
# #     handles=dataset_legend,
# #     loc='best',
# #     fontsize=20,
# #     framealpha=0.9
# # )

# plt.xticks(fontsize=20)
# plt.yticks(fontsize=20)

# plt.tight_layout()

# plt.savefig(
#     "runtime_comparison_three_datasets.png",
#     dpi=300,
#     bbox_inches="tight"
# )

# print("✓ Plot saved as runtime_comparison_three_datasets.png")

# plt.show()




# !/usr/bin/env python3


# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np

# # Read the CSV file
# df = pd.read_csv("/Users/naserihab/Desktop/averageincome_sweep_c_epsilon5.csv")
# # df = df[df["k"] == 4.0].copy()
# df = df.sort_values("C")
# # Create figure and axis
# fig, ax = plt.subplots(figsize=(10, 6))

# # Plot Alg2 (yellow)
# ax.plot(df['C'], df['alg2_time'], 'o-', color='#FFC900', linewidth=2, 
#         markersize=6, label='Alg2 (naive)', zorder=3)

# # Plot Alg4 (blue)
# ax.plot(df['C'], df['alg4_time'], 's-', color='#1F77B4', linewidth=2, 
#         markersize=6, label='Alg4 (DP)', zorder=3)

# # Plot Alg5_EC (green)
# ax.plot(df['C'], df['alg5_time'], '^-', color='#2CA02C', linewidth=2, 
#         markersize=6, label='Alg5 (edge-consistent)', zorder=3)

# # Set y-axis to log scale
# ax.set_yscale('log')

# # Labels and title
# ax.set_xlabel('C', fontsize=12)
# ax.set_ylabel('time (s, log scale)', fontsize=12)
# ax.set_title('Runtime vs C — Alg2, Alg4, Alg5(EC)', fontsize=14, fontweight='bold')

# # Grid
# ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=0.5)
# ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.3)

# # Legend
# ax.legend(loc='best', fontsize=11, framealpha=0.9)

# # Tight layout
# plt.tight_layout()

# # Save the figure
# plt.savefig("epsilon_comparison.png", dpi=300, bbox_inches='tight')
# print("✓ Plot saved as epsilon_comparison.png")

# # Display the plot
# plt.show()




# from matplotlib.patches import Patch
# from matplotlib.lines import Line2D
# import pandas as pd
# import matplotlib.pyplot as plt

# # CSV files
# files = {
#     "Dataset 1": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimesAVGincome.csv",
#     "Dataset 2": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimesMaxincome.csv",
#     "Dataset 3": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimes.csv",
# }

# # Same color + marker for the same algorithm
# algorithms = {
#     "naive": {
#         "column": "Alg2_Time_sec",
#         "color": "#FFC900",
#         "marker": "o",
#     },
#     "DP": {
#         "column": "Alg4_Time_sec",
#         "color": "#1F77B4",
#         "marker": "s",
#     },
#     "Graph-Based": {
#         "column": "Alg5_Time_sec",
#         "color": "#2CA02C",
#         "marker": "^",
#     },
# }

# # Different line style for each dataset
# dataset_styles = {
#     "Dataset 1": "-",
#     "Dataset 2": "--",
#     "Dataset 3": ":",
# }


# # =========================================================
# # MAIN PLOT
# # =========================================================

# fig, ax = plt.subplots(figsize=(10, 6))

# for dataset_name, file_path in files.items():

#     # Read CSV
#     df = pd.read_csv(file_path)

#     # Sort by k
#     df = df.sort_values("k")

#     # Convert runtime columns to numeric
#     for alg_info in algorithms.values():
#         column = alg_info["column"]

#         df[column] = pd.to_numeric(
#             df[column],
#             errors="coerce"
#         )

#     # Plot each algorithm
#     for alg_name, alg_info in algorithms.items():

#         ax.plot(
#             df["k"],
#             df[alg_info["column"]],
#             color=alg_info["color"],
#             marker=alg_info["marker"],
#             linestyle=dataset_styles[dataset_name],
#             linewidth=4,
#             markersize=8,
#             zorder=6,
#         )


# # Log scale
# ax.set_yscale("log")
# ax.set_ylim(1e-2, 2e2)

# # Axis labels
# ax.set_xlabel("k", fontsize=28)
# ax.set_ylabel("time (s, log scale)", fontsize=28)

# # Limits
# ax.set_xlim(2, 11)

# # Grid
# ax.grid(
#     True,
#     which="both",
#     alpha=0.3,
#     linestyle="-",
#     linewidth=1
# )

# ax.grid(
#     True,
#     which="minor",
#     alpha=0.15,
#     linestyle=":",
#     linewidth=0.6
# )

# # Tick sizes
# ax.tick_params(
#     axis="both",
#     which="major",
#     labelsize=20
# )

# ax.tick_params(
#     axis="both",
#     which="minor",
#     labelsize=20
# )

# plt.tight_layout()

# # Save ONLY the plot
# plt.savefig(
#     "runtime_comparison_three_datasets.png",
#     dpi=300,
#     bbox_inches="tight"
# )

# print("✓ Plot saved as runtime_comparison_three_datasets.png")

# plt.show()


# # =========================================================
# # SEPARATE LEGEND
# # =========================================================

# dataset_legend = [
#     Patch(
#         facecolor="#FFC900",
#         edgecolor="black",
#         label="Naive"
#     ),

#     Patch(
#         facecolor="#1F77B4",
#         edgecolor="black",
#         label="DP"
#     ),

#     Patch(
#         facecolor="#2CA02C",
#         edgecolor="black",
#         label="Graph based"
#     ),

#     Line2D(
#         [0], [0],
#         color="black",
#         linewidth=4,
#         linestyle="-",
#         label="AVG Query"
#     ),

#     Line2D(
#         [0], [0],
#         color="black",
#         linewidth=4,
#         linestyle="--",
#         label="MAX Query"
#     ),

#     Line2D(
#         [0], [0],
#         color="black",
#         linewidth=4,
#         linestyle=":",
#         label="MIN Query"
#     ),
# ]


# # Create a completely separate figure for the legend
# fig_legend = plt.figure(figsize=(10, 0.5))

# fig_legend.legend(
#     handles=dataset_legend,
#     loc="center",
#     ncol=6,

#     fontsize=20,

#     handlelength=2.5,
#     handleheight=1.6,
#     handletextpad=0.7,

#     columnspacing=1.4,

#     borderpad=0.7,

#     frameon=True,
#     framealpha=1
# )

# # Remove all extra whitespace
# fig_legend.savefig(
#     "runtime_legend.png",
#     dpi=300,
#     bbox_inches="tight",
#     pad_inches=0.05
# )

# print("✓ Legend saved as runtime_legend.png")

# plt.show()