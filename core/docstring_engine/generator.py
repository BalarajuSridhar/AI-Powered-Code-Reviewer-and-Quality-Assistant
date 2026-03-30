
"""
core.docstring_engine.generator

Generates style-consistent docstrings using:
- LLM for semantic content
- Deterministic formatters for structure
"""

from typing import Dict, List, Optional
from core.docstring_engine.llm_integration import generate_docstring_content


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _arg_type_str(arg: Dict) -> str:
    return arg.get("annotation") or "TYPE"


def _format_args_section(args: List[Dict], arg_desc: Dict[str, str]) -> str:
    if not args:
        return ""
    lines = ["Args:"]
    for a in args:
        name = a["name"]
        typ = _arg_type_str(a)
        desc = arg_desc.get(name, "DESCRIPTION")
        lines.append(f"    {name} ({typ}): {desc}")
    return "\n".join(lines)


def _format_returns_section(returns: Optional[str], return_desc: str) -> str:
    if not returns:
        return ""
    return f"Returns:\n    {returns}: {return_desc or 'DESCRIPTION'}"


# -------------------------------------------------
# Google style
# -------------------------------------------------
def generate_google_docstring(fn: Dict, llm: Dict) -> str:
    summary = llm.get("summary", f"Short description of `{fn['name']}`.")
    arg_desc = llm.get("args", {})
    return_desc = llm.get("returns", "")
    raises_desc = llm.get("raises", {})

    parts = [summary, ""]

    args_section = _format_args_section(fn.get("args", []), arg_desc)
    if args_section:
        parts.append(args_section)
        parts.append("")

    returns_section = _format_returns_section(fn.get("returns"), return_desc)
    if returns_section:
        parts.append(returns_section)
        parts.append("")

    if raises_desc:
        parts.append("Raises:")
        for exc, desc in raises_desc.items():
            parts.append(f"    {exc}: {desc}")
        parts.append("")

    doc = "\n".join(parts).strip()
    return f'"""\n{doc}\n"""'


# -------------------------------------------------
# NumPy style
# -------------------------------------------------
def generate_numpy_docstring(fn: Dict, llm: Dict) -> str:
    summary = llm.get("summary", f"{fn['name']} function.")
    arg_desc = llm.get("args", {})
    return_desc = llm.get("returns", "")
    raises_desc = llm.get("raises", {})

    lines = [summary, "", "Parameters", "----------"]

    for arg in fn.get("args", []):
        t = arg.get("annotation") or "TYPE"
        desc = arg_desc.get(arg["name"], "DESCRIPTION")
        lines.append(f"{arg['name']} : {t}")
        lines.append(f"    {desc}")

    if fn.get("returns"):
        lines.extend([
            "",
            "Returns",
            "-------",
            f"{fn['returns']}",
            f"    {return_desc or 'DESCRIPTION'}"
        ])

    if raises_desc:
        lines.extend(["", "Raises", "------"])
        for exc, desc in raises_desc.items():
            lines.append(f"{exc}")
            lines.append(f"    {desc}")

    return f'"""\n' + "\n".join(lines) + '\n"""'


# -------------------------------------------------
# reST style
# -------------------------------------------------
def generate_rest_docstring(fn: Dict, llm: Dict) -> str:
    summary = llm.get("summary", f"{fn['name']} function.")
    arg_desc = llm.get("args", {})
    return_desc = llm.get("returns", "")
    raises_desc = llm.get("raises", {})

    lines = [summary, ""]

    for arg in fn.get("args", []):
        t = arg.get("annotation") or "TYPE"
        desc = arg_desc.get(arg["name"], "DESCRIPTION")
        lines.append(f":param {arg['name']}: {desc}")
        lines.append(f":type {arg['name']}: {t}")

    if fn.get("returns"):
        lines.append(f":return: {return_desc or 'DESCRIPTION'}")
        lines.append(f":rtype: {fn['returns']}")

    for exc, desc in raises_desc.items():
        lines.append(f":raises {exc}: {desc}")

    return f'"""\n' + "\n".join(lines) + '\n"""'


# -------------------------------------------------
# Main entry
# -------------------------------------------------
def generate_docstring(fn: Dict, style: str = "google") -> str:
    """
    Generate docstring using:
    - LLM for meaning
    - Code for formatting
    """

    llm_content = generate_docstring_content(fn)

    if style == "google":
        return generate_google_docstring(fn, llm_content)
    elif style == "numpy":
        return generate_numpy_docstring(fn, llm_content)
    elif style == "rest":
        return generate_rest_docstring(fn, llm_content)
    else:
        raise ValueError(f"Unknown style: {style}")
