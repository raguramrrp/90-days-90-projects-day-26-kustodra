"""
KUSTODRA - Integrity Laboratory Page
Dedicated cryptographic verification workspace:
- Select cataloged artifact
- Select verification source (Vault baseline, Upload, Benchmark Specimens)
- Calculate SHA-256 and constant-time comparison
- Side-by-side comparison panel (Registered vs Calculated)
- Highlight diffs on mismatch
- Record permanent verification history
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st
import pandas as pd

from kustodra.database import DatabaseManager, get_iso_now
from kustodra.core.crypto_engine import CryptoEngine
from kustodra.core.audit_engine import AuditEngine
from kustodra.ui.components import render_header, render_hash_view, get_status_badge_html


def render_page(db: DatabaseManager, current_user: dict, samples_dir: Path) -> None:
    """Render the Integrity Laboratory workspace."""
    render_header(
        title="Integrity Lab",
        current_user=current_user,
        show_import=False,
        breadcrumb="CRYPTOGRAPHIC VERIFICATION"
    )

    all_evidence = db.get_evidence_list()
    if not all_evidence:
        st.info("No artifacts cataloged yet. Ingest an item first to perform verification.")
        return

    selected_id = st.session_state.get("selected_evidence_id", all_evidence[0]["evidence_id"])
    evidence_options = [e["evidence_id"] for e in all_evidence]
    if selected_id not in evidence_options:
        selected_id = evidence_options[0]

    # 1. Artifact Selection
    with st.container(border=True):
        st.markdown("#### 1. Target Artifact Reference")
        col_s1, col_s2 = st.columns([3, 2])
        with col_s1:
            chosen_id = st.selectbox(
                "Select Cataloged Artifact Item",
                options=evidence_options,
                index=evidence_options.index(selected_id),
                format_func=lambda x: f"{x} — {[e['title'] for e in all_evidence if e['evidence_id'] == x][0]} ({[e['original_filename'] for e in all_evidence if e['evidence_id'] == x][0]})"
            )
            if chosen_id != selected_id:
                st.session_state["selected_evidence_id"] = chosen_id
                st.rerun()

        ev = db.get_evidence_by_id(chosen_id)
        with col_s2:
            st.markdown(f"**Current Status:** {get_status_badge_html(ev['integrity_status'])}", unsafe_allow_html=True)
            last_v = ev.get('last_verified_at', 'Never')[:19].replace('T', ' ') if ev.get('last_verified_at') else 'Never'
            st.markdown(f"**Last Verified:** `{last_v} UTC`")

    # 2. Comparison Source Selection
    with st.container(border=True):
        st.markdown("#### 2. Comparison Source")

        verif_mode = st.segmented_control(
            "Source Mode",
            options=[
                "Vault Stored Copy",
                "Upload External Copy",
                "Validation Benchmark Suite"
            ],
            default="Vault Stored Copy",
            label_visibility="collapsed"
        )

        file_bytes_to_verify: bytes | None = None
        source_label = ""

        if verif_mode == "Vault Stored Copy" or "Vault Stored" in (verif_mode or ""):
            storage_path_str = ev.get("storage_rel_path") or ev.get("storage_path")
            vault_path = DatabaseManager.resolve_file_path(storage_path_str)
            if vault_path and vault_path.is_file():
                source_label = f"Vault Archive: {vault_path.name}"
                st.caption(f"✓ Secure vault copy verified: `{vault_path.name}` ({vault_path.stat().st_size:,} Bytes)")
                file_bytes_to_verify = vault_path.read_bytes()
            else:
                st.error("Vault archive file not accessible at registered storage path.")

        elif verif_mode == "Upload External Copy" or "Upload" in (verif_mode or ""):
            uploaded_verify = st.file_uploader(
                "Upload file instance for cryptographic verification",
                type=None,
                label_visibility="collapsed"
            )
            if uploaded_verify:
                source_label = f"External File: {uploaded_verify.name}"
                file_bytes_to_verify = uploaded_verify.getvalue()
                st.caption(f"Loaded instance: `{uploaded_verify.name}` ({len(file_bytes_to_verify):,} Bytes)")

        elif verif_mode == "Validation Benchmark Suite" or "Benchmark" in (verif_mode or ""):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                if st.button("Load Authentic Sample (server_access_log.log)", use_container_width=True):
                    sample_file = samples_dir / "server_access_log.log"
                    if sample_file.is_file():
                        st.session_state["sample_verify_bytes"] = sample_file.read_bytes()
                        st.session_state["sample_verify_name"] = "server_access_log.log (Authentic)"
            with col_d2:
                if st.button("Load Tampered Sample (tampered_server_log.log)", use_container_width=True):
                    sample_file = samples_dir / "tampered_server_log.log"
                    if sample_file.is_file():
                        st.session_state["sample_verify_bytes"] = sample_file.read_bytes()
                        st.session_state["sample_verify_name"] = "tampered_server_log.log (Tampered)"

            if "sample_verify_bytes" in st.session_state:
                file_bytes_to_verify = st.session_state["sample_verify_bytes"]
                source_label = st.session_state["sample_verify_name"]
                st.caption(f"Active Sample: **{source_label}** ({len(file_bytes_to_verify):,} Bytes)")

    # 3. Verification Execution & Hash Comparison Panel
    if file_bytes_to_verify is not None:
        with st.container(border=True):
            st.markdown("#### 3. Cryptographic Fingerprint Comparison")

            calc_hashes = CryptoEngine.calculate_hashes_from_bytes(file_bytes_to_verify)
            calc_sha256 = calc_hashes["sha256"]
            registered_sha256 = ev["sha256_hash"]

            # Constant-time comparison
            is_match = CryptoEngine.verify_sha256_constant_time(file_bytes_to_verify, registered_sha256)

            # Two-Column Comparison Display
            col_left_hash, col_right_hash = st.columns(2)
            with col_left_hash:
                st.markdown("<div class='tv-compare-panel'>", unsafe_allow_html=True)
                st.markdown("**REGISTERED SHA-256 FINGERPRINT (REFERENCE)**")
                st.code(registered_sha256, language=None)
                st.caption(f"Baseline Size: {ev['file_size_bytes']:,} Bytes &bull; Ingested: {ev['created_at'][:10]}")
                st.markdown("</div>", unsafe_allow_html=True)

            with col_right_hash:
                st.markdown("<div class='tv-compare-panel'>", unsafe_allow_html=True)
                st.markdown("**CALCULATED SHA-256 FINGERPRINT (INSTANCE)**")
                st.code(calc_sha256, language=None)
                st.caption(f"Instance Size: {len(file_bytes_to_verify):,} Bytes &bull; Source: {source_label}")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            # Match / Mismatch Result State
            if is_match:
                st.markdown("""
                <div class="tv-diff-match">
                    <div style="font-size: 15px; font-weight: 700; letter-spacing: 0.5px;">&#x2713; INTEGRITY MATCH</div>
                    <div style="font-size: 13px; margin-top: 4px;">
                        The calculated SHA-256 fingerprint matches the registered reference. The evidence bitstream is authentic and unmodified.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="tv-diff-mismatch">
                    <div style="font-size: 15px; font-weight: 700; letter-spacing: 0.5px;">&#x26A0; INTEGRITY MISMATCH</div>
                    <div style="font-size: 13px; margin-top: 4px;">
                        The calculated fingerprint differs from the registered reference. The file contents are not identical.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Show character-level mismatch locator
                mismatch_indices = [i for i in range(len(registered_sha256)) if registered_sha256[i] != calc_sha256[i]]
                st.caption(f"**Cryptographic Divergence:** {len(mismatch_indices)} of 64 hexadecimal characters differ. First mismatch at nibble #{mismatch_indices[0] if mismatch_indices else 'N/A'}.")

            # Record Verification Action
            col_save1, col_save2 = st.columns([3, 1])
            with col_save1:
                st.caption(f"Examiner: **{current_user.get('full_name', 'Forensic Examiner')}** &bull; Timestamp: **{get_iso_now()} UTC**")
            with col_save2:
                if st.button("Record Verification to Ledger", type="primary", use_container_width=True):
                    res_status = "Match" if is_match else "Mismatch"
                    db.record_integrity_check({
                        "evidence_id": chosen_id,
                        "checked_by_id": current_user.get("user_id", "USR-101"),
                        "expected_sha256": registered_sha256,
                        "calculated_sha256": calc_sha256,
                        "result_status": res_status,
                        "check_mode": source_label or "Laboratory Verification",
                        "details": f"Verification against {source_label}: result was {res_status}."
                    })

                    audit = AuditEngine(db)
                    event_type = "INTEGRITY_CHECK_MATCH" if is_match else "INTEGRITY_CHECK_MISMATCH"
                    audit.log_event(
                        event_type=event_type,
                        user_id=current_user.get("user_id", "USR-101"),
                        evidence_id=chosen_id,
                        details=f"SHA-256 verification against {source_label}: {res_status}. Calculated digest: {calc_sha256[:16]}..."
                    )
                    st.success("Verification check permanently recorded to immutable SQLite ledger!")
                    st.rerun()

    # 4. Historical Verification Ledger
    with st.container(border=True):
        st.markdown("#### 4. Historical Verification Ledger")

        checks = db.get_integrity_checks_for_evidence(chosen_id)
        if checks:
            check_table = []
            for c in checks:
                calc_hash = c.get("calculated_sha256", "")
                hash_snip = f"{calc_hash[:16]}...{calc_hash[-8:]}" if len(calc_hash) > 24 else calc_hash
                check_table.append({
                    "Timestamp (UTC)": str(c.get("check_timestamp", ""))[:19].replace("T", " "),
                    "Examiner": c.get("checked_by_name") or c.get("checked_by_id", "Examiner"),
                    "Mode / Source": c.get("check_mode", "Baseline"),
                    "Result": c.get("result_status", "Unknown"),
                    "Calculated SHA-256": hash_snip
                })
            df_hist = pd.DataFrame(check_table)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("No prior verification records for this artifact.")
