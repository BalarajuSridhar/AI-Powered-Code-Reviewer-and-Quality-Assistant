"""
Compute docstring coverage and write report to JSON.
"""

import json
from typing import List, Dict, Any


def compute_coverage(per_file_results: List[Dict[str, Any]], threshold: int = 90) -> Dict[str, Any]:
    """
    Compute docstring coverage with threshold checking.
    
    Args:
        per_file_results: List from python_parser.parse_path
        threshold: Minimum coverage percentage required (default: 90)
    
    Returns:
        Coverage dict with per-file and aggregate stats including threshold check
    """
    report = {"files": [], "aggregate": {}}
    total_funcs = 0
    total_with_doc = 0
    total_generated = 0
    total_files = len(per_file_results)
    parsing_errors_total = 0

    for f in per_file_results:
        funcs = f.get("functions", [])
        file_total = len(funcs)
        file_with_doc = sum(1 for fn in funcs if fn.get("has_docstring"))
        file_generated = sum(1 for fn in funcs if fn.get("generated_docstring"))
        
        total_funcs += file_total
        total_with_doc += file_with_doc + file_generated
        total_generated += file_generated
        parsing_errors_total += len(f.get("parsing_errors", []))
        
        coverage = 0.0
        if file_total:
            coverage = (file_with_doc + file_generated) / file_total * 100.0
        
        report["files"].append({
            "file_path": f.get("file_path"),
            "total_functions": file_total,
            "functions_with_docstring": file_with_doc,
            "generated_docstrings": file_generated,
            "coverage_percent": round(coverage, 2),
            "parsing_errors": f.get("parsing_errors", []),
        })

    aggregate_coverage = 0.0
    if total_funcs:
        aggregate_coverage = total_with_doc / total_funcs * 100.0

    report["aggregate"] = {
        "total_files": total_files,
        "total_functions": total_funcs,
        "documented": total_with_doc,
        "generated_docstrings": total_generated,
        "coverage_percent": round(aggregate_coverage, 2),
        "meets_threshold": aggregate_coverage >= threshold,
        "parsing_errors_total": parsing_errors_total,
    }
    return report


def write_report(report: Dict[str, Any], path: str) -> None:
    """Write coverage report to JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)