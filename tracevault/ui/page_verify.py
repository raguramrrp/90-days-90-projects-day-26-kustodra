"""
TRACEVAULT - Integrity Verification Page
Dedicated verification engine. Calculates current SHA-256 digest, compares with
baseline intake hash, determines Match/Mismatch states, and records audit logs.
"""

from __future__ import annotations
import uuid
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st

from tracevault.database import DatabaseManager, get_iso_now
from tracevault.core.crypto_engine import CryptoEngine
from tracevault.core.audit_engine import AuditEngine
from tracevault.ui.components import render_hash_view, render_status_badge


def render_page(db: DatabaseManager, current_user: dict, samples_dir: Path) -> None:
    """Render the Integrity Verification Workspace."""
    st.markdown("### Integrity Verification")
    st.markdown("<div style='font-size: 13px; color: #68736F; margin-bottom: 16px;'>Cryptographic file comparison engine. Calculate current SHA-256 hashes against immutable registration baselines.</div>", unsafe_allow_html=True)

    all_evidence = db.get_evidence_list()
    if not all_evidence:
        st.info("No evidence registered yet. Register an item first to perform verification.")
        return

    selected_id = st.session_state.get("selected_evidence_id")
    evidence_options = [e["evidence_id"] for e in all_evidence]
    if not selected_id or selected_id not in evidence_options:
        selected_id = evidence_options[0]

    # Evidence Selection Card
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">1. Select Registered Evidence</div>
                <div class="tv-card-subtitle">Choose the evidence record to test for bitstream integrity</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([3, 2])
    with col_s1:
        chosen_id = st.selectbox(
            "Registered Evidence Item",
            options=evidence_options,
            index=evidence_options.index(selected_id) if selected_id in evidence_options else 0,
            format_func=lambda x: f"{x} &mdash; {[e['title'] for e in all_evidence if e['evidence_id'] == x][0]} ({[e['original_filename'] for e in all_evidence if e['evidence_id'] == x][0]})"
        )
        if chosen_id != selected_id:
            st.session_state["selected_evidence_id"] = chosen_id
            st.rerun()

    ev = db.get_evidence_by_id(chosen_id)
    with col_s2:
        st.markdown(f"**Current Status:** {render_status_badge(ev['integrity_status'])}", unsafe_allow_html=True)
        st.markdown(f"**Last Verified:** {ev.get('last_verified_at', 'Never')[:19].replace('T', ' ') if ev.get('last_verified_at') else 'Never'}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Verification Source Mode
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">2. Select Verification Source</div>
                <div class="tv-card-subtitle">Choose file payload source to calculate current SHA-256 hash</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    verif_mode = st.radio(
        "Verification Mode",
        options=[
            "Verify Stored Vault Copy (Test local vault storage bit-rot/tampering)",
            "Upload File to Verify (Test external copy, thumb drive, or opposing counsel exhibit)",
            "Forensic Sample Test (Load clean or tampered sample for instant demonstration)"
        ],
        index=0
    )

    file_bytes_to_verify: bytes | None = None
    verification_source_name = ""

    if "Stored Vault Copy" in verif_mode:
        vault_path = Path(ev["storage_rel_path"])
        if vault_path.is_file():
            verification_source_name = f"Vault Storage: {vault_path.name}"
            st.success(f"Located stored vault file: `{vault_path.resolve()}` ({vault_path.stat().st_size:,} Bytes)")
            with open(vault_path, "rb") as f:
                file_bytes_to_verify = f.read()
        else:
            st.error(f"Vault storage file not found at path: {vault_path}")

    elif "Upload File to Verify" in verif_mode:
        uploaded_verify_file = st.file_uploader(
            "Select local file to compare against registered evidence hash",
            type=None,
            help="Upload the file you wish to verify against this evidence record's baseline."
        )
        if uploaded_verify_file:
            verification_source_name = f"Uploaded File: {uploaded_verify_file.name}"
            file_bytes_to_verify = uploaded_verify_file.getvalue()
            st.info(f"Loaded: `{uploaded_verify_file.name}` ({len(file_bytes_to_verify):,} Bytes)")

    elif "Forensic Sample Test" in verif_mode:
        st.markdown("<div style='font-size: 12px; color: #4A5653; margin-bottom: 8px;'>Select a pre-configured sample to test Match or Mismatch states immediately:</div>", unsafe_allow_html=True)
        col_demo1, col_demo2 = st.columns(2)
        with col_demo1:
            if st.button("Load Authentic Sample (server_access_log.log)", use_container_width=True):
                sample_file = samples_dir / "server_access_log.log"
                if sample_file.is_file():
                    st.session_state["demo_sample_bytes"] = sample_file.read_bytes()
                    st.session_state["demo_sample_name"] = "server_access_log.log (Authentic)"
                    st.rerun()
        with col_demo2:
            if st.button("Load Tampered Sample (tampered_server_log.log)", use_container_width=True):
                sample_file = samples_dir / "tampered_server_log.log"
                if sample_file.is_file():
                    st.session_state["demo_sample_bytes"] = sample_file.read_bytes()
                    st.session_state["demo_sample_name"] = "tampered_server_log.log (Scrubbed IP / Modified)"
                    st.rerun()

        if "demo_sample_bytes" in st.session_state:
            file_bytes_to_verify = st.session_state["demo_sample_bytes"]
            verification_source_name = st.session_state.get("demo_sample_name", "Forensic Sample")
            st.info(f"Active Test Payload: **{verification_source_name}** ({len(file_bytes_to_verify):,} Bytes)")

    st.markdown("</div>", unsafe_allow_html=True)

    # Execute Verification Action
    if file_bytes_to_verify is not None:
        st.markdown("""
        <div class="tv-card">
            <div class="tv-card-header">
                <div>
                    <div class="tv-card-title">3. Hash Calculation & Comparison</div>
                    <div class="tv-card-subtitle">Constant-time cryptographic digest verification</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Execute Integrity Verification", type="primary"):
            calculated_hashes = CryptoEngine.calculate_hashes_from_bytes(file_bytes_to_verify)
            calc_sha256 = calculated_hashes["sha256"]
            expected_sha256 = ev["sha256_hash"]

            is_match = CryptoEngine.verify_hash(expected_sha256, calc_sha256)
            timestamp = get_iso_now()
            check_id = f"CHK-{uuid.uuid4().hex[:8].upper()}"

            result_status = "Match" if is_match else "Mismatch"
            tamper_details = None if is_match else f"Calculated SHA-256 differs. Source: {verification_source_name}."

            # Save check to database
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
                "notes": f"Verification performed by {current_user['full_name']}. Source: {verification_source_name}."
            })

            # Record audit event
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
                "source": verification_source_name
            }
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # Display Last Verification Result
    last_res = st.session_state.get("last_verification_result")
    if last_res:
        st.markdown("""
        <div class="tv-card">
            <div class="tv-card-header">
                <div>
                    <div class="tv-card-title">Verification Result</div>
                    <div class="tv-card-subtitle">Official cryptographic determination</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if last_res["is_match"]:
            st.success(f"""
            **MATCH CONFIRMED (100% BIT-LEVEL INTEGRITY)**
            
            The calculated SHA-256 hash matches the registered hash.
            The tested file contents are identical to the baseline registered in the vault.
            
            &bull; **Verification ID:** `{last_res['check_id']}`  
            &bull; **Verified At:** `{last_res['timestamp'][:19].replace('T', ' ')} UTC`  
            &bull; **Source Tested:** `{last_res['source']}`
            """)
        else:
            st.error(f"""
            **INTEGRITY MISMATCH DETECTED (TAMPERING ALERT)**
            
            The calculated SHA-256 hash does not match the registered hash.
            The file contents differ from the registered version.
            
            &bull; **Verification ID:** `{last_res['check_id']}`  
            &bull; **Alert Level:** High Forensic Severity  
            &bull; **Action Taken:** Marked as 'Integrity Mismatch' in vault registry & chained audit log.
            """)

        col_comp1, col_comp2 = st.columns(2)
        with col_comp1:
            render_hash_view(last_res["expected"], label="EXPECTED SHA-256 (REGISTERED BASELINE)")
        with col_comp2:
            render_hash_view(last_res["calculated"], label="CALCULATED SHA-256 (CURRENT FILE PAYLOAD)")

        st.markdown("</div>", unsafe_allow_html=True)

    # Historical Verification Checks Table
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">Verification History for this Record</div>
                <div class="tv-card-subtitle">Log of all prior integrity comparisons executed on {ev['evidence_id']}</div>
            </div>
        </div>
    """.format(ev=ev), unsafe_allow_html=True)

    checks = db.get_integrity_checks_for_evidence(ev["evidence_id"])
    if checks:
        for chk in checks:
            time_str = chk["check_timestamp"][:19].replace("T", " ")
            status_badge = render_status_badge(chk["result_status"])
            st.markdown(f"""
            <div style="border-bottom: 1px solid #E1E6E3; padding: 8px 0; font-size: 12px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <b>{time_str} UTC</b> &bull; Examiner: <b>{chk.get('checked_by_name', chk['checked_by_id'])}</b> &bull; Mode: {chk.get('check_mode', 'N/A')}
                    <div style="font-family: monospace; font-size: 11px; color: #68736F; margin-top: 2px;">
                        Hash: {chk['calculated_sha256'][:24]}... &bull; Notes: {chk.get('notes', 'None')}
                    </div>
                </div>
                <div>{status_badge}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No prior integrity verification checks on file for this evidence item.")

    st.markdown("</div>", unsafe_allow_html=True)
