"""
PM4Py helper functions for loading event logs and discovering process trees.
"""

import pm4py
from typing import Any
try:
    from Functions.process_tree.conversion import enumerate_tau
    from Functions.utils.imports import *
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.process_tree.conversion import enumerate_tau
    from Functions.utils.imports import *


def load_event_log(path: str):
    """Load event log from XES file."""
    return pm4py.read_xes(path)


def discover_tree_inductive(event_log, noise: float):
    """Discover process tree using inductive miner with noise threshold."""
    return pm4py.discover_process_tree_inductive(event_log, noise_threshold=noise)


def assign_tau_labels(tree: Any):
    """Assign tau labels to empty nodes in process tree."""
    counter = [1]
    enumerate_tau(tree, counter)
    return tree

