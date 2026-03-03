"""
TPTP format transformer.
"""

import re
from Functions.utils.imports import *


_exist_pattern = re.compile(r"(?i)Exist\s*\((.*?)\)", re.DOTALL)
_op_pattern = re.compile(r"\s*(&|\||=>)\s*")
_atom_pattern = re.compile(r"\b[A-Za-z][A-Za-z0-9_]*\b")
_pred_call_pattern = re.compile(r"([a-z][0-9a-z_]*\(\s*X\s*\))")


def transform_to_tptp(input_str: str) -> str:
    """
    Transform formulas into TPTP format.
    
    Args:
        input_str: Input formula string
        
    Returns:
        TPTP format string
    """
    def inline_existentials(formula: str) -> str:
        prev = None
        while prev != formula:
            prev = formula
            formula = _exist_pattern.sub(
                lambda m: f"?[X]: ( {inline_existentials(m.group(1).strip().rstrip('.-'))} )",
                formula
            )
        return formula

    lines = [ln.strip() for ln in input_str.splitlines() if ln.strip()]
    result = []

    for idx, line in enumerate(lines, start=1):
        name = f"f{idx}"
        content = line.strip()

        quant = ""
        if content.startswith("ForAll"):
            quant = "!"
            content = content[len("ForAll"):].strip()
        elif content.startswith("Exist"):
            quant = "?"
            content = content[len("Exist"):].strip()

        if content.startswith("(") and content.endswith(")"):
            content = content[1:-1].strip()

        content = inline_existentials(content)

        content = content.replace("^", "&")
        content = _op_pattern.sub(lambda m: f" {m.group(1)} ", content)
        content = " ".join(content.split())

        content = content.replace(".", "")
        content = content.replace("-", "")

        def atom_to_pred(m: re.Match) -> str:
            tok = m.group(0)
            if tok in {"&", "|", "=>", "?", "!", "[", "]", ":", "X"}:
                return tok
            return f"{tok.lower()}(X)"

        expr = _atom_pattern.sub(atom_to_pred, content)
        expr = _pred_call_pattern.sub(r"(\1)", expr)

        prefix = f"{quant}[X]:" if quant in ("!", "?") else ""

        result.append(f"fof({name}, axiom, {prefix} {expr}).")

    return "\n".join(result)

