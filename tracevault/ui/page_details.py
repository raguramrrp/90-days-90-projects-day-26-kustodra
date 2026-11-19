"""
TRACEVAULT - Advanced Evidence Detail Workspace
Multi-tab forensic inspector:
- Header & Identity Summary
- Tab 1: Overview
- Tab 2: Technical Metadata (Key-Value Inspector)
- Tab 3: Cryptographic Integrity & Verification History
- Tab 4: Chain-of-Custody Timeline
- Tab 5: Immutable Audit History
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from pathlib import Path

from tracevault.database import DatabaseManager
from tracevault.core.forensic_analyzer import ForensicAnalyzer
from tracevault.core.metadata_inspector import MetadataInspector
from tracevault.ui.components import render_hash_view, get_type_tag, get_status_badge_html


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Advanced Evidence Detail Workspace."""
    all_evidence = db.get_evidence_list()
    if not all_evidence:
        st.info("No evidence registered in the vault yet.")
        return

    selected_id = st.session_state.get("selected_evidence_id")
    evidence_options = [e["evidence_id"] for e in all_evidence]
    if not selected_id or selected_id not in evidence_options:
        selected_id = evidence_options[0]
        st.session_state["selected_evidence_id"] = selected_id

    # Record Selector & Quick Navigation Bar
    col_sel, col_act1, col_act2, col_act3 = st.columns([4, 1.3, 1.3, 1.3])
    with col_sel:
        chosen_id = st.selectbox(
            "Select Evidence Record",
            options=evidence_options,
            index=evidence_options.index(selected_id),
            format_func=lambda x: f"{x} — {[e['title'] for e in all_evidence if e['evidence_id'] == x][0]}",
            label_visibility="collapsed"
        )
        if chosen_id != selected_id:
            st.session_state["selected_evidence_id"] = chosen_id
            st.rerun()

    with col_act1:
        if st.button("Integrity Lab →", use_container_width=True):
            st.session_state["active_nav"] = "Integrity Lab"
            st.rerun()
    with col_act2:
        if st.button("Transfer Custody →", use_container_width=True):
            st.session_state["active_nav"] = "Chain of Custody"
            st.rerun()
    with col_act3:
        if st.button("Audit Report →", use_container_width=True):
            st.session_state["active_nav"] = "Audit & Reports"
            st.rerun()

    ev = db.get_evidence_by_id(chosen_id)
    if not ev:
        st.error(f"Unable to load record '{chosen_id}'.")
        return

    # Header: Evidence Name & Evidence ID
    st.markdown(f"### {ev['title']} &nbsp;`{ev['evidence_id']}`")

    # Compact Identity Summary Strip
    with st.container(border=True):
        col_s1, col_s2, col_s3, col_s4, col_s5, col_s6 = st.columns(6)
        with col_s1:
            st.caption("CASE REF")
            st.markdown(f"`{ev['case_id']}`")
        with col_s2:
            st.caption("FILE TYPE")
            tag = get_type_tag(ev.get("category", ""))
            st.markdown(f"`{tag}`")
        with col_s3:
            st.caption("FILE SIZE")
            sz = ev['file_size_bytes']
            sz_str = f"{sz / 1024:.1f} KB" if sz < 1024 * 1024 else f"{sz / (1024*1024):.2f} MB" if sz >= 1024*1024 else f"{sz} B"
            st.markdown(f"**{sz_str}**")
        with col_s4:
            st.caption("REGISTERED")
            st.markdown(f"`{ev['created_at'][:10]}`")
        with col_s5:
            st.caption("CUSTODIAN")
            st.markdown(f"**{ev.get('custodian_name', 'N/A')}**")
        with col_s6:
            st.caption("INTEGRITY")
            st.markdown(get_status_badge_html(ev['integrity_status']), unsafe_allow_html=True)

    # 5 Structured Forensic Tabs
    tab_overview, tab_meta, tab_integrity, tab_custody, tab_audit = st.tabs([
        "Overview",
        "Technical Metadata",
        "Cryptographic Integrity",
        "Chain of Custody",
        "Audit History"
    ])

    # Tab 1: Overview
    with tab_overview:
        with st.container(border=True):
            st.markdown("#### Evidence Description & Provenance")
            st.caption("Background context, initial seizure details, and legal classification.")

            col_o1, col_o2 = st.columns(2)
            with col_o1:
                st.markdown(f"**Title:** {ev['title']}")
                st.markdown(f"**Category:** {ev['category']}")
                st.markdown(f"**Original Filename:** `{ev['original_filename']}`")
                st.markdown(f"**MIME Type:** `{ev['mime_type']}`")
                st.markdown(f"**Case Reference:** `{ev['case_id']}` — {ev.get('case_title', 'N/A')}")
            with col_o2:
                st.markdown(f"**Collected By:** {ev.get('collected_by', 'N/A')}")
                st.markdown(f"**Collection Date:** `{ev.get('collection_date', 'N/A')}`")
                st.markdown(f"**Collection Location:** {ev.get('collection_location') or 'Field Seizure'}")
                st.markdown(f"**Registered By:** {ev.get('registered_by_name') or ev.get('registered_by_id', 'N/A')}")
                st.markdown(f"**Storage Reference:** `{Path(ev['storage_path']).name if ev.get('storage_path') else 'Vault'}`")

            if ev.get("description"):
                st.markdown("**Detailed Description:**")
                st.write(ev["description"])

            if ev.get("notes"):
                st.markdown(f"**Operational Notes:** _{ev['notes']}_")

    # Tab 2: Technical Metadata Inspector
    with tab_meta:
        with st.container(border=True):
            st.markdown("#### Technical Metadata Inspector")
            st.caption("Structured key-value breakdown distinguishing filesystem properties, container headers, and timestamps.")

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown("##### 1. File Identity & Container")
                st.markdown(f"- **Filename:** `{ev['original_filename']}`")
                st.markdown(f"- **Extension:** `{Path(ev['original_filename']).suffix.lower() or 'None'}`")
                st.markdown(f"- **MIME Type:** `{ev['mime_type']}`")
                st.markdown(f"- **Exact Byte Size:** {ev['file_size_bytes']:,} Bytes")
                st.markdown(f"- **Stored Vault Path:** `{ev.get('storage_path', 'N/A')}`")

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                st.markdown("##### 2. Cryptographic Measures")
                st.markdown(f"- **Shannon Entropy:** {ev.get('shannon_entropy', 0.0):.4f} bits per byte (Scale: 0.0 – 8.0)")
                entropy_interp = ForensicAnalyzer.interpret_entropy(ev.get("shannon_entropy", 0.0), ev.get("mime_type", ""))
                st.caption(f"**Entropy Assessment:** {entropy_interp['type']} — {entropy_interp['implication']}")

            with col_m2:
                st.markdown("##### 3. Chronological Timestamp Hierarchy")
                st.markdown(f"- **Evidence Collection Timestamp:** `{ev.get('collection_date', 'N/A')}`")
                st.markdown(f"- **Workstation Ingestion Timestamp:** `{ev['created_at'][:19].replace('T', ' ')} UTC`")

                storage_file = Path(ev["storage_path"]) if ev.get("storage_path") else None
                if storage_file and storage_file.is_file():
                    stat_info = storage_file.stat()
                    st.markdown(f"- **Vault File System Modified:** `{pd.to_datetime(stat_info.st_mtime, unit='s')} UTC`")
                else:
                    st.markdown(f"- **Vault File System Status:** Stored in secure archive")

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                st.markdown("##### 4. Forensic Classification")
                risk = ForensicAnalyzer.evaluate_risk(ev, [])
                st.markdown(f"- **Classification Category:** `{ev['category']}`")
                st.markdown(f"- **Forensic Risk Score:** `{risk['score']} / 100` ({risk['level']} Risk)")

    # Tab 3: Cryptographic Integrity
    with tab_integrity:
        with st.container(border=True):
            st.markdown("#### Cryptographic Fingerprints & Baseline")
            st.caption("Immutable cryptographic seals recorded at ingestion. Used for mathematical tampering verification.")

            render_hash_view(ev["sha256_hash"], label="SHA-256 PRIMARY REFERENCE DIGEST")

            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                render_hash_view(ev["md5_hash"], label="MD5 Digest")
            with col_h2:
                render_hash_view(ev["sha1_hash"], label="SHA-1 Digest")
            with col_h3:
                st.markdown("<span style='font-size: 11px; font-weight: 600; color: #527C78; text-transform: uppercase;'>Shannon Entropy</span>", unsafe_allow_html=True)
                st.code(f"{ev.get('shannon_entropy', 0.0):.4f} / 8.0000", language=None)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.markdown("#### Historical Integrity Verification Checks")

            checks = db.get_integrity_checks_for_evidence(chosen_id)
            if checks:
                check_table = []
                for c in checks:
                    calc_hash = c.get("calculated_sha256", "")
                    hash_display = f"{calc_hash[:16]}...{calc_hash[-8:]}" if len(calc_hash) > 24 else calc_hash
                    check_table.append({
                        "Timestamp (UTC)": str(c.get("check_timestamp", ""))[:19].replace("T", " "),
                        "Examiner": c.get("checked_by_name") or c.get("checked_by_id", "Examiner"),
                        "Mode": c.get("check_mode", "Baseline"),
                        "Result": c.get("result_status", "Unknown"),
                        "Calculated SHA-256": hash_display
                    })
                df_chk = pd.DataFrame(check_table)
                st.dataframe(df_chk, use_container_width=True, hide_index=True)
            else:
                st.info("No verification checks recorded for this evidence item.")

    # Tab 4: Chain of Custody
    with tab_custody:
        with st.container(border=True):
            st.markdown("#### Custody Possession Timeline")
            st.caption("Complete legal custody and handover history for this artifact.")

            timeline = db.get_custody_logs_for_evidence(chosen_id)
            if timeline:
                for idx, log in enumerate(timeline):
                    with st.container(border=True):
                        time_str = log.get("transfer_timestamp", "")[:19].replace("T", " ")
                        sender = log.get("sender_name") or log.get("sender_id", "Sender")
                        receiver = log.get("receiver_name") or log.get("receiver_id", "Receiver")
                        reason = log.get("transfer_reason", "Transfer")
                        token = log.get("signature_token", "")
                        token_snip = f"{token[:16]}..." if token else "N/A"

                        st.markdown(f"**Transfer #{idx+1}: {sender} ➔ {receiver}**")
                        st.caption(f"Date: `{time_str} UTC` &bull; Reason: **{reason}**")
                        if log.get("notes"):
                            st.write(f"_{log['notes']}_")
                        if log.get("integrity_verified_on_transfer"):
                            st.caption("✅ Integrity verified during transfer")
                        st.caption(f"Receipt Token: `{token_snip}`")
            else:
                st.info("No custody transfers recorded. Remains with initial collecting custodian.")

    # Tab 5: Audit History
    with tab_audit:
        with st.container(border=True):
            st.markdown("#### System Activity Ledger")
            st.caption("Immutable chronological events recorded for this artifact.")

            audit_logs = db.get_audit_logs_for_evidence(chosen_id)
            if audit_logs:
                for a in audit_logs:
                    ts = a["timestamp"][:19].replace("T", " ") if a.get("timestamp") else "N/A"
                    st.markdown(f"""
                    <div class="tv-stream-item">
                        <div style="display: flex; justify-content: space-between;">
                            <b>{a['event_type'].replace('_', ' ').title()}</b>
                            <span style="font-size: 11px; color: #697570;">{ts} UTC</span>
                        </div>
                        <div style="font-size: 11px; color: #4A5653; margin-top: 2px;">
                            {a['details']} &bull; User: <code>{a.get('user_id', 'System')}</code>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No audit logs recorded for this evidence artifact.")
