# dashboard_ui/dashboard.py

"""
Dashboard UI – Milestone 4

Single-file implementation:
- Coverage summary
- Pytest results (real or manual)
- Search & filters
- Export (JSON / CSV)
- Feature cards
"""

import os
import json
import csv
import io
import streamlit as st
import pandas as pd


# -------------------------------------------------
# CONFIG
# -------------------------------------------------
PYTEST_REPORT_PATH = "storage/reports/pytest_results.json"


# -------------------------------------------------
# DATA LOADERS
# -------------------------------------------------
def load_pytest_results():
    if not os.path.exists(PYTEST_REPORT_PATH):
        return None
    with open(PYTEST_REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------------------------------
# FILTER + SEARCH LOGIC
# -------------------------------------------------
def filter_functions(functions, search=None, status=None):
    results = functions

    if search:
        results = [
            fn for fn in results
            if search.lower() in fn["name"].lower()
        ]

    if status == "OK":
        results = [fn for fn in results if fn.get("has_docstring")]
    elif status == "Fix":
        results = [fn for fn in results if not fn.get("has_docstring")]

    return results


# -------------------------------------------------
# EXPORT HELPERS
# -------------------------------------------------
def export_json(data):
    return json.dumps(data, indent=2)


def export_csv(functions):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["File", "Function", "Has Docstring"])

    for fn in functions:
        writer.writerow([
            fn.get("file_path"),
            fn.get("name"),
            fn.get("has_docstring")
        ])

    return buffer.getvalue()


