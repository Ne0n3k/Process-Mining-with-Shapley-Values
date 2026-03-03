"""
Process tree conversion functions.
"""

from typing import Any
try:
    from Functions.process_tree.ast_nodes import ASTNode, LiteralASTNode, OperatorASTNode
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.process_tree.ast_nodes import ASTNode, LiteralASTNode, OperatorASTNode


def enumerate_tau(node, counter):
    """
    Enumerate empty (tau) nodes with labels.
    
    Args:
        node: Process tree node
        counter: List with single integer counter
    """
    if (not hasattr(node, "children") or not node.children) and getattr(node, "label", None) is None:
        node.label = f"tau_{counter[0]}"
        counter[0] += 1

    if hasattr(node, "children") and node.children is not None:
        for child in node.children:
            enumerate_tau(child, counter)


def process_tree_to_ast(pt: Any) -> ASTNode:
    """
    Convert process tree to AST.
    
    Args:
        pt: Process tree node
        
    Returns:
        ASTNode representation
    """
    if hasattr(pt, "children") and pt.children:
        op = getattr(pt, "operator", None) or "Seq"
        children_ast = [process_tree_to_ast(c) for c in pt.children]
        return OperatorASTNode(operator=str(op), children=children_ast)
    else:
        label = getattr(pt, "label", None) or "tau"
        return LiteralASTNode(label=str(label))

