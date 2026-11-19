"""
TRACEVAULT - Evidence Registration Page
Sequential 5-step intake workflow: file selection, metadata extraction,
cryptographic hashing, review, and vault registration.
"""

from __future__ import annotations
import uuid
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
    """Render the Evidence Registration sequence."""
    st.markdown("### Register New Evidence")
    st.markdown("<p style='font-size: 13px; color: #68736F; margin-top: -8px; margin-bottom: 16px;'>Ingest digital artifacts into secure vault custody with automated SHA-256 hashing and provenance records.</p>", unsafe_allow_html=True)

    # Step 1: Select File
    with st.container(border=True):
        st.markdown("#### 1. Select File")
        uploaded_file = st.file_uploader(
            "Select evidence file",
            type=None,
            help="Upload any digital file format (logs, images, videos, documents, or binary archives).",
            label_visibility="collapsed"
        )

        if not uploaded_file:
            st.info("Select or drag a file to begin registration.")
            return

        file_bytes = uploaded_file.getvalue()
        file_size = len(file_bytes)

        # Immediate Hashing & Inspection
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

        # Metric summary of uploaded file
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Filename", uploaded_file.name)
        col2.metric("Size", meta["file_size_formatted"])
        col3.metric("Detected Header", meta["magic_signature"])
        col4.metric("Entropy", f"{entropy:.2f} / 8.0")

        if meta["is_spoofed"]:
            st.warning(f"Header Divergence Alert: {meta['spoof_warning']}")

        duplicates = db.find_duplicates_by_hash(hashes["sha256"])
        if duplicates:
            st.warning(f"Duplicate Match: This exact SHA-256 hash was previously registered in case {duplicates[0]['case_id']} as {duplicates[0]['evidence_id']}.")

    # Step 2: Enter Evidence Details
    with st.container(border=True):
        st.markdown("#### 2. Evidence Details")

        cases = db.get_cases()
        case_options = {c["case_id"]: f"{c['case_id']} — {c['case_title']}" for c in cases}
        case_ids = list(case_options.keys())

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            selected_case = st.selectbox(
                "Associated Case Reference *",
                options=case_ids,
                format_func=lambda cid: case_options.get(cid, cid)
            )
            evidence_title = st.text_input(
                "Evidence Title *",
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
            evidence_category = st.selectbox("Category *", options=category_options, index=category_options.index(default_cat))

        with col_d2:
            collected_by = st.text_input("Collected By *", value=current_user.get("full_name", "Forensic Examiner"))
            collection_date = st.text_input("Collection Date & Time (UTC) *", value=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
            collection_location = st.text_input("Collection Location (Optional)", placeholder="e.g. Workstation 4 / Network Switch Port 2")

        evidence_desc = st.text_area("Description & Context (Optional)", placeholder="Enter relevant investigative context...", height=65)

    # Step 3: Calculate SHA-256
    with st.container(border=True):
        st.markdown("#### 3. Cryptographic Hashing")
        st.caption("Calculated SHA-256 bitstream fingerprint anchored at intake")

        render_hash_view(hashes["sha256"], label="SHA-256 BASELINE HASH")

        with st.expander("Secondary Hashes (MD5 & SHA-1)"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                render_hash_view(hashes["md5"], label="MD5")
            with col_m2:
                render_hash_view(hashes["sha1"], label="SHA-1")

    # Step 4 & 5: Review & Register
    with st.container(border=True):
        st.markdown("#### 4. Review & Register")
        st.markdown(f"""
        - **Exhibit:** {evidence_title} (`{uploaded_file.name}`)
        - **Category:** {evidence_category} &bull; **Size:** {meta['file_size_formatted']}
        - **Case:** {selected_case} &bull; **Custodian:** {collected_by}
        - **SHA-256:** `{hashes['sha256']}`
        """)

        col_reg, _ = st.columns([1, 3])
        with col_reg:
            if st.button("Register Evidence", type="primary", use_container_width=True):
                if not evidence_title.strip():
                    st.error("Please provide an Evidence Title.")
                    return

                new_id = f"EV-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:4].upper()}"

                # Store file in vault
                vault_dir.mkdir(parents=True, exist_ok=True)
                stored_name = f"{new_id}_{uploaded_file.name}"
                target_path = vault_dir / stored_name
                with open(target_path, "wb") as f:
                    f.write(file_bytes)

                evidence_payload = {
                    "evidence_id": new_id,
                    "case_id": selected_case,
                    "title": evidence_title.strip(),
                    "description": evidence_desc.strip(),
                    "category": evidence_category,
                    "original_filename": uploaded_file.name,
                    "file_extension": meta["file_extension"],
                    "mime_type": meta["mime_type"],
                    "magic_signature": meta["magic_signature"],
                    "file_size_bytes": file_size,
                    "sha256_hash": hashes["sha256"],
                    "md5_hash": hashes["md5"],
                    "sha1_hash": hashes["sha1"],
                    "shannon_entropy": entropy,
                    "collection_date": collection_date,
                    "collection_location": collection_location.strip(),
                    "collected_by": collected_by.strip(),
                    "registered_by_id": current_user["user_id"],
                    "current_custodian_id": current_user["user_id"],
                    "integrity_status": "Not Yet Verified",
                    "storage_rel_path": str(target_path.as_posix()),
                    "metadata": meta
                }

                db.add_evidence(evidence_payload)

                # Chained audit event
                audit = AuditEngine(db)
                audit.log_event(
                    event_type="EVIDENCE_REGISTERED",
                    user_id=current_user["user_id"],
                    evidence_id=new_id,
                    details=f"Evidence {new_id} ('{evidence_title}') registered. SHA-256: {hashes['sha256'][:16]}..."
                )

                st.success(f"Evidence successfully registered under ID: {new_id}")
                st.session_state["selected_evidence_id"] = new_id
                st.session_state["active_nav"] = "Evidence Details & Metadata"
                st.rerun()
