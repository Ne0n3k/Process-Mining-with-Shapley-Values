"""
Helper functions for process trees.
"""

from typing import Any


def count_nodes(tree: Any) -> int:
    """
    Count total number of nodes in a process tree.
    
    Args:
        tree: Process tree node
        
    Returns:
        Total node count
    """
    if not hasattr(tree, "children") or not tree.children:
        return 1
    return 1 + sum(count_nodes(c) for c in tree.children)

