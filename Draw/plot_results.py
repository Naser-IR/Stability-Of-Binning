# # #!/usr/bin/env python3
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# from matplotlib.ticker import FuncFormatter
# # Read the CSV file
# df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/adult_reconstruction_runtimes.csv")
# # df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/min_sum/aggregates_k_eps_min_stable.csv")
# # keep only epsilon = 1
# # df = df[df["epsilon"] == 1.0].copy()
# # df['Alg2_Time_sec'] = pd.to_numeric(
# #     df['Alg2_Time_sec'],
# #     errors='coerce'
# # )
# df = df.sort_values("C_Threshold")
# # Create figure and axis
# fig, ax = plt.subplots(figsize=(10, 6))


# # ax.plot(df['C_Multiplier']*100, df['Equi_Width_Success_Pct'], 'o-', color='#1f77b4', linewidth=4, 
# #         markersize=8, label='Width', zorder=6)

# # # Plot Alg4 (blue)
# # ax.plot(df['C_Multiplier']*100, df['Equi_Depth_Success_Pct'], 's-', color='#ff7f0e', linewidth=4, 
# #         markersize=8, label='Depth', zorder=6)
# # Plot Alg2 (yellow)
# ax.plot(df['C_Threshold'], df['Alg2_Time_sec'], 'o-', color='#FFC900', linewidth=4, 
#         markersize=8, label='naive', zorder=6)

# # Plot Alg4 (blue)
# ax.plot(df['C_Threshold'], df['Alg4_Time_sec'], 's-', color='#1F77B4', linewidth=4, 
#         markersize=8, label='DP', zorder=6)

# # Plot Alg5_EC (green)
# ax.plot(df['C_Threshold'], df['Alg5_Time_sec'], '^-', color='#2CA02C', linewidth=4, 
#         markersize=8, label='Graph-Based ', zorder=6)

# # Set y-axis to log scale
# # ax.set_yscale('log')
# # ax.set_ylim(1e-2, 2e2)
# def sci_format(x, pos):
#     if x == 0:
#         return "0"
#     exponent = 3
#     value = x / 10**exponent
#     return rf"${value:g}$"

# ax.xaxis.set_major_formatter(FuncFormatter(sci_format))
# # Labels and title
# ax.set_xlabel(r"C ($\times 10^3$)", fontsize=28)
# ax.set_ylabel('time (s)', fontsize=28)
# # ax.set_title('Runtime vs k — Alg2, Alg4, Alg5(EC)', fontsize=14, fontweight='bold')

# # Grid
# ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
# ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)

# # Legend
# ax.legend(loc='best', fontsize=20, framealpha=0.9)

# # Set x-axis limits
# ax.set_xlim(0, 5500)
# ax.set_xticks(np.arange(0, 5600, 500))

# plt.xticks(fontsize=20)
# plt.yticks(fontsize=20)

# # Tight layout
# plt.tight_layout()

# # Save the figure
# plt.savefig("changing_C_income.png", dpi=300, bbox_inches='tight')
# print("✓ Plot saved as changing_C_income.png")

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





#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import ScalarFormatter
# ==========================================
# GLOBAL CONFIGURATION VARIABLES
# ==========================================
FIG_SIZE = (10, 5)
FONT_SIZE_LABEL = 30
FONT_SIZE_TICKS = 22
FONT_SIZE_LEGEND = 22
LINE_WIDTH = 5
MARKER_SIZE = 10
DPI = 300
GRID_ALPHA_MAJOR = 0.3
GRID_ALPHA_MINOR = 0.15

# Colors and Markers
COLOR_NAIVE = '#FFC900'
COLOR_DP = '#1F77B4'
COLOR_GRAPH = '#2CA02C'

