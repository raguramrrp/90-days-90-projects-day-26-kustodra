"""
TRACEVAULT - Evidence Details & Metadata Page
Forensic investigation workspace providing comprehensive metadata inspection,
cryptographic baseline comparisons, and authorized evidence actions.
"""

from __future__ import annotations
import json
import streamlit as st
from pathlib import Path

from tracevault.database import DatabaseManager
from tracevault.core.forensic_analyzer import ForensicAnalyzer
from tracevault.ui.components import render_status_badge, render_hash_view


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Evidence Details & Metadata workspace."""
    # Retrieve active evidence selection
    selected_id = st.session_state.get("selected_evidence_id")
    all_evidence = db.get_evidence_list()

    if not all_evidence:
        st.info("No evidence registered in the vault yet. Register an item to inspect its metadata.")
        return

    # Selector dropdown
    evidence_options = [e["evidence_id"] for e in all_evidence]
    if not selected_id or selected_id not in evidence_options:
        selected_id = evidence_options[0]
        st.session_state["selected_evidence_id"] = selected_id

    col_sel, col_btns = st.columns([3, 4])
    with col_sel:
        chosen_id = st.selectbox(
            "Select Evidence Record to Inspect",
            options=evidence_options,
            index=evidence_options.index(selected_id) if selected_id in evidence_options else 0,
            format_func=lambda x: f"{x} &mdash; {[e['title'] for e in all_evidence if e['evidence_id'] == x][0]}",
            label_visibility="collapsed"
        )
        if chosen_id != selected_id:
            st.session_state["selected_evidence_id"] = chosen_id
            st.rerun()

    ev = db.get_evidence_by_id(selected_id)
    if not ev:
        st.error(f"Evidence record '{selected_id}' could not be loaded.")
        return

    with col_btns:
        st.markdown("<div style='display: flex; gap: 8px; justify-content: flex-end;'>", unsafe_allow_html=True)
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("Verify Integrity", use_container_width=True):
                st.session_state["active_nav"] = "Integrity Verification"
                st.rerun()
        with col_b2:
            if st.button("Transfer Custody", use_container_width=True):
                st.session_state["active_nav"] = "Chain of Custody"
                st.rerun()
        with col_b3:
            if st.button("Generate Report", use_container_width=True):
                st.session_state["active_nav"] = "Audit Reports"
                st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 1. Identity & Provenance
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">1. Evidence Identity & Provenance</div>
                <div class="tv-card-subtitle">Official case filing, classification, and custody parameters</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_id1, col_id2, col_id3 = st.columns(3)
    with col_id1:
        st.markdown(f"**Evidence ID:** `{ev['evidence_id']}`")
        st.markdown(f"**Title:** {ev['title']}")
        st.markdown(f"**Forensic Category:** {ev['category']}")
        st.markdown(f"**Original Filename:** `{ev['original_filename']}`")

    with col_id2:
        st.markdown(f"**Case Reference:** `{ev['case_id']}`")
        st.markdown(f"**Case Title:** {ev.get('case_title', 'N/A')}")
        st.markdown(f"**Jurisdiction:** {ev.get('jurisdiction', 'N/A')}")
        st.markdown(f"**File Size:** {ev['file_size_bytes']:,} Bytes")

    with col_id3:
        st.markdown(f"**Registration Date:** {ev['created_at'][:19].replace('T', ' ')} UTC")
        st.markdown(f"**Registered By:** {ev.get('registered_by_name', ev['registered_by_id'])}")
        st.markdown(f"**Current Custodian:** <b>{ev.get('custodian_name', ev['current_custodian_id'])}</b>")
        st.markdown(f"**Integrity Status:** {render_status_badge(ev['integrity_status'])}", unsafe_allow_html=True)

    if ev.get("description"):
        st.markdown(f"<div style='font-size: 12px; color: #4A5653; margin-top: 8px; background: #EDF1EE; padding: 8px 12px; border-radius: 3px;'><b>Context / Notes:</b> {ev['description']}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Cryptographic Integrity Baseline
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">2. Cryptographic Integrity Baseline (SHA-256)</div>
                <div class="tv-card-subtitle">Mathematical bitstream hashes anchored at ingestion</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    render_hash_view(ev["sha256_hash"], label="ORIGINAL SHA-256 HASH (INGESTION SEAL)")

    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        render_hash_view(ev["md5_hash"], label="MD5 Digest")
    with col_h2:
        render_hash_view(ev["sha1_hash"], label="SHA-1 Digest")
    with col_h3:
        entropy_val = ev.get("shannon_entropy", 0.0)
        entropy_eval = ForensicAnalyzer.interpret_entropy(entropy_val)
        st.markdown(f"""
        <div style='font-size: 11px; font-weight: 600; color: #68736F; margin-bottom: 2px;'>SHANNON ENTROPY</div>
        <div class="tv-hash-box" style="font-family: inherit;">
            <b>{entropy_val:.2f} / 8.00</b><br>
            <span style="font-size: 11px; color: #68736F;">{entropy_eval['level']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Intelligent Metadata Summary & Risk Analysis
    meta = ev.get("metadata", {})
    duplicates = db.find_duplicates_by_hash(ev["sha256_hash"], exclude_id=ev["evidence_id"])
    risk = ForensicAnalyzer.evaluate_risk(
        is_spoofed=meta.get("is_spoofed", False),
        entropy=ev.get("shannon_entropy", 0.0),
        integrity_status=ev["integrity_status"],
        has_duplicates=len(duplicates) > 0
    )

    summary_text = ForensicAnalyzer.generate_evidence_summary(
        title=ev["title"],
        filename=ev["original_filename"],
        category=ev["category"],
        size_formatted=f"{ev['file_size_bytes']:,} Bytes",
        mime_type=ev["mime_type"],
        entropy=ev.get("shannon_entropy", 0.0),
        sha256_hash=ev["sha256_hash"],
        is_spoofed=meta.get("is_spoofed", False),
        duplicates_count=len(duplicates)
    )

    col_sum, col_risk = st.columns([3, 2])
    with col_sum:
        st.markdown("""
        <div class="tv-card">
            <div class="tv-card-header">
                <div>
                    <div class="tv-card-title">3. Forensic Intelligence Brief</div>
                    <div class="tv-card-subtitle">Automated metadata synthesis & artifact characterization</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 12px; color: #202927; line-height: 1.5;'>{summary_text}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_risk:
        st.markdown(f"""
        <div class="tv-card">
            <div class="tv-card-header">
                <div>
                    <div class="tv-card-title">Forensic Risk Score</div>
                    <div class="tv-card-subtitle">Integrity & tampering indicators</div>
                </div>
            </div>
            <div style="display: flex; align-items: baseline; gap: 8px; margin-bottom: 8px;">
                <span style="font-size: 26px; font-weight: 700; color: {risk['color']};">{risk['score']}</span>
                <span style="font-size: 12px; font-weight: 600; color: {risk['color']};">/ 100 ({risk['level']})</span>
            </div>
        """, unsafe_allow_html=True)
        for ind in risk["indicators"]:
            st.markdown(f"<div style='font-size: 11px; color: #4A5653; margin-bottom: 4px;'>&bull; {ind}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. Structured Technical Metadata Inspector
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">4. Deep Metadata Inspector</div>
                <div class="tv-card-subtitle">Container properties, binary headers, and extracted embedded attributes</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size: 11px; color: #68736F; margin-bottom: 12px; font-style: italic;'>
    Note: Extracted metadata reflects embedded attributes parsed from the file payload. Metadata should be evaluated in forensic context and does not independently prove original authorship.
    </div>
    """, unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"**MIME Type:** `{ev['mime_type']}`")
        st.markdown(f"**Magic Signature:** `{ev.get('magic_signature', 'N/A')}`")
        st.markdown(f"**Extension:** `{ev['file_extension']}`")
        st.markdown(f"**Seizure Location:** {ev.get('collection_location') or 'Not recorded'}")

    with col_m2:
        details = meta.get("details", {})
        if "image" in details:
            img = details["image"]
            st.markdown(f"**Image Dimensions:** `{img.get('dimensions')}`")
            st.markdown(f"**Color Mode:** `{img.get('color_mode')}`")
            st.markdown(f"**Format:** `{img.get('image_format')}`")
            if "exif" in img:
                st.markdown(f"**EXIF Tags Detected:** `{len(img['exif'])} tags`")
        elif "text" in details:
            txt = details["text"]
            st.markdown(f"**Encoding:** `{txt.get('encoding')}`")
            st.markdown(f"**Line Count:** `{txt.get('total_lines'):,} lines`")
            st.markdown(f"**Word Count:** `{txt.get('word_count'):,} words`")
        else:
            st.markdown("**Container Status:** Standard binary artifact")

    # If text preview available
    if "text" in meta.get("details", {}) and "preview" in meta["details"]["text"]:
        with st.expander("View Text Evidence Preview"):
            st.code(meta["details"]["text"]["preview"], language="text")

    st.markdown("</div>", unsafe_allow_html=True)
