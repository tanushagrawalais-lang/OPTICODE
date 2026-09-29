from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from opticode.models.common import NodeType
from opticode.models.analysis import StructuralNode
from opticode.parser.adapters.base import LanguageAdapter
from opticode.parser.types import SyntaxNode


class GoAdapter(LanguageAdapter):
    """Structural adapter for Go."""

    def classify_node(
        self,
        node: SyntaxNode,
        parent: Optional[StructuralNode],
    ) -> Optional[Tuple[NodeType, Optional[str], Dict[str, Any]]]:
        t = node.type

        # Functions
        if t == "function_declaration":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.FUNCTION, name, {"is_method": False})

        # Methods (with receiver)
        elif t == "method_declaration":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            rcv_node = node.child_by_field_name("receiver")
            receiver = rcv_node.text if rcv_node else ""
            return (NodeType.METHOD, name, {"receiver": receiver, "is_method": True})

        # Type Declarations (Structs and Interfaces)
        elif t == "type_declaration":
            type_spec = node.find_first_by_type("type_spec")
            if type_spec:
                name_node = type_spec.child_by_field_name("name")
                name = name_node.text if name_node else None
                type_node = type_spec.child_by_field_name("type")
                if type_node and type_node.type == "interface_type":
                    return (NodeType.INTERFACE, name, {"is_interface": True})
                return (NodeType.CLASS, name, {"is_struct": True})

        # Loops (Go only has 'for')
        elif t == "for_statement":
            return (NodeType.LOOP, None, {"loop_kind": "for"})

        # Conditionals
        elif t in ("if_statement", "expression_switch_statement", "type_switch_statement", "select_statement"):
            return (NodeType.CONDITIONAL, None, {"conditional_kind": t})

        # Imports
        elif t == "import_declaration":
            import_path = node.text.replace("import", "").strip()
            return (NodeType.IMPORT, None, {"import_path": import_path})

        # Calls
        elif t == "call_expression":
            func_node = node.child_by_field_name("function")
            name = func_node.text if func_node else None
            return (NodeType.CALL, name, {"callee": name})

        # Assignments
        elif t in ("short_var_declaration", "assignment_statement"):
            left_node = node.child_by_field_name("left")
            name = left_node.text if left_node else None
            return (NodeType.ASSIGNMENT, name, {"target": name})
        elif t == "var_spec":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.ASSIGNMENT, name, {"target": name})

        return None