# ==========================================
# 12 SPECIFIC GRAPH FUNCTIONS
# ==========================================
def plot_graph_K_count_crime():
        df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/query result/algorithm_runtimes_crimescount.csv")

        df = df.sort_values("k")
        # Create figure and axis
        fig, ax = plt.subplots(figsize=FIG_SIZE)

        # Plot Alg2 (yellow)
        ax.plot(df['k'], df['Alg2_Time_sec'], 'o-', color='#FFC900', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='naive', zorder=6)

        # Plot Alg4 (blue)
        ax.plot(df['k'], df['Alg4_Time_sec'], 's-', color='#1F77B4', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='DP', zorder=6)

        # Plot Alg5_EC (green)
        ax.plot(df['k'], df['Alg5_Time_sec'], '^-', color='#2CA02C', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='Graph-Based ', zorder=6)

        # Set y-axis to log scale
        ax.set_yscale('log')

        # ax.xaxis.set_major_formatter(FuncFormatter(sci_format))
        # Labels and title
        ax.set_xlabel("k", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel('time (s, log scale)', fontsize=FONT_SIZE_LABEL)
        # ax.set_title('Runtime vs k — Alg2, Alg4, Alg5(EC)', fontsize=14, fontweight='bold')

        # Grid
        ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)

        # Legend
        # ax.legend(loc='best', fontsize=FONT_SIZE_LEGEND, framealpha=0.9)

        # Set x-axis limits
        ax.set_xlim(2, 11)
        ax.set_xticks(np.arange(2, 11))

        plt.xticks(fontsize=FONT_SIZE_TICKS)
        plt.yticks(fontsize=FONT_SIZE_TICKS)

        # Tight layout
        plt.tight_layout()

        # Save the figure
        plt.savefig("changing_k_crimescount.png", dpi=300, bbox_inches='tight')
        print("✓ Plot saved as changing_k_crimescount.png")

        # Display the plot
        plt.show()


def plot_graph_K_count_car():
        df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/query result/algorithm_runtimes_countcar.csv")

        df = df.sort_values("k")
        # Create figure and axis
        fig, ax = plt.subplots(figsize=FIG_SIZE)


        # Plot Alg2 (yellow)
        ax.plot(df['k'], df['Alg2_Time_sec'], 'o-', color='#FFC900', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='naive', zorder=6)

        # Plot Alg4 (blue)
        ax.plot(df['k'], df['Alg4_Time_sec'], 's-', color='#1F77B4', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='DP', zorder=6)

        # Plot Alg5_EC (green)
        ax.plot(df['k'], df['Alg5_Time_sec'], '^-', color='#2CA02C', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='Graph-Based ', zorder=6)

        # Set y-axis to log scale
        ax.set_yscale('log')
        # ax.set_ylim(1e-2, 2e2)

        # Labels and title
        ax.set_xlabel("k", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel('time (s, log scale)', fontsize=FONT_SIZE_LABEL)
        # ax.set_title('Runtime vs k — Alg2, Alg4, Alg5(EC)', fontsize=14, fontweight='bold')

        # Grid
        ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)



        # Set x-axis limits
        ax.set_xlim(2, 11)
        ax.set_xticks(np.arange(2, 11))

        plt.xticks(fontsize=FONT_SIZE_TICKS)
        plt.yticks(fontsize=FONT_SIZE_TICKS)

        # Tight layout
        plt.tight_layout()

        # Save the figure
        plt.savefig("changing_k_countcar.png", dpi=300, bbox_inches='tight')
        print("✓ changing_k_countcar.png")

        # Display the plot
        plt.show()

