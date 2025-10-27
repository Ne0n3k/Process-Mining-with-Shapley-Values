# Shapley Mining — logical specifications for process models & Shapley-value analysis

This repository ships the Jupyter notebook `Notebooks/Shapley_mining.ipynb`, which implements a complete pipeline:
- process tree → AST (abstract syntax tree),
- generation of logical specifications (safety/liveness) for workflow patterns,
- optional satisfiability/entailment checks in TPTP using the Vampire prover,
- Shapley-value analysis to estimate each component’s contribution,
- exporting artifacts (CSV, graphs, importance maps) and basic stability diagnostics.

Key files: `Notebooks/Shapley_mining.ipynb`, `requirements.txt`.

---

## Table of Contents
1) Requirements
2) Installation
3) Quickstart
4) Input Data
5) Notebook Overview
6) Proof Configuration (TPTP/Vampire)
7) Shapley-Value Analysis
8) Artifacts & Outputs
9) Parameters & Configuration
10) Troubleshooting

---

## 1) Requirements

- **Python**: 3.11–3.14 recommended (project tested on 3.11)
- **Jupyter**: to run the notebook
- **Python packages**: pinned in `requirements.txt` (e.g., numpy, pandas, pm4py[all], graphviz, matplotlib, plotly, scikit-learn)
- **System dependencies**:
  - **Graphviz binaries** for graph rendering (`dot -V` should work in your shell)
  - **Vampire** (optional) for first-order logic proving on TPTP problems

---

## 2) Installation

1) Create and activate a virtual environment

    python -m venv .venv
    #### macOS/Linux
    source .venv/bin/activate
    #### Windows (PowerShell)
    .venv\Scripts\Activate.ps1

2) Install dependencies

    pip install -r requirements.txt

3) Verify Graphviz

    dot -V

4) (Optional) Install Vampire and ensure it’s on PATH

    vampire --version

---

## 3) Quickstart

1) Launch Jupyter and open the notebook

    jupyter notebook Notebooks/Shapley_mining.ipynb

2) In the data-loading cell(s), point to your event log (e.g., a `.xes` file).

3) Run cells in order:
   - build the process tree and AST,
   - generate logical specifications,
   - (optional) run satisfiability/entailment checks,
   - estimate Shapley values and export results.

---

## 4) Input Data

- The notebook supports **XES** logs via `pm4py` and, depending on the demo cells, simple CSV inputs.
- Place files under `./Data` or adjust the path in the data-loading cells.

---

## 5) Notebook Overview

- **Imports & Utils** — core libraries, formatting helpers, I/O.
- **Process Tree → AST** — node definitions and conversion logic.
- **Visitor / LogicalSpecificationVisitor** — emits safety/liveness formulas for workflow patterns.
- **Workflow Patterns** — operator templates (sequence, XOR, loop, parallel, etc.).
- **Consolidation** — merges formulas into a normalized specification.
- **TPTP & Vampire (optional)** — generates TPTP problems and invokes Vampire with time limits.
- **Coalitions & Shapley** — defines “players”, builds coalitions, estimates Shapley values (Monte Carlo / random sampling), computes stability metrics, and exports artifacts.
- **Visualization** — Graphviz/Matplotlib for expression trees, importance maps, and convergence plots.

---

## 6) Proof Configuration (TPTP/Vampire)

Example settings inside the notebook:

    VAMPIRE_TIME_LIMIT_S = 2
    VAMPIRE_EXTRA_ARGS = ["--mode", "casc"]

- Ensure the `vampire` binary is available on `PATH`. Otherwise, set an absolute path via a helper or environment variable.
- Provided helpers include:
  - `tptp_from_spec_and_conjecture(spec_text, conj_text)` — generate a TPTP problem,
  - `eval_satisfiable(path)` — satisfiability check,
  - `eval_entails(path)` — entailment check.

---

## 7) Shapley-Value Analysis

- **Players**: model/specification elements (e.g., labels, nodes, properties).
- **Value function** `v(·)`: measures coalition “quality” (e.g., satisfiability/entailment outcome or a fitness metric).
- **Estimators**:
  - **Monte Carlo (permutations)** — marginal gains along random orders,
  - **Random Sampling (coalitions)** — random subsets with appropriate weighting.
- **Stability**: L1, max difference, correlations; exported as plots and CSVs.

---

## 8) Artifacts & Outputs

- **CSVs**
  - `players_values.csv` — Shapley values for all players,
  - `configs_meta.csv` — experiment metadata,
  - `stability_summary.csv` — convergence/stability summary.
- **Importance maps**: `shapley_values/maps/` — highlights highest-contribution elements.
- **Graphs**: AST/specification visualizations via Graphviz.
- **Prover logs**: `Docs/Problems/out/` — TPTP problems and Vampire outputs.

---

## 9) Parameters & Configuration

Common knobs:
- input/output paths,
- number of permutations/coalitions for Shapley estimation,
- prover time limits and mode,
- caching of intermediate results.

---

## 10) Troubleshooting

- `dot: command not found` — install Graphviz; confirm with `dot -V`.
- Vampire not found — ensure the binary is on `PATH` or provide an absolute path.
- `pm4py`/XES issues — check `lxml`/`pm4py` versions and the integrity of your `.xes` file.
- Graphs not rendering — ensure **system** Graphviz binaries are installed (Python `graphviz` package alone is not enough).
- Shapley estimation is slow — reduce the number of permutations/coalitions, enable caching, and persist intermediate CSVs.

---
