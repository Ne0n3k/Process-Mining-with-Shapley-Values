"""
AST node classes for process trees.
"""

from abc import ABC, abstractmethod
from typing import List, Any, cast
try:
    from Functions.utils.imports import *
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.utils.imports import *


class ASTNode(ABC):
    """Abstract base class for AST nodes."""
    
    @abstractmethod
    def to_string(self, depth: int = 0) -> str:
        pass


class LiteralASTNode(ASTNode):
    """AST node representing a literal (activity label)."""
    
    def __init__(self, label: str):
        self.label = label

    def to_string(self, depth: int = 0) -> str:
        indent = "    " * depth
        return f"{indent}Literal: '{self.label}'"


class OperatorASTNode(ASTNode):
    """AST node representing an operator with children."""
    
    def __init__(self, operator: str, children: List[ASTNode]):
        self.operator = operator
        self.children = children

    def to_string(self, depth: int = 0) -> str:
        indent = "    " * depth
        child_str = "\n".join(child.to_string(depth + 1) for child in self.children)
        return f"{indent}Operator: {self.operator}\n{child_str}"


class ASTVisitor(ABC):
    """Abstract visitor for AST nodes."""
    
    @abstractmethod
    def visit_literal(self, node: LiteralASTNode):
        pass

    @abstractmethod
    def visit_operator(self, node: OperatorASTNode):
        pass

    def visit(self, node: ASTNode) -> Any:
        if isinstance(node, LiteralASTNode):
            lit = cast(LiteralASTNode, node)
            return self.visit_literal(lit)
        elif isinstance(node, OperatorASTNode):
            op = cast(OperatorASTNode, node)
            return self.visit_operator(op)
        else:
            ...

