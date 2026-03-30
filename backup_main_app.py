# """
# Streamlit app for Milestone 1:
# - choose a folder
# - run scan
# - view per-file metadata
# - view generated docstrings (Google style)
# - download the aggregate report JSON
# """

# import json
# import os
# import streamlit as st
# from core.parser.python_parser import parse_path
# from core.docstring_engine.generator import generate_google_docstring
# from core.reporter.coverage_reporter import compute_coverage, write_report

# st.set_page_config(page_title="AI Code Reviewer - Milestone 1", layout="wide")

# st.title("AI Code Reviewer — Milestone 1 (Parser & Baseline Docstrings)")
# st.markdown(
#     "Upload / select a project folder (or enter a path). Click **Scan** to run the AST parser and generate baseline Google-style docstrings (non-destructive)."
# )

# col1, col2 = st.columns([3, 1])

# with col2:
#     st.info("How to use\n1. Select folder path\n2. Click Scan\n3. Inspect results and download JSON")
#     scan_path = st.text_input("Path to scan", value="examples")
#     generate_docs = st.checkbox("Generate baseline docstrings (non-destructive)", value=True)
#     out_path = st.text_input("Output JSON path", value="storage/review_logs.json")
#     if st.button("Scan"):
#         if not os.path.exists(scan_path):
#             st.error(f"Path not found: {scan_path}")
#         else:
#             with st.spinner("Parsing files..."):
#                 results = parse_path(scan_path)
#                 # attach generated docs
#                 if generate_docs:
#                     for f in results:
#                         for fn in f.get("functions", []):
#                             if not fn.get("has_docstring"):
#                                 fn["generated_docstring"] = generate_google_docstring(fn)
#                 report = compute_coverage(results)
#                 # ensure output dir exists
#                 out_dir = os.path.dirname(out_path)
#                 if out_dir and not os.path.exists(out_dir):
#                     os.makedirs(out_dir, exist_ok=True)
#                 write_report(report, out_path)
#                 st.success(f"Scan complete — report written to {out_path}")
#                 st.session_state["last_scan_results"] = results
#                 st.session_state["last_report"] = report

# # Show summary
# report = st.session_state.get("last_report")
# if report:
#     st.subheader("Aggregate Coverage")
#     agg = report["aggregate"]
#     st.metric("Coverage %", f"{agg['coverage_percent']}%")
#     st.write(f"Total files: {agg['total_files']}, Total functions: {agg['total_functions']}, Generated docs: {agg['generated_docstrings']}")

# # Show per-file results table
# results = st.session_state.get("last_scan_results")
# if results:
#     st.subheader("Per-file summary")
#     rows = []
#     for f in results:
#         rows.append({
#             "file": f.get("file_path"),
#             "functions": len(f.get("functions", [])),
#             "parsing_errors": len(f.get("parsing_errors", [])),
#             "generated_docstrings": sum(1 for fn in f.get("functions", []) if fn.get("generated_docstring")),
#         })
#     st.table(rows)

#     st.subheader("Files (expand to inspect)")
#     for f in results:
#         with st.expander(f.get("file_path")):
#             st.write("Imports:", f.get("imports", []))
#             st.write("Parsing errors:", f.get("parsing_errors", []))
#             for fn in f.get("functions", []):
#                 fn_title = f"{fn.get('name')}  (lines {fn.get('start_line')}–{fn.get('end_line')})"
#                 st.markdown(f"**{fn_title}**")
#                 st.write(f"Has docstring: {fn.get('has_docstring')}")
#                 st.write(f"Args: {[a['name'] for a in fn.get('args', [])]}")
#                 st.write(f"Returns: {fn.get('returns')}")
#                 st.write(f"Complexity (heuristic): {fn.get('complexity')}, nesting: {fn.get('nesting_depth')}")
#                 if fn.get("has_docstring"):
#                     st.code(fn.get("docstring") or "—")
#                 if fn.get("generated_docstring"):
#                     st.subheader("Generated (Google-style) docstring")
#                     st.code(fn.get("generated_docstring"))
#     # Download button for report
#     report_json = json.dumps(st.session_state.get("last_report", {}), indent=2)
#     st.download_button("Download report JSON", data=report_json, file_name="review_report.json", mime="application/json")
# else:
#     st.info("No scan run yet. Enter a path and hit Scan.")









