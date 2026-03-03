"""
Coalition building and masking functions.
"""

import hashlib
import re
from functools import lru_cache
try:
    from Functions.players.player_enumeration import list_players_from_expression
    from Functions.properties.property_builder import (
        extract_ini_fin,
        build_full_spec,
        evaluate_property,
    )
    from Functions.utils.imports import *
except ImportError:
    # Relative imports for when Functions is a package
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.players.player_enumeration import list_players_from_expression
    from Functions.properties.property_builder import (
        extract_ini_fin,
        build_full_spec,
        evaluate_property,
    )
    from Functions.utils.imports import *


def _hash_text(s: str) -> str:
    """Hash text for cache key."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def mask_expression_with_coalition(named_expr: str, include_ids: set[str]) -> str:
    """Mask expression by replacing excluded players' subtrees with 'tau'."""
    players = list_players_from_expression(named_expr)
    out = named_expr
    for p in sorted(players, key=lambda x: x.label, reverse=True):
        if p.id not in include_ids:
            out = re.sub(re.escape(p.snippet), "tau", out, count=1)
    return out


def extract_ini_fin_for_any_expr(expr: str, pattern_templates) -> tuple[str, str]:
    """Safe ini/fin for atomic expressions."""
    if "(" not in expr:
        return expr, expr
    return extract_ini_fin(expr, pattern_templates)


def build_spec_for_expr(expr: str, pattern_templates) -> str:
    """Build spec even if some patterns were masked out."""
    if "(" not in expr:
        return ""  # no pattern rules when only atomic remains
    return build_full_spec(expr, pattern_templates)


def build_coalition_artifacts(base_named_expr: str, selected_player_ids: set[str], pattern_templates):
    """Build coalition artifacts: masked expression, derived spec, and ini/fin."""
    masked_expr = mask_expression_with_coalition(base_named_expr, selected_player_ids)
    spec = build_spec_for_expr(masked_expr, pattern_templates)
    ini, fin = extract_ini_fin_for_any_expr(masked_expr, pattern_templates)
    return masked_expr, spec, ini, fin


@lru_cache(maxsize=4096)
def cached_coalition_artifacts():
    """Sentinel function - use make_coalition_evaluator instead."""
    raise RuntimeError("This is a sentinel; use make_coalition_evaluator to bind the expression text.")


def make_coalition_evaluator(base_named_expr: str, pattern_templates, property_type: str, pattern: str = "standard"):
    """Build v(C) evaluator with memoized coalition artifacts."""
    base_hash = _hash_text(base_named_expr)
    players = list_players_from_expression(base_named_expr)
    player_ids = [p.id for p in players]

    local_cache = {}

    def artifacts_for(ids: frozenset):
        key = (base_hash, ids)
        if key in local_cache:
            return local_cache[key]
        masked_expr, spec, ini, fin = build_coalition_artifacts(base_named_expr, set(ids), pattern_templates)
        local_cache[key] = (masked_expr, spec, ini, fin)
        return masked_expr, spec, ini, fin

    def vC(ids_set: set[str]) -> int:
        masked_expr, spec, ini, fin = artifacts_for(frozenset(ids_set))
        if property_type == "satisfiability":
            return evaluate_property(spec, "satisfiability", pattern=pattern)
        elif property_type == "liveness":
            return evaluate_property(spec, "liveness", ini, fin, pattern)
        elif property_type == "safety":
            return evaluate_property(spec, "safety", ini, fin, pattern)
        else:
            raise ValueError(property_type)

    return player_ids, vC

