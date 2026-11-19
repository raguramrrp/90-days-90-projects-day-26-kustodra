"""
TRACEVAULT - Overview Dashboard Page
Clean, native Streamlit implementation with balanced metrics,
functional Recent Evidence dataframe, and chronological activity stream.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from tracevault.database import DatabaseManager
from tracevault.ui.components import render_summary_metrics


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Overview Dashboard."""
    # 1. Header with integrated Register button
    col_head, col_action = st.columns([4, 1])
    with col_head:
        st.markdown("### Evidence Overview")
        st.markdown("<p style='font-size: 13px; color: #68736F; margin-top: -8px; margin-bottom: 12px;'>Manage registered evidence, verify file integrity and review custody activity.</p>", unsafe_allow_html=True)
    with col_action:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        if st.button("+ Register Evidence", type="primary", use_container_width=True):
            st.session_state["active_nav"] = "Register Evidence"
            st.rerun()

    # 2. Compact Native Summary Metrics
    metrics = db.get_dashboard_metrics()
    render_summary_metrics(
        total=metrics["total_evidence"],
        verified=metrics["verified_count"],
        pending=metrics["pending_count"],
        mismatch=metrics["mismatch_count"] + metrics["failed_count"]
    )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. Two Balanced Sections
    col_left, col_right = st.columns([3, 2])

    # Left Section: Recent Evidence Table
    with col_left:
        with st.container(border=True):
            st.markdown("#### Recent Evidence")
            st.caption("Latest registered artifacts in custody")

            evidence_list = db.get_evidence_list()[:8]
            if evidence_list:
                table_data = []
                for ev in evidence_list:
                    table_data.append({
                        "Evidence ID": ev["evidence_id"],
                        "Filename": ev["original_filename"],
                        "File Type": ev["category"],
                        "Registration Date": ev["created_at"][:10] if ev.get("created_at") else "N/A",
                        "Current Custodian": ev.get("custodian_name", "N/A"),
                        "Integrity Status": ev["integrity_status"]
                    })
                df_recent = pd.DataFrame(table_data)

                st.dataframe(
                    df_recent,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Evidence ID": st.column_config.TextColumn("Evidence ID", width="small"),
                        "Filename": st.column_config.TextColumn("Filename", width="medium"),
                        "File Type": st.column_config.TextColumn("File Type", width="medium"),
                        "Registration Date": st.column_config.TextColumn("Registered", width="small"),
                        "Current Custodian": st.column_config.TextColumn("Custodian", width="medium"),
                        "Integrity Status": st.column_config.TextColumn("Status", width="small")
                    }
                )

                # Quick action to open evidence record
                col_sel, col_open = st.columns([3, 1])
                with col_sel:
                    options = [e["evidence_id"] for e in evidence_list]
                    chosen_id = st.selectbox(
                        "Select evidence to inspect",
                        options=options,
                        format_func=lambda x: f"{x} — {[e['title'] for e in evidence_list if e['evidence_id'] == x][0]}",
                        label_visibility="collapsed"
                    )
                with col_open:
                    if st.button("Open Record", key="btn_open_recent", use_container_width=True):
                        st.session_state["selected_evidence_id"] = chosen_id
                        st.session_state["active_nav"] = "Evidence Details & Metadata"
                        st.rerun()
            else:
                st.info("No evidence registered yet. Click '+ Register Evidence' above to begin.")

    # Right Section: Recent Activity Chronological List
    with col_right:
        with st.container(border=True):
            st.markdown("#### Recent Activity")
            st.caption("Chronological ledger of verified system events")

            audit_logs = db.get_audit_logs(limit=7)
            if audit_logs:
                for log in audit_logs:
                    timestamp_str = log["timestamp"][:19].replace("T", " ") if log.get("timestamp") else "N/A"
                    event_title = log["event_type"].replace("_", " ").title()
                    eid = f" &bull; <code>{log['evidence_id']}</code>" if log.get("evidence_id") else ""

                    # Color dot based on event
                    color = "#315F50"
                    if "MATCH" in log["event_type"]:
                        color = "#287A54"
                    elif "MISMATCH" in log["event_type"] or "TAMPER" in log["event_type"]:
                        color = "#B74747"
                    elif "CUSTODY" in log["event_type"]:
                        color = "#B77B29"

                    st.markdown(f"""
                    <div style="padding-bottom: 8px; margin-bottom: 8px; border-bottom: 1px solid #E1E6E3; font-size: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600; color: {color};">{event_title}</span>
                            <span style="font-size: 11px; color: #68736F;">{timestamp_str}</span>
                        </div>
                        <div style="font-size: 11px; color: #4A5653; margin-top: 2px;">{log['details']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No system activity recorded yet.")
