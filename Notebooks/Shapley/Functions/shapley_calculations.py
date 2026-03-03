"""
Shapley value calculation functions.
"""

import random
import time
from typing import Dict, Set, Any
try:
    from Functions.coalition.coalition_builder import make_coalition_evaluator
    from Functions.players.player_enumeration import derive_player_blocks
    from Functions.utils.imports import *
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.coalition.coalition_builder import make_coalition_evaluator
    from Functions.players.player_enumeration import derive_player_blocks
    from Functions.utils.imports import *


def shapley_mc_permutations(
    base_named_expr: str, 
    pattern_templates, 
    property_type: str,
    n_perm: int = 1000, 
    seed: int = 42,
    progress_every: int = 25, 
    pattern: str = "standard"
):
    """Monte Carlo Shapley with progress and memoized coalition values."""
    rng = random.Random(seed)
    player_ids, vC = make_coalition_evaluator(base_named_expr, pattern_templates, property_type, pattern)
    n = len(player_ids)

    v_cache: Dict[frozenset, int] = {}

    def v_cached(S: Set[str]) -> int:
        key = frozenset(S)
        if key in v_cache:
            return v_cache[key]
        val = vC(S)
        v_cache[key] = val
        return val

    contrib = {pid: 0.0 for pid in player_ids}
    total_value = 0.0
    start = time.time()

    for it in range(1, n_perm + 1):
        perm = player_ids[:]
        rng.shuffle(perm)
        S: Set[str] = set()
        prev = v_cached(S)
        for pid in perm:
            S_with = S | {pid}
            val = v_cached(S_with)
            contrib[pid] += (val - prev)
            prev = val
            S = S_with
        total_value += prev

        if it % progress_every == 0:
            elapsed = time.time() - start
            print(f"      ... MC progress {it}/{n_perm} "
                  f"(players={n}, cached={len(v_cache)}) [{elapsed:.1f}s]", flush=True)

    for pid in contrib:
        contrib[pid] /= n_perm
    avg_value = total_value / n_perm
    dur = time.time() - start

    meta = {
        "n_perm": n_perm,
        "property_type": property_type,
        "avg_value": avg_value,
        "players": n,
        "seconds": dur,
        "cache_entries": len(v_cache)
    }
    return contrib, meta


def shapley_random_subsets(
    base_named_expr: str, 
    pattern_templates, 
    property_type: str,
    n_samples: int = 2000, 
    keep_frac_range=(0.5, 0.8), 
    seed: int = 123,
    progress_every: int = 100, 
    pattern: str = "standard"
):
    """Random subset Shapley with progress."""
    rng = random.Random(seed)
    player_ids, vC = make_coalition_evaluator(base_named_expr, pattern_templates, property_type, pattern)
    n = len(player_ids)

    with_sums = {pid: 0.0 for pid in player_ids}
    with_cnts = {pid: 0 for pid in player_ids}
    without_sums = {pid: 0.0 for pid in player_ids}
    without_cnts = {pid: 0 for pid in player_ids}

    total_value = 0.0
    start = time.time()

    for it in range(1, n_samples + 1):
        keep_frac = rng.uniform(*keep_frac_range)
        k = max(0, min(n, int(round(keep_frac * n))))
        subset = set(rng.sample(player_ids, k)) if k > 0 else set()

        val = vC(subset)
        total_value += val

        for pid in player_ids:
            if pid in subset:
                with_sums[pid] += val
                with_cnts[pid] += 1
            else:
                without_sums[pid] += val
                without_cnts[pid] += 1

        if it % progress_every == 0:
            elapsed = time.time() - start
            print(f"      ... RS progress {it}/{n_samples} "
                  f"(players={n}) [{elapsed:.1f}s]", flush=True)

    influence = {}
    for pid in player_ids:
        m_with = with_sums[pid] / with_cnts[pid] if with_cnts[pid] > 0 else 0.0
        m_without = without_sums[pid] / without_cnts[pid] if without_cnts[pid] > 0 else 0.0
        influence[pid] = m_with - m_without

    dur = time.time() - start
    meta = {
        "n_samples": n_samples,
        "property_type": property_type,
        "avg_value": total_value / n_samples,
        "players": n,
        "keep_frac_range": keep_frac_range,
        "seconds": dur
    }
    return influence, meta