# import streamlit as st
# import difflib

# from core.parser.python_parser import parse_path
# from core.docstring_engine.generator import generate_docstring
# from core.validator.validator import (
#     validate_docstrings,
#     compute_complexity,
#     compute_maintainability
# )
# from core.reporter.coverage_reporter import compute_coverage

# # -------------------------------------------------
# # Page config
# # -------------------------------------------------
# st.set_page_config(page_title="AI Code Reviewer", layout="wide")

# # -------------------------------------------------
# # Load project
# # -------------------------------------------------
# PROJECT_PATH = "examples"
# parsed_files = parse_path(PROJECT_PATH)

# functions = []
# for f in parsed_files:
#     for fn in f["functions"]:
#         fn["file_path"] = f["file_path"]
#         functions.append(fn)

# coverage = compute_coverage(parsed_files)

# # -------------------------------------------------
# # Helper functions
# # -------------------------------------------------
# def get_status_badge(fn):
#     violations = validate_docstrings(fn["file_path"])
#     if fn.get("has_docstring") and not violations:
#         return "🟢 OK"
#     return "🔴 Fix"


# def generate_diff(old, new):
#     old_lines = old.splitlines(keepends=True)
#     new_lines = new.splitlines(keepends=True)
#     diff = difflib.unified_diff(
#         old_lines,
#         new_lines,
#         fromfile="Before",
#         tofile="After",
#         lineterm=""
#     )
#     return "".join(diff)

# # -------------------------------------------------
# # Sidebar
# # -------------------------------------------------
# st.sidebar.title("🧠 AI Code Reviewer")

# menu = st.sidebar.radio(
#     "Navigation",
#     ["🏠 Home", "📘 Docstrings", "📊 Validation", "📐 Metrics"]
# )

# st.sidebar.metric("📄 Files", len(parsed_files))
# st.sidebar.metric("📌 Coverage", f"{coverage['coverage_percent']}%")
# st.sidebar.metric("📚 Styles", 3)

# # -------------------------------------------------
# # HOME
# # -------------------------------------------------
# if menu == "🏠 Home":
#     st.title("AI-Powered Code Reviewer")

#     st.markdown("""
#     ### Milestone 2 – Features
#     ✔ Multiple docstring styles  
#     ✔ Documentation validation (PEP-257)  
#     ✔ Code complexity & maintainability metrics  
#     ✔ Status badges (OK / Fix)  
#     ✔ Diff-based review (Before vs After)  
#     """)

# # -------------------------------------------------
# # DOCSTRINGS + STATUS + DIFF
# # -------------------------------------------------
# elif menu == "📘 Docstrings":
#     st.title("📘 Docstring Generator")

#     style = st.radio("Select Docstring Style", ["google", "numpy", "rest"])

#     fn_display = [
#         f"{fn['name']}  {get_status_badge(fn)}"
#         for fn in functions
#     ]
#     selected_display = st.selectbox("Select Function", fn_display)

#     selected_fn = functions[fn_display.index(selected_display)]

#     generated_doc = generate_docstring(selected_fn, style)
#     existing_doc = selected_fn.get("docstring") or "❌ No existing docstring"

#     col1, col2 = st.columns(2)

#     with col1:
#         st.subheader("📄 Before")
#         st.code(existing_doc, language="python")

#     with col2:
#         st.subheader("✨ After")
#         st.code(generated_doc, language="python")

#     st.subheader("🔍 Diff View")
#     diff_text = generate_diff(existing_doc, generated_doc)
#     st.code(diff_text or "No differences", language="diff")

