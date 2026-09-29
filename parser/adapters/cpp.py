from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from opticode.models.common import NodeType
from opticode.models.analysis import StructuralNode
from opticode.parser.adapters.base import LanguageAdapter
from opticode.parser.adapters.c import extract_c_declarator_name
from opticode.parser.types import SyntaxNode


class CppAdapter(LanguageAdapter):
    """Structural adapter for C++."""

    def classify_node(
        self,
        node: SyntaxNode,
        parent: Optional[StructuralNode],
    ) -> Optional[Tuple[NodeType, Optional[str], Dict[str, Any]]]:
        t = node.type

        # Classes and Structs
        if t in ("class_specifier", "struct_specifier"):
            body_node = node.child_by_field_name("body")
            if body_node is not None:
                name_node = node.child_by_field_name("name")
                name = name_node.text if name_node else None
                return (NodeType.CLASS, name, {"specifier": t})
            return None

        # Functions and Methods
        elif t == "function_definition":
            name = extract_c_declarator_name(node)
            is_member_of_class = parent is not None and parent.node_type == NodeType.CLASS
            # Also check if declarator has a scope qualification (e.g. ClassName::method)
            decl = node.child_by_field_name("declarator")
            has_scoped_id = False
            if decl:
                for child in decl.walk():
                    if child.type in ("scoped_identifier", "qualified_identifier"):
                        has_scoped_id = True
                        break

            is_method = is_member_of_class or has_scoped_id
            node_type = NodeType.METHOD if is_method else NodeType.FUNCTION
            return (node_type, name, {"is_method": is_method})

        # Loops
        elif t in ("for_statement", "for_range_loop", "while_statement", "do_statement"):
            return (NodeType.LOOP, None, {"loop_kind": t})

        # Conditionals
        elif t in ("if_statement", "switch_statement"):
            return (NodeType.CONDITIONAL, None, {"conditional_kind": t})

        # Imports (#include and using namespace)
        elif t == "preproc_include":
            path_node = node.child_by_field_name("path")
            import_path = path_node.text if path_node else node.text.strip()
            return (NodeType.IMPORT, None, {"import_path": import_path})
        elif t == "using_declaration":
            return (NodeType.IMPORT, None, {"import_path": node.text.strip()})

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