def plot_graph_K_income():
        # CSV files
        files = {
        "Dataset 1": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimesAVGincome.csv",
        "Dataset 2": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimesMaxincome.csv",
        "Dataset 3": "/Users/naserihab/Desktop/dataset-search/query result/adult_reconstruction_runtimes.csv",
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


        # =========================================================
        # MAIN PLOT
        # =========================================================

        fig, ax = plt.subplots(figsize=FIG_SIZE)

        for dataset_name, file_path in files.items():

        # Read CSV
                df = pd.read_csv(file_path)

                # Sort by k
                df = df.sort_values("k")

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
                        df["k"],
                        df[alg_info["column"]],
                        color=alg_info["color"],
                        marker=alg_info["marker"],
                        linestyle=dataset_styles[dataset_name],
                        linewidth=LINE_WIDTH,
                        markersize=MARKER_SIZE,
                        zorder=6,
                        )


        # Log scale
        ax.set_yscale("log")
        ax.set_ylim(1e-2, 2e2)

        # Axis labels
        ax.set_xlabel("k", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel("time (s, log scale)", fontsize=FONT_SIZE_LABEL)

        # Limits
        ax.set_xlim(2, 11)

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

        # Tick sizes
        ax.tick_params(
        axis="both",
        which="major",
        labelsize=FONT_SIZE_TICKS
        )

        ax.tick_params(
        axis="both",
        which="minor",
        labelsize=FONT_SIZE_TICKS
        )

        plt.tight_layout()

        # Save ONLY the plot
        plt.savefig(
        "runtime_comparison_three_datasets.png",
        dpi=300,
        bbox_inches="tight"
        )

        print("✓ Plot saved as runtime_comparison_three_datasets.png")

        plt.show()

def ms_sci_format(y, pos):
    if y == 0:
        return "0"
    
    # Convert seconds (e.g., 0.012) to milliseconds (12.0)
    y_ms = y * 1000
    
    # Format as a general number (removes unnecessary trailing zeros)
    return f"{y_ms:g}"

# Apply the formatter to the Y-axis


def plot_graph_epsilon_count_car():
        df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/algorithm_runtimes_count_epsilon_car.csv")

        df = df.sort_values("Epsilon")
        # Create figure and axis
        fig, ax = plt.subplots(figsize=FIG_SIZE)

        ax.plot(df['Epsilon'], df['Alg2_Time_sec']*1000, 'o-', color='#FFC900', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='naive', zorder=6)

        # Plot Alg4 (blue)
        ax.plot(df['Epsilon'], df['Alg4_Time_sec']*1000, 's-', color='#1F77B4', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='DP', zorder=6)

        # Plot Alg5_EC (green)
        ax.plot(df['Epsilon'], df['Alg5_Time_sec']*1000, '^-', color='#2CA02C', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='Graph-Based ', zorder=6)

        # Set y-axis to log scale
        ax.set_yscale('log')

        y_formatter = ScalarFormatter()
        y_formatter.set_scientific(False)
        ax.yaxis.set_major_formatter(y_formatter)
        ax.yaxis.set_minor_formatter(y_formatter)

        # Labels and title
        ax.set_xlabel("Epsilon", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel('time (ms, log scale)', fontsize=FONT_SIZE_LABEL)
        # ax.set_title('Runtime vs k — Alg2, Alg4, Alg5(EC)', fontsize=14, fontweight='bold')

        # Grid
        ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)


        # Set x-axis limits
        ax.set_xlim(0, 6)
        ax.set_xticks(np.arange(0, 7))

        plt.xticks(fontsize=FONT_SIZE_TICKS)
        ax.tick_params(axis='both', which='both', labelsize=FONT_SIZE_TICKS)

        # Tight layout
        plt.tight_layout()

        # Save the figure
        plt.savefig("changing_epsilon_car_ount.png", dpi=300, bbox_inches='tight')
        print("✓ Plot saved as changing_epsilon_car_ount.png")

        # Display the plot
        plt.show()

def plot_graph_epsilon_count_crimes():
        df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/query result/algorithm_runtimescountepsilon_crimes.csv")

        df = df.sort_values("Epsilon")
        # Create figure and axis
        fig, ax = plt.subplots(figsize=FIG_SIZE)

        ax.plot(df['Epsilon'], df['Alg2_Time_sec']*1000, 'o-', color='#FFC900', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='naive', zorder=6)

        # Plot Alg4 (blue)
        ax.plot(df['Epsilon'], df['Alg4_Time_sec']*1000, 's-', color='#1F77B4', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='DP', zorder=6)

        # Plot Alg5_EC (green)
        ax.plot(df['Epsilon'], df['Alg5_Time_sec']*1000, '^-', color='#2CA02C', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='Graph-Based ', zorder=6)

        # Set y-axis to log scale
        ax.set_yscale('log')
        
        ax.set_yticks([6, 10])
        # ax.set_yticks(np.arange(5, 15,1))

        y_formatter = ScalarFormatter()
        y_formatter.set_scientific(False)
        ax.yaxis.set_major_formatter(y_formatter)
        # ax.yaxis.set_minor_formatter(y_formatter)

        # Labels and title
        ax.set_xlabel("Epsilon", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel('time (ms, log scale)', fontsize=FONT_SIZE_LABEL)
        # ax.set_title('Runtime vs k — Alg2, Alg4, Alg5(EC)', fontsize=14, fontweight='bold')

        # Grid
        ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)


        # Set x-axis limits
        ax.set_xlim(0, 6)
        ax.set_xticks(np.arange(0, 7))

        plt.xticks(fontsize=FONT_SIZE_TICKS)
        ax.tick_params(axis='both', which='both', labelsize=FONT_SIZE_TICKS)

        # Tight layout
        plt.tight_layout()

        # Save the figure
        plt.savefig("changing_epsilon_crimescount.png", dpi=300, bbox_inches='tight')
        print("✓ Plot saved as changing_epsilon_crimescount.png")

        # Display the plot
        plt.show()

def plot_graph_epsilon_income():
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

        fig, ax = plt.subplots(figsize=FIG_SIZE)

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
                        linewidth=LINE_WIDTH,
                        markersize=MARKER_SIZE,
                        zorder=6,
                        )


        # Log scale
        ax.set_yscale("log")
        ax.set_ylim(1e-2, 2e2)

        # Axis labels
        ax.set_xlabel("Epsilon", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel("time (s, log scale)", fontsize=FONT_SIZE_LABEL)

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

        plt.xticks(fontsize=FONT_SIZE_TICKS)
        plt.yticks(fontsize=FONT_SIZE_TICKS)

        plt.tight_layout()

        plt.savefig(
        "untime_comparison_three_datasets_epsilon.png",
        dpi=300,
        bbox_inches="tight"
        )

        print("✓ Plot saved as runtime_comparison_three_datasets_epsilon.png")

        plt.show()


def plot_graph_C_count_car():
        df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/algorithm_runtimes_count_car.csv")

        df = df.sort_values("C_Base")
        
        # ==========================================
        # THE FIX: Divide the X-axis data by 1000
        # ==========================================
        df['C_Base'] = df['C_Base'] / 1000
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=FIG_SIZE)

        ax.plot(df['C_Base'], df['Alg2_Time_sec'], 'o-', color='#FFC900', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='naive', zorder=6)

        # Plot Alg4 (blue)
        ax.plot(df['C_Base'], df['Alg4_Time_sec'], 's-', color='#1F77B4', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='DP', zorder=6)

        # Plot Alg5_EC (green)
        ax.plot(df['C_Base'], df['Alg5_Time_sec'], '^-', color='#2CA02C', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='Graph-Based ', zorder=6)

        # Set y-axis to log scale
        # ax.set_yscale('log')

        # y_formatter = ScalarFormatter()
        # y_formatter.set_scientific(False)
        # ax.yaxis.set_major_formatter(y_formatter)
        # ax.yaxis.set_minor_formatter(y_formatter)

        # ==========================================
        # THE FIX: Add the multiplier to the X label
        # ==========================================
        ax.set_xlabel(r"C ($\times 10^3$)", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel('time (s)', fontsize=FONT_SIZE_LABEL)

        # Grid
        ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)

        # ==========================================
        # ADJUST LIMITS: If your data is 15, 16, etc.
        # 0 to 6 will hide it! Let Matplotlib auto-scale 
        # or set new limits like ax.set_xlim(10, 25)
        # ==========================================
        # ax.set_xlim(0, 6)
        # ax.set_xticks(np.arange(0, 7))

        ax.tick_params(axis='both', which='both', labelsize=FONT_SIZE_TICKS)
        # Legend
        ax.legend(loc='best', fontsize=FONT_SIZE_LEGEND, framealpha=0.9)

        # Tight layout
        plt.tight_layout()

        # Save the figure
        plt.savefig("C_runtimes_count_car.png", dpi=300, bbox_inches='tight')
        print("✓ Plot saved as C_runtimes_count_car.png")

        # Display the plot
        plt.show()

