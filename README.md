# Stability of Binning

This repository contains the implementations of the algorithms used for stability verification, radius computation, and the construction problem.

## Stability Verification and Radius Algorithms

The `par.py` file contains the **stability verification algorithm** and the **radius algorithm** for the `COUNT` aggregation function, including all optimizations.

To run the optimized versions of these algorithms:

- `alg1_opt.py` — runs the optimized **stability verification algorithm**.
- `alg2_opt.py` — runs the optimized **radius algorithm**.
- `par2.py` — contains the corresponding algorithms for the **other aggregation functions**.

## Construction Problem

Use `stable_run.py` to run the construction problem with the constraints of interest.

The implementations for the `COUNT` aggregation function are divided into:

- `stable_construction.py` — implementation of the construction problem **without constraints**.
- `stable_constrain.py` — implementation of the construction problem **with constraints**.

For the other aggregation functions:

- `run_glop.py` — can be used to run the construction problem with constraints for the other aggregation functions.
- `glopal.py` — contains the full implementation for these aggregation functions.

## Plotting and Figures

The `Draw` directory contains the Python code used to generate the graphs and figures presented in the paper.

## Experiments

The repository also contains the code used to reproduce the experiments presented in the paper you will able to found the main for running the algorithms including changing the wanted parameters.

### Census Data Reconstruction

The `exp.py` file contains the code used to reconstruct the Census dataset and reproduce the corresponding experimental results.

### Equal-Width and Equal-Depth Binning

The `exp.py` file also contains the experiments comparing **equal-width binning** and **equal-depth binning**.

### Runtime Comparison

The `stable.py` file contains the code used to generate datasets with different domain sizes and compare the runtime of the **graph-based algorithm** and the **filtering-based algorithm**.

## Results

The `\results_csv` directory contains the CSV files for all experiments presented in the paper.

These files can be used to reproduce the figures by running the `plot_results` script located in the `\Draw` directory.


