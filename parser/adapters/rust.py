from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from opticode.models.common import NodeType
from opticode.models.analysis import StructuralNode
from opticode.parser.adapters.base import LanguageAdapter
from opticode.parser.types import SyntaxNode


class RustAdapter(LanguageAdapter):
    """Structural adapter for Rust."""

    def classify_node(
        self,
        node: SyntaxNode,
        parent: Optional[StructuralNode],
    ) -> Optional[Tuple[NodeType, Optional[str], Dict[str, Any]]]:
        t = node.type

        # Structs, Enums, Unions
        if t in ("struct_item", "enum_item", "union_item"):
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.CLASS, name, {"item_kind": t})

        # Traits (Interfaces)
        elif t == "trait_item":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.INTERFACE, name, {"is_trait": True})

        # Impl Blocks (treated as Class container for methods)
        elif t == "impl_item":
            type_node = node.child_by_field_name("type")
            trait_node = node.child_by_field_name("trait")
            target_name = type_node.text if type_node else None
            name = f"impl {target_name}" if target_name else "impl"
            metadata = {
                "target_type": target_name,
                "trait": trait_node.text if trait_node else None,
                "is_impl": True,
            }
            return (NodeType.CLASS, name, metadata)

        # Functions and Methods
        elif t == "function_item":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            is_method = parent is not None and parent.node_type == NodeType.CLASS
            node_type = NodeType.METHOD if is_method else NodeType.FUNCTION
            params_node = node.child_by_field_name("parameters")
            params = params_node.text if params_node else ""
            ret_node = node.child_by_field_name("return_type")
            return (node_type, name, {"parameters": params, "return_type": ret_node.text if ret_node else None, "is_method": is_method})

        # Loops
        elif t in ("for_expression", "while_expression", "loop_expression"):
            return (NodeType.LOOP, None, {"loop_kind": t})

        # Conditionals
        elif t in ("if_expression", "match_expression"):
            return (NodeType.CONDITIONAL, None, {"conditional_kind": t})

        # Imports
        elif t == "use_declaration":
            import_path = node.text.replace("use", "").replace(";", "").strip()
            return (NodeType.IMPORT, None, {"import_path": import_path})

        # Calls and Macros
        elif t in ("call_expression", "macro_invocation"):
            func_node = node.child_by_field_name("function") or node.child_by_field_name("macro")
            name = func_node.text if func_node else None
            return (NodeType.CALL, name, {"callee": name, "is_macro": t == "macro_invocation"})

        # Assignments
        elif t == "let_declaration":
            pat_node = node.child_by_field_name("pattern")
            name = pat_node.text if pat_node else None
            return (NodeType.ASSIGNMENT, name, {"target": name})
        elif t == "assignment_expression":
            left_node = node.child_by_field_name("left")
            name = left_node.text if left_node else None
            return (NodeType.ASSIGNMENT, name, {"target": name})

        return None
