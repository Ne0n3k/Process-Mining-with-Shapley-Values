"""
Ranking and comparison utility functions.
"""

import math
from typing import Dict, List
from scipy.stats import kendalltau
import numpy as np
try:
    from Functions.utils.imports import *
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.utils.imports import *


def sort_players(values: Dict[str, float]) -> list[str]:
    """Sort players by value (descending)."""
    return [pid for pid, _ in sorted(values.items(), key=lambda kv: kv[1], reverse=True)]


def jaccard_at_k(values_a: Dict[str, float], values_b: Dict[str, float], k: int = 10) -> float:
    """Calculate Jaccard similarity at top-k."""
    top_a = set(sort_players(values_a)[:k])
    top_b = set(sort_players(values_b)[:k])
    if not top_a and not top_b:
        return 1.0
    union = top_a | top_b
    return len(top_a & top_b) / len(union) if union else 1.0


def kendall_tau_rank(values_a: Dict[str, float], values_b: Dict[str, float]) -> float:
    """Calculate Kendall tau rank correlation."""
    common = sorted(set(values_a) & set(values_b))
    if len(common) < 2:
        return float("nan")
    order_a = sort_players(values_a)
    order_b = sort_players(values_b)
    rank_a = {pid: idx for idx, pid in enumerate(order_a)}
    rank_b = {pid: idx for idx, pid in enumerate(order_b)}
    a = [rank_a[pid] for pid in common]
    b = [rank_b[pid] for pid in common]
    tau, _ = kendalltau(a, b)
    return tau if tau is not None else float("nan")


def method_stats(name: str, values: Dict[str, float], runtime_s: float) -> dict:
    """Calculate statistics for a method."""
    vec = list(values.values())
    return {
        "method": name,
        "std": float(np.std(vec)) if vec else 0.0,
        "runtime_s": runtime_s,
        "max": float(max(vec)) if vec else 0.0,
        "min": float(min(vec)) if vec else 0.0
    }


def compare_methods(label: str, values_a: Dict[str, float], values_b: Dict[str, float], k: int = 10) -> dict:
    """Compare two methods."""
    tau = kendall_tau_rank(values_a, values_b)
    if math.isnan(tau):
        tau = 0.0
    return {
        "pair": label,
        "kendall_tau": tau,
        f"jaccard@{k}": jaccard_at_k(values_a, values_b, k)
    }


def aggregate_group_values(values: Dict[str, float], groups: Dict[str, list[str]]) -> dict[str, float]:
    """Aggregate values by groups."""
    return {
        gid: sum(values.get(pid, 0.0) for pid in members)
        for gid, members in groups.items()
    }


def coverage_ratio(group_values: Dict[str, float], top_k: int = 3) -> float:
    """Calculate coverage ratio for top-k groups."""
    magnitudes = sorted((abs(v) for v in group_values.values()), reverse=True)
    if not magnitudes:
        return 0.0
    top = sum(magnitudes[:top_k])
    total = sum(magnitudes)
    return top / total if total else 0.0


def mean_std_across_values(per_seed_values: list[Dict[str, float]]) -> tuple[Dict[str, float], Dict[str, float], float]:
    """Calculate mean and std across multiple seed runs."""
    if not per_seed_values:
        return {}, {}, 0.0
    players = per_seed_values[0].keys()
    avg_vals: Dict[str, float] = {}
    std_vals: Dict[str, float] = {}
    for pid in players:
        series = [vals.get(pid, 0.0) for vals in per_seed_values]
        avg_vals[pid] = float(np.mean(series))
        std_vals[pid] = float(np.std(series))
    avg_std = float(np.mean(list(std_vals.values()))) if std_vals else 0.0
    return avg_vals, std_vals, avg_std