# # -------------------------------------------------
# # VALIDATION
# # -------------------------------------------------
# elif menu == "📊 Validation":
#     st.title("📊 Validation Results")

#     fn_display = [
#         f"{fn['name']}  {get_status_badge(fn)}"
#         for fn in functions
#     ]
#     selected_display = st.selectbox("Select Function", fn_display)
#     fn = functions[fn_display.index(selected_display)]

#     violations = validate_docstrings(fn["file_path"])
#     warnings = [v for v in violations if v["code"].startswith("D")]
#     errors = [v for v in violations if not v["code"].startswith("D")]

#     st.bar_chart({
#         "Compliant": 1 if not violations else 0,
#         "Warnings": len(warnings),
#         "Errors": len(errors)
#     })

#     if not violations:
#         st.success("All docstrings follow PEP-257 standards ✅")
#     else:
#         for w in warnings:
#             st.warning(f"{w['code']} (line {w['line']}): {w['message']}")
#         for e in errors:
#             st.error(f"{e['code']} (line {e['line']}): {e['message']}")

# # -------------------------------------------------
# # METRICS
# # -------------------------------------------------
# elif menu == "📐 Metrics":
#     st.title("📐 Code Metrics")

#     fn_display = [
#         f"{fn['name']}  {get_status_badge(fn)}"
#         for fn in functions
#     ]
#     selected_display = st.selectbox("Select Function", fn_display)
#     fn = functions[fn_display.index(selected_display)]

#     with open(fn["file_path"], "r", encoding="utf-8") as f:
#         source = f.read()

#     st.metric("Maintainability Index", compute_maintainability(source))
#     st.subheader("Cyclomatic Complexity")
#     st.json(compute_complexity(source))







#----------------------------------------------------
#  Combined Milestone 1 + Milestone 2 Streamlit App
#----------------------------------------------------



"""
Combined Milestone 1 + Milestone 2 Streamlit App
(CORRECT COVERAGE LOGIC – NO FALSE 100%)

- Scan project
- Show baseline coverage (existing docstrings only)
- Generate docstrings for preview (does NOT affect coverage)
- Validate (PEP-257)
- Show diff (before vs after)
- Show metrics
"""

import json
import os
import difflib
import streamlit as st
import ast

from core.parser.python_parser import parse_path
from core.docstring_engine.generator import generate_docstring
from core.validator.validator import (
    validate_docstrings,
    compute_complexity,
    compute_maintainability
)
from core.reporter.coverage_reporter import compute_coverage, write_report
from dashboard_ui.dashboard import render_dashboard


# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(page_title="AI Code Reviewer", layout="wide")

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def get_status_badge_by_file(file_path, file_data, selected_style):
    """
    Check ONLY if file has complete docstrings in the selected style.
    Does NOT check PEP-257 violations (that's for Validation tab).
    """
    # Check if any function is missing a valid docstring in the selected style
    for fn in file_data.get("functions", []):
        if not is_docstring_complete(fn, selected_style):
            return "🔴 Fix"
    
    # All functions have complete docstrings in this style
    return "🟢 OK"


def generate_diff(before, after):
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="Before",
            tofile="After",
            lineterm=""
        )
    )


def coverage_badge(percent):
    if percent < 70:
        return "🔴 Poor"
    elif percent < 90:
        return "🟡 Average"
    return "🟢 Excellent"




