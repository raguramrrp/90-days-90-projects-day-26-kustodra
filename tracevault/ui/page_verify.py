"""
TRACEVAULT - Integrity Verification Page
Dedicated verification workspace. Calculates current SHA-256 digest,
compares with baseline intake hash, determines Match/Mismatch states, and records audit logs.
"""

from __future__ import annotations
import uuid
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st
import pandas as pd

from tracevault.database import DatabaseManager, get_iso_now
from tracevault.core.crypto_engine import CryptoEngine
from tracevault.core.audit_engine import AuditEngine
from tracevault.ui.components import render_hash_view, get_status_badge_html


def render_page(db: DatabaseManager, current_user: dict, samples_dir: Path) -> None:
    """Render the Integrity Verification Workspace."""
    st.markdown("### Integrity Verification")
    st.markdown("<p style='font-size: 13px; color: #68736F; margin-top: -8px; margin-bottom: 16px;'>Cryptographic file comparison engine. Calculate current SHA-256 hashes against immutable registration baselines.</p>", unsafe_allow_html=True)

    all_evidence = db.get_evidence_list()
    if not all_evidence:
        st.info("No evidence registered yet. Register an item first to perform verification.")
        return

    selected_id = st.session_state.get("selected_evidence_id", all_evidence[0]["evidence_id"])
    evidence_options = [e["evidence_id"] for e in all_evidence]
    if selected_id not in evidence_options:
        selected_id = evidence_options[0]

    # 1. Select Evidence
    with st.container(border=True):
        st.markdown("#### 1. Select Registered Evidence")
        col_s1, col_s2 = st.columns([3, 2])
        with col_s1:
            chosen_id = st.selectbox(
                "Registered Evidence Item",
                options=evidence_options,
                index=evidence_options.index(selected_id),
                format_func=lambda x: f"{x} — {[e['title'] for e in all_evidence if e['evidence_id'] == x][0]} ({[e['original_filename'] for e in all_evidence if e['evidence_id'] == x][0]})"
            )
            if chosen_id != selected_id:
                st.session_state["selected_evidence_id"] = chosen_id
                st.rerun()

        ev = db.get_evidence_by_id(chosen_id)
        with col_s2:
            status_html = get_status_badge_html(ev['integrity_status'])
            st.markdown(f"**Current Status:** {status_html}", unsafe_allow_html=True)
            last_v = ev.get('last_verified_at', 'Never')[:19].replace('T', ' ') if ev.get('last_verified_at') else 'Never'
            st.markdown(f"**Last Verified:** {last_v}")

    # 2. Select Verification Source
    with st.container(border=True):
        st.markdown("#### 2. Select File Source to Verify")
        verif_mode = st.radio(
            "Verification Source Mode",
            options=[
                "Verify Stored Vault Copy (Test local vault storage bit-rot/tampering)",
                "Upload File to Verify (Test external copy, thumb drive, or opposing exhibit)",
                "Forensic Sample Test (Load clean or tampered sample for instant testing)"
            ],
            index=0
        )

        file_bytes_to_verify: bytes | None = None
        source_name = ""

        if "Stored Vault Copy" in verif_mode:
            vault_path = Path(ev["storage_rel_path"])
            if vault_path.is_file():
                source_name = f"Vault Storage: {vault_path.name}"
                st.caption(f"Located stored vault file: `{vault_path.name}` ({vault_path.stat().st_size:,} Bytes)")
                with open(vault_path, "rb") as f:
                    file_bytes_to_verify = f.read()
            else:
                st.error(f"Vault storage file not found at path: {vault_path}")

        elif "Upload File to Verify" in verif_mode:
            uploaded_verify = st.file_uploader(
                "Upload local file to compare against registered hash",
                type=None,
                label_visibility="collapsed"
            )
            if uploaded_verify:
                source_name = f"Uploaded File: {uploaded_verify.name}"
                file_bytes_to_verify = uploaded_verify.getvalue()
                st.caption(f"Loaded: `{uploaded_verify.name}` ({len(file_bytes_to_verify):,} Bytes)")

        elif "Forensic Sample Test" in verif_mode:
            st.caption("Select a sample file to test Match vs Mismatch states:")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                if st.button("Load Authentic Sample (server_access_log.log)", use_container_width=True):
                    sample_file = samples_dir / "server_access_log.log"
                    if sample_file.is_file():
                        st.session_state["demo_sample_bytes"] = sample_file.read_bytes()
                        st.session_state["demo_sample_name"] = "server_access_log.log (Authentic)"
                        st.rerun()
            with col_d2:
                if st.button("Load Tampered Sample (tampered_server_log.log)", use_container_width=True):
                    sample_file = samples_dir / "tampered_server_log.log"
                    if sample_file.is_file():
                        st.session_state["demo_sample_bytes"] = sample_file.read_bytes()
                        st.session_state["demo_sample_name"] = "tampered_server_log.log (Scrubbed IP / Modified)"
                        st.rerun()

            if "demo_sample_bytes" in st.session_state:
                file_bytes_to_verify = st.session_state["demo_sample_bytes"]
                source_name = st.session_state.get("demo_sample_name", "Forensic Sample")
                st.info(f"Loaded: **{source_name}** ({len(file_bytes_to_verify):,} Bytes)")

    # 3. Execute Verification
    if file_bytes_to_verify is not None:
        with st.container(border=True):
            st.markdown("#### 3. Execute Verification")

            if st.button("Calculate Current SHA-256 & Compare", type="primary"):
                hashes = CryptoEngine.calculate_hashes_from_bytes(file_bytes_to_verify)
                calc_sha256 = hashes["sha256"]
                expected_sha256 = ev["sha256_hash"]

                is_match = CryptoEngine.verify_hash(expected_sha256, calc_sha256)
                timestamp = get_iso_now()
                check_id = f"CHK-{uuid.uuid4().hex[:8].upper()}"

                result_status = "Match" if is_match else "Mismatch"
                tamper_details = None if is_match else f"Calculated SHA-256 differs. Source: {source_name}."

                db.add_integrity_check({
                    "check_id": check_id,
                    "evidence_id": ev["evidence_id"],
                    "checked_by_id": current_user["user_id"],
                    "check_timestamp": timestamp,
                    "expected_sha256": expected_sha256,
                    "calculated_sha256": calc_sha256,
                    "result_status": result_status,
                    "tamper_details": tamper_details,
                    "check_mode": verif_mode.split("(")[0].strip(),
                    "notes": f"Verification performed by {current_user['full_name']}. Source: {source_name}."
                })

                audit = AuditEngine(db)
                event_type = "INTEGRITY_CHECK_MATCH" if is_match else "INTEGRITY_CHECK_MISMATCH"
                audit.log_event(
                    event_type=event_type,
                    user_id=current_user["user_id"],
                    evidence_id=ev["evidence_id"],
                    details=f"Verification result: {result_status.upper()} for {ev['evidence_id']}. Expected: {expected_sha256[:16]}... Calculated: {calc_sha256[:16]}..."
                )

                st.session_state["last_verification_result"] = {
                    "check_id": check_id,
                    "is_match": is_match,
                    "expected": expected_sha256,
                    "calculated": calc_sha256,
                    "timestamp": timestamp,
                    "source": source_name
                }
                st.rerun()

    # 4. Result Display
    last_res = st.session_state.get("last_verification_result")
    if last_res:
        with st.container(border=True):
            st.markdown("#### Verification Result")

            if last_res["is_match"]:
                st.success(f"""
                **MATCH CONFIRMED**
                
                The calculated SHA-256 hash matches the registered hash.  
                The file contents are identical to the registered baseline version.
                
                - **Verification Reference:** `{last_res['check_id']}`
                - **Timestamp:** {last_res['timestamp'][:19].replace('T', ' ')} UTC
                - **Source Tested:** {last_res['source']}
                """)
            else:
                st.error(f"""
                **INTEGRITY MISMATCH DETECTED**
                
                The calculated SHA-256 hash does not match the registered hash.  
                The file contents differ from the registered baseline version.
                
                - **Verification Reference:** `{last_res['check_id']}`
                - **Alert:** Integrity Mismatch logged to audit ledger
                - **Source Tested:** {last_res['source']}
                """)

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                render_hash_view(last_res["expected"], label="EXPECTED SHA-256 (INTAKE BASELINE)")
            with col_c2:
                render_hash_view(last_res["calculated"], label="CALCULATED SHA-256 (PAYLOAD TESTED)")

    # 5. History Table
    with st.container(border=True):
        st.markdown(f"#### Verification History for {ev['evidence_id']}")
        checks = db.get_integrity_checks_for_evidence(ev["evidence_id"])
        if checks:
            chk_rows = []
            for c in checks:
                chk_rows.append({
                    "Timestamp": c["check_timestamp"][:19].replace("T", " "),
                    "Examiner": c.get("checked_by_name", c["checked_by_id"]),
                    "Mode": c.get("check_mode", "Upload"),
                    "Result": c["result_status"],
                    "Calculated Hash": c["calculated_sha256"][:24] + "..."
                })
            st.dataframe(pd.DataFrame(chk_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No verification checks recorded yet for this item.")