def plot_graph_C_count_crimes():
        df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/algorithm_runtimes_count_crimes.csv")

        df = df.sort_values("C_Base")
        
        # ==========================================
        # THE FIX: Divide the X-axis data by 1000
        # ==========================================
        df['C_Base'] = df['C_Base'] / 1000
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=FIG_SIZE)

        ax.plot(df['C_Base'], df['Alg2_Time_sec'], 'o-', color='#FFC900', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='naive', zorder=6)

        # Plot Alg4 (blue)
        ax.plot(df['C_Base'], df['Alg4_Time_sec'], 's-', color='#1F77B4', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='DP', zorder=6)

        # Plot Alg5_EC (green)
        ax.plot(df['C_Base'], df['Alg5_Time_sec'], '^-', color='#2CA02C', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='Graph-Based ', zorder=6)

        # Set y-axis to log scale
        # ax.set_yscale('log')

        # y_formatter = ScalarFormatter()
        # y_formatter.set_scientific(False)
        # ax.yaxis.set_major_formatter(y_formatter)
        # ax.yaxis.set_minor_formatter(y_formatter)

        # ==========================================
        # THE FIX: Add the multiplier to the X label
        # ==========================================
        ax.set_xlabel(r"C ($\times 10^3$)", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel('time (s)', fontsize=FONT_SIZE_LABEL)

        # Grid
        ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)

        # ==========================================
        # ADJUST LIMITS: If your data is 15, 16, etc.
        # 0 to 6 will hide it! Let Matplotlib auto-scale 
        # or set new limits like ax.set_xlim(10, 25)
        # ==========================================
        # ax.set_xlim(0, 6)
        # ax.set_xticks(np.arange(0, 7))
        # Legend
        ax.legend(loc='best', fontsize=FONT_SIZE_LEGEND, framealpha=0.9)
        ax.tick_params(axis='both', which='both', labelsize=FONT_SIZE_TICKS)

        # Tight layout
        plt.tight_layout()

        # Save the figure
        plt.savefig("C_runtimes_count_crimes.png", dpi=300, bbox_inches='tight')
        print("✓ Plot saved as C_runtimes_count_crimes.png")

        # Display the plot
        plt.show()

