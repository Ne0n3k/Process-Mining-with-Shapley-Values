"""
Logical specification generation from workflow patterns.
"""

from .workflow_patterns import WorkflowPatternTemplate, WorkflowPattern
from .consolidated_expression import CalculatingConsolidatedExpression
from .logical_spec_generator import GeneratingLogicalSpecifications

__all__ = [
    'WorkflowPatternTemplate',
    'WorkflowPattern',
    'CalculatingConsolidatedExpression',
    'GeneratingLogicalSpecifications',
]

