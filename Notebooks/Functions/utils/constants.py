"""
Constants used across the project.
"""

import os
from typing import Dict

# Pattern rules path
PATTERN_RULES_PATH = "../Data/patterns.json"

# Output directories
OUT_DIR = "../Docs/Problems/out"
OUT_ROOT = "../Docs/Problems/shapley_values"
OUT_SHAPLEY_DIR = os.path.join(OUT_ROOT, "shapley")
SHAPLEY_CACHE_PATH = os.path.join(OUT_SHAPLEY_DIR, "shapley_results.json")

# Vampire settings
VAMPIRE_TIME_LIMIT_S = 2
VAMPIRE_EXTRA_ARGS = ["--mode", "casc"]

# Noise levels
NOISE_LEVELS = [0.0, 0.25, 0.5, 1.0]

# Log paths
LOG_PATHS: Dict[str, str] = {
    "running_example": "../Data/running-example.xes",
    "hospital_billing": "../Data/Hospital Billing - Event Log.xes",
    "bpi_2012": "../Data/BPI_Challenge_2012.xes",
}