def plot_graph_C_income():
        df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/adult_reconstruction_runtimes_C.csv")

        df = df.sort_values("C_Threshold")
        
        # ==========================================
        # THE FIX: Divide the X-axis data by 1000
        # ==========================================
        df['C_Threshold'] = df['C_Threshold'] / 1000
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=FIG_SIZE)

        ax.plot(df['C_Threshold'], df['Alg2_Time_sec'], 'o-', color='#FFC900', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='naive', zorder=6)

        # Plot Alg4 (blue)
        ax.plot(df['C_Threshold'], df['Alg4_Time_sec'], 's-', color='#1F77B4', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='DP', zorder=6)

        # Plot Alg5_EC (green)
        ax.plot(df['C_Threshold'], df['Alg5_Time_sec'], '^-', color='#2CA02C', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='Graph-Based ', zorder=6)

        # Set y-axis to log scale
        # ax.set_yscale('log')



        # ==========================================
        # THE FIX: Add the multiplier to the X label
        # ==========================================
        ax.set_xlabel(r"C ($\times 10^3$)", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel('time (s)', fontsize=FONT_SIZE_LABEL)

        # Grid
        ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)

        # ==========================================
        # ADJUST LIMITS: If your data is 15, 16, etc.
        # 0 to 6 will hide it! Let Matplotlib auto-scale 
        # or set new limits like ax.set_xlim(10, 25)
   
        # Legend
        ax.legend(loc='best', fontsize=FONT_SIZE_LEGEND, framealpha=0.9)
        ax.tick_params(axis='both', which='both', labelsize=FONT_SIZE_TICKS)

        # Tight layout
        plt.tight_layout()

        # Save the figure
        plt.savefig("changing_C_income.png", dpi=300, bbox_inches='tight')
        print("✓ Plot saved as changing_C_income.png")

        # Display the plot
        plt.show()

