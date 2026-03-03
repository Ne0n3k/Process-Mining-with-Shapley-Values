"""
Prover glue: cache, TPTP building, and evaluation functions.
"""

import hashlib
import os
import re
try:
    from Functions.prover.vampire import run_vampire, parse_vampire_status
    from Functions.prover.tptp_transformer import transform_to_tptp
    from Functions.utils.constants import OUT_DIR
    from Functions.utils.imports import *
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.prover.vampire import run_vampire, parse_vampire_status
    from Functions.prover.tptp_transformer import transform_to_tptp
    from Functions.utils.constants import OUT_DIR
    from Functions.utils.imports import *

# Ensure output directory exists
os.makedirs(OUT_DIR, exist_ok=True)

# Prover cache
_PROVER_CACHE: dict[tuple[str, str], int] = {}


def _hash_key(text: str) -> str:
    """Hash text for cache key."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tptp_from_spec(spec_text: str) -> str:
    """Build TPTP from specification text."""
    return transform_to_tptp(spec_text)


def tptp_from_spec_and_conjecture(spec_text: str, conjecture_text: str) -> str:
    """Build TPTP from specification and conjecture."""
    t_axioms = transform_to_tptp(spec_text)
    t_conj = transform_to_tptp(conjecture_text).strip().splitlines()
    t_conj = [ln.replace(", axiom,", ", conjecture,") for ln in t_conj]
    return t_axioms.rstrip() + "\n" + "\n".join(t_conj) + "\n"


def eval_satisfiable(spec_text: str, *, verbose: bool = False) -> int:
    """Evaluate satisfiability of specification."""
    key = (_hash_key(spec_text), "sat")
    if key in _PROVER_CACHE:
        return _PROVER_CACHE[key]
    tptp_content = tptp_from_spec(spec_text)
    path = os.path.join(OUT_DIR, "out_sat_tmp.p")
    with open(path, "w", encoding="utf-8") as f:
        f.write(tptp_content)
    ok, out = run_vampire(path, verbose=verbose)
    status = parse_vampire_status(out if ok else "")
    val = 1 if status.lower() == "satisfiable" else 0
    _PROVER_CACHE[key] = val
    return val


def eval_entails(spec_text: str, property_text: str, *, verbose: bool = False) -> int:
    """Evaluate if specification entails property."""
    key = (_hash_key(spec_text + "\n#\n" + property_text), "entails")
    if key in _PROVER_CACHE:
        return _PROVER_CACHE[key]
    tptp_content = tptp_from_spec_and_conjecture(spec_text, property_text)
    path = os.path.join(OUT_DIR, "out_entails_tmp.p")
    with open(path, "w", encoding="utf-8") as f:
        f.write(tptp_content)
    ok, out = run_vampire(path, verbose=verbose)
    status = parse_vampire_status(out if ok else "")
    val = 1 if status.lower() == "theorem" else 0
    _PROVER_CACHE[key] = val
    return val