def banzhaf_random_coalitions(
    base_named_expr: str, 
    pattern_templates, 
    property_type: str,
    n_samples: int = 1500, 
    inclusion_prob: float = 0.5,
    seed: int = 1337, 
    progress_every: int = 100
):
    """Estimate Banzhaf index via uniform random coalitions."""
    rng = random.Random(seed)
    player_ids, vC = make_coalition_evaluator(base_named_expr, pattern_templates, property_type)

    with_sums = {pid: 0.0 for pid in player_ids}
    with_cnts = {pid: 0 for pid in player_ids}
    without_sums = {pid: 0.0 for pid in player_ids}
    without_cnts = {pid: 0 for pid in player_ids}

    start = time.time()
    for it in range(1, n_samples + 1):
        subset = {pid for pid in player_ids if rng.random() < inclusion_prob}
        val = vC(subset)

        for pid in player_ids:
            if pid in subset:
                with_sums[pid] += val
                with_cnts[pid] += 1
            else:
                without_sums[pid] += val
                without_cnts[pid] += 1

        if it % progress_every == 0:
            elapsed = time.time() - start
            print(f"      ... Banzhaf progress {it}/{n_samples} (players={len(player_ids)}) [{elapsed:.1f}s]",
                  flush=True)

    beta_raw = {}
    for pid in player_ids:
        if with_cnts[pid] == 0 or without_cnts[pid] == 0:
            beta_raw[pid] = 0.0
            continue
        mean_with = with_sums[pid] / with_cnts[pid]
        mean_without = without_sums[pid] / without_cnts[pid]
        beta_raw[pid] = mean_with - mean_without

    norm = sum(abs(v) for v in beta_raw.values()) or 1.0
    beta_normalized = {pid: val / norm for pid, val in beta_raw.items()}

    meta = {
        "n_samples": n_samples,
        "property_type": property_type,
        "players": len(player_ids),
        "inclusion_prob": inclusion_prob,
        "seconds": time.time() - start
    }
    return {"raw": beta_raw, "normalized": beta_normalized}, meta


def owen_value_permutations(
    base_named_expr: str, 
    pattern_templates, 
    property_type: str,
    block_partition: dict[str, list[str]] | None = None,
    n_perm: int = 1000, 
    seed: int = 2025, 
    progress_every: int = 25
):
    """Compute Owen value (Shapley with blocks) via constrained permutations."""
    rng = random.Random(seed)
    player_ids, vC = make_coalition_evaluator(base_named_expr, pattern_templates, property_type)

    if block_partition is None:
        block_partition = derive_player_blocks(base_named_expr)

    filtered_blocks: list[tuple[str, list[str]]] = []
    assigned = set()
    for block_id, members in block_partition.items():
        filtered = [pid for pid in members if pid in player_ids]
        if filtered:
            filtered_blocks.append((block_id, filtered))
            assigned.update(filtered)

    for pid in player_ids:
        if pid not in assigned:
            filtered_blocks.append((pid, [pid]))

    v_cache: Dict[frozenset, int] = {}

    def v_cached(S: Set[str]) -> int:
        key = frozenset(S)
        if key in v_cache:
            return v_cache[key]
        val = vC(S)
        v_cache[key] = val
        return val

    contrib = {pid: 0.0 for pid in player_ids}
    start = time.time()

    for it in range(1, n_perm + 1):
        block_order = filtered_blocks[:]
        rng.shuffle(block_order)
        global_order: list[str] = []
        for _, members in block_order:
            local = members[:]
            rng.shuffle(local)
            global_order.extend(local)

        S: Set[str] = set()
        prev = v_cached(S)
        for pid in global_order:
            S_with = S | {pid}
            val = v_cached(S_with)
            contrib[pid] += (val - prev)
            prev = val
            S = S_with

        if it % progress_every == 0:
            elapsed = time.time() - start
            print(f"      ... Owen progress {it}/{n_perm} (blocks={len(filtered_blocks)}) [{elapsed:.1f}s]",
                  flush=True)

    for pid in contrib:
        contrib[pid] /= n_perm

    meta = {
        "n_perm": n_perm,
        "property_type": property_type,
        "players": len(player_ids),
        "blocks": len(filtered_blocks),
        "seconds": time.time() - start,
        "cache_entries": len(v_cache)
    }
    return contrib, meta


def max_abs_diff(d_now: Dict[str, float], d_prev: Dict[str, float]) -> float:
    """Compute maximum absolute difference between two dictionaries."""
    return max(abs(d_now.get(pid, 0.0) - d_prev.get(pid, 0.0)) for pid in set(d_now.keys()) | set(d_prev.keys()))


def l1_norm(d_now: Dict[str, float], d_prev: Dict[str, float]) -> float:
    """Compute L1 norm between two dictionaries."""
    all_pids = set(d_now.keys()) | set(d_prev.keys())
    return sum(abs(d_now.get(pid, 0.0) - d_prev.get(pid, 0.0)) for pid in all_pids)


