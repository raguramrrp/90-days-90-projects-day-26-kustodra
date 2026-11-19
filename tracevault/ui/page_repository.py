"""
TRACEVAULT - Evidence Repository Page
Professional evidentiary data table with compact search and multi-criteria filters.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from tracevault.database import DatabaseManager


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Evidence Repository page."""
    st.markdown("### Evidence Repository")
    st.markdown("<p style='font-size: 13px; color: #68736F; margin-top: -8px; margin-bottom: 12px;'>Search and inspect all registered digital evidence artifacts and their integrity states.</p>", unsafe_allow_html=True)

    # Compact Search & Filter Bar
    with st.container(border=True):
        col_s, col_cat, col_case, col_stat = st.columns([3, 2, 2, 2])
        with col_s:
            search_query = st.text_input("Search", placeholder="Search by ID, filename, or hash...", label_visibility="collapsed")
        with col_cat:
            cat_filter = st.selectbox(
                "Category Filter",
                options=["All Categories", "System & Audit Log", "Forensic Still Image", "Surveillance Video", "Digital Document", "Audio Recording", "Forensic Disk Image", "Encrypted / Packed Payload", "Compressed / Encrypted Archive", "Executable / Malware Artifact"],
                label_visibility="collapsed"
            )
        with col_case:
            cases = db.get_cases()
            case_options = ["All Cases"] + [c["case_id"] for c in cases]
            case_filter = st.selectbox("Case Filter", options=case_options, label_visibility="collapsed")
        with col_stat:
            status_filter = st.selectbox(
                "Status Filter",
                options=["All Statuses", "Verified", "Not Yet Verified", "Integrity Mismatch", "Verification Failed"],
                label_visibility="collapsed"
            )

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
        st.info("No evidence records match the selected criteria.")
        return

    # Data Table Container
    with st.container(border=True):
        st.markdown(f"<div style='font-size: 12px; color: #68736F; margin-bottom: 8px;'>Showing <b>{len(evidence_list)}</b> registered record(s)</div>", unsafe_allow_html=True)

        table_rows = []
        for e in evidence_list:
            size_bytes = e["file_size_bytes"]
            size_str = f"{size_bytes / 1024:.1f} KB" if size_bytes < 1024 * 1024 else f"{size_bytes / (1024 * 1024):.2f} MB" if size_bytes >= 1024 * 1024 else f"{size_bytes} B"
            table_rows.append({
                "Evidence ID": e["evidence_id"],
                "Filename": e["original_filename"],
                "File Type": e["category"],
                "Size": size_str,
                "Case Reference": e["case_id"],
                "Registered Date": e["created_at"][:10] if e.get("created_at") else "N/A",
                "Current Custodian": e.get("custodian_name", "N/A"),
                "Integrity Status": e["integrity_status"]
            })

        df_repo = pd.DataFrame(table_rows)

        st.dataframe(
            df_repo,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Evidence ID": st.column_config.TextColumn("Evidence ID", width="small"),
                "Filename": st.column_config.TextColumn("Filename", width="medium"),
                "File Type": st.column_config.TextColumn("File Type", width="medium"),
                "Size": st.column_config.TextColumn("Size", width="small"),
                "Case Reference": st.column_config.TextColumn("Case", width="small"),
                "Registered Date": st.column_config.TextColumn("Registered", width="small"),
                "Current Custodian": st.column_config.TextColumn("Custodian", width="medium"),
                "Integrity Status": st.column_config.TextColumn("Status", width="small")
            }
        )

        # Record Inspector
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
            if st.button("Inspect Details", key="btn_inspect_repo", type="primary", use_container_width=True):
                st.session_state["selected_evidence_id"] = chosen_record
                st.session_state["active_nav"] = "Evidence Details & Metadata"
                st.rerun()
