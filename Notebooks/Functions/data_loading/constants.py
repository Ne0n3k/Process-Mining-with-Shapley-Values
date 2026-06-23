"""
Constants for data loading.
"""

from typing import Dict

LOG_PATHS: Dict[str, str] = {
    "sepsis": "../Data/Sepsis Cases - Event Log.xes",
    "bpi_2013_incidents": "../Data/BPI_Challenge_2013_incidents.xes",
    "road_traffic_fines": "../Data/Road_Traffic_Fine_Management_Process.xes",
}

NOISE_LEVELS = [0.0, 0.25, 0.5, 1.0]

