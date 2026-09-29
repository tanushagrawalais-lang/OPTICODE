from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from opticode.models.common import NodeType
from opticode.models.analysis import StructuralNode
from opticode.parser.adapters.base import LanguageAdapter
from opticode.parser.types import SyntaxNode


def extract_c_declarator_name(node: SyntaxNode) -> Optional[str]:
    """Helper to extract symbol name from C/C++ declarator trees."""
    decl = node.child_by_field_name("declarator")
    while decl:
        if decl.type in ("identifier", "type_identifier", "field_identifier"):
            return decl.text
        if decl.type == "function_declarator":
            inner = decl.child_by_field_name("declarator")
            if inner and inner.type in ("identifier", "type_identifier", "field_identifier"):
                return inner.text
            decl = inner
        elif decl.type in ("pointer_declarator", "parenthesized_declarator"):
            decl = decl.child_by_field_name("declarator")
        else:
            for child in decl.walk():
                if child.type in ("identifier", "type_identifier", "field_identifier"):
                    return child.text
            break
    return None


class CAdapter(LanguageAdapter):
    """Structural adapter for C."""

    def classify_node(
        self,
        node: SyntaxNode,
        parent: Optional[StructuralNode],
    ) -> Optional[Tuple[NodeType, Optional[str], Dict[str, Any]]]:
        t = node.type

        # Functions
        if t == "function_definition":
            name = extract_c_declarator_name(node)
            return (NodeType.FUNCTION, name, {"is_method": False})

        # Structs, Unions, Enums
        elif t in ("struct_specifier", "union_specifier", "enum_specifier"):
            body_node = node.child_by_field_name("body")
            if body_node is not None:
                name_node = node.child_by_field_name("name")
                name = name_node.text if name_node else None
                return (NodeType.CLASS, name, {"type_kind": t})
            return None

        # Loops
        elif t in ("for_statement", "while_statement", "do_statement"):
            return (NodeType.LOOP, None, {"loop_kind": t})

        # Conditionals
        elif t in ("if_statement", "switch_statement"):
            return (NodeType.CONDITIONAL, None, {"conditional_kind": t})

        # Imports (#include)
        elif t == "preproc_include":
            path_node = node.child_by_field_name("path")
            import_path = path_node.text if path_node else node.text.strip()
            return (NodeType.IMPORT, None, {"import_path": import_path})

        # Calls
        elif t == "call_expression":
            func_node = node.child_by_field_name("function")
            name = func_node.text if func_node else None
            return (NodeType.CALL, name, {"callee": name})

        # Assignments
        elif t == "init_declarator":
            name_node = node.child_by_field_name("declarator")
            name = name_node.text if name_node else None
            return (NodeType.ASSIGNMENT, name, {"target": name})
        elif t == "assignment_expression":
            left_node = node.child_by_field_name("left")
            name = left_node.text if left_node else None
            return (NodeType.ASSIGNMENT, name, {"target": name})

        return None
