"""
Pattern operator classes for workflow patterns.
"""

from collections import defaultdict
from Functions.utils.imports import *


class Sequence:
    """Sequence pattern operator."""
    
    _counter = defaultdict(int)

    @staticmethod
    def change_symbol_into_name(labelled_expression, pattern_label_number):
        n = len(labelled_expression)
        if not (2 <= n <= 15):
            raise Exception(f"Pattern for Seq{n} does not exist")

        Sequence._counter[n] += 1

        pattern_name = f'Seq{n}'
        old = f"({pattern_label_number}]" + ",".join(labelled_expression) + f"[{pattern_label_number})"
        new = old

        return pattern_name, old, new


class Loop:
    """Loop pattern operator."""
    
    _counter = defaultdict(int)

    @staticmethod
    def change_symbol_into_name(labelled_expression, pattern_label_number):
        n = len(labelled_expression)
        if not (2 <= n <= 30):
            raise Exception(f"Pattern for Loop{n} does not exist")

        Loop._counter[n] += 1
        idx = Loop._counter[n]

        pattern_name = f'Loop{n}'
        old = "(" + str(pattern_label_number) + "]" + ",".join(labelled_expression) + "[" + str(pattern_label_number) + ")"

        start = f'l{n}_s_{idx}'
        end   = f'l{n}_e_{idx}'
        labelled_expression = [start] + labelled_expression + [end]

        new = "(" + str(pattern_label_number) + "]" + ",".join(labelled_expression) + "[" + str(pattern_label_number) + ")"
        return pattern_name, old, new


class ExclusiveChoice:
    """Exclusive choice (XOR) pattern operator."""
    
    _counter = defaultdict(int)

    @staticmethod
    def change_symbol_into_name(labelled_expression, pattern_label_number):
        n = len(labelled_expression)
        if not (2 <= n <= 30):
            raise Exception(f"Pattern for Xor{n} does not exist")

        ExclusiveChoice._counter[n] += 1
        idx = ExclusiveChoice._counter[n]
        pattern_name = f'Xor{n}'
        labelled_expression_to_replace = "(" + str(pattern_label_number) + "]" + ",".join(
            labelled_expression) + "[" + str(pattern_label_number) + ")"

        start = f'x{n}_s_{idx}'
        end   = f'x{n}_e_{idx}'
        labelled_expression = [start] + labelled_expression + [end]

        new_labelled_expression = "(" + str(pattern_label_number) + "]" + ",".join(
            labelled_expression) + "[" + str(pattern_label_number) + ")"
        return pattern_name, labelled_expression_to_replace, new_labelled_expression


class Parallelism:
    """Parallelism (AND) pattern operator."""
    
    _counter = defaultdict(int)

    @staticmethod
    def change_symbol_into_name(labelled_expression, pattern_label_number):
        n = len(labelled_expression)

        if not (2 <= n <= 30):
            raise Exception(f"Pattern for And{n} does not exist")

        Parallelism._counter[n] += 1
        idx = Parallelism._counter[n]

        pattern_name = f'And{n}'
        labelled_expression_to_replace = "(" + str(pattern_label_number) + "]" + ",".join(
            labelled_expression) + "[" + str(pattern_label_number) + ")"

        start = f'a{n}_s_{idx}'
        end   = f'a{n}_e_{idx}'
        labelled_expression = [start] + labelled_expression + [end]

        new_labelled_expression = "(" + str(pattern_label_number) + "]" + ",".join(
            labelled_expression) + "[" + str(pattern_label_number) + ")"
        return pattern_name, labelled_expression_to_replace, new_labelled_expression

