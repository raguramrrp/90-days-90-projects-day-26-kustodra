"""
KUSTODRA - Overview Page: System Intelligence
Command desk for artifact inventory, cryptographic integrity status, and custody timeline.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd

from kustodra.database import DatabaseManager
from kustodra.ui.components import render_header, render_summary_metrics, get_type_tag


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the System Intelligence overview workspace."""
    # 1. Header with integrated Ingest button
    render_header(
        title="System Intelligence",
        current_user=current_user,
        show_import=True,
        breadcrumb="ANALYTICS & INTEGRITY"
    )

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

    # Left Column: Active Artifact Inventory
    with col_left:
        with st.container(border=True):
            col_reg_title, col_reg_all = st.columns([3, 1])
            with col_reg_title:
                st.markdown("#### Active Artifact Inventory")
            with col_reg_all:
                if st.button("View All →", key="btn_view_all_repo", use_container_width=True):
                    st.session_state["active_nav"] = "Artifact Vault"
                    st.rerun()

            evidence_list = db.get_evidence_list()[:7]
            if evidence_list:
                table_data = []
                for ev in evidence_list:
                    tag = get_type_tag(ev["category"])
                    table_data.append({
                        "Artifact ID": ev["evidence_id"],
                        "Artifact Title": ev["title"],
                        "Format": tag,
                        "Ingested At": ev["created_at"][:10] if ev.get("created_at") else "N/A",
                        "Custodian": ev.get("custodian_name", "N/A"),
                        "Integrity State": ev["integrity_status"]
                    })
                df_recent = pd.DataFrame(table_data)

                st.dataframe(
                    df_recent,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Artifact ID": st.column_config.TextColumn("Artifact ID", width=110),
                        "Artifact Title": st.column_config.TextColumn("Artifact Title", width="large"),
                        "Format": st.column_config.TextColumn("Format", width=90),
                        "Ingested At": st.column_config.TextColumn("Ingested", width=110),
                        "Custodian": st.column_config.TextColumn("Custodian", width=140),
                        "Integrity State": st.column_config.TextColumn("Integrity", width=110)
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
                        st.session_state["active_nav"] = "Artifact Inspector"
                        st.rerun()
            else:
                st.info("No artifacts cataloged yet. Click '+ Ingest Artifact' above to begin intake.")

    # Right Column: Custodial Activity Stream
    with col_right:
        with st.container(border=True):
            st.markdown("#### Custodial Activity Stream")

            audit_logs = db.get_audit_logs(limit=7)
            if audit_logs:
                for log in audit_logs:
                    timestamp_str = log["timestamp"][:19].replace("T", " ") if log.get("timestamp") else "N/A"
                    event_title = log["event_type"].replace("_", " ").title()
                    eid = f" &bull; <code>{log['evidence_id']}</code>" if log.get("evidence_id") else ""

                    # Border/Text accent based on event type
                    color = "#315F50"
                    if "MATCH" in log["event_type"]:
                        color = "#287A54"
                    elif "MISMATCH" in log["event_type"] or "TAMPER" in log["event_type"]:
                        color = "#B74747"
                    elif "CUSTODY" in log["event_type"]:
                        color = "#B77B29"

                    st.markdown(f"""
                    <div class="ks-stream-item">
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
        st.markdown("#### Integrity Verification Ledger")

        recent_checks = db.get_recent_integrity_checks(limit=6)
        if recent_checks:
            check_rows = []
            for chk in recent_checks:
                calc_hash = chk.get("calculated_sha256", "")
                hash_snip = f"{calc_hash[:16]}...{calc_hash[-8:]}" if len(calc_hash) > 24 else calc_hash
                check_rows.append({
                    "Artifact Ref": chk["evidence_id"],
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
                    "Artifact Ref": st.column_config.TextColumn("Artifact Reference", width=120),
                    "Timestamp (UTC)": st.column_config.TextColumn("Verified At", width=140),
                    "Examiner": st.column_config.TextColumn("Examiner", width=130),
                    "Mode": st.column_config.TextColumn("Mode", width=120),
                    "Result": st.column_config.TextColumn("Result", width=110),
                    "Calculated SHA-256 Digest": st.column_config.TextColumn("Calculated Hash", width="medium")
                }
            )
        else:
            st.info("No integrity verification checks conducted yet. Run verifications in the Integrity Lab.")
