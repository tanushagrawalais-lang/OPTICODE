from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from opticode.models.common import NodeType
from opticode.models.analysis import StructuralNode
from opticode.parser.adapters.base import LanguageAdapter
from opticode.parser.types import SyntaxNode


class PythonAdapter(LanguageAdapter):
    """Structural adapter for Python."""

    def classify_node(
        self,
        node: SyntaxNode,
        parent: Optional[StructuralNode],
    ) -> Optional[Tuple[NodeType, Optional[str], Dict[str, Any]]]:
        t = node.type

        # Functions & Methods
        if t == "function_definition":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            is_method = parent is not None and parent.node_type == NodeType.CLASS
            node_type = NodeType.METHOD if is_method else NodeType.FUNCTION
            params_node = node.child_by_field_name("parameters")
            params = params_node.text if params_node else ""
            return (node_type, name, {"parameters": params, "is_method": is_method})

        # Classes
        elif t == "class_definition":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            superclasses_node = node.child_by_field_name("superclasses")
            superclasses = superclasses_node.text if superclasses_node else ""
            return (NodeType.CLASS, name, {"superclasses": superclasses})

        # Loops
        elif t in ("for_statement", "while_statement"):
            loop_type = "for" if t == "for_statement" else "while"
            return (NodeType.LOOP, None, {"loop_kind": loop_type})

        # Conditionals
        elif t in ("if_statement", "match_statement"):
            cond_type = "if" if t == "if_statement" else "match"
            return (NodeType.CONDITIONAL, None, {"conditional_kind": cond_type})

        # Imports
        elif t in ("import_statement", "import_from_statement"):
            import_path = node.text.strip()
            return (NodeType.IMPORT, None, {"import_path": import_path})

        # Calls
        elif t == "call":
            func_node = node.child_by_field_name("function")
            func_name = func_node.text if func_node else None
            return (NodeType.CALL, func_name, {"callee": func_name})

        # Assignments
        elif t in ("assignment", "augmented_assignment"):
            left_node = node.child_by_field_name("left")
            target = left_node.text if left_node else None
            return (NodeType.ASSIGNMENT, target, {"target": target})

        return None
