"""
Player enumeration and grouping functions.
"""

import re
from dataclasses import dataclass
from collections import defaultdict
from typing import Any
try:
    from Functions.pattern_operators.adapter import ProcessTreeAdapter
    from Functions.utils.imports import *
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.pattern_operators.adapter import ProcessTreeAdapter
    from Functions.utils.imports import *


@dataclass(frozen=True)
class Player:
    """Represents a player (pattern node) in the game."""
    id: str
    name: str
    label: int
    snippet: str


def _parse_labelled_expression_to_tree(labelled_expr: str):
    """Parse labelled expression to tree structure."""
    m = re.match(r"^([A-Za-z0-9_]+)\((\d+)\]", labelled_expr)
    if not m:
        return {"type": "literal", "text": labelled_expr}

    name = m.group(1)
    label_num = int(m.group(2))
    args, _pat_label = ProcessTreeAdapter.extract_arguments_from_labelled_expression(labelled_expr)

    children = []
    for a in args:
        if re.search(r"\(\d+\]", a):
            children.append(_parse_labelled_expression_to_tree(a))
        else:
            children.append({"type": "literal", "text": a})

    return {
        "type": "pattern",
        "name": name,
        "label": label_num,
        "id": f"{name}@{label_num}",
        "children": children,
    }


def _extract_pattern_by_label(named_expr: str, l: int, occurrence: int = 1) -> tuple[str, str] | None:
    """Extract pattern by label and occurrence."""
    entry_occ = named_expr.count(f"({l}]")
    end_occ = named_expr.count(f"[{l})")
    if entry_occ != end_occ or entry_occ == 0 or occurrence < 1 or occurrence > entry_occ:
        return None
    parts = re.split(rf"\({l}\]", named_expr)
    pattern_content = re.split(rf"\[{l}\)", parts[occurrence])[0]
    prefix = re.split(r"\]", parts[occurrence - 1])[-1]
    workflow_name = re.split(r",", prefix)[-1]
    snippet = f"{workflow_name}({l}]{pattern_content}[{l})"
    return workflow_name, snippet


def _enumerate_pattern_nodes(named_expr: str) -> list[dict[str, Any]]:
    """Enumerate all pattern nodes from named expression."""
    tree = _parse_labelled_expression_to_tree(named_expr)
    nodes: list[dict[str, Any]] = []
    totals: dict[str, int] = defaultdict(int)

    def tally(node):
        if node.get("type") == "pattern":
            totals[node["id"]] += 1
        for ch in node.get("children", []):
            tally(ch)

    tally(tree)
    seen: dict[str, int] = defaultdict(int)

    def collect(node, parent_id: str | None):
        if node.get("type") != "pattern":
            return None
        base_id = node["id"]
        seen[base_id] += 1
        occurrence = seen[base_id]
        total_occurrences = totals[base_id]
        suffix = f"@{occurrence}" if total_occurrences > 1 else ""
        extracted = _extract_pattern_by_label(named_expr, node["label"], occurrence)
        if extracted is None:
            name, snippet = node["name"], base_id
        else:
            name, snippet = extracted
        resolved_id = f"{base_id}{suffix}"
        child_ids: list[str] = []
        for ch in node.get("children", []):
            child_id = collect(ch, resolved_id)
            if child_id is not None:
                child_ids.append(child_id)
        nodes.append({
            "id": resolved_id,
            "name": name,
            "label": node["label"],
            "snippet": snippet,
            "parent_id": parent_id,
            "children": child_ids
        })
        return resolved_id

    collect(tree, None)
    return nodes


def list_players_from_expression(named_expr: str) -> list[Player]:
    """List all players from named expression."""
    return [
        Player(id=node["id"], name=node["name"], label=node["label"], snippet=node["snippet"])
        for node in _enumerate_pattern_nodes(named_expr)
    ]


def derive_player_blocks(named_expr: str, drop_root: bool = False) -> dict[str, list[str]]:
    """Derive player blocks (parent -> children mapping)."""
    nodes = _enumerate_pattern_nodes(named_expr)
    root_id = next((n["id"] for n in nodes if n["parent_id"] is None), None)
    block_map: dict[str, list[str]] = {}
    for node in nodes:
        if node["children"]:
            block_map[node["id"]] = list(node["children"])
    if drop_root and root_id in block_map:
        block_map.pop(root_id, None)
    return block_map


def derive_subtree_groups(named_expr: str, drop_root: bool = True) -> dict[str, list[str]]:
    """Derive subtree groups (all descendants of each node)."""
    nodes = _enumerate_pattern_nodes(named_expr)
    root_id = next((n["id"] for n in nodes if n["parent_id"] is None), None)
    child_map = {node["id"]: node["children"] for node in nodes}
    cache: dict[str, list[str]] = {}

    def gather(node_id: str) -> list[str]:
        if node_id in cache:
            return cache[node_id]
        members = [node_id]
        for child in child_map.get(node_id, []):
            members.extend(gather(child))
        cache[node_id] = members
        return members

    groups = {
        node_id: gather(node_id)
        for node_id, children in child_map.items()
        if children
    }
    if drop_root and root_id in groups:
        groups.pop(root_id)
    return groups

