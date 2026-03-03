"""
Vampire prover integration and TPTP transformation.
"""

from .vampire import run_vampire, parse_vampire_status, _find_vampire
from .tptp_transformer import transform_to_tptp
from .prover_glue import (
    tptp_from_spec,
    tptp_from_spec_and_conjecture,
    eval_satisfiable,
    eval_entails,
    _PROVER_CACHE,
)

__all__ = [
    'run_vampire',
    'parse_vampire_status',
    '_find_vampire',
    'transform_to_tptp',
    'tptp_from_spec',
    'tptp_from_spec_and_conjecture',
    'eval_satisfiable',
    'eval_entails',
    '_PROVER_CACHE',
]