def detect_docstring_style(docstring):
    """
    Detect if docstring follows Google, NumPy, or reST style.
    Returns: 'google', 'numpy', 'rest', or None
    """
    if not docstring:
        return None
    
    # Clean the docstring
    doc = docstring.strip()
    doc_lower = doc.lower()
    
    # Google style: "Args:", "Returns:", "Raises:", "Yields:"
    google_keywords = ['args:', 'returns:', 'raises:', 'yields:', 'attributes:', 'example:', 'examples:', 'note:', 'notes:']
    if any(keyword in doc_lower for keyword in google_keywords):
        return 'google'
    
    # NumPy style: "Parameters\n----------" or "Returns\n-------"
    if ('parameters' in doc_lower and '----------' in doc) or \
       ('returns' in doc_lower and '-------' in doc) or \
       ('--------' in doc or '----------' in doc):
        return 'numpy'
    
    # reST style: ":param", ":type", ":return", ":rtype", ":raises"
    rest_keywords = [':param', ':type', ':return', ':rtype', ':raises', ':raise']
    if any(keyword in doc_lower for keyword in rest_keywords):
        return 'rest'
    
    return None


def is_docstring_complete(fn, style):
    """
    Check if function has a complete docstring in the specified style.
    """
    if not fn.get("has_docstring"):
        return False
    
    docstring = fn.get("docstring", "")
    if not docstring or len(docstring.strip()) < 10:
        return False
    
    detected_style = detect_docstring_style(docstring)
    
    # Check if detected style matches selected style
    if detected_style != style:
        return False
    
    # Check if it's not just a placeholder template
    if "DESCRIPTION." in docstring or "DESCRIPTION" in docstring.upper():
        return False
    
    # Additional check: ensure it's not an empty template
    doc_lower = docstring.lower()
    
    if style == "google":
        # Must have actual content after Args: or Returns:
        if "args:" in doc_lower:
            # Check if there's actual description, not just "DESCRIPTION"
            args_section = docstring[docstring.lower().index("args:"):]
            if "DESCRIPTION" in args_section.upper() and args_section.count("DESCRIPTION") > 0:
                return False
        return True
    
    elif style == "numpy":
        # Must have parameters section with content
        if "parameters" in doc_lower:
            params_section = docstring[docstring.lower().index("parameters"):]
            if "DESCRIPTION" in params_section.upper():
                return False
        return True
    
    elif style == "rest":
        # Must have :param with actual content
        if ":param" in doc_lower:
            if "DESCRIPTION" in docstring.upper():
                return False
        return True
    
    return True



def apply_docstring(file_path, fn, generated_docstring):
    """
    Replace existing docstring or insert new one.
    Handles both top-level functions and class methods.
    """
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    def_indent = fn.get("indent", 0)
    body_indent = " " * (def_indent + 4)

    # Normalize generated docstring
    doc = generated_docstring.strip()
    if doc.startswith('"""') and doc.endswith('"""'):
        doc = doc[3:-3].strip()

    # Build new docstring lines
    doc_lines = [body_indent + '"""' + "\n"]
    for line in doc.splitlines():
        doc_lines.append(body_indent + line.rstrip() + "\n")
    doc_lines.append(body_indent + '"""' + "\n")

    insert_line = fn["start_line"]  # Line after def

    # CHECK IF DOCSTRING EXISTS
    if fn.get("has_docstring"):
        # Find existing docstring boundaries
        start_idx = insert_line
        end_idx = insert_line
        
        # Scan forward to find docstring end
        found_start = False
        for i in range(insert_line, min(insert_line + 50, len(lines))):
            line = lines[i].strip()
            
            if not found_start and '"""' in line:
                start_idx = i
                found_start = True
                
                # Check if single-line docstring
                if line.count('"""') >= 2:
                    end_idx = i
                    break
            elif found_start and '"""' in line:
                end_idx = i
                break
        
        # REPLACE existing docstring
        lines[start_idx:end_idx + 1] = doc_lines
    else:
        # INSERT new docstring
        lines[insert_line:insert_line] = doc_lines

    # Write back
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.title("🧠 AI Code Reviewer")

menu = st.sidebar.selectbox(
    "Select View",
    ["🏠 Home", "📘 Docstrings", "📊 Validation", "📐 Metrics", "📊 Dashboard"]
)

st.sidebar.markdown("---")

scan_path = st.sidebar.text_input("Path to scan", value="examples")
out_path = st.sidebar.text_input("Output JSON path", value="storage/review_logs.json")

