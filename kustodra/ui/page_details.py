"""
KUSTODRA - Artifact Inspector
Structured digital artifact inspector displaying:
- Header: Artifact ID, Title, Format tag, Integrity status, actions
- Identity strip: File name, File size, Case ref, MIME type, Ingestion timestamp, Custodian
- Compact tabs: Overview, Metadata, Integrity, Custody History, Audit History
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from pathlib import Path

from kustodra.database import DatabaseManager
from kustodra.core.forensic_analyzer import ForensicAnalyzer
from kustodra.ui.components import render_header, render_hash_view, get_type_tag, get_format_icon, get_status_badge_html


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the structured Artifact Detail View."""
    all_evidence = db.get_evidence_list()
    if not all_evidence:
        st.info("No artifacts cataloged in the vault yet.")
        return

    selected_id = st.session_state.get("selected_evidence_id")
    evidence_options = [e["evidence_id"] for e in all_evidence]
    if not selected_id or selected_id not in evidence_options:
        selected_id = evidence_options[0]
        st.session_state["selected_evidence_id"] = selected_id

    ev = db.get_evidence_by_id(selected_id)
    if not ev:
        st.error(f"Unable to load record '{selected_id}'.")
        return

    # Header with Back Action
    col_hdr_left, col_hdr_right = st.columns([4, 2])
    with col_hdr_left:
        st.markdown(f"""
        <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px;">
            <span style="font-size: 22px; font-weight: 700; color: #252B2A;">{ev['title']}</span>
            <span style="font-family: 'JetBrains Mono', Consolas, monospace; font-size: 14px; font-weight: 600; color: #315F50;">{ev['evidence_id']}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_hdr_right:
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("← Back", use_container_width=True):
                st.session_state["active_nav"] = "Artifact Vault"
                st.rerun()
        with col_b2:
            if st.button("🔬 Verify", use_container_width=True):
                st.session_state["active_nav"] = "Integrity Lab"
                st.rerun()
        with col_b3:
            if st.button("⛓️ Custody", use_container_width=True):
                st.session_state["active_nav"] = "Chain of Custody"
                st.rerun()

    # Identity Summary Strip
    with st.container(border=True):
        col_s1, col_s2, col_s3, col_s4, col_s5, col_s6 = st.columns(6)
        with col_s1:
            st.caption("CASE REFERENCE")
            st.markdown(f"**{ev['case_id']}**")
        with col_s2:
            st.caption("FILE TYPE")
            tag = get_type_tag(ev.get("category", ""))
            icon = get_format_icon(ev.get("category", ""))
            st.markdown(f"{icon} `{tag}`")
        with col_s3:
            st.caption("FILE SIZE")
            sz = ev['file_size_bytes']
            sz_str = f"{sz / 1024:.1f} KB" if sz < 1024 * 1024 else f"{sz / (1024*1024):.2f} MB" if sz >= 1024*1024 else f"{sz} B"
            st.markdown(f"**{sz_str}**")
        with col_s4:
            st.caption("REGISTERED ON")
            st.markdown(f"`{ev['created_at'][:10]}`")
        with col_s5:
            st.caption("CURRENT CUSTODIAN")
            st.markdown(f"**{ev.get('custodian_name', 'N/A')}**")
        with col_s6:
            st.caption("INTEGRITY STATUS")
            st.markdown(get_status_badge_html(ev['integrity_status']), unsafe_allow_html=True)

    # 5 Structured Inspection Tabs
    tab_overview, tab_meta, tab_integrity, tab_custody, tab_audit = st.tabs([
        "Overview",
        "Metadata",
        "Integrity",
        "Custody History",
        "Audit History"
    ])

    # Tab 1: Overview
    with tab_overview:
        with st.container(border=True):
            st.markdown("#### Artifact Overview & Provenance")
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
                vault_file = DatabaseManager.resolve_file_path(ev.get('storage_rel_path') or ev.get('storage_path'))
                st.markdown(f"**Vault Archive:** `{vault_file.name if vault_file else 'Stored'}`")

            if ev.get("description"):
                st.markdown("**Artifact Description:**")
                st.write(ev["description"])

            if ev.get("notes"):
                st.markdown(f"**Operational Notes:** _{ev['notes']}_")

        # Visual Content / Bitstream Preview Panel
        with st.container(border=True):
            st.markdown("#### 👁️ Specimen Content & Bitstream Inspector")
            resolved_p = DatabaseManager.resolve_file_path(ev.get("storage_rel_path") or ev.get("storage_path"))
            if resolved_p and resolved_p.is_file():
                ext = resolved_p.suffix.lower()
                cat = ev.get("category", "").lower()

                # Image viewer with details
                if ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"] or "image" in cat:
                    col_img_v, col_img_m = st.columns([2, 1])
                    with col_img_v:
                        st.image(str(resolved_p), caption=f"Specimen Preview: {resolved_p.name} ({ev['file_size_bytes']:,} Bytes)", use_container_width=True)
                    with col_img_m:
                        st.caption("FORENSIC VISUAL ANALYSIS")
                        st.markdown(f"- **Format:** `{ext.upper()[1:]}`")
                        st.markdown(f"- **Resolution:** Native forensic capture")
                        st.markdown(f"- **Integrity State:** {get_status_badge_html(ev['integrity_status'])}", unsafe_allow_html=True)
                        st.markdown(f"- **SHA-256 Digest:**")
                        st.code(ev['sha256_hash'][:24] + "...", language=None)

                # CSV / Tabular viewer
                elif ext in [".csv", ".tsv"] or "financial" in cat or "ledger" in cat:
                    try:
                        df_preview = pd.read_csv(resolved_p, nrows=100)
                        st.caption(f"Structured Data Preview ({len(df_preview)} rows rendered):")
                        st.dataframe(df_preview, use_container_width=True)
                    except Exception:
                        st.text(resolved_p.read_text(encoding="utf-8", errors="replace")[:1500])

                # Text / Log viewer
                elif ext in [".log", ".txt", ".json", ".xml", ".sql"] or "log" in cat:
                    try:
                        txt_content = resolved_p.read_text(encoding="utf-8", errors="replace")
                        lines = txt_content.splitlines()
                        st.caption(f"Raw Text Content ({len(lines)} lines &bull; {len(txt_content):,} characters):")
                        st.code("\n".join(lines[:200]), language=None)
                        if len(lines) > 200:
                            st.caption(f"... ({len(lines) - 200} more lines truncated in preview)")
                    except Exception:
                        raw_bytes = resolved_p.read_bytes()[:512]
                        st.code(raw_bytes.hex(), language=None)

                # Binary / Encrypted Payload - Forensic Hex Dump View
                else:
                    st.caption("Forensic Hexadecimal Bitstream Preview (First 256 Bytes):")
                    raw_b = resolved_p.read_bytes()[:256]
                    hex_lines = []
                    for offset in range(0, len(raw_b), 16):
                        chunk = raw_b[offset:offset+16]
                        hex_str = " ".join(f"{b:02X}" for b in chunk)
                        ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                        hex_lines.append(f"{offset:08X}  {hex_str:<48}  |{ascii_str}|")
                    st.code("\n".join(hex_lines), language=None)
            else:
                st.info("Specimen bitstream archive not available on local disk for direct preview.")

    # Tab 2: Metadata Inspector
    with tab_meta:
        with st.container(border=True):
            st.markdown("#### Technical Metadata Inspector")

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown("##### File System & Container")
                st.markdown(f"- **Filename:** `{ev['original_filename']}`")
                st.markdown(f"- **MIME Type:** `{ev['mime_type']}`")
                st.markdown(f"- **Exact Size:** {ev['file_size_bytes']:,} Bytes")
                st.markdown(f"- **Entropy:** {ev.get('shannon_entropy', 0.0):.4f} / 8.0000 bits per byte")
                interp = ForensicAnalyzer.interpret_entropy(ev.get("shannon_entropy", 0.0), ev.get("mime_type", ""))
                st.caption(f"**Density Analysis:** {interp['type']} — {interp['implication']}")

            with col_m2:
                st.markdown("##### Timestamps & Classification")
                st.markdown(f"- **Seizure Date:** `{ev.get('collection_date', 'N/A')}`")
                st.markdown(f"- **Intake Ingestion:** `{ev['created_at'][:19].replace('T', ' ')} UTC`")
                risk = ForensicAnalyzer.evaluate_risk(ev, [])
                st.markdown(f"- **Risk Classification:** `{risk['score']} / 100` ({risk['level']} Risk)")

    # Tab 3: Integrity
    with tab_integrity:
        with st.container(border=True):
            st.markdown("#### Cryptographic Fingerprint & History")

            render_hash_view(ev["sha256_hash"], label="SHA-256 Reference Baseline")

            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                render_hash_view(ev["md5_hash"], label="MD5 Digest")
            with col_h2:
                render_hash_view(ev["sha1_hash"], label="SHA-1 Digest")
            with col_h3:
                st.markdown("<span style='font-size: 11px; font-weight: 600; color: #527C78;'>SHANNON ENTROPY</span>", unsafe_allow_html=True)
                st.code(f"{ev.get('shannon_entropy', 0.0):.4f} / 8.0", language=None)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.markdown("##### Verification Audit Trail")
            checks = db.get_integrity_checks_for_evidence(selected_id)
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
                st.dataframe(pd.DataFrame(check_table), use_container_width=True, hide_index=True)
            else:
                st.info("No verification checks recorded for this artifact.")

    # Tab 4: Custody History
    with tab_custody:
        with st.container(border=True):
            st.markdown("#### Chain of Custody History")
            timeline = db.get_custody_logs_for_evidence(selected_id)
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
                        st.caption(f"Cryptographic Receipt: `{token_snip}`")
            else:
                st.info("No transfers recorded. Artifact remains with initial collecting custodian.")

    # Tab 5: Audit History
    with tab_audit:
        with st.container(border=True):
            st.markdown("#### Activity Ledger")
            audit_logs = db.get_audit_logs_for_evidence(selected_id)
            if audit_logs:
                for a in audit_logs:
                    ts = a["timestamp"][:19].replace("T", " ") if a.get("timestamp") else "N/A"
                    st.markdown(f"""
                    <div style="padding-bottom: 6px; margin-bottom: 6px; border-bottom: 1px solid #E1E4E3; font-size: 12px;">
                        <b>{a['event_type'].replace('_', ' ').title()}</b> &bull; <span style="color: #777F7D;">{ts} UTC</span>
                        <div style="color: #252B2A; margin-top: 2px;">{a['details']} &bull; Actor: <code>{a.get('user_id', 'System')}</code></div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No audit logs recorded for this artifact.")
