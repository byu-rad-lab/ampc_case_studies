# AMPC Case Studies

This repository contains the code for the case studies that go along with a paper submission.

## Dependencies

This repo requires the following python packages to be on the python path:

- affine_mpc
  - A [repo](https://github.com/byu-rad-lab/affine_mpc) released with the paper submission to perform MPC
- numpy
- matplotlib
- PyQt5
- tqdm
- tabulate

#### Set up Virtual Environment

(This assumes a Linux development environment)

```sh
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

## File Overview

- `run_analysis.py`
  - Runs an approximation point analysis for a single system and reference trajectory combination.
- `plot_analysis.py`
  - Plots results from a single approximation point analysis.
- `run_all.sh`
  - Runs `run_analysis.py` for each system and reference trajectory combination used in the paper.
- `summary_analysis.py`
  - Performs a summary analysis on all the data from `run_all.sh`.
- `summary_plots.py`
  - Generates plots used in the paper after running `summary_analysis.py`

Most of the Python scripts use `argparse` so you can use `-h` to see how to use them.
For example,

```sh
python run_analysis.py -h
```

You can also look at `run_all.sh` to see how I ran all the experiments for the paper.

## Experiment Data

The experiment data used in the paper submission currently can be found [here](https://byu.box.com/s/c34yvr86718yohrkvozcqby3uh6jni58).
This location may change if the need for a more permanent location arises.