if st.sidebar.button("Scan"):
    if not os.path.exists(scan_path):
        st.sidebar.error("Path not found")
    else:
        with st.spinner("Parsing files..."):
            parsed_files = parse_path(scan_path)
            coverage = compute_coverage(parsed_files)

            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            write_report(coverage, out_path)

            st.session_state["parsed_files"] = parsed_files
            st.session_state["coverage"] = coverage
            st.session_state["selected_file"] = None
            st.session_state["doc_style"] = "google"

            st.sidebar.success("Scan completed")

# -------------------------------------------------
# LOAD STATE
# -------------------------------------------------
parsed_files = st.session_state.get("parsed_files")
coverage = st.session_state.get("coverage")

# -------------------------------------------------
# HOME
# -------------------------------------------------
if menu == "🏠 Home":
    st.title("AI-Powered Code Reviewer")

    if coverage:
        percent = coverage["coverage_percent"]
        status = coverage_badge(percent)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("📊 Coverage %", f"{percent}%", status)
        with c2:
            st.metric("📄 Total Functions", coverage.get("total_functions", "—"))
        with c3:
            st.metric("📘 Documented", coverage.get("documented", "—"))

    st.markdown("""
    ### Important
    - Coverage shows **existing documentation only**
    - Previewed docstrings do NOT change coverage
    - Coverage updates only after real fixes
    """)

# -------------------------------------------------
# DOCSTRINGS (UPDATED – SAME STRUCTURE)
# -------------------------------------------------

elif menu == "📘 Docstrings":
    st.title("📘 Docstring Review")

    if not parsed_files:
        st.info("Run a scan first")
    else:
        # Initialize style in session state
        if "doc_style" not in st.session_state:
            st.session_state["doc_style"] = "google"
        
        # ---- STYLE BUTTONS (TOP, HIGHLIGHTED) ----
        st.subheader("📄 Docstring Styles")
        sc1, sc2, sc3 = st.columns(3)

        style_changed = False

        with sc1:
            if st.button("Google", type="primary" if st.session_state["doc_style"] == "google" else "secondary"):
                if st.session_state["doc_style"] != "google":
                    st.session_state["doc_style"] = "google"
                    style_changed = True
        with sc2:
            if st.button("NumPy", type="primary" if st.session_state["doc_style"] == "numpy" else "secondary"):
                if st.session_state["doc_style"] != "numpy":
                    st.session_state["doc_style"] = "numpy"
                    style_changed = True
        with sc3:
            if st.button("reST", type="primary" if st.session_state["doc_style"] == "rest" else "secondary"):
                if st.session_state["doc_style"] != "rest":
                    st.session_state["doc_style"] = "rest"
                    style_changed = True

        # Force rerun when style changes to update badges
        if style_changed:
            st.rerun()

        style = st.session_state["doc_style"]

        st.markdown("---")

        left, right = st.columns([1, 2], gap="small")

        # ---- LEFT: FILES (WITH DYNAMIC BADGES) ----
        with left:
            st.subheader("📂 Files")
            st.caption(f"Total files: {len(parsed_files)} | Style: {style.upper()}")

            for idx, f in enumerate(parsed_files):
                file_path = f["file_path"]
                
                # Count functions that need docstrings in this style
                needs_fix = False
                for fn in f.get("functions", []):
                    if not fn.get("has_docstring"):
                        needs_fix = True
                        break
                    
                    docstring = fn.get("docstring", "")
                    detected = detect_docstring_style(docstring)
                    
                    if detected != style:
                        needs_fix = True
                        break
                
                status = "🔴 Fix" if needs_fix else "🟢 OK"
                
                if st.button(
                    f"{os.path.basename(file_path)}   {status}", 
                    key=f"file_{idx}_{style}",
                    use_container_width=True
                ):
                    st.session_state["selected_file"] = file_path


        # ---- RIGHT: PREVIEW + APPLY ----
        with right:
            selected_file = st.session_state.get("selected_file")

            if not selected_file:
                st.info("Select a file to view docstrings")
            else:
                file_data = next(f for f in parsed_files if f["file_path"] == selected_file)
                
                has_changes = False

                for fn in file_data["functions"]:
                    # Skip if already has valid docstring in selected style
                    if is_docstring_complete(fn, style):
                        continue
                    
                    has_changes = True
                    
                    st.markdown(f"### Function: `{fn['name']}`")

                    # Get before/after
                    existing = fn.get("docstring") or ""
                    
                    # Add triple quotes to before
                    if existing:
                        before = f'"""\n{existing}\n"""'
                    else:
                        before = "❌ No existing docstring"
                    
                    after = generate_docstring(fn, style)

                    c1, c2 = st.columns(2, gap="small")
                    with c1:
                        st.caption("Before")
                        st.code(before, language="python")
                    with c2:
                        st.caption("After (Preview)")
                        st.code(after, language="python")

                        a1, a2 = st.columns(2)
                        with a1:
                            if st.button("✅ Accept", key=f"accept_{fn['name']}_{selected_file}_{style}"):
                                apply_docstring(selected_file, fn, after)

                                # 🔄 RE-PARSE + RE-SCAN AFTER CHANGE
                                updated_files = parse_path(scan_path)
                                updated_coverage = compute_coverage(updated_files)
                                
                                st.session_state["parsed_files"] = updated_files
                                st.session_state["coverage"] = updated_coverage
                                
                                st.success("Docstring applied!")
                                st.rerun()
                        with a2:
                            st.button("❌ Reject", key=f"reject_{fn['name']}_{selected_file}_{style}")

                    st.caption("Diff")
                    st.code(generate_diff(before, after), language="diff")
                    st.markdown("---")
                
                if not has_changes:
                    st.success(f"✅ All docstrings are complete and valid in {style.upper()} style!")


