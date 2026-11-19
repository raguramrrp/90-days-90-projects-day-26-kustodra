"""
TRACEVAULT - Chain of Custody Page
Forensic ledger tracking possession and transfer history of digital evidence.
Provides chronological ledger timeline, cryptographic handover receipts, and custody transfer authorization.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd

from tracevault.database import DatabaseManager
from tracevault.core.custody_manager import CustodyManager
from tracevault.ui.components import get_status_badge_html


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Chain of Custody ledger and transfer workflow."""
    st.markdown("### Chain of Custody")
    st.caption("Review the documented possession and transfer history of digital evidence.")

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

    # 1. Current Legal Custodian Banner
    with st.container(border=True):
        col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
        with col_c1:
            st.caption("CURRENT ACTIVE CUSTODIAN")
            custodian_name = ev.get("custodian_name") or ev.get("current_custodian_id", "Unknown")
            custodian_role = ev.get("custodian_role", "Evidence Custodian")
            st.markdown(f"**{custodian_name}**")
            st.caption(f"Role: {custodian_role} &bull; Org: {ev.get('custodian_org', 'Evidence Management Unit')}")

        with col_c2:
            st.caption("EVIDENCE IDENTIFIER")
            st.markdown(f"**{ev['evidence_id']}** &mdash; {ev['title']}")
            st.caption(f"Original file: `{ev['original_filename']}` ({ev['file_size_bytes']:,} Bytes)")

        with col_c3:
            st.caption("INTEGRITY STATUS")
            st.markdown(get_status_badge_html(ev['integrity_status']), unsafe_allow_html=True)

    col_tl, col_trans = st.columns([3, 2])

    # 2. Chronological Possession Ledger (Left Column)
    with col_tl:
        with st.container(border=True):
            st.markdown("#### Chronological Custody Ledger")
            st.caption("Documented historical sequence of releases, receipts, and custody handovers.")

            # Seizure / Intake Initial Entry
            with st.container(border=True):
                st.markdown(f"**Event #0: Initial Seizure & Registration** &bull; `{ev['collection_date']}`")
                st.caption(
                    f"Collected by **{ev['collected_by']}** at *{ev.get('collection_location') or 'Field Location'}*.\n"
                    f"Ingested into vault archive by **{ev.get('registered_by_name', ev['registered_by_id'])}**."
                )

            # Historical Transfers
            if timeline:
                for idx, log in enumerate(timeline):
                    with st.container(border=True):
                        time_str = log["transfer_timestamp"][:19].replace("T", " ")
                        sender = log.get("sender_name") or log.get("sender_id", "Sender")
                        receiver = log.get("receiver_name") or log.get("receiver_id", "Receiver")
                        reason = log.get("transfer_reason", "Transfer")
                        token = log.get("signature_token", "")
                        token_snip = f"{token[:16]}..." if token else "N/A"

                        st.markdown(f"**Event #{idx + 1}: {sender} &rarr; {receiver}**")
                        st.caption(f"Timestamp: `{time_str} UTC` &bull; Reason: **{reason}**")

                        if log.get("notes"):
                            st.write(f"_{log['notes']}_")

                        if log.get("integrity_verified_on_transfer"):
                            st.caption("✅ Integrity verified during transfer")

                        st.caption(f"Cryptographic Receipt Token: `{token_snip}`")
            else:
                st.info("No transfers recorded. Evidence remains with initial collecting custodian.")

    # 3. Transfer Custody Action Panel (Right Column)
    with col_trans:
        with st.container(border=True):
            st.markdown("#### Record Custody Transfer")
            st.caption("Document and authorize legal evidence release to another registered custodian.")

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
                st.warning("No alternative registered custodians available to receive custody.")
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

            notes = st.text_area("Transfer Notes", placeholder="E.g. Handover locker ID, courier pouch tracking...", height=70)
            verify_on_transfer = st.checkbox("Verify SHA-256 integrity on release", value=True)
            confirm_transfer = st.checkbox("I authorize and certify this legal custody transfer *")

            if st.button("Authorize Transfer", type="primary", use_container_width=True):
                if not confirm_transfer:
                    st.error("Transfer authorization confirmation is required.")
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
                    st.success("Custody transfer executed and sealed with cryptographic receipt token!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Transfer error: {e}")
