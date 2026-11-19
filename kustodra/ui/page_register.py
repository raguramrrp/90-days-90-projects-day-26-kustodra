"""
KUSTODRA - Intake & Ingestion Page
Controlled artifact intake workflow:
- File Acquisition & Magic Header Inspection
- Artifact Metadata & Case Context
- Live Cryptographic Fingerprinting (SHA-256, MD5, SHA-1, Shannon Entropy)
- Review & Seal into KUSTODRA Vault
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st

from kustodra.database import DatabaseManager, get_iso_now
from kustodra.core.crypto_engine import CryptoEngine
from kustodra.core.metadata_inspector import MetadataInspector
from kustodra.core.forensic_analyzer import ForensicAnalyzer
from kustodra.core.audit_engine import AuditEngine
from kustodra.ui.components import render_header, render_hash_view


def render_page(db: DatabaseManager, current_user: dict, vault_dir: Path) -> None:
    """Render the controlled Artifact Intake sequence."""
    render_header(
        title="Intake & Ingestion",
        current_user=current_user,
        show_import=False,
        breadcrumb="INGESTION & HASHING"
    )

    # Section A — File Acquisition
    with st.container(border=True):
        st.markdown("#### 1. Artifact Acquisition")

        uploaded_file = st.file_uploader(
            "Acquire Digital Artifact",
            type=None,
            label_visibility="collapsed"
        )

        if not uploaded_file:
            st.info("Select or drag a digital evidence file to acquire its bitstream.")
            return

        file_bytes = uploaded_file.getvalue()
        file_size = len(file_bytes)
        file_ext = Path(uploaded_file.name).suffix.lower() or "None"

        # Immediate Hashing & File Inspection
        hashes = CryptoEngine.calculate_hashes_from_bytes(file_bytes)
        entropy = CryptoEngine.calculate_shannon_entropy(file_bytes)
        meta = MetadataInspector.inspect_file(file_bytes, uploaded_file.name)
        classification = ForensicAnalyzer.classify_evidence(
            filename=uploaded_file.name,
            signature_id=meta["signature_id"],
            mime_type=meta["mime_type"],
            entropy=entropy,
            file_size=file_size
        )

        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        with col_a1:
            st.metric("Filename", uploaded_file.name)
        with col_a2:
            st.metric("Reported Ext", file_ext)
        with col_a3:
            st.metric("Detected MIME", meta["mime_type"])
        with col_a4:
            st.metric("File Size", meta["file_size_formatted"])

        st.caption(f"**Acquisition Status:** Processed {file_size:,} bytes &bull; Magic Header: <code>{meta['magic_signature']}</code>")

        if meta["is_spoofed"]:
            st.warning(f"⚠️ Header Divergence Alert: {meta['spoof_warning']} (Extension does not confirm true file identity)")

        duplicates = db.find_duplicates_by_hash(hashes["sha256"])
        if duplicates:
            st.warning(f"⚠️ Duplicate Hash Detected: Identical bitstream already exists in Case {duplicates[0]['case_id']} as Record {duplicates[0]['evidence_id']}.")

    # Section B — Artifact Context
    with st.container(border=True):
        st.markdown("#### 2. Artifact Context & Case Reference")

        cases = db.get_cases()
        case_options = {c["case_id"]: f"{c['case_id']} — {c['case_title']}" for c in cases}
        case_ids = list(case_options.keys())

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            selected_case = st.selectbox(
                "Case Reference *",
                options=case_ids,
                format_func=lambda cid: case_options.get(cid, cid)
            )
            evidence_title = st.text_input(
                "Artifact Title *",
                value=Path(uploaded_file.name).stem.replace("_", " ").title()
            )
            category_options = [
                "System & Audit Log",
                "Forensic Still Image",
                "Surveillance Video",
                "Digital Document",
                "Audio Recording",
                "Forensic Disk Image",
                "Encrypted / Packed Payload",
                "Compressed / Encrypted Archive",
                "Executable / Malware Artifact"
            ]
            default_cat = classification["category"] if classification["category"] in category_options else category_options[0]
            evidence_category = st.selectbox(
                "Artifact Category *",
                options=category_options,
                index=category_options.index(default_cat)
            )

        with col_b2:
            collected_by = st.text_input("Collected By *", value=current_user.get("full_name", "Forensic Examiner"))
            collection_date = st.date_input("Collection Date *", value=datetime.now(timezone.utc).date())
            collection_location = st.text_input("Collection Location / Device", placeholder="E.g. Primary Server Rack 3 / Suspect Workstation")

        description = st.text_area(
            "Artifact Description",
            placeholder="Detailed description of artifact context, chain of seizure, or initial observations...",
            height=70
        )
        notes = st.text_input("Operational Notes", placeholder="E.g. Write-blocker used during acquisition")

    # Section C — Cryptographic Fingerprint & Vault Sealing
    with st.container(border=True):
        st.markdown("#### 3. Cryptographic Baseline & Sealing")

        render_hash_view(hashes["sha256"], label="SHA-256 Digest (Reference Baseline)")

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown("<span style='font-size: 11px; font-weight: 600; color: #527C78;'>MD5 DIGEST</span>", unsafe_allow_html=True)
            st.code(hashes["md5"], language=None)
        with col_c2:
            st.markdown("<span style='font-size: 11px; font-weight: 600; color: #527C78;'>SHA-1 DIGEST</span>", unsafe_allow_html=True)
            st.code(hashes["sha1"], language=None)
        with col_c3:
            st.markdown("<span style='font-size: 11px; font-weight: 600; color: #527C78;'>SHANNON ENTROPY</span>", unsafe_allow_html=True)
            st.code(f"{entropy:.4f} / 8.0000 bits/byte", language=None)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if st.button("Seal Artifact into Vault", type="primary", use_container_width=True):
            if not evidence_title.strip():
                st.error("Artifact Title is required.")
                return

            with st.spinner("Sealing artifact into KUSTODRA vault and generating custody token..."):
                evidence_id = db.generate_artifact_id()
                vault_dir.mkdir(parents=True, exist_ok=True)
                safe_name = f"{evidence_id}_{uploaded_file.name}"
                dest_path = vault_dir / safe_name
                dest_path.write_bytes(file_bytes)

                db.create_evidence({
                    "evidence_id": evidence_id,
                    "case_id": selected_case,
                    "title": evidence_title.strip(),
                    "category": evidence_category,
                    "description": description.strip(),
                    "original_filename": uploaded_file.name,
                    "file_size_bytes": file_size,
                    "mime_type": meta["mime_type"],
                    "sha256_hash": hashes["sha256"],
                    "md5_hash": hashes["md5"],
                    "sha1_hash": hashes["sha1"],
                    "shannon_entropy": entropy,
                    "storage_path": str(dest_path),
                    "storage_rel_path": f"data/vault_storage/{safe_name}",
                    "current_custodian_id": current_user.get("user_id", "USR-101"),
                    "collected_by": collected_by.strip(),
                    "collection_date": str(collection_date),
                    "collection_location": collection_location.strip(),
                    "integrity_status": "Verified",
                    "registered_by_id": current_user.get("user_id", "USR-101"),
                    "notes": notes.strip()
                })

                # Log initial custody receipt
                db.add_custody_log({
                    "evidence_id": evidence_id,
                    "sender_id": current_user.get("user_id", "USR-101"),
                    "receiver_id": current_user.get("user_id", "USR-101"),
                    "transfer_reason": "Initial Seizure & Intake Ingestion",
                    "recorded_by_id": current_user.get("user_id", "USR-101"),
                    "signature_token": CryptoEngine.generate_custody_receipt_token(
                        evidence_id, current_user.get("user_id", "USR-101"), current_user.get("user_id", "USR-101"), hashes["sha256"]
                    ),
                    "notes": "Artifact bitstream ingested and sealed in KUSTODRA vault.",
                    "integrity_verified_on_transfer": 1
                })

                # Initial baseline integrity check
                db.record_integrity_check({
                    "evidence_id": evidence_id,
                    "checked_by_id": current_user.get("user_id", "USR-101"),
                    "expected_sha256": hashes["sha256"],
                    "calculated_sha256": hashes["sha256"],
                    "result_status": "Match",
                    "check_mode": "Baseline Intake Verification",
                    "details": "Cryptographic fingerprint confirmed matching at intake."
                })

                # Audit log entry
                audit = AuditEngine(db)
                audit.log_event(
                    event_type="ARTIFACT_INGESTED",
                    user_id=current_user.get("user_id", "USR-101"),
                    evidence_id=evidence_id,
                    details=f"Artifact {evidence_id} ingested into KUSTODRA vault with SHA-256 {hashes['sha256'][:16]}... by {current_user.get('full_name', 'Forensic Examiner')}."
                )

                st.session_state["just_registered_id"] = evidence_id

    # Post-Registration Notification & Quick Navigate
    if "just_registered_id" in st.session_state:
        reg_id = st.session_state["just_registered_id"]
        st.success(f"✅ Digital Artifact successfully ingested in KUSTODRA with ID: **{reg_id}**")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button("Inspect Artifact Details →", type="primary", use_container_width=True):
                st.session_state["selected_evidence_id"] = reg_id
                st.session_state["active_nav"] = "Artifact Inspector"
                del st.session_state["just_registered_id"]
                st.rerun()
        with col_g2:
            if st.button("Go to Artifact Vault →", type="secondary", use_container_width=True):
                st.session_state["active_nav"] = "Artifact Vault"
                del st.session_state["just_registered_id"]
                st.rerun()