# -------------------------------------------------
# MAIN DASHBOARD RENDER
# -------------------------------------------------
def render_dashboard(parsed_files, coverage):
    st.title("📊 Dashboard")

    st.markdown("---")



    # =================================================
    # 📊 REAL MULTI-BAR TEST CATEGORY CHART (DYNAMIC)
    # =================================================

    pytest_data = load_pytest_results()   # ✅ ADD THIS LINE

    if not pytest_data:
        st.warning("pytest_results.json not found. Run tests to generate results.")
        return

    tests = pytest_data.get("tests", [])

    if tests:
        rows = []

        for t in tests:
            nodeid = t.get("nodeid", "")
            outcome = t.get("outcome", "")

            # Extract category from test file name
            # tests/test_parser.py::test_xxx → Parser Tests
            if nodeid.startswith("tests/"):
                test_file = nodeid.split("::")[0]
                base = os.path.basename(test_file)
                category = (
                    base.replace("test_", "")
                        .replace(".py", "")
                        .replace("_", " ")
                        .title()
                    + " Tests"
                )
            else:
                category = "Other Tests"

            rows.append({
                "Category": category,
                "Outcome": outcome
            })

        df = pd.DataFrame(rows)

        summary_df = (
            df.groupby(["Category", "Outcome"])
            .size()
            .unstack(fill_value=0)
            .sort_index()
        )

        st.subheader("📊 Test Results")
        st.bar_chart(summary_df, width="stretch")


    # =================================================
    # ✅ PER-CATEGORY PASS SUMMARY (LIKE IMAGE)
    # =================================================
    for category in summary_df.index:
        passed = summary_df.loc[category].get("passed", 0)
        failed = summary_df.loc[category].get("failed", 0)
        total = passed + failed

        if failed == 0:
            st.markdown(
                f"""
                <div style="background:#d1fae5;border-left:4px solid #10b981;
                            padding:12px 16px;border-radius:6px;margin-bottom:10px;">
                    <b>✅ {category}</b>
                    <span style="float:right;">{passed}/{total} passed</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="background:#fee2e2;border-left:4px solid #ef4444;
                            padding:12px 16px;border-radius:6px;margin-bottom:10px;">
                    <b>⚠️ {category}</b>
                    <span style="float:right;">{passed}/{total} passed</span>
                </div>
                """,
                unsafe_allow_html=True
            )    


    st.markdown("---")


    # =================================================
    # INTERACTIVE FEATURE CARDS (COLORFUL & MODERN)
    # =================================================
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);padding:15px;border-radius:10px;color:white;box-shadow:0 4px 6px rgba(0,0,0,0.1)">
            <b style="font-size:20px;">✨ Enhanced UI Features</b>
            <p style="margin:5px 0 0 0;opacity:0.9;font-size:14px;">Explore powerful analysis tools</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Initialize selected feature in session state
    if "selected_feature" not in st.session_state:
        st.session_state["selected_feature"] = None

    # Create 4 columns for clickable boxes with modern styling
    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        if st.button("", key="filter_btn_card", width="stretch", type="secondary", help="Click to open Advanced Filters"):
            st.session_state["selected_feature"] = "filters"
        st.markdown(
            """
            <div style='text-align:center;padding:25px 15px;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius:12px;box-shadow:0 4px 15px rgba(102,126,234,0.3);cursor:pointer;margin-top:-60px;pointer-events:none;'>
                <div style='font-size:40px;margin-bottom:10px;'>🔍</div>
                <div style='font-weight:bold;font-size:16px;color:white;'>Advanced Filters</div>
                <div style='font-size:12px;color:rgba(255,255,255,0.9);margin-top:5px;'>Filter by status</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:
        if st.button("", key="search_btn_card", width="stretch", type="secondary", help="Click to open Search"):
            st.session_state["selected_feature"] = "search"
        st.markdown(
            """
            <div style='text-align:center;padding:25px 15px;background:linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        border-radius:12px;box-shadow:0 4px 15px rgba(240,147,251,0.3);cursor:pointer;margin-top:-60px;pointer-events:none;'>
                <div style='font-size:40px;margin-bottom:10px;'>🔎</div>
                <div style='font-weight:bold;font-size:16px;color:white;'>Search</div>
                <div style='font-size:12px;color:rgba(255,255,255,0.9);margin-top:5px;'>Find functions</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:
        if st.button("", key="export_btn_card", width="stretch", type="secondary", help="Click to open Export"):
            st.session_state["selected_feature"] = "export"
        st.markdown(
            """
            <div style='text-align:center;padding:25px 15px;background:linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                        border-radius:12px;box-shadow:0 4px 15px rgba(79,172,254,0.3);cursor:pointer;margin-top:-60px;pointer-events:none;'>
                <div style='font-size:40px;margin-bottom:10px;'>📤</div>
                <div style='font-weight:bold;font-size:16px;color:white;'>Export</div>
                <div style='font-size:12px;color:rgba(255,255,255,0.9);margin-top:5px;'>JSON & CSV</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col4:
        if st.button("", key="tooltip_btn_card", width="stretch", type="secondary", help="Click to view Help & Tips"):
            st.session_state["selected_feature"] = "tooltips"
        st.markdown(
            """
            <div style='text-align:center;padding:25px 15px;background:linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                        border-radius:12px;box-shadow:0 4px 15px rgba(67,233,123,0.3);cursor:pointer;margin-top:-60px;pointer-events:none;'>
                <div style='font-size:40px;margin-bottom:10px;'>ℹ️</div>
                <div style='font-weight:bold;font-size:16px;color:white;'>Help & Tips</div>
                <div style='font-size:12px;color:rgba(255,255,255,0.9);margin-top:5px;'>Quick guide</div>
            </div>
            """,
            unsafe_allow_html=True
        )        


    st.markdown("<br>", unsafe_allow_html=True)

    # Flatten functions once (reuse for all features)
    functions = []
    if parsed_files:
        for f in parsed_files:
            for fn in f.get("functions", []):
                fn["file_path"] = f.get("file_path")
                functions.append(fn)

    # =================================================
    # DYNAMIC CONTENT BASED ON SELECTED FEATURE
    # =================================================
    selected = st.session_state.get("selected_feature")

    if selected == "filters":
        # Animated header
        st.markdown(
            """
            <div style='background:linear-gradient(90deg, #667eea 0%, #764ba2 100%);padding:15px;border-radius:8px;margin-bottom:20px;'>
                <h3 style='color:white;margin:0;'>🔍 Advanced Filters</h3>
                <p style='color:rgba(255,255,255,0.9);margin:5px 0 0 0;font-size:14px;'>Filter dynamically by file, function, and documentation status</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Filter controls with better styling
        col_a, col_b = st.columns([2, 1])
        with col_a:
            status = st.selectbox("📊 Documentation status", ["All", "OK", "Fix"], help="Filter functions by documentation status")
        with col_b:
            st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
            total_count = len(functions)
        
        filtered = filter_functions(
            functions,
            search=None,
            status=None if status == "All" else status
        )
        
        # Stats badges
        st.markdown(
            f"""
            <div style='display:flex;gap:10px;margin-bottom:15px;'>
                <div style='background:#667eea;color:white;padding:10px 20px;border-radius:8px;flex:1;text-align:center;'>
                    <div style='font-size:24px;font-weight:bold;'>{len(filtered)}</div>
                    <div style='font-size:12px;opacity:0.9;'>Showing</div>
                </div>
                <div style='background:#764ba2;color:white;padding:10px 20px;border-radius:8px;flex:1;text-align:center;'>
                    <div style='font-size:24px;font-weight:bold;'>{len(functions)}</div>
                    <div style='font-size:12px;opacity:0.9;'>Total</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if filtered:
            table_rows = ""
            for idx, fn in enumerate(filtered):
                status_badge = "✅ Yes" if fn.get("has_docstring") else "❌ No"
                status_bg = "#10b981" if fn.get("has_docstring") else "#ef4444"
                
                table_rows += "<tr class='table-row' style='transition:all 0.3s ease;'>"
                table_rows += f"<td style='padding:15px;border-bottom:1px solid #e5e7eb;'>{os.path.basename(fn['file_path'])}</td>"
                table_rows += f"<td style='padding:15px;border-bottom:1px solid #e5e7eb;font-family:\"Courier New\",monospace;font-weight:500;'>{fn['name']}</td>"
                table_rows += f"<td style='padding:15px;border-bottom:1px solid #e5e7eb;text-align:center;'><span style='background:{status_bg};color:white;padding:6px 16px;border-radius:20px;font-size:12px;font-weight:600;display:inline-block;'>{status_badge}</span></td>"
                table_rows += "</tr>"
            
            st.markdown("""
            <style>
                .table-row:hover {
                    background-color: #f3f4f6 !important;
                    transform: scale(1.01);
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='overflow-x:auto;border-radius:12px;border:1px solid #e5e7eb;box-shadow:0 4px 12px rgba(0,0,0,0.08);'>
                <table style='width:100%;border-collapse:collapse;background:white;'>
                    <thead>
                        <tr style='background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
                            <th style='padding:18px;text-align:left;color:white;font-size:14px;font-weight:600;letter-spacing:0.5px;'>📁 FILE</th>
                            <th style='padding:18px;text-align:left;color:white;font-size:14px;font-weight:600;letter-spacing:0.5px;'>⚙️ FUNCTION</th>
                            <th style='padding:18px;text-align:center;color:white;font-size:14px;font-weight:600;letter-spacing:0.5px;'>✅ DOCSTRING</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No functions found matching the filter criteria.")


    elif selected == "search":
        st.markdown(
            """
            <div style='background:linear-gradient(90deg, #f093fb 0%, #f5576c 100%);padding:15px;border-radius:8px;margin-bottom:20px;'>
                <h3 style='color:white;margin:0;'>🔎 Search Functions</h3>
                <p style='color:rgba(255,255,255,0.9);margin:5px 0 0 0;font-size:14px;'>Instant search across all parsed functions</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        search = st.text_input("🔍 Enter function name", key="search_input", placeholder="Type to search...", help="Search is case-insensitive")
        
        filtered = filter_functions(
            functions,
            search=search,
            status=None
        )
        
        # Search results count
        if search:
            st.markdown(
                f"""
                <div style='background:#f093fb;color:white;padding:12px;border-radius:8px;margin-bottom:15px;text-align:center;'>
                    <span style='font-size:18px;font-weight:bold;'>{len(filtered)}</span> results found for "<b>{search}</b>"
                </div>
                """,
                unsafe_allow_html=True
            )
        
            if filtered:
                table_rows = ""
                for idx, fn in enumerate(filtered):
                    status_badge = "✅ Yes" if fn.get("has_docstring") else "❌ No"
                    status_bg = "#10b981" if fn.get("has_docstring") else "#ef4444"
                    
                    table_rows += "<tr class='table-row' style='transition:all 0.3s ease;'>"
                    table_rows += f"<td style='padding:15px;border-bottom:1px solid #e5e7eb;'>{os.path.basename(fn['file_path'])}</td>"
                    table_rows += f"<td style='padding:15px;border-bottom:1px solid #e5e7eb;font-family:\"Courier New\",monospace;font-weight:500;'>{fn['name']}</td>"
                    table_rows += f"<td style='padding:15px;border-bottom:1px solid #e5e7eb;text-align:center;'><span style='background:{status_bg};color:white;padding:6px 16px;border-radius:20px;font-size:12px;font-weight:600;display:inline-block;'>{status_badge}</span></td>"
                    table_rows += "</tr>"
                
                st.markdown("""
                <style>
                    .table-row:hover {
                        background-color: #f3f4f6 !important;
                        transform: scale(1.01);
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style='overflow-x:auto;border-radius:12px;border:1px solid #e5e7eb;box-shadow:0 4px 12px rgba(0,0,0,0.08);'>
                    <table style='width:100%;border-collapse:collapse;background:white;'>
                        <thead>
                            <tr style='background:linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
                                <th style='padding:18px;text-align:left;color:white;font-size:14px;font-weight:600;letter-spacing:0.5px;'>📁 FILE</th>
                                <th style='padding:18px;text-align:left;color:white;font-size:14px;font-weight:600;letter-spacing:0.5px;'>⚙️ FUNCTION</th>
                                <th style='padding:18px;text-align:center;color:white;font-size:14px;font-weight:600;letter-spacing:0.5px;'>✅ DOCSTRING</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No functions found. Try a different search term.")

    elif selected == "export":
        st.markdown(
            """
            <div style='background:linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);padding:15px;border-radius:8px;margin-bottom:20px;'>
                <h3 style='color:white;margin:0;'>📤 Export Data</h3>
                <p style='color:rgba(255,255,255,0.9);margin:5px 0 0 0;font-size:14px;'>Download analysis results in JSON or CSV format</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Export stats
        st.markdown(
            f"""
            <div style='background:#e3f2fd;padding:15px;border-radius:8px;margin-bottom:20px;border-left:4px solid #4facfe;'>
                <div style='font-size:16px;color:#333;'><b>📊 Export Summary</b></div>
                <div style='margin-top:10px;color:#666;'>
                    • Total Functions: <b>{len(functions)}</b><br>
                    • Documented: <b>{sum(1 for f in functions if f.get("has_docstring"))}</b><br>
                    • Missing Docstrings: <b>{sum(1 for f in functions if not f.get("has_docstring"))}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2, gap="large")
        
        with c1:
            st.download_button(
                "📥 Export as JSON",
                data=export_json(functions),
                file_name="functions.json",
                mime="application/json",
                width="stretch",
                type="primary"
            )
            st.caption("💡 JSON format for programmatic access")
        
        with c2:
            st.download_button(
                "📥 Export as CSV",
                data=export_csv(functions),
                file_name="functions.csv",
                mime="text/csv",
                width="stretch",
                type="primary"
            )
            st.caption("💡 CSV format for Excel/spreadsheets")

    elif selected == "tooltips":
        st.markdown(
            """
            <div style='background:linear-gradient(90deg, #43e97b 0%, #38f9d7 100%);padding:15px;border-radius:8px;margin-bottom:20px;'>
                <h3 style='color:white;margin:0;'>ℹ️ Interactive Help & Tips</h3>
                <p style='color:rgba(255,255,255,0.9);margin:5px 0 0 0;font-size:14px;'>Contextual help and quick reference guide</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Feature cards
        info_col1, info_col2 = st.columns(2, gap="medium")
        
        with info_col1:
            st.markdown(
                """
                <div style='background:#e8f5e9;padding:20px;border-radius:8px;border-left:4px solid #43e97b;'>
                    <h4 style='color:#2e7d32;margin-top:0;'>📊 Coverage Metrics</h4>
                    <p style='color:#555;font-size:14px;line-height:1.6;'>
                        • Coverage % = (Documented / Total) × 100<br>
                        • Green badge (🟢): ≥90% coverage<br>
                        • Yellow badge (🟡): 70-89% coverage<br>
                        • Red badge (🔴): <70% coverage
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown(
                """
                <div style='background:#e3f2fd;padding:20px;border-radius:8px;border-left:4px solid #4facfe;'>
                    <h4 style='color:#1565c0;margin-top:0;'>🧪 Test Results</h4>
                    <p style='color:#555;font-size:14px;line-height:1.6;'>
                        • Real-time test execution monitoring<br>
                        • Pass/fail ratio visualization<br>
                        • Per-file test breakdown<br>
                        • Integration with pytest reports
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with info_col2:
            st.markdown(
                """
                <div style='background:#fff3e0;padding:20px;border-radius:8px;border-left:4px solid #ff9800;'>
                    <h4 style='color:#e65100;margin-top:0;'>✅ Function Status</h4>
                    <p style='color:#555;font-size:14px;line-height:1.6;'>
                        • ✅ Green: Complete docstring present<br>
                        • ❌ Red: Missing or incomplete docstring<br>
                        • Auto-detection of docstring styles<br>
                        • Style-specific validation
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown(
                """
                <div style='background:#f3e5f5;padding:20px;border-radius:8px;border-left:4px solid #9c27b0;'>
                    <h4 style='color:#6a1b9a;margin-top:0;'>📝 Docstring Styles</h4>
                    <p style='color:#555;font-size:14px;line-height:1.6;'>
                        • <b>Google</b>: Args:, Returns:, Raises:<br>
                        • <b>NumPy</b>: Parameters/Returns with dashes<br>
                        • <b>reST</b>: :param, :type, :return directives<br>
                        • Auto-style detection & validation
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Expandable advanced guide
        with st.expander("📖 Advanced Usage Guide", expanded=False):
            st.markdown("""
            ### 🚀 Getting Started
            
            1. **Scan Your Project**: Enter the path and click 'Scan' in the sidebar
            2. **Review Coverage**: Check the home page for overall statistics
            3. **Generate Docstrings**: Navigate to the Docstrings tab to preview and apply
            4. **Validate**: Use the Validation tab to ensure PEP-257 compliance
            5. **Export**: Download reports in your preferred format
            
            ### 💡 Pro Tips
            
            - Use filters to focus on undocumented functions
            - Preview before applying changes to maintain code quality
            - Export reports for team reviews and CI/CD integration
            - Check metrics regularly to track documentation progress
            
            ### 🔧 Keyboard Shortcuts
            
            - `Ctrl + K`: Focus search box
            - `Ctrl + Enter`: Apply docstring (when focused)
            - `Esc`: Clear filters
            """)

    else:
        st.markdown("---")
        st.info("👆 Click on any feature card above to explore functionality")