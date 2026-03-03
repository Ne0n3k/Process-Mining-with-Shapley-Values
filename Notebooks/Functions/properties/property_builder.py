"""
Property building and evaluation functions.
"""

import re
try:
    from Functions.logical_spec.consolidated_expression import CalculatingConsolidatedExpression
    from Functions.logical_spec.logical_spec_generator import GeneratingLogicalSpecifications
    from Functions.prover.prover_glue import eval_satisfiable, eval_entails
    from Functions.utils.imports import *
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.logical_spec.consolidated_expression import CalculatingConsolidatedExpression
    from Functions.logical_spec.logical_spec_generator import GeneratingLogicalSpecifications
    from Functions.prover.prover_glue import eval_satisfiable, eval_entails
    from Functions.utils.imports import *


def extract_ini_fin(named_pattern_expr: str, pattern_templates) -> tuple[str, str]:
    """Extract ini/fin formulas for a named expression."""
    ini = CalculatingConsolidatedExpression.generate_consolidated_expression(
        named_pattern_expr, "ini", pattern_templates
    )
    fin = CalculatingConsolidatedExpression.generate_consolidated_expression(
        named_pattern_expr, "fin", pattern_templates
    )
    return ini, fin


def build_full_spec(named_pattern_expr: str, pattern_templates) -> str:
    """Build full logical specification from named pattern expression."""
    return GeneratingLogicalSpecifications.generate_logical_specifications(
        named_pattern_expr, pattern_templates, verbose=False
    )


def temporal_to_fo_wrappers(formula: str) -> str:
    """Convert []/<> wrappers to FO-friendly forms."""
    s = formula
    s = re.sub(r"\s+", " ", s).strip()

    def _wrap_all(match: re.Match) -> str:
        inner = match.group(1)
        return f"ForAll({inner})"

    def _wrap_exist(match: re.Match) -> str:
        inner = match.group(1)
        return f"Exist({inner})"

    s = re.sub(r"\[\]\s*\((.*?)\)", _wrap_all, s)
    s = re.sub(r"<>\s*\((.*?)\)", _wrap_exist, s)
    return s


def build_liveness_property(ini: str, fin: str, pattern: str = "standard") -> str:
    """Build liveness property."""
    pattern = pattern.lower()
    if pattern == "standard" or pattern == "response":
        return temporal_to_fo_wrappers(f"[] ({ini} => <> ({fin}))")
    elif pattern == "eventual":
        return temporal_to_fo_wrappers(f"<> ({fin})")
    else:
        raise ValueError(f"Unknown liveness pattern: {pattern}")


def build_safety_property(ini: str, fin: str, pattern: str = "standard") -> str:
    """Build safety property."""
    pattern = pattern.lower()
    if pattern == "standard" or pattern == "mutual_exclusion":
        return temporal_to_fo_wrappers(f"[] ~({ini} & {fin})")
    elif pattern == "precedence":
        return temporal_to_fo_wrappers(f"[] ({fin} => ({ini} WU {fin}))")
    elif pattern == "absence":
        return temporal_to_fo_wrappers(f"[] ~({ini})")
    elif pattern == "invariant":
        return temporal_to_fo_wrappers(f"[] ({ini} => {fin})")
    elif pattern == "until":
        return temporal_to_fo_wrappers(f"[] ({ini} => ({ini} | <> {fin}))")
    else:
        raise ValueError(f"Unknown safety pattern: {pattern}")


def evaluate_property(
    spec_text: str, 
    property_type: str, 
    ini: str | None = None, 
    fin: str | None = None, 
    pattern: str = "standard", 
    *, 
    verbose: bool = False
) -> int:
    """Evaluate property (satisfiability, liveness, or safety)."""
    p = property_type.lower()
    
    if p == "satisfiability":
        return eval_satisfiable(spec_text, verbose=verbose)
    elif p == "liveness":
        assert ini is not None and fin is not None, "ini/fin required for liveness"
        prop = build_liveness_property(ini, fin, pattern)
        return eval_entails(spec_text, prop, verbose=verbose)
    elif p == "safety":
        assert ini is not None and fin is not None, "ini/fin required for safety"
        prop = build_safety_property(ini, fin, pattern)
        return eval_entails(spec_text, prop, verbose=verbose)
    else:
        raise ValueError(f"Unknown property type: {property_type}. Supported: satisfiability, liveness, safety")