def plot_graph_algorithm1():
        df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/algorithm1_runtime_3.csv")

        df = df.sort_values("epsilon")
        
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=FIG_SIZE)


        ax.plot(df['epsilon'], df['naive_runtime_seconds'], 'o-', color='#1f77b4', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='naive', zorder=6)

        # Plot Alg4 (blue)
        ax.plot(df['epsilon'], df['prefix_runtime_including_preprocessing_seconds'], 's-', color='#ff7f0e', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='prefix', zorder=6)

        ax.plot(df['epsilon'], df['extreme_runtime_including_preprocessing_seconds'], 'o-', color='#FFC900', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='prefix + monotonic', zorder=6)


        # Set y-axis to log scale
        ax.set_yscale('log')


        # ==========================================
        # THE FIX: Add the multiplier to the X label
        # ==========================================
        ax.set_xlabel('Epsilon', fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel('time (s,log scale)', fontsize=FONT_SIZE_LABEL)

        # Grid
        ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)

        # ==========================================
        # ADJUST LIMITS: If your data is 15, 16, etc.
        # 0 to 6 will hide it! Let Matplotlib auto-scale 
        # or set new limits like ax.set_xlim(10, 25)
        # ==========================================
        ax.set_xlim(0, 8)
        ax.set_xticks(np.arange(0, 9))
        # Legend
        ax.legend(loc='best', fontsize=FONT_SIZE_LEGEND, framealpha=0.9)
        ax.tick_params(axis='both', which='both', labelsize=FONT_SIZE_TICKS)

        # Tight layout
        plt.tight_layout()

        # Save the figure
        plt.savefig("algo1opt.png", dpi=300, bbox_inches='tight')
        print("✓ Plot saved as algo1opt.png")

        # Display the plot
        plt.show()

def plot_graph_algorithm3():
        df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/algorithm3_C_runtime_monotonic.csv")

        df = df.sort_values("C")
        # Assuming your column is named 'C'
        df['C'] = df['C'] / 1000000 
        
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=FIG_SIZE)


        ax.plot(df['C'], df['naive_runtime_seconds'], 'o-', color='#1f77b4', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='naive', zorder=6)

        # Plot Alg4 (blue)
        ax.plot(df['C'], df['prefix_runtime_including_preprocessing_seconds'], 's-', color='#ff7f0e', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='prefix', zorder=6)

        ax.plot(df['C'], df['prefix_monotonic_runtime_including_preprocessing_seconds'], 'o-', color='#FFC900', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='prefix + monotonic', zorder=6)


        # Set y-axis to log scale
        ax.set_yscale('log')

        # ==========================================
        # THE FIX: Add the multiplier to the X label
        # ==========================================
        ax.set_xlabel(r"C ($\times 10^6$)", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel('time (s,log scale)', fontsize=FONT_SIZE_LABEL)

        # Grid
        ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)

        # ==========================================
        # ADJUST LIMITS: If your data is 15, 16, etc.
        # 0 to 6 will hide it! Let Matplotlib auto-scale 
        # or set new limits like ax.set_xlim(10, 25)
        # ==========================================
        # To specifically show ticks from 0.2 to 1.0 in steps of 0.1
        ax.set_xlim(0.1, 1.1)
        ax.set_xticks(np.arange(0.2, 1.1, 0.1))
        # Legend
        ax.legend(loc='best', fontsize=FONT_SIZE_LEGEND, framealpha=0.9)
        ax.tick_params(axis='both', which='both', labelsize=FONT_SIZE_TICKS)

        # Tight layout
        plt.tight_layout()

        # Save the figure
        plt.savefig("algo3opt.png", dpi=300, bbox_inches='tight')
        print("✓ Plot saved as algo3opt.png")

        # Display the plot
        plt.show()

