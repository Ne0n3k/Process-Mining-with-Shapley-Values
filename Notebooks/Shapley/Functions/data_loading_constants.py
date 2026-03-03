"""
Constants for data loading.
"""

from typing import Dict

LOG_PATHS: Dict[str, str] = {
    "running_example": "../Data/running-example.xes",
    "hospital_billing": "../Data/Hospital Billing - Event Log.xes",
    "bpi_2012": "../Data/BPI_Challenge_2012.xes",
}

NOISE_LEVELS = [0.0, 0.25, 0.5, 1.0]

