"""
File I/O utility functions.
"""

import os
import json
import csv
from typing import List, Dict, Tuple
try:
    from Functions.utils.constants import SHAPLEY_CACHE_PATH
    from Functions.utils.imports import *
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.utils.constants import SHAPLEY_CACHE_PATH
    from Functions.utils.imports import *


def ensure_dir(path: str):
    """Ensure directory exists."""
    os.makedirs(path, exist_ok=True)


def save_json(path: str, data):
    """Save data to JSON file."""
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_rows_csv(path: str, rows: List[Dict]):
    """Append rows to CSV file."""
    ensure_dir(os.path.dirname(path))
    fieldnames = sorted({k for r in rows for k in r.keys()})
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            w.writeheader()
        for r in rows:
            w.writerow(r)


def load_cached_shapley_results() -> List[Dict]:
    """Load cached SHAPLEY_RESULTS if the cache file is available."""
    if os.path.exists(SHAPLEY_CACHE_PATH):
        try:
            with open(SHAPLEY_CACHE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"[CACHE] Loaded {len(data)} configs from {SHAPLEY_CACHE_PATH}")
            return data
        except Exception as exc:
            print(f"[CACHE] Failed to load {SHAPLEY_CACHE_PATH}: {exc}")
    return []


def persist_shapley_results(results: List[Dict]):
    """Persist SHAPLEY_RESULTS so later experiments can reuse them."""
    if not results:
        return
    save_json(SHAPLEY_CACHE_PATH, results)
    print(f"[CACHE] Saved {len(results)} configs to {SHAPLEY_CACHE_PATH}")


def top_k(d: Dict[str, float], k: int = 5) -> List[Tuple[str, float]]:
    """Get top-k items from dictionary."""
    return sorted(d.items(), key=lambda kv: kv[1], reverse=True)[:k]


def split_player_id(pid: str) -> Tuple[str, str]:
    """Split player ID into name and label."""
    if "@" in pid:
        name, label = pid.split("@", 1)
        return name, label
    return pid, ""

