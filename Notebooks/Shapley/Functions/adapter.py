"""
Process tree adapter for argument extraction and manipulation.
"""

import re
from Functions.utils.imports import *


class ProcessTreeAdapter:
    """Adapter for extracting and manipulating process tree expressions."""
    
    @staticmethod
    def extract_arguments_from_labelled_expression(labelled_expression):
        """Extract arguments from a labelled expression."""
        pattern_label_number = int(labelled_expression[labelled_expression.index(
            "(") + 1:labelled_expression.index("]")])
        trimmed_labelled_expression = labelled_expression[labelled_expression.index("]") + 1: list(re.finditer(r'\[', labelled_expression))[-1].start()]
        split = trimmed_labelled_expression.split(",")
        arguments = []
        brackets_counter = 0
        temp_arg = ""
        for s in split:
            brackets_counter += s.count('(')
            brackets_counter -= s.count(')')
            temp_arg += s + ","
            if brackets_counter == 0:
                temp_arg = temp_arg[:-1]
                arguments.append(temp_arg)
                temp_arg = ""
        return arguments, pattern_label_number

    @staticmethod
    def find_symbol(labelled_expression):
        """Find the symbol at the start of a labelled expression."""
        pattern = r'^[^()]*'
        match = re.match(pattern, labelled_expression)
        if match:
            return re.sub(r'\s+', '', match.group())
        else:
            raise Exception("No match")

    @staticmethod
    def replace_symbol_with_name(labelled_pattern_expression, pattern_label_number, old_symbol, new_name):
        """Replace a symbol with a new name in a labelled pattern expression."""
        pattern = rf"{re.escape(old_symbol)}\(\s*{pattern_label_number}\s*\]"
        final_name = f"{new_name}({pattern_label_number}]"
        replaced_string = re.sub(pattern, final_name, labelled_pattern_expression, count=1)
        return replaced_string

    @staticmethod
    def get_highest_label(labelledExpression: str) -> int:
        """Get the highest label number from a labelled expression."""
        maxLabel = -1
        active = False
        sb = ""
        for c in labelledExpression:
            if c == '(':
                active = True
            elif c == ']':
                if int(sb) > maxLabel:
                    maxLabel = int(sb)
                sb = ""
                active = False
            elif active:
                sb += c
        return maxLabel

