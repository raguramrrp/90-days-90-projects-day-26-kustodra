"""
TRACEVAULT - Register New Evidence Page
Guided workflow to ingest evidence files, extract forensic metadata,
compute cryptographic digests, detect duplicates, and record initial custody.
"""

from __future__ import annotations
import uuid
import shutil
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st

from tracevault.database import DatabaseManager, get_iso_now
from tracevault.core.crypto_engine import CryptoEngine
from tracevault.core.metadata_inspector import MetadataInspector
from tracevault.core.forensic_analyzer import ForensicAnalyzer
from tracevault.core.audit_engine import AuditEngine
from tracevault.ui.components import render_hash_view


def render_page(db: DatabaseManager, current_user: dict, vault_dir: Path) -> None:
    """Render the Register New Evidence workflow."""
    st.markdown("### Register New Evidence")
    st.markdown("<div style='font-size: 13px; color: #68736F; margin-bottom: 16px;'>Ingest digital artifacts into secure vault custody with automatic SHA-256 hashing and metadata extraction.</div>", unsafe_allow_html=True)

    # 1. Select Evidence File
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">Step 1 &mdash; Select Evidence File</div>
                <div class="tv-card-subtitle">Upload digital file (documents, images, videos, logs, archives, memory dumps)</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Select a file to register as digital evidence",
        type=None,
        help="Any format is supported: image, document, raw packet log, audio, binary payload, or archive.",
        label_visibility="collapsed"
    )

    if not uploaded_file:
        st.info("Select a file from your workstation or drag and drop to begin the registration process.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Compute live hash and inspect metadata from uploaded stream
    file_bytes = uploaded_file.getvalue()
    hashes = CryptoEngine.calculate_hashes_from_bytes(file_bytes)
    entropy = CryptoEngine.calculate_shannon_entropy(file_bytes)
    meta = MetadataInspector.inspect_file(file_bytes, uploaded_file.name)
    classification = ForensicAnalyzer.classify_evidence(
        filename=uploaded_file.name,
        signature_id=meta["signature_id"],
        mime_type=meta["mime_type"],
        entropy=entropy,
        file_size=len(file_bytes)
    )

    # Check for duplicate files in database
    duplicates = db.find_duplicates_by_hash(hashes["sha256"])

    col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
    with col_meta1:
        st.metric("Filename", uploaded_file.name)
    with col_meta2:
        st.metric("File Size", meta["file_size_formatted"])
    with col_meta3:
        st.metric("Detected Header", meta["magic_signature"])
    with col_meta4:
        st.metric("Shannon Entropy", f"{entropy:.2f} / 8.0")

    if meta["is_spoofed"]:
        st.warning(meta["spoof_warning"])

    if duplicates:
        st.warning(f"DUPLICATE DETECTED: This identical file (SHA-256: {hashes['sha256'][:16]}...) has already been registered in case {duplicates[0]['case_id']} as {duplicates[0]['evidence_id']} ('{duplicates[0]['title']}'). Registration can still proceed if this is a separate exhibit.")

    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Evidence Details & Case Association
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">Step 2 &mdash; Evidence Details & Case Association</div>
                <div class="tv-card-subtitle">Document investigative context, seizure location, and chain of custody baseline</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    cases = db.get_cases()
    case_options = {c["case_id"]: f"{c['case_id']} &mdash; {c['case_title']}" for c in cases}
    case_ids = list(case_options.keys())

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_case_id = st.selectbox(
            "Investigative Case File *",
            options=case_ids,
            format_func=lambda cid: case_options.get(cid, cid)
        )
        evidence_title = st.text_input(
            "Evidence Title *",
            value=f"Exhibit: {Path(uploaded_file.name).stem.replace('_', ' ').title()}",
            placeholder="e.g. Gateway Server Access Log / Suspect Phone Extraction"
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
            "Executable / Malware Artifact",
            "Digital Evidentiary Artifact"
        ]
        # Pre-select detected classification
        default_cat_idx = category_options.index(classification["category"]) if classification["category"] in category_options else 0
        evidence_category = st.selectbox("Forensic Category *", options=category_options, index=default_cat_idx)

    with col_f2:
        collected_by = st.text_input("Collected / Seized By *", value=current_user.get("full_name", ""))
        collection_datetime = st.text_input(
            "Collection Date & UTC Time *",
            value=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        )
        collection_location = st.text_input(
            "Collection Location (Optional)",
            placeholder="e.g. Server Room B, Rack 4 / Seized Dell Laptop Workstation"
        )

    evidence_description = st.text_area(
        "Evidence Description & Context",
        placeholder="Document the investigative relevance, system source, and circumstances of collection...",
        height=70
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Cryptographic Baseline Preview
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">Step 3 &mdash; Cryptographic Baseline Fingerprints</div>
                <div class="tv-card-subtitle">Exact bitstream hashes calculated from the uploaded file</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size: 12px; color: #4A5653; margin-bottom: 8px;'>The SHA-256 hash below represents the immutable mathematical signature of this specific file payload. Any single bit modification will fundamentally alter this digest.</div>", unsafe_allow_html=True)

    render_hash_view(hashes["sha256"], label="SHA-256 PRIMARY INTEGRITY SEAL")
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        render_hash_view(hashes["md5"], label="MD5 (Legacy Reference)")
    with col_h2:
        render_hash_view(hashes["sha1"], label="SHA-1 (Forensic Compatibility)")

    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Review & Register
    col_act, _ = st.columns([2, 4])
    with col_act:
        if st.button("Register Evidence", type="primary", use_container_width=True):
            if not evidence_title.strip():
                st.error("Evidence Title is required.")
                return
            if not collected_by.strip():
                st.error("Collected By is required.")
                return

            # Generate unique Evidence ID: EV-YYYY-XXXX
            new_ev_id = f"EV-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:4].upper()}"

            # Save file to vault storage
            vault_dir.mkdir(parents=True, exist_ok=True)
            stored_filename = f"{new_ev_id}_{uploaded_file.name}"
            target_storage_path = vault_dir / stored_filename
            with open(target_storage_path, "wb") as f:
                f.write(file_bytes)

            evidence_data = {
                "evidence_id": new_ev_id,
                "case_id": selected_case_id,
                "title": evidence_title.strip(),
                "description": evidence_description.strip(),
                "category": evidence_category,
                "original_filename": uploaded_file.name,
                "file_extension": meta["file_extension"],
                "mime_type": meta["mime_type"],
                "magic_signature": meta["magic_signature"],
                "file_size_bytes": len(file_bytes),
                "sha256_hash": hashes["sha256"],
                "md5_hash": hashes["md5"],
                "sha1_hash": hashes["sha1"],
                "shannon_entropy": entropy,
                "collection_date": collection_datetime,
                "collection_location": collection_location.strip(),
                "collected_by": collected_by.strip(),
                "registered_by_id": current_user["user_id"],
                "current_custodian_id": current_user["user_id"],
                "integrity_status": "Not Yet Verified",
                "storage_rel_path": str(target_storage_path.as_posix()),
                "metadata": meta
            }

            db.add_evidence(evidence_data)

            # Record chained audit log
            audit = AuditEngine(db)
            audit.log_event(
                event_type="EVIDENCE_REGISTERED",
                user_id=current_user["user_id"],
                evidence_id=new_ev_id,
                details=f"Evidence {new_ev_id} ('{evidence_title}') registered by {current_user['full_name']} into case {selected_case_id}. SHA-256: {hashes['sha256'][:16]}..."
            )

            st.success(f"SUCCESS: Evidence registered under ID: {new_ev_id}!")
            st.session_state["selected_evidence_id"] = new_ev_id
            st.session_state["active_nav"] = "Evidence Details & Metadata"
            st.rerun()
