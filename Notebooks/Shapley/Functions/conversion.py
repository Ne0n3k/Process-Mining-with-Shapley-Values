"""
Tree to pattern expression conversion functions.
"""

try:
    from Functions.formatting.format_class import Format
    from Functions.pattern_operators.pattern_generator import GetPatternExpression
    from Functions.utils.imports import *
except ImportError:
    # Relative imports
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.formatting.format_class import Format
    from Functions.pattern_operators.pattern_generator import GetPatternExpression
    from Functions.utils.imports import *


def _op_symbol(op_obj) -> str:
    """Map pm4py operator to symbol."""
    s = str(op_obj).lower()
    if "loop" in s:
        return "*"
    if "parallel" in s or "and" in s:
        return "+"
    if "xor" in s or "exclusive" in s:
        return "X"
    # default: sequence
    return "->"


def tree_to_pattern_expr(node) -> str:
    """Build raw pattern expression from process tree."""
    has_children = hasattr(node, "children") and node.children
    if not has_children:
        label = getattr(node, "label", "tau")
        return f"'{label}'"
    sym = _op_symbol(getattr(node, "operator", "Seq"))
    args = [tree_to_pattern_expr(c) for c in node.children]
    inner = ",".join(args)
    return f"{sym}({inner})"


def sanitize_pattern_expression(raw_expr: str) -> str:
    """Sanitize pattern expression."""
    s1 = Format.lowercase_in_quotes(raw_expr)
    s2 = Format.replace_parens_in_quotes(s1)
    s3 = Format.replace_colons_in_quotes(s2)
    s4 = Format.replace_spaces_with_underscore(s3)
    return s4


def label_and_convert(expr_noquotes: str) -> str:
    """Label and convert expression."""
    labelled = Format.label_expressions(expr_noquotes)
    return GetPatternExpression.get_pattern_expression(labelled)


def tree_to_named_pattern_expression(tree) -> str:
    """Convert tree to named pattern expression."""
    raw = tree_to_pattern_expr(tree)
    clean = sanitize_pattern_expression(raw)
    named = label_and_convert(clean)
    return named

