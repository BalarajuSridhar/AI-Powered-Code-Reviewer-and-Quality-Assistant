from pydocstyle import check
from radon.complexity import cc_visit
from radon.metrics import mi_visit


def validate_docstrings(file_path):
    violations = []
    for error in check([file_path]):
        violations.append({
            "code": getattr(error, "code", "PARSE_ERROR"),
            "line": getattr(error, "line", None),
            "message": str(error)
        })
    return violations


def compute_complexity(source):
    results = cc_visit(source)
    return [{"name": r.name, "complexity": r.complexity, "line": r.lineno} for r in results]


def compute_maintainability(source):
    return round(mi_visit(source, True), 2)
