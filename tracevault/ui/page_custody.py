"""
TRACEVAULT - Chain of Custody Timeline Page
Visual custody timeline and transfer authorization workspace.
Generates cryptographic transfer receipts and updates active custodian.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from datetime import datetime, timezone

from tracevault.database import DatabaseManager, get_iso_now
from tracevault.core.custody_manager import CustodyManager
from tracevault.core.crypto_engine import CryptoEngine


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Chain-of-Custody timeline and transfer workflow."""
    st.markdown("### Chain of Custody")
    st.caption("Forensic possession ledger. Track, transfer, and record legal custody across examiners, investigators, and secure vaults.")

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
        format_func=lambda x: f"{x} — {[e['title'] for e in all_evidence if e['evidence_id'] == x][0]}"
    )
    if chosen_id != selected_id:
        st.session_state["selected_evidence_id"] = chosen_id
        st.rerun()

    ev = db.get_evidence_by_id(chosen_id)
    custody_manager = CustodyManager(db)
    timeline = custody_manager.get_timeline(chosen_id)

    # 1. Active Custodian Summary
    with st.container(border=True):
        col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
        with col_c1:
            st.caption("CURRENT CUSTODIAN")
            custodian_name = ev.get("custodian_name") or ev.get("current_custodian_id", "Unknown")
            custodian_role = ev.get("custodian_role", "Evidence Custodian")
            st.markdown(f"**{custodian_name}**")
            st.caption(f"Role: {custodian_role}")

        with col_c2:
            st.caption("EVIDENCE RECORD")
            st.markdown(f"**{ev['evidence_id']}** — {ev['title']}")
            st.caption(f"Original file: `{ev['original_filename']}` ({ev['file_size_bytes']:,} bytes)")

        with col_c3:
            st.caption("INTEGRITY STATUS")
            status = ev["integrity_status"]
            if status == "Verified":
                st.success(f"● {status}")
            elif status == "Mismatch":
                st.error(f"● {status}")
            else:
                st.warning(f"● {status}")

    col_tl, col_trans = st.columns([3, 2])

    # 2. Chronological Timeline
    with col_tl:
        with st.container(border=True):
            st.markdown("#### Custody Timeline")
            st.caption("Chronological record of custody intake, handovers, and releases.")

            # Baseline Intake
            with st.container(border=True):
                st.markdown(f"**Intake & Initial Registration** &nbsp;·&nbsp; `{ev['collection_date']}`")
                st.caption(
                    f"Collected by **{ev['collected_by']}** from *{ev.get('collection_location') or 'Field Location'}*.\n"
                    f"Registered in vault by **{ev.get('registered_by_name', ev['registered_by_id'])}**."
                )

            # Timeline Events
            if timeline:
                for idx, log in enumerate(timeline):
                    with st.container(border=True):
                        time_str = log["transfer_timestamp"][:19].replace("T", " ")
                        sender = log.get("sender_name") or log.get("sender_id", "N/A")
                        receiver = log.get("receiver_name") or log.get("receiver_id", "N/A")
                        reason = log.get("transfer_reason", "Transfer")
                        token = log.get("signature_token", "")
                        token_snip = f"{token[:16]}..." if token else "N/A"

                        st.markdown(f"**Transfer #{idx + 1}: {sender} ➔ {receiver}**")
                        st.caption(f"Date: `{time_str} UTC` · Reason: **{reason}**")

                        if log.get("notes"):
                            st.write(f"_{log['notes']}_")

                        if log.get("integrity_verified_on_transfer"):
                            st.caption("✅ Integrity verified during transfer")

                        st.caption(f"Receipt Token: `{token_snip}`")
            else:
                st.info("No transfers recorded yet. Evidence remains with initial custodian.")

    # 3. Transfer Custody Form
    with col_trans:
        with st.container(border=True):
            st.markdown("#### Record Transfer")
            st.caption("Transfer evidence to another registered custodian.")

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
                st.warning("No alternative registered custodians available.")
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

            notes = st.text_area("Transfer Notes", placeholder="E.g., Courier details, locker number...", height=70)
            verify_on_transfer = st.checkbox("Verify SHA-256 integrity on transfer", value=True)
            confirm_transfer = st.checkbox("Confirm transfer authorization *")

            if st.button("Record Transfer", type="primary", use_container_width=True):
                if not confirm_transfer:
                    st.error("Please check the confirmation box to authorize this transfer.")
                    return

                try:
                    current_hash = ev["sha256_hash"]
                    custody_manager.transfer_custody(
                        evidence_id=ev["evidence_id"],
                        sender_id=sender_id,
                        receiver_id=receiver_id,
                        transfer_reason=transfer_reason,
                        recorded_by_id=current_user.get("user_id", "USR-101"),
                        notes=notes.strip(),
                        verify_hash_now=verify_on_transfer,
                        current_file_hash=current_hash
                    )
                    st.success("Custody transfer recorded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Transfer error: {e}")
