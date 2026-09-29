from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from opticode.models.common import NodeType
from opticode.models.analysis import StructuralNode
from opticode.parser.adapters.base import LanguageAdapter
from opticode.parser.types import SyntaxNode


class JavascriptAdapter(LanguageAdapter):
    """Structural adapter for JavaScript."""

    def classify_node(
        self,
        node: SyntaxNode,
        parent: Optional[StructuralNode],
    ) -> Optional[Tuple[NodeType, Optional[str], Dict[str, Any]]]:
        t = node.type

        # Classes
        if t in ("class_declaration", "class_expression"):
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.CLASS, name, {"is_class": True})

        # Functions
        elif t in ("function_declaration", "generator_function_declaration"):
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.FUNCTION, name, {"is_method": False})

        # Methods inside classes/objects
        elif t == "method_definition":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.METHOD, name, {"is_method": True})

        # Loops
        elif t in ("for_statement", "for_in_statement", "for_of_statement", "while_statement", "do_statement"):
            return (NodeType.LOOP, None, {"loop_kind": t})

        # Conditionals
        elif t in ("if_statement", "switch_statement"):
            return (NodeType.CONDITIONAL, None, {"conditional_kind": t})

        # Imports
        elif t == "import_statement":
            source_node = node.child_by_field_name("source")
            import_path = source_node.text.strip("'\"") if source_node else node.text.strip()
            return (NodeType.IMPORT, None, {"import_path": import_path})

        # Calls
        elif t in ("call_expression", "new_expression"):
            func_node = node.child_by_field_name("function") or node.child_by_field_name("constructor")
            name = func_node.text if func_node else None
            return (NodeType.CALL, name, {"callee": name})

        # Assignments
        elif t == "variable_declarator":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.ASSIGNMENT, name, {"target": name})
        elif t == "assignment_expression":
            left_node = node.child_by_field_name("left")
            name = left_node.text if left_node else None
            return (NodeType.ASSIGNMENT, name, {"target": name})

        return None
