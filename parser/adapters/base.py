from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from opticode.models.analysis import StructuralNode, StructuralOutline
from opticode.models.common import CodeRange, NodeType
from opticode.parser.types import ParsedSyntaxTree, SyntaxNode


class LanguageAdapter(ABC):
    """Abstract base adapter for normalizing language-specific CSTs into StructuralNodes."""

    def extract(self, tree: ParsedSyntaxTree) -> StructuralOutline:
        """Extracts a normalized StructuralOutline from a ParsedSyntaxTree."""
        imports: List[str] = []
        symbol_index: Dict[str, List[CodeRange]] = {}
        root_nodes: List[StructuralNode] = []
        node_counter = [0]

        # Traverse the syntax tree starting at root
        for child in tree.root.children:
            extracted = self._process_syntax_node(
                node=child,
                parent=None,
                imports=imports,
                symbol_index=symbol_index,
                node_counter=node_counter,
            )
            root_nodes.extend(extracted)

        return StructuralOutline(
            root_nodes=root_nodes,
            imports=imports,
            symbol_index=symbol_index,
        )

    def _process_syntax_node(
        self,
        node: SyntaxNode,
        parent: Optional[StructuralNode],
        imports: List[str],
        symbol_index: Dict[str, List[CodeRange]],
        node_counter: List[int],
    ) -> List[StructuralNode]:
        classification = self.classify_node(node, parent)

        if classification is not None:
            node_type, symbol_name, metadata = classification
            node_counter[0] += 1
            node_id = f"{node_type.value}_{node_counter[0]}"

            struct_node = StructuralNode(
                id=node_id,
                node_type=node_type,
                range=node.range,
                name=symbol_name,
                parent_id=parent.id if parent else None,
                children=[],
                metadata=metadata,
            )

            # Record symbol in index
            if symbol_name:
                if symbol_name not in symbol_index:
                    symbol_index[symbol_name] = []
                symbol_index[symbol_name].append(node.range)

            # Record import
            if node_type == NodeType.IMPORT:
                import_text = metadata.get("import_path") or symbol_name or node.text.strip()
                if import_text and import_text not in imports:
                    imports.append(import_text)

            # Process children with this structural node as the parent
            for child in node.children:
                child_structs = self._process_syntax_node(
                    node=child,
                    parent=struct_node,
                    imports=imports,
                    symbol_index=symbol_index,
                    node_counter=node_counter,
                )
                struct_node.children.extend(child_structs)

            return [struct_node]
        else:
            # Transparent node (e.g. block, compound_statement, statement_list)
            # Propagate children up to the current parent
            results: List[StructuralNode] = []
            for child in node.children:
                results.extend(
                    self._process_syntax_node(
                        node=child,
                        parent=parent,
                        imports=imports,
                        symbol_index=symbol_index,
                        node_counter=node_counter,
                    )
                )
            return results

    @abstractmethod
    def classify_node(
        self,
        node: SyntaxNode,
        parent: Optional[StructuralNode],
    ) -> Optional[Tuple[NodeType, Optional[str], Dict[str, Any]]]:
        """Inspects a CST SyntaxNode and returns (NodeType, symbol_name, metadata) if

        it represents a structural element, or None if it is a container/intermediate node.
        """
        pass
