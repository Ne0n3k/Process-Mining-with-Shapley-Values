"""
Logical specification generator from workflow patterns.
"""

import re
from typing import List, Any
try:
    from Functions.logical_spec.workflow_patterns import WorkflowPatternTemplate, WorkflowPattern
    from Functions.logical_spec.consolidated_expression import CalculatingConsolidatedExpression
    from Functions.pattern_operators.adapter import ProcessTreeAdapter
    from Functions.utils.imports import *
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.logical_spec.workflow_patterns import WorkflowPatternTemplate, WorkflowPattern
    from Functions.logical_spec.consolidated_expression import CalculatingConsolidatedExpression
    from Functions.pattern_operators.adapter import ProcessTreeAdapter
    from Functions.utils.imports import *


class GeneratingLogicalSpecifications:
    """Generates logical specifications from pattern expressions."""
    
    @staticmethod
    def generate_logical_specifications(
        pattern_expression: str, 
        pattern_property_set: List[WorkflowPatternTemplate], 
        verbose=False
    ) -> str:
        """
        Generate logical specification from pattern expression.
        
        Args:
            pattern_expression: Pattern expression string
            pattern_property_set: List of workflow pattern templates
            verbose: Whether to print intermediate results
            
        Returns:
            Logical specification string
        """
        logical_specification = []
        labelled_expression = pattern_expression
        highest_label_number = ProcessTreeAdapter.get_highest_label(labelled_expression)
        
        for l in range(highest_label_number, 0, -1):
            c = 1
            pat = GeneratingLogicalSpecifications.get_pat(
                labelled_expression, l, c, pattern_property_set)
            while pat is not None:
                L2 = pat.get_workflow_pattern_filled_rules()
                L2 = L2[2:]
                for arg in pat.get_pattern_arguments():
                    if WorkflowPattern.is_not_atomic(arg):
                        cons = CalculatingConsolidatedExpression.generate_consolidated_expression(
                            arg, "ini", pattern_property_set) + " | " + CalculatingConsolidatedExpression.generate_consolidated_expression(arg, "fin", pattern_property_set)
                        L2_cons = [outcome.replace(arg, cons) for outcome in L2]
                        L2 = L2_cons
                c += 1
                logical_specification.extend(L2)
                pat = GeneratingLogicalSpecifications.get_pat(
                    labelled_expression, l, c, pattern_property_set)

        logical_specification = list(set(logical_specification))
        connected_string = ""
        if verbose:
            print("\nResult: ")
        for l_value in logical_specification:
            connected_string += l_value + "\n"
            if verbose:
                print(l_value)
        return connected_string

    @staticmethod
    def get_pat(
        labelled_expression: str, 
        l: int, 
        c: int, 
        pattern_property_set: List[WorkflowPatternTemplate]
    ) -> Any:
        """Get pattern at specific label and occurrence."""
        entry_occurrences = labelled_expression.count("(" + str(l) + "]")
        end_occurrences = labelled_expression.count("[" + str(l) + ")")
        if entry_occurrences != end_occurrences:
            raise Exception("(" + str(l) + "] not equal [" + str(l) + ")")

        if entry_occurrences < c:
            return None

        expression_split_by_entry = re.split(rf"\({l}\]", labelled_expression)
        pattern_content = re.split(rf"\[{l}\)", expression_split_by_entry[c])[0]
        split_by_bracket = re.split(r"\]", expression_split_by_entry[c - 1])
        workflow_name = re.split(r",", split_by_bracket[-1])[-1]
        workflow_exp = workflow_name + f"({l}]" + pattern_content + f"[{l})"
        return WorkflowPattern.get_workflow_pattern_from_expression(workflow_exp, pattern_property_set)