# -------------------------------------------------
# VALIDATION
# -------------------------------------------------
# In the Validation section
elif menu == "📊 Validation":
    st.title("📊 Validation")

    if not parsed_files:
        st.info("Run a scan first")
    else:
        st.subheader("📂 Files")
        
        for f in parsed_files:
            file_path = f["file_path"]
            violations = validate_docstrings(file_path)
            
            # PEP-257 specific badge
            pep_status = "🟢 OK" if not violations else "🔴 Fix"
            
            if st.button(
                f"{os.path.basename(file_path)}   {pep_status}", 
                key=f"val_btn_{file_path}"
            ):
                st.session_state["validation_file"] = file_path
        
        st.markdown("---")
        
        selected_file = st.session_state.get("validation_file")
        if selected_file:
            violations = validate_docstrings(selected_file)
            
            st.bar_chart({
                "Compliant": 1 if not violations else 0,
                "Violations": len(violations)
            })

            if not violations:
                st.success("✅ No PEP-257 issues")
            else:
                for v in violations:
                    st.error(f"{v['code']} (line {v['line']}): {v['message']}")
# -------------------------------------------------
# METRICS
# -------------------------------------------------
elif menu == "📐 Metrics":
    st.title("📐 Code Metrics")

    if not parsed_files:
        st.info("Run a scan first")
    else:
        file_paths = [f["file_path"] for f in parsed_files]
        selected_file = st.selectbox("Select File", file_paths)

        with open(selected_file, "r", encoding="utf-8") as f:
            src = f.read()

        st.metric("Maintainability Index", compute_maintainability(src))
        st.json(compute_complexity(src))



# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------


elif menu == "📊 Dashboard":
    render_dashboard(
        parsed_files=parsed_files,
        coverage=coverage
    )

    

# -------------------------------------------------
# DOWNLOAD
# -------------------------------------------------
if coverage:
    st.markdown("---")
    st.download_button(
        "Download Coverage Report JSON",
        data=json.dumps(coverage, indent=2),
        file_name="review_report.json",
        mime="application/json"
    )
