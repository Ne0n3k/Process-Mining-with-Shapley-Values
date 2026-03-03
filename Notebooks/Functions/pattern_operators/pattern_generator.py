"""
Pattern expression generator for converting labelled expressions to named patterns.
"""

import re
try:
    from Functions.pattern_operators.adapter import ProcessTreeAdapter
    from Functions.pattern_operators.operators import Sequence, Loop, ExclusiveChoice, Parallelism
    from Functions.utils.imports import *
except ImportError:
    # Relative imports
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.pattern_operators.adapter import ProcessTreeAdapter
    from Functions.pattern_operators.operators import Sequence, Loop, ExclusiveChoice, Parallelism
    from Functions.utils.imports import *


class PatternExpressionGenerator:
    """Generates pattern expressions by identifying and converting operators."""
    
    def __init__(self, converted_expression):
        self.converted_expression = converted_expression

    def add_approved_workflow_patterns(self, expression):
        """Add approved workflow patterns to the expression."""
        if expression is None or isinstance(expression, list):
            return

        symbol = ProcessTreeAdapter.find_symbol(expression)
        up = symbol.upper()
        if up.startswith("SEQ"):
            symbol = "->"
        elif up.startswith("AND"):
            symbol = "+"
        elif up.startswith("XOR"):
            symbol = "X"
        elif up.startswith("LOOP"):
            symbol = "*"

        pattern = r'>|X|\+|\*'
        matches = re.findall(pattern, expression)

        if len(matches) != 0:
            arguments = ProcessTreeAdapter.extract_arguments_from_labelled_expression(expression)
            expression = arguments[0]
            pattern_label_number = arguments[1]

            if symbol == '->' or symbol.upper().startswith("SEQ"):
                new_name = Sequence.change_symbol_into_name(expression, pattern_label_number)
                self.converted_expression = ProcessTreeAdapter.replace_symbol_with_name(
                    self.converted_expression, pattern_label_number, symbol, new_name[0])
                expr_tmp = self.converted_expression
                self.converted_expression = expr_tmp.replace(new_name[1], new_name[2])

            elif symbol == '*' or symbol.upper().startswith("LOOP"):
                new_name = Loop.change_symbol_into_name(expression, pattern_label_number)
                self.converted_expression = ProcessTreeAdapter.replace_symbol_with_name(
                    self.converted_expression, pattern_label_number, symbol, new_name[0])
                self.converted_expression = self.converted_expression.replace(new_name[1], new_name[2])

            elif symbol == '+' or symbol.upper().startswith("AND"):
                new_name = Parallelism.change_symbol_into_name(expression, pattern_label_number)
                self.converted_expression = ProcessTreeAdapter.replace_symbol_with_name(
                    self.converted_expression, pattern_label_number, symbol, new_name[0])
                self.converted_expression = self.converted_expression.replace(new_name[1], new_name[2])

            elif symbol == 'X' or symbol.upper().startswith("XOR"):
                new_name = ExclusiveChoice.change_symbol_into_name(expression, pattern_label_number)
                self.converted_expression = ProcessTreeAdapter.replace_symbol_with_name(
                    self.converted_expression, pattern_label_number, symbol, new_name[0])
                self.converted_expression = self.converted_expression.replace(new_name[1], new_name[2])

            else:
                raise Exception(f"Pattern for {symbol} does not exist")

        return expression

    def get_converted_expression(self):
        """Get the converted expression."""
        return self.converted_expression


class GetPatternExpression:
    """Orchestrates the process of recursively converting a labeled expression to a named expression."""
    
    @staticmethod
    def process_patterns(pattern_list: list, instance) -> list:
        """Process a list of patterns."""
        new_pattern_list = []
        for pattern in pattern_list:
            new_pattern = instance.add_approved_workflow_patterns(pattern)
            if isinstance(new_pattern, list):
                new_pattern = GetPatternExpression.process_patterns(new_pattern, instance)
            new_pattern_list.append(new_pattern)
        return new_pattern_list

    @staticmethod
    def recursive_process(pattern_list: list, instance, depth: int) -> list:
        """Recursively process patterns up to a given depth."""
        if depth <= 0:
            return pattern_list
        pattern_list = GetPatternExpression.process_patterns(pattern_list, instance)
        return GetPatternExpression.recursive_process(pattern_list, instance, depth - 1)

    @staticmethod
    def get_pattern_expression(labelled_pattern_expression: str) -> str:
        """Get pattern expression from a labelled pattern expression."""
        pattern_list = [labelled_pattern_expression]
        generator = PatternExpressionGenerator(labelled_pattern_expression)
        max_label = ProcessTreeAdapter.get_highest_label(labelled_pattern_expression)
        GetPatternExpression.recursive_process(pattern_list, generator, max_label)
        return generator.get_converted_expression()

