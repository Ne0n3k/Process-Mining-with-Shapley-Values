"""
Consolidated expression generator for ini/fin formulas.
"""

from typing import List
try:
    from Functions.logical_spec.workflow_patterns import WorkflowPatternTemplate, WorkflowPattern
    from Functions.utils.imports import *
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.logical_spec.workflow_patterns import WorkflowPatternTemplate, WorkflowPattern
    from Functions.utils.imports import *


class CalculatingConsolidatedExpression:
    """Generates consolidated expressions (ini/fin) from pattern expressions."""
    
    @staticmethod
    def generate_consolidated_expression(
        pattern_expression: str, 
        expression_type: str, 
        pattern_property_set: List[WorkflowPatternTemplate]
    ) -> str:
        """
        Generate consolidated expression (ini or fin).
        
        Args:
            pattern_expression: Pattern expression string
            expression_type: Either "ini" or "fin"
            pattern_property_set: List of workflow pattern templates
            
        Returns:
            Consolidated expression string
        """
        if expression_type not in ("ini", "fin"):
            raise Exception("Type must equal 'ini' or 'fin'!")

        workflow_pattern = WorkflowPattern.get_workflow_pattern_from_expression(
            pattern_expression, pattern_property_set)
        rules_with_atomic_activities = workflow_pattern.get_workflow_pattern_filled_rules()
        ini = rules_with_atomic_activities[0]
        fin = rules_with_atomic_activities[1]

        if expression_type == "ini":
            ex = ini
        else:
            ex = fin

        expression_arguments = WorkflowPattern.extract_arguments_from_labelled_expression(
            pattern_expression, pattern_property_set)
        for argument in expression_arguments:
            if WorkflowPattern.is_not_atomic(argument):
                inner_consolidated_expression = CalculatingConsolidatedExpression.generate_consolidated_expression(
                    argument, expression_type, pattern_property_set)
                ex = ex.replace(argument, inner_consolidated_expression)
        return ex

