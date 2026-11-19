"""
TRACEVAULT - Evidence Details & Metadata Page
Structured evidence inspection workspace displaying cryptographic baselines,
container properties, metadata, and authorized operations.
"""

from __future__ import annotations
import streamlit as st
from tracevault.database import DatabaseManager
from tracevault.core.forensic_analyzer import ForensicAnalyzer
from tracevault.ui.components import render_hash_view, get_status_badge_html


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Evidence Details & Metadata workspace."""
    all_evidence = db.get_evidence_list()
    if not all_evidence:
        st.info("No evidence registered in the vault yet.")
        return

    selected_id = st.session_state.get("selected_evidence_id")
    evidence_options = [e["evidence_id"] for e in all_evidence]
    if not selected_id or selected_id not in evidence_options:
        selected_id = evidence_options[0]
        st.session_state["selected_evidence_id"] = selected_id

    # Record Selector & Action Bar
    col_sel, col_act1, col_act2, col_act3 = st.columns([4, 1.3, 1.3, 1.3])
    with col_sel:
        chosen_id = st.selectbox(
            "Select Evidence Record",
            options=evidence_options,
            index=evidence_options.index(selected_id),
            format_func=lambda x: f"{x} — {[e['title'] for e in all_evidence if e['evidence_id'] == x][0]}",
            label_visibility="collapsed"
        )
        if chosen_id != selected_id:
            st.session_state["selected_evidence_id"] = chosen_id
            st.rerun()

    with col_act1:
        if st.button("Verify Integrity", use_container_width=True):
            st.session_state["active_nav"] = "Integrity Verification"
            st.rerun()
    with col_act2:
        if st.button("Transfer Custody", use_container_width=True):
            st.session_state["active_nav"] = "Chain of Custody"
            st.rerun()
    with col_act3:
        if st.button("Generate Report", use_container_width=True):
            st.session_state["active_nav"] = "Audit Reports"
            st.rerun()

    ev = db.get_evidence_by_id(chosen_id)
    if not ev:
        st.error(f"Unable to load record '{chosen_id}'.")
        return

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # 1. Evidence Identity & Provenance
    with st.container(border=True):
        st.markdown("#### Evidence Identity & Provenance")

        col_id1, col_id2, col_id3 = st.columns(3)
        with col_id1:
            st.markdown(f"**Evidence ID:** `{ev['evidence_id']}`")
            st.markdown(f"**Title:** {ev['title']}")
            st.markdown(f"**Filename:** `{ev['original_filename']}`")
            st.markdown(f"**Category:** {ev['category']}")

        with col_id2:
            st.markdown(f"**Case Reference:** `{ev['case_id']}`")
            st.markdown(f"**Case Title:** {ev.get('case_title', 'N/A')}")
            st.markdown(f"**File Size:** {ev['file_size_bytes']:,} Bytes")
            st.markdown(f"**MIME Type:** `{ev['mime_type']}`")

        with col_id3:
            status_badge = get_status_badge_html(ev['integrity_status'])
            st.markdown(f"**Registration:** {ev['created_at'][:19].replace('T', ' ')} UTC")
            st.markdown(f"**Current Custodian:** {ev.get('custodian_name', ev['current_custodian_id'])}")
            st.markdown(f"**Status:** {status_badge}", unsafe_allow_html=True)

        if ev.get("description"):
            st.info(f"**Context / Description:** {ev['description']}")

    # 2. Cryptographic Integrity Baseline
    with st.container(border=True):
        st.markdown("#### Cryptographic Baseline Fingerprints")
        st.caption("Immutable cryptographic digests recorded at intake")

        render_hash_view(ev["sha256_hash"], label="SHA-256 PRIMARY INTEGRITY SEAL")

        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            render_hash_view(ev["md5_hash"], label="MD5 Digest")
        with col_h2:
            render_hash_view(ev["sha1_hash"], label="SHA-1 Digest")
        with col_h3:
            entropy = ev.get("shannon_entropy", 0.0)
            entropy_info = ForensicAnalyzer.interpret_entropy(entropy)
            st.markdown("<span style='font-size: 11px; font-weight: 600; color: #68736F;'>SHANNON ENTROPY</span>", unsafe_allow_html=True)
            st.markdown(f"**{entropy:.2f} / 8.00** — *{entropy_info['level']}*")

    # 3. Deep Metadata Inspector
    with st.container(border=True):
        st.markdown("#### Technical Metadata Inspector")
        st.caption("Extracted container attributes, header signatures, and payload metrics")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"**Header Signature:** {ev.get('magic_signature', 'N/A')}")
            st.markdown(f"**File Extension:** `{ev['file_extension']}`")
            st.markdown(f"**Seizure Location:** {ev.get('collection_location') or 'Not recorded'}")
            st.markdown(f"**Collected By:** {ev.get('collected_by', 'N/A')}")

        meta = ev.get("metadata", {})
        details = meta.get("details", {})

        with col_m2:
            if "image" in details:
                img = details["image"]
                st.markdown(f"**Dimensions:** {img.get('dimensions')}")
                st.markdown(f"**Color Mode:** {img.get('color_mode')}")
                st.markdown(f"**Format:** {img.get('image_format')}")
            elif "text" in details:
                txt = details["text"]
                st.markdown(f"**Encoding:** {txt.get('encoding')}")
                st.markdown(f"**Line Count:** {txt.get('total_lines'):,} lines")
                st.markdown(f"**Word Count:** {txt.get('word_count'):,} words")
            else:
                st.markdown("**Container Status:** Standard binary artifact")

        if "text" in details and "preview" in details["text"]:
            with st.expander("View Text Content Preview"):
                st.text(details["text"]["preview"])