def shapley_mc_convergence(
    base_named_expr: str, 
    pattern_templates, 
    property_type: str,
    steps: list[int], 
    seed: int = 123, 
    progress_every: int = 25,
    pattern: str = "standard"
):
    """
    Monte Carlo Shapley convergence analysis.
    
    Tracks Shapley value estimates at specified checkpoints and computes
    convergence metrics (max absolute difference, L1 norm) between consecutive snapshots.
    
    Args:
        base_named_expr: Named pattern expression
        pattern_templates: Pattern templates
        property_type: Property type (satisfiability, liveness, safety)
        steps: List of iteration checkpoints to record snapshots
        seed: Random seed
        progress_every: Print progress every N iterations
        pattern: Pattern type
        
    Returns:
        Dictionary with convergence data including series, snapshots, and deltas
    """
    rng = random.Random(seed)
    player_ids, vC_base = make_coalition_evaluator(base_named_expr, pattern_templates, property_type, pattern)
    n = len(player_ids)
    contrib_sum = {pid: 0.0 for pid in player_ids}
    v_cache: Dict[frozenset, int] = {}
    current_step_target = max(steps)
    series = {pid: [] for pid in player_ids}
    checkpoints = set(steps)
    snapshots: list[Dict[str, float]] = []
    deltas_max: list[float] = []
    deltas_l1: list[float] = []

    def v_cached(S: Set[str]) -> int:
        key = frozenset(S)
        if key in v_cache:
            return v_cache[key]
        val = vC_base(S)
        v_cache[key] = val
        return val

    start = time.time()
    for it in range(1, current_step_target + 1):
        perm = player_ids[:]
        rng.shuffle(perm)
        S: Set[str] = set()
        prev = v_cached(S)
        for pid in perm:
            S_with = S | {pid}
            val = v_cached(S_with)
            contrib_sum[pid] += (val - prev)
            prev = val
            S = S_with

        if it % progress_every == 0:
            print(f"      ... MC conv {it}/{current_step_target} cached={len(v_cache)}", flush=True)

        if it in checkpoints:
            est = {pid: contrib_sum[pid] / it for pid in player_ids}
            snapshots.append(est)
            if len(snapshots) > 1:
                deltas_max.append(max_abs_diff(snapshots[-1], snapshots[-2]))
                deltas_l1.append(l1_norm(snapshots[-1], snapshots[-2]))
            else:
                deltas_max.append(0.0)
                deltas_l1.append(0.0)
            for pid in player_ids:
                series[pid].append(est[pid])

    duration = time.time() - start
    return {
        "players": player_ids,
        "steps": steps,
        "series": series,
        "snapshots": snapshots,
        "deltas_max": deltas_max,
        "deltas_l1": deltas_l1,
        "duration": duration,
        "cache_entries": len(v_cache)
    }


def shapley_rs_convergence(
    base_named_expr: str, 
    pattern_templates, 
    property_type: str,
    steps: list[int], 
    keep_frac_range=(0.5, 0.8), 
    seed: int = 321,
    progress_every: int = 100,
    pattern: str = "standard"
):
    """
    Random Subsets Shapley convergence analysis.
    
    Tracks Shapley value estimates at specified checkpoints and computes
    convergence metrics (max absolute difference, L1 norm) between consecutive snapshots.
    
    Args:
        base_named_expr: Named pattern expression
        pattern_templates: Pattern templates
        property_type: Property type (satisfiability, liveness, safety)
        steps: List of iteration checkpoints to record snapshots
        keep_frac_range: Range for random subset size fraction
        seed: Random seed
        progress_every: Print progress every N iterations
        pattern: Pattern type
        
    Returns:
        Dictionary with convergence data including series, snapshots, and deltas
    """
    rng = random.Random(seed)
    player_ids, vC_base = make_coalition_evaluator(base_named_expr, pattern_templates, property_type, pattern)
    n = len(player_ids)
    with_sums = {pid: 0.0 for pid in player_ids}
    with_cnts = {pid: 0 for pid in player_ids}
    without_sums = {pid: 0.0 for pid in player_ids}
    without_cnts = {pid: 0 for pid in player_ids}
    series = {pid: [] for pid in player_ids}
    checkpoints = set(steps)
    snapshots: list[Dict[str, float]] = []
    deltas_max: list[float] = []
    deltas_l1: list[float] = []

    start = time.time()
    for it in range(1, max(steps) + 1):
        keep_frac = rng.uniform(*keep_frac_range)
        k = max(0, min(n, int(round(keep_frac * n))))
        subset = set(rng.sample(player_ids, k)) if k > 0 else set()
        val = vC_base(subset)
        for pid in player_ids:
            if pid in subset:
                with_sums[pid] += val
                with_cnts[pid] += 1
            else:
                without_sums[pid] += val
                without_cnts[pid] += 1

        if it % progress_every == 0:
            print(f"      ... RS conv {it}/{max(steps)}", flush=True)

        if it in checkpoints:
            est = {}
            for pid in player_ids:
                m_with = with_sums[pid] / with_cnts[pid] if with_cnts[pid] else 0.0
                m_without = without_sums[pid] / without_cnts[pid] if without_cnts[pid] else 0.0
                est[pid] = m_with - m_without
            snapshots.append(est)
            if len(snapshots) > 1:
                deltas_max.append(max_abs_diff(snapshots[-1], snapshots[-2]))
                deltas_l1.append(l1_norm(snapshots[-1], snapshots[-2]))
            else:
                deltas_max.append(0.0)
                deltas_l1.append(0.0)
            for pid in player_ids:
                series[pid].append(est[pid])

    duration = time.time() - start
    return {
        "players": player_ids,
        "steps": steps,
        "series": series,
        "snapshots": snapshots,
        "deltas_max": deltas_max,
        "deltas_l1": deltas_l1,
        "duration": duration,
        "keep_frac_range": keep_frac_range
    }

