import os
import tree_sitter_rust as tsrust
from tree_sitter import Language, Parser

RUST_LANG = Language(tsrust.language())
parser = Parser(RUST_LANG)

class ASTCodebaseGraph:
    """
    Phase 3 Upgrade: Parses multi-file engine codebases into an Abstract Syntax Tree (AST)
    symbol index so Cyberdeck sub-agents see exact structs, functions, and constants.
    """
    def __init__(self, project_root: str = "/kaggle/working/AI_Cyberdeck/CyberArenaEngine"):
        self.project_root = project_root

    def _extract_rust_symbols(self, filepath: str) -> list[str]:
        with open(filepath, "rb") as f:
            source = f.read()
        tree = parser.parse(source)
        symbols = []

        def walk(node):
            if node.type in ("function_item", "struct_item", "const_item", "enum_item"):
                first_line = source[node.start_byte:node.end_byte].decode("utf-8", errors="ignore").splitlines()[0]
                symbols.append(first_line.rstrip(" {").strip())
            for child in node.children:
                walk(child)

        walk(tree.root_node)
        return symbols

    def build_context_map(self) -> str:
        report = [f"=== AST REPOSITORY SYMBOL MAP ({os.path.basename(self.project_root)}) ==="]
        for root, _, files in os.walk(self.project_root):
            if "target" in root:
                continue
            for file in sorted(files):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.project_root)
                if file.endswith(".rs"):
                    syms = self._extract_rust_symbols(full_path)
                    report.append(f"\n[RUST FILE] {rel_path}")
                    for s in syms:
                        report.append(f"  • {s}")
                elif file.endswith(".wgsl"):
                    report.append(f"\n[WGSL SHADER] {rel_path} (@vertex vs_main, @fragment fs_main)")
        return "\n".join(report)

if __name__ == "__main__":
    graph = ASTCodebaseGraph()
    print(graph.build_context_map())
