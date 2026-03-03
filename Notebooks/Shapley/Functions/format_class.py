"""
Formatting utilities for pattern expressions.
"""

import re
try:
    from Functions.utils.imports import *
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.utils.imports import *


class Format:
    """Static methods for formatting pattern expressions."""
    
    @staticmethod
    def lowercase_in_quotes(s: str) -> str:
        """Convert text inside quotes to lowercase."""
        def _repl(m: re.Match) -> str:
            inner = m.group(1)
            return f"'{inner.lower()}'"
        return re.sub(r"'([^']*)'", _repl, s)

    @staticmethod
    def replace_parens_in_quotes(s: str) -> str:
        """Replace parentheses inside quotes with dashes."""
        def _repl(m: re.Match) -> str:
            inner = m.group(1).replace('(', '-').replace(')', '-')
            return f"'{inner}'"
        return re.sub(r"'([^']*)'", _repl, s)

    @staticmethod
    def replace_colons_in_quotes(s: str) -> str:
        """Replace colons inside quotes with underscores."""
        def _repl(m: re.Match) -> str:
            inner = m.group(1)
            return f"'{inner.replace(':', '_')}'"
        return re.sub(r"'([^']*)'", _repl, s)

    @staticmethod
    def replace_spaces_with_underscore(text: str) -> str:
        """Replace spaces inside quotes with underscores and remove quotes."""
        def replace_spaces(m: re.Match) -> str:
            return re.sub(r'\s+', '_', m.group(0))
        text_with_underscore = re.sub(r"'(.*?)'", replace_spaces, text)
        text_no_quotes = re.sub(r"'", '', text_with_underscore)
        return text_no_quotes

    @staticmethod
    def label_expressions(expression: str) -> str:
        """Label nested expressions with bracket numbers."""
        labelled_expression = ""
        label_number = 0
        for c in expression:
            if c == '(':
                label_number += 1
                labelled_expression += f"({label_number}]"
            elif c == ')':
                labelled_expression += f"[{label_number})"
                label_number -= 1
            else:
                labelled_expression += c
        return labelled_expression

