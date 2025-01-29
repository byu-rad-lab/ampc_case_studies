# AMPC Case Studies
This repository contains the code for the case studies that go along with a paper submission.

## Dependencies
This repo requires the following python packages to be on the python path:
- affine_mpc
  - A [repo](https://github.com/byu-rad-lab/affine_mpc) released with the paper submission to perform MPC
- numpy
- matplotlib
- PyQt5 (or newer)
- tqdm
- tabulate

## File Overview
- `run_analysis.py`
  - Runs an approximation point analysis for a single system and reference trajectory combination.
- `plot_analysis.py`
  - Plots results from a single approximation point analysis.
- `run_all.sh`
  - Runs all of the approximation point analyses used in the paper.
- `summary_analysis.py`
  - Performs a summary analysis on all of the data from `run_all.sh`.
- `summary_plots.py`
  - Generates plots used in the paper after running `summary_analysis.py`