def plot_graph_baseline_compa():
        df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/query result/success_percentages_summary.csv")

        df = df.sort_values("C_Multiplier")
        # Assuming your column is named 'C'

        
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=FIG_SIZE)


        ax.plot(df['C_Multiplier']*100, df['Equi_Width_Success_Pct'], 'o-', color='#1f77b4', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='Width', zorder=6)

        # Plot Alg4 (blue)
        ax.plot(df['C_Multiplier']*100, df['Equi_Depth_Success_Pct'], 's-', color='#ff7f0e', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='Depth', zorder=6)


        # Set y-axis to log scale
        # ax.set_yscale('log')



        # ==========================================
        # THE FIX: Add the multiplier to the X label
        # ==========================================
        ax.set_xlabel('C (percentage)', fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel('time (s)', fontsize=FONT_SIZE_LABEL)

        # Grid
        ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)

        # ==========================================
        # ADJUST LIMITS: If your data is 15, 16, etc.
        # 0 to 6 will hide it! Let Matplotlib auto-scale 
        # or set new limits like ax.set_xlim(10, 25)
        # ==========================================
        # To specifically show ticks from 0.2 to 1.0 in steps of 0.1
        ax.set_xlim(240, 360)
        ax.set_xticks(np.arange(240, 361, 10))
        # Legend
        ax.legend(loc='best', fontsize=FONT_SIZE_LEGEND, framealpha=0.9)
        ax.tick_params(axis='both', which='both', labelsize=FONT_SIZE_TICKS)

        # Tight layout
        plt.tight_layout()

        # Save the figure
        plt.savefig("baselineComp.png", dpi=300, bbox_inches='tight')
        print("✓ Plot saved as baselineComp.png")

        # Display the plot
        plt.show()



def plot_graph_M_changing():
        df = pd.read_csv("/Users/naserihab/Desktop/dataset-search/changing_m.csv")

        df = df.sort_values("m")
        # Assuming your column is named 'C'

        
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=FIG_SIZE)


        ax.plot(df['m'], df['alg5_original_time'], 'o-', color='#1f77b4', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='graph-based', zorder=6)

        # Plot Alg4 (blue)
        ax.plot(df['m'], df['alg5_optimized_time'], 's-', color='#ff7f0e', linewidth=LINE_WIDTH, 
                markersize=MARKER_SIZE, label='boundary-point-filtering ', zorder=6)


        # Set y-axis to log scale
        ax.set_yscale('log')


        # ==========================================
        # THE FIX: Add the multiplier to the X label
        # ==========================================
        ax.set_xlabel('m', fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel('time (s, log scale)', fontsize=FONT_SIZE_LABEL)

        # Grid
        ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=1)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.6)

        # ==========================================
        # ADJUST LIMITS: If your data is 15, 16, etc.
        # 0 to 6 will hide it! Let Matplotlib auto-scale 
        # or set new limits like ax.set_xlim(10, 25)
        # ==========================================

        ax.set_xlim(0, 6000)
        ax.set_xticks(np.arange(0, 6001, 1000))
        # Legend
        ax.legend(loc='best', fontsize=FONT_SIZE_LEGEND, framealpha=0.9)
        ax.tick_params(axis='both', which='both', labelsize=FONT_SIZE_TICKS)

        # Tight layout
        plt.tight_layout()

        # Save the figure
        plt.savefig("m_random.png", dpi=300, bbox_inches='tight')
        print("✓ Plot saved as m_random.png")

        # Display the plot
        plt.show()
# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("Starting batch graph generation...")
#     plot_graph_K_count_crime()
#     plot_graph_K_count_car()
#     plot_graph_K_income()
#     plot_graph_epsilon_count_car()
    plot_graph_epsilon_count_crimes()
#     plot_graph_epsilon_income()
#     plot_graph_C_count_car()
#     plot_graph_C_count_crimes()
#     plot_graph_C_income()
#     plot_graph_algorithm1()
#     plot_graph_algorithm3()
#     plot_graph_baseline_compa()
#     plot_graph_M_changing()
    
    print("Batch generation complete!")