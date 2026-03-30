"""
Simple CLI to run Milestone 1 scan from terminal.
Usage:
    python -m cli.commands scan <path> [--out storage/review_logs.json] [--generate-docs]
"""

import argparse
import json
import os
from core.parser.python_parser import parse_path
from core.docstring_engine.generator import generate_google_docstring
from core.reporter.coverage_reporter import compute_coverage, write_report


def _attach_generated_docstrings(results, generate_docs: bool = False):
    if not generate_docs:
        return results
    for f in results:
        for fn in f.get("functions", []):
            if not fn.get("has_docstring"):
                fn["generated_docstring"] = generate_google_docstring(fn)
    return results


def cmd_scan(args):
    path = args.path
    results = parse_path(path)
    results = _attach_generated_docstrings(results, args.generate_docs)
    report = compute_coverage(results)
    out = args.out
    out_dir = os.path.dirname(out)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    write_report(report, out)
    print(f"Scanned {len(results)} files — aggregate coverage: {report['aggregate']['coverage_percent']}%")
    print(f"Report written to {out}")


def main():
    parser = argparse.ArgumentParser(prog="ai-code-reviewer")
    sub = parser.add_subparsers(dest="command")
    scan = sub.add_parser("scan")
    scan.add_argument("path", type=str, help="Path to file or directory to scan")
    scan.add_argument("--out", type=str, default="storage/review_logs.json", help="Output JSON path")
    scan.add_argument("--generate-docs", action="store_true", default=False)
    args = parser.parse_args()
    if args.command == "scan":
        cmd_scan(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
