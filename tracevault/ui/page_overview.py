"""
TRACEVAULT - Overview Page: Evidence Intelligence
Command desk for evidence inventory, cryptographic integrity status, and custody timeline.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd

from tracevault.database import DatabaseManager
from tracevault.ui.components import render_summary_metrics, get_type_tag


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Evidence Intelligence overview workspace."""
    # 1. Header with integrated Register button
    col_head, col_action = st.columns([4, 1])
    with col_head:
        st.markdown("### Evidence Intelligence")
        st.caption("Monitor evidence records, cryptographic integrity and chain-of-custody activity.")
    with col_action:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        if st.button("+ Register Evidence", type="primary", use_container_width=True):
            st.session_state["active_nav"] = "Evidence Intake"
            st.rerun()

    # 2. Compact Summary Strip
    metrics = db.get_dashboard_metrics()
    render_summary_metrics(
        total=metrics["total_evidence"],
        verified=metrics["verified_count"],
        pending=metrics["pending_count"],
        mismatch=metrics["mismatch_count"] + metrics["failed_count"]
    )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 3. Two-Column Main Workspace
    col_left, col_right = st.columns([3, 2])

    # Left Column: Evidence Register
    with col_left:
        with st.container(border=True):
            col_reg_title, col_reg_all = st.columns([3, 1])
            with col_reg_title:
                st.markdown("#### Evidence Register")
                st.caption("Active digital artifacts in custody")
            with col_reg_all:
                if st.button("View All →", key="btn_view_all_repo", use_container_width=True):
                    st.session_state["active_nav"] = "Evidence Repository"
                    st.rerun()

            evidence_list = db.get_evidence_list()[:7]
            if evidence_list:
                table_data = []
                for ev in evidence_list:
                    tag = get_type_tag(ev["category"])
                    table_data.append({
                        "Evidence ID": ev["evidence_id"],
                        "Evidence Name": ev["title"],
                        "Type": tag,
                        "Registration Date": ev["created_at"][:10] if ev.get("created_at") else "N/A",
                        "Custodian": ev.get("custodian_name", "N/A"),
                        "Status": ev["integrity_status"]
                    })
                df_recent = pd.DataFrame(table_data)

                st.dataframe(
                    df_recent,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Evidence ID": st.column_config.TextColumn("ID", width="small"),
                        "Evidence Name": st.column_config.TextColumn("Evidence Name", width="medium"),
                        "Type": st.column_config.TextColumn("Type", width="small"),
                        "Registration Date": st.column_config.TextColumn("Registered", width="small"),
                        "Custodian": st.column_config.TextColumn("Custodian", width="medium"),
                        "Status": st.column_config.TextColumn("Status", width="small")
                    }
                )

                # Direct record inspector
                col_sel, col_open = st.columns([3, 1])
                with col_sel:
                    options = [e["evidence_id"] for e in evidence_list]
                    chosen_id = st.selectbox(
                        "Inspect record",
                        options=options,
                        format_func=lambda x: f"{x} — {[e['title'] for e in evidence_list if e['evidence_id'] == x][0]}",
                        label_visibility="collapsed"
                    )
                with col_open:
                    if st.button("Open Record", key="btn_open_recent_reg", use_container_width=True):
                        st.session_state["selected_evidence_id"] = chosen_id
                        st.session_state["active_nav"] = "Evidence Details & Metadata"
                        st.rerun()
            else:
                st.info("No evidence registered yet. Click '+ Register Evidence' above to begin intake.")

    # Right Column: Custody Activity
    with col_right:
        with st.container(border=True):
            st.markdown("#### Custody Activity")
            st.caption("Chronological timeline of custody events")

            audit_logs = db.get_audit_logs(limit=7)
            if audit_logs:
                for log in audit_logs:
                    timestamp_str = log["timestamp"][:19].replace("T", " ") if log.get("timestamp") else "N/A"
                    event_title = log["event_type"].replace("_", " ").title()
                    eid = f" &bull; <code>{log['evidence_id']}</code>" if log.get("evidence_id") else ""
                    user_str = log.get("user_id", "System")

                    # Border/Text accent based on event type
                    color = "#315F50"
                    if "MATCH" in log["event_type"]:
                        color = "#287A54"
                    elif "MISMATCH" in log["event_type"] or "TAMPER" in log["event_type"]:
                        color = "#B74747"
                    elif "CUSTODY" in log["event_type"]:
                        color = "#B77B29"

                    st.markdown(f"""
                    <div class="tv-stream-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600; color: {color};">{event_title}</span>
                            <span style="font-size: 11px; color: #697570;">{timestamp_str}</span>
                        </div>
                        <div style="font-size: 11px; color: #4A5653; margin-top: 2px;">
                            {log['details']}{eid}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recorded custody events.")

    # 4. Bottom Section: Integrity Activity
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("#### Integrity Activity")
        st.caption("Recent cryptographic hash verifications and authenticity checks")

        recent_checks = db.get_recent_integrity_checks(limit=6)
        if recent_checks:
            check_rows = []
            for chk in recent_checks:
                calc_hash = chk.get("calculated_sha256", "")
                hash_snip = f"{calc_hash[:16]}...{calc_hash[-8:]}" if len(calc_hash) > 24 else calc_hash
                check_rows.append({
                    "Evidence Ref": chk["evidence_id"],
                    "Timestamp (UTC)": str(chk.get("check_timestamp", ""))[:19].replace("T", " "),
                    "Examiner": chk.get("checked_by_name") or chk.get("checked_by_id", "Examiner"),
                    "Mode": chk.get("check_mode", "Baseline"),
                    "Result": chk.get("result_status", "Unknown"),
                    "Calculated SHA-256 Digest": hash_snip
                })
            df_checks = pd.DataFrame(check_rows)
            st.dataframe(
                df_checks,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Evidence Ref": st.column_config.TextColumn("Evidence Reference", width="small"),
                    "Timestamp (UTC)": st.column_config.TextColumn("Verified At", width="small"),
                    "Examiner": st.column_config.TextColumn("Examiner", width="small"),
                    "Mode": st.column_config.TextColumn("Mode", width="small"),
                    "Result": st.column_config.TextColumn("Result", width="small"),
                    "Calculated SHA-256 Digest": st.column_config.TextColumn("Calculated Hash", width="medium")
                }
            )
        else:
            st.info("No integrity verification checks conducted yet. Run verifications in the Integrity Lab.")
