from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from opticode.models.common import NodeType
from opticode.models.analysis import StructuralNode
from opticode.parser.adapters.base import LanguageAdapter
from opticode.parser.types import SyntaxNode


class JavaAdapter(LanguageAdapter):
    """Structural adapter for Java."""

    def classify_node(
        self,
        node: SyntaxNode,
        parent: Optional[StructuralNode],
    ) -> Optional[Tuple[NodeType, Optional[str], Dict[str, Any]]]:
        t = node.type

        # Classes
        if t in ("class_declaration", "record_declaration", "enum_declaration"):
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.CLASS, name, {"class_kind": t})

        # Interfaces
        elif t in ("interface_declaration", "annotation_type_declaration"):
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.INTERFACE, name, {"interface_kind": t})

        # Methods & Constructors
        elif t in ("method_declaration", "constructor_declaration"):
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            params_node = node.child_by_field_name("parameters")
            params = params_node.text if params_node else ""
            ret_node = node.child_by_field_name("type")
            return (NodeType.METHOD, name, {"parameters": params, "return_type": ret_node.text if ret_node else None})

        # Loops
        elif t in ("for_statement", "enhanced_for_statement", "while_statement", "do_statement"):
            return (NodeType.LOOP, None, {"loop_kind": t})

        # Conditionals
        elif t in ("if_statement", "switch_expression", "switch_statement"):
            return (NodeType.CONDITIONAL, None, {"conditional_kind": t})

        # Imports
        elif t == "import_declaration":
            import_path = node.text.replace("import", "").replace(";", "").strip()
            return (NodeType.IMPORT, None, {"import_path": import_path})

        # Calls
        elif t in ("method_invocation", "object_creation_expression"):
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.CALL, name, {"callee": name})

        # Assignments
        elif t == "variable_declarator":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.ASSIGNMENT, name, {"target": name})
        elif t == "assignment_expression":
            left_node = node.child_by_field_name("left")
            target = left_node.text if left_node else None
            return (NodeType.ASSIGNMENT, target, {"target": target})

        return None
