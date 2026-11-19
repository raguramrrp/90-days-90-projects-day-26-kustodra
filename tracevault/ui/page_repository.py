"""
TRACEVAULT - Evidence Repository Page
Forensic archive inventory with structured search, multi-criteria filters,
and deep artifact inspection.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

from tracevault.database import DatabaseManager
from tracevault.ui.components import get_type_tag


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Evidence Repository archive."""
    st.markdown("### Evidence Repository")
    st.caption("Search and inspect registered digital artifacts.")

    # Compact Search & Multi-Criteria Filter Bar
    with st.container(border=True):
        col_s, col_cat, col_case, col_stat = st.columns([3, 2, 2, 2])
        with col_s:
            search_query = st.text_input(
                "Search",
                placeholder="Search by ID, title, filename, or hash...",
                label_visibility="collapsed"
            )
        with col_cat:
            cat_options = [
                "All Categories",
                "System & Audit Log",
                "Forensic Still Image",
                "Surveillance Video",
                "Digital Document",
                "Audio Recording",
                "Forensic Disk Image",
                "Encrypted / Packed Payload",
                "Compressed / Encrypted Archive",
                "Executable / Malware Artifact"
            ]
            cat_filter = st.selectbox("Category", options=cat_options, label_visibility="collapsed")
        with col_case:
            cases = db.get_cases()
            case_options = ["All Cases"] + [c["case_id"] for c in cases]
            case_filter = st.selectbox("Case", options=case_options, label_visibility="collapsed")
        with col_stat:
            stat_options = ["All Statuses", "Verified", "Not Yet Verified", "Integrity Mismatch", "Verification Failed"]
            status_filter = st.selectbox("Status", options=stat_options, label_visibility="collapsed")

    filter_cat = None if cat_filter == "All Categories" else cat_filter
    filter_case = None if case_filter == "All Cases" else case_filter
    filter_stat = None if status_filter == "All Statuses" else status_filter

    evidence_list = db.get_evidence_list(
        search_query=search_query,
        category_filter=filter_cat,
        case_filter=filter_case,
        status_filter=filter_stat
    )

    if not evidence_list:
        st.info("No evidence records match the selected filter criteria.")
        return

    # Data Table Container
    with st.container(border=True):
        col_c_left, col_c_right = st.columns([3, 1])
        with col_c_left:
            st.markdown(f"<span style='font-size: 12px; color: #697570;'>Archive Inventory: <b>{len(evidence_list)}</b> record(s) cataloged</span>", unsafe_allow_html=True)

        table_rows = []
        for e in evidence_list:
            size_bytes = e["file_size_bytes"]
            size_str = f"{size_bytes / 1024:.1f} KB" if size_bytes < 1024 * 1024 else f"{size_bytes / (1024 * 1024):.2f} MB" if size_bytes >= 1024 * 1024 else f"{size_bytes} B"
            type_tag = get_type_tag(e.get("category", ""))

            table_rows.append({
                "Evidence ID": e["evidence_id"],
                "Evidence Name": e["title"],
                "Type": type_tag,
                "File Size": size_str,
                "Case Ref": e["case_id"],
                "Registered Date": e["created_at"][:10] if e.get("created_at") else "N/A",
                "Custodian": e.get("custodian_name", "N/A"),
                "Integrity Status": e["integrity_status"]
            })

        df_repo = pd.DataFrame(table_rows)

        st.dataframe(
            df_repo,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Evidence ID": st.column_config.TextColumn("Evidence ID", width="small"),
                "Evidence Name": st.column_config.TextColumn("Evidence Name", width="medium"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "File Size": st.column_config.TextColumn("Size", width="small"),
                "Case Ref": st.column_config.TextColumn("Case", width="small"),
                "Registered Date": st.column_config.TextColumn("Registered", width="small"),
                "Custodian": st.column_config.TextColumn("Custodian", width="medium"),
                "Integrity Status": st.column_config.TextColumn("Status", width="small")
            }
        )

        # Artifact Detail Inspector Action Bar
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        col_pick, col_inspect = st.columns([3, 1])
        with col_pick:
            record_options = [e["evidence_id"] for e in evidence_list]
            chosen_record = st.selectbox(
                "Select record to inspect",
                options=record_options,
                format_func=lambda x: f"{x} — {[e['title'] for e in evidence_list if e['evidence_id'] == x][0]}",
                label_visibility="collapsed"
            )
        with col_inspect:
            if st.button("Inspect Artifact →", type="primary", use_container_width=True):
                st.session_state["selected_evidence_id"] = chosen_record
                st.session_state["active_nav"] = "Evidence Details & Metadata"
                st.rerun()
