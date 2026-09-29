from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from opticode.models.common import NodeType
from opticode.models.analysis import StructuralNode
from opticode.parser.adapters.javascript import JavascriptAdapter
from opticode.parser.types import SyntaxNode


class TypescriptAdapter(JavascriptAdapter):
    """Structural adapter for TypeScript."""

    def classify_node(
        self,
        node: SyntaxNode,
        parent: Optional[StructuralNode],
    ) -> Optional[Tuple[NodeType, Optional[str], Dict[str, Any]]]:
        t = node.type

        # Interfaces
        if t == "interface_declaration":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.INTERFACE, name, {"is_interface": True})

        # Enums
        elif t == "enum_declaration":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.CLASS, name, {"is_enum": True})

        # Type Aliases
        elif t == "type_alias_declaration":
            name_node = node.child_by_field_name("name")
            name = name_node.text if name_node else None
            return (NodeType.CLASS, name, {"is_type_alias": True})

        # Delegate remaining classifications to JavascriptAdapter
        return super().classify_node(node, parent)
