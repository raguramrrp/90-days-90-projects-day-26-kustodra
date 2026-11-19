"""
TRACEVAULT - Evidence Repository Page
Structured, searchable forensic evidence inventory table with multi-factor filters.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from tracevault.database import DatabaseManager
from tracevault.ui.components import render_status_badge


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Evidence Repository page."""
    st.markdown("### Evidence Repository")
    st.markdown("<div style='font-size: 13px; color: #68736F; margin-bottom: 16px;'>Forensic evidentiary inventory. Search, filter, and access complete case provenance records.</div>", unsafe_allow_html=True)

    # Filter Bar
    col_s, col_cat, col_case, col_stat = st.columns([3, 2, 2, 2])
    with col_s:
        search_query = st.text_input("Search (ID, Title, Filename, Hash)", placeholder="Search evidence...", label_visibility="collapsed")
    with col_cat:
        cat_filter = st.selectbox(
            "Category Filter",
            options=["All", "System & Audit Log", "Forensic Still Image", "Surveillance Video", "Digital Document", "Audio Recording", "Forensic Disk Image", "Encrypted / Packed Payload", "Compressed / Encrypted Archive", "Executable / Malware Artifact"],
            label_visibility="collapsed"
        )
    with col_case:
        cases = db.get_cases()
        case_filter_options = ["All"] + [c["case_id"] for c in cases]
        case_filter = st.selectbox("Case Filter", options=case_filter_options, label_visibility="collapsed")
    with col_stat:
        status_filter = st.selectbox("Status Filter", options=["All", "Verified", "Not Yet Verified", "Integrity Mismatch", "Verification Failed"], label_visibility="collapsed")

    evidence_list = db.get_evidence_list(
        search_query=search_query,
        category_filter=cat_filter,
        case_filter=case_filter,
        status_filter=status_filter
    )

    st.markdown(f"<div style='font-size: 12px; color: #68736F; margin-bottom: 10px;'>Displaying <b>{len(evidence_list)}</b> evidence item(s) matching criteria</div>", unsafe_allow_html=True)

    if not evidence_list:
        st.info("No evidence records match the selected search or filter criteria.")
        return

    # Render structured table with inspection actions
    st.markdown("""
    <div class="tv-card" style="padding: 0px; overflow: hidden;">
    """, unsafe_allow_html=True)

    # Use interactive selection
    for idx, ev in enumerate(evidence_list):
        col_id, col_info, col_case_ref, col_reg, col_cust, col_st, col_act = st.columns([1.2, 3, 1.8, 1.4, 1.6, 1.5, 1.2])

        status_html = render_status_badge(ev["integrity_status"])
        reg_date = ev["created_at"][:10] if ev.get("created_at") else "N/A"

        with col_id:
            st.markdown(f"<div style='padding-top: 10px; font-weight: 700; color: #315F50; font-size: 12px;'>{ev['evidence_id']}</div>", unsafe_allow_html=True)
        with col_info:
            st.markdown(f"""
            <div style='padding-top: 6px;'>
                <div style='font-size: 13px; font-weight: 600; color: #202927;'>{ev['title']}</div>
                <div style='font-size: 11px; color: #68736F;'>{ev['original_filename']} &bull; {ev['category']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_case_ref:
            st.markdown(f"<div style='padding-top: 10px; font-size: 12px; color: #4A5653;'>{ev['case_id']}</div>", unsafe_allow_html=True)
        with col_reg:
            st.markdown(f"<div style='padding-top: 10px; font-size: 12px; color: #68736F;'>{reg_date}</div>", unsafe_allow_html=True)
        with col_cust:
            st.markdown(f"<div style='padding-top: 10px; font-size: 12px; color: #202927;'>{ev.get('custodian_name', 'N/A')}</div>", unsafe_allow_html=True)
        with col_st:
            st.markdown(f"<div style='padding-top: 8px;'>{status_html}</div>", unsafe_allow_html=True)
        with col_act:
            if st.button("Inspect", key=f"btn_inspect_{ev['evidence_id']}_{idx}"):
                st.session_state["selected_evidence_id"] = ev["evidence_id"]
                st.session_state["active_nav"] = "Evidence Details & Metadata"
                st.rerun()

        st.markdown("<hr style='margin: 0; border: none; border-top: 1px solid #E1E6E3;'>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
