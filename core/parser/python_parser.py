"""
core.parser.python_parser
AST-based per-file Python parser for Milestone 1.

Extracts:
- functions (name, args, annotations, defaults, returns, start/end lines)
- classes (and their methods)
- imports
- simple complexity estimate (heuristic)
- nesting depth
- presence of docstring
"""

import ast
import os
from typing import Any, Dict, List, Optional


def _get_annotation_str(node: Optional[ast.AST]) -> Optional[str]:
    if node is None:
        return None
    try:
        # ast.unparse available in Python 3.9+
        return ast.unparse(node)
    except Exception:
        # Fallback for older Python or weird nodes
        if isinstance(node, ast.Name):
            return node.id
        return None


def _get_default_str(node: Optional[ast.AST]) -> Optional[str]:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        try:
            if isinstance(node, ast.Constant):
                return repr(node.value)
        except Exception:
            return None
    return None


def _simple_complexity(node: ast.FunctionDef) -> int:
    """
    Heuristic estimate for cyclomatic complexity:
    Count occurrences of: If, For, While, With, Try, BooleanOp, Comprehension
    Minimum complexity = 1.
    """
    counter = 1

    class Visitor(ast.NodeVisitor):
        def visit_If(self, n):  # noqa: N802
            nonlocal counter
            counter += 1
            self.generic_visit(n)

        def visit_For(self, n):  # noqa: N802
            nonlocal counter
            counter += 1
            self.generic_visit(n)

        def visit_While(self, n):  # noqa: N802
            nonlocal counter
            counter += 1
            self.generic_visit(n)

        def visit_With(self, n):  # noqa: N802
            nonlocal counter
            counter += 1
            self.generic_visit(n)

        def visit_Try(self, n):  # noqa: N802
            nonlocal counter
            counter += 1
            self.generic_visit(n)

        def visit_BoolOp(self, n):  # noqa: N802
            nonlocal counter
            # boolean ops like a and b add to complexity
            counter += len(n.values) - 1
            self.generic_visit(n)

        def visit_ListComp(self, n):  # noqa: N802
            nonlocal counter
            counter += 1
            self.generic_visit(n)

        def visit_DictComp(self, n):  # noqa: N802
            nonlocal counter
            counter += 1
            self.generic_visit(n)

    Visitor().visit(node)
    return max(counter, 1)


def _max_nesting_depth(node: ast.FunctionDef) -> int:
    """
    Compute maximum block nesting depth inside function body.
    """

    max_depth = 0

    class DepthVisitor(ast.NodeVisitor):
        def __init__(self):
            super().__init__()
            self.depth = 0
            self.max_depth = 0

        def generic_visit(self, n):
            is_block = isinstance(n, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.FunctionDef, ast.AsyncFunctionDef))
            if is_block:
                self.depth += 1
                if self.depth > self.max_depth:
                    self.max_depth = self.depth
                super().generic_visit(n)
                self.depth -= 1
            else:
                super().generic_visit(n)

    v = DepthVisitor()
    v.visit(node)
    return v.max_depth


def parse_functions(node: ast.AST) -> List[Dict[str, Any]]:
    funcs = []
    for n in ast.walk(node):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            try:
                sig_args = []
                for arg in n.args.args:
                    ann = _get_annotation_str(arg.annotation)
                    sig_args.append({"name": arg.arg, "annotation": ann, "default": None})
                # handle defaults (map from end)
                total_args = len(n.args.args)
                num_defaults = len(n.args.defaults)
                if num_defaults:
                    for i in range(num_defaults):
                        arg_index = total_args - num_defaults + i
                        default_node = n.args.defaults[i]
                        sig_args[arg_index]["default"] = _get_default_str(default_node)

                returns = _get_annotation_str(n.returns)
                doc = ast.get_docstring(n)
                start_line = getattr(n, "lineno", None)
                end_line = getattr(n, "end_lineno", None)
                complexity = _simple_complexity(n)
                nesting = _max_nesting_depth(n)
                # quick scan for raises and yields
                raises = []
                yields = False
                for sub in ast.walk(n):
                    if isinstance(sub, ast.Raise):
                        # try to get raised exception name
                        exc = getattr(sub, "exc", None)
                        raises.append(_get_annotation_str(exc) or "Exception")
                    if isinstance(sub, (ast.Yield, ast.YieldFrom)):
                        yields = True

                indent = n.col_offset        

                funcs.append(
                    {
                        "name": n.name,
                        "args": sig_args,
                        "returns": returns,
                        "decorators": [ast.unparse(d) if hasattr(ast, "unparse") else None for d in n.decorator_list],
                        "has_docstring": bool(doc),
                        "docstring": doc,
                        "start_line": start_line,
                        "end_line": end_line,
                        "complexity": complexity,
                        "nesting_depth": nesting,
                        "raises": list(set(raises)),
                        "yields": yields,
                        "indent": indent,
                    }
                )
            except Exception as e:
                # skip problematic function but record error in top-level parser
                funcs.append({"name": getattr(n, "name", "<unknown>"), "parse_error": str(e)})
    return funcs


def parse_classes(node: ast.AST) -> List[Dict[str, Any]]:
    classes = []
    for n in ast.walk(node):
        if isinstance(n, ast.ClassDef):
            try:
                methods = []
                for body_item in n.body:
                    if isinstance(body_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # reuse parse_functions logic by wrapping into module
                        method_info = parse_functions(body_item)[0] if parse_functions(body_item) else {}
                        methods.append(method_info)
                doc = ast.get_docstring(n)
                classes.append(
                    {
                        "name": n.name,
                        "bases": [_get_annotation_str(b) for b in n.bases],
                        "has_docstring": bool(doc),
                        "docstring": doc,
                        "start_line": getattr(n, "lineno", None),
                        "end_line": getattr(n, "end_lineno", None),
                        "methods": methods,
                    }
                )
            except Exception as e:
                classes.append({"name": getattr(n, "name", "<unknown>"), "parse_error": str(e)})
    return classes


def parse_imports(node: ast.AST) -> List[str]:
    imports = []
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.append(alias.name)
        if isinstance(n, ast.ImportFrom):
            module = n.module or ""
            for alias in n.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)
    return imports


def parse_file(path: str) -> Dict[str, Any]:
    """
    Parse a single python file and return metadata.
    """
    data = {
        "file_path": path,
        "functions": [],
        "classes": [],
        "imports": [],
        "parsing_errors": [],
    }
    try:
        with open(path, "r", encoding="utf-8") as fh:
            src = fh.read()
        node = ast.parse(src, filename=path)
        data["functions"] = parse_functions(node)
        data["classes"] = parse_classes(node)
        data["imports"] = parse_imports(node)
    except SyntaxError as e:
        data["parsing_errors"].append({"type": "SyntaxError", "message": str(e)})
    except Exception as e:
        data["parsing_errors"].append({"type": type(e).__name__, "message": str(e)})
    return data


def parse_path(path: str, recursive: bool = True, skip_dirs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Parse all .py files found at path. If path is a file, parse that file.
    Returns list of file metadata dicts.
    """
    results = []
    skip_dirs = skip_dirs or ["venv", ".venv", "__pycache__", ".git"]
    if os.path.isfile(path):
        if path.endswith(".py"):
            results.append(parse_file(path))
        return results

    for root, dirs, files in os.walk(path):
        # filter skip dirs
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                results.append(parse_file(fpath))
    return results
