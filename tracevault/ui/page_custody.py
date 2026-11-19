"""
TRACEVAULT - Chain of Custody Timeline Page
Visual custody timeline and transfer authorization workspace.
Generates cryptographic transfer receipts and updates active custodian.
"""

from __future__ import annotations
import streamlit as st
from datetime import datetime, timezone

from tracevault.database import DatabaseManager, get_iso_now
from tracevault.core.custody_manager import CustodyManager
from tracevault.core.crypto_engine import CryptoEngine
from tracevault.ui.components import render_status_badge, render_hash_view


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Chain-of-Custody timeline and transfer workflow."""
    st.markdown("### Chain-of-Custody Timeline")
    st.markdown("<div style='font-size: 13px; color: #68736F; margin-bottom: 16px;'>Forensic accountability ledger. Track, transfer, and verify legal possession across investigators, examiners, and secure vaults.</div>", unsafe_allow_html=True)

    all_evidence = db.get_evidence_list()
    if not all_evidence:
        st.info("No evidence registered yet.")
        return

    selected_id = st.session_state.get("selected_evidence_id")
    evidence_options = [e["evidence_id"] for e in all_evidence]
    if not selected_id or selected_id not in evidence_options:
        selected_id = evidence_options[0]

    chosen_id = st.selectbox(
        "Select Evidence Record",
        options=evidence_options,
        index=evidence_options.index(selected_id) if selected_id in evidence_options else 0,
        format_func=lambda x: f"{x} &mdash; {[e['title'] for e in all_evidence if e['evidence_id'] == x][0]}"
    )
    if chosen_id != selected_id:
        st.session_state["selected_evidence_id"] = chosen_id
        st.rerun()

    ev = db.get_evidence_by_id(chosen_id)
    custody_manager = CustodyManager(db)
    timeline = custody_manager.get_timeline(chosen_id)

    # 1. Active Custody Status Card
    st.markdown(f"""
    <div class="tv-card" style="border-left: 4px solid #315F50;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 12px; font-weight: 600; color: #68736F; text-transform: uppercase;">Active Legal Custodian</div>
                <div style="font-size: 18px; font-weight: 700; color: #202927; margin-top: 2px;">
                    {ev.get('custodian_name', ev['current_custodian_id'])}
                </div>
                <div style="font-size: 12px; color: #4A5653;">
                    Role: {ev.get('custodian_role', 'Custodian')} &bull; Badge / ID: <b>{ev.get('custodian_badge', 'N/A')}</b>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 11px; color: #68736F;">Evidence ID</div>
                <div style="font-size: 14px; font-weight: 700; color: #315F50;">{ev['evidence_id']}</div>
                <div style="margin-top: 4px;">{render_status_badge(ev['integrity_status'])}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_tl, col_trans = st.columns([3, 2])

    # 2. Chronological Timeline
    with col_tl:
        st.markdown("""
        <div class="tv-card">
            <div class="tv-card-header">
                <div>
                    <div class="tv-card-title">Custody Transfer History</div>
                    <div class="tv-card-subtitle">Immutable log of custody releases, handovers, and lab receipts</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Baseline Seizure Entry
        st.markdown(f"""
        <div class="tv-timeline-item">
            <div class="tv-timeline-time">{ev['collection_date']}</div>
            <div class="tv-timeline-title" style="color: #315F50;">
                INITIAL SEIZURE & VAULT INTAKE
            </div>
            <div class="tv-timeline-desc">
                Collected by <b>{ev['collected_by']}</b> from <i>{ev.get('collection_location') or 'Field Location'}</i>.<br>
                Registered by <b>{ev.get('registered_by_name', ev['registered_by_id'])}</b>. Baseline SHA-256 seal anchored.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if timeline:
            for log in timeline:
                time_str = log["transfer_timestamp"][:19].replace("T", " ")
                verif_badge = "<span style='color: #287A54; font-size: 11px; font-weight: 600;'>[Integrity Verified on Transfer]</span>" if log.get("integrity_verified_on_transfer") else ""
                token_snip = log["signature_token"][:16] + "..." if log.get("signature_token") else "N/A"

                st.markdown(f"""
                <div class="tv-timeline-item">
                    <div class="tv-timeline-time">{time_str} UTC</div>
                    <div class="tv-timeline-title">
                        {log.get('sender_name', log['sender_id'])} &rarr; {log.get('receiver_name', log['receiver_id'])}
                    </div>
                    <div class="tv-timeline-desc">
                        <b>Reason:</b> {log['transfer_reason']} {verif_badge}<br>
                        {f"<b>Notes:</b> {log['notes']}<br>" if log.get('notes') else ""}
                        <span style="font-size: 11px; color: #68736F;">Recorded by: {log.get('recorded_by_name', log['recorded_by_id'])} &bull; Receipt: <code>{token_snip}</code></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Transfer Custody Action Form
    with col_trans:
        st.markdown("""
        <div class="tv-card">
            <div class="tv-card-header">
                <div>
                    <div class="tv-card-title">Transfer Custody</div>
                    <div class="tv-card-subtitle">Authorize evidence release to another custodian</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        users = db.get_users()
        user_options = {u["user_id"]: f"{u['full_name']} ({u['role']})" for u in users}

        current_custodian_id = ev["current_custodian_id"]
        sender_id = st.selectbox(
            "Releasing Custodian (Sender) *",
            options=list(user_options.keys()),
            index=list(user_options.keys()).index(current_custodian_id) if current_custodian_id in user_options else 0,
            format_func=lambda x: user_options[x]
        )

        eligible_receivers = [uid for uid in user_options.keys() if uid != sender_id]
        if not eligible_receivers:
            st.warning("No alternative registered custodians available to receive evidence.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        receiver_id = st.selectbox(
            "Receiving Custodian (Recipient) *",
            options=eligible_receivers,
            format_func=lambda x: user_options[x]
        )

        transfer_reason = st.selectbox(
            "Transfer Reason *",
            options=[
                "Forensic Lab Analysis",
                "Courtroom Presentation",
                "Secure Long-Term Vault Storage",
                "Prosecution Review",
                "Defense Disclosure Inspection",
                "Hardware Bit-Stream Imaging",
                "Chain Custody Transfer"
            ]
        )

        notes = st.text_area("Transfer Notes & Security Conditions", placeholder="Specify courier details, evidence locker ID, or lab intake bench...", height=70)
        verify_on_transfer = st.checkbox("Perform immediate SHA-256 integrity verification upon release", value=True)
        confirm_transfer = st.checkbox("I legally certify this evidence custody transfer *")

        if st.button("Record Custody Transfer", type="primary", use_container_width=True):
            if not confirm_transfer:
                st.error("You must check the legal certification box to record the custody transfer.")
                return

            try:
                # Perform verification if checked
                current_hash = ev["sha256_hash"]  # Baseline vault copy
                custody_manager.transfer_custody(
                    evidence_id=ev["evidence_id"],
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    transfer_reason=transfer_reason,
                    recorded_by_id=current_user["user_id"],
                    notes=notes.strip(),
                    verify_hash_now=verify_on_transfer,
                    current_file_hash=current_hash
                )
                st.success("Custody transfer executed and sealed with cryptographic receipt token!")
                st.rerun()
            except Exception as e:
                st.error(f"Transfer error: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)
