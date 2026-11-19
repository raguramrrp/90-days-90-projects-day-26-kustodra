"""
KUSTODRA - UI Components
Provides top header, status badge formatters, format icons, and cryptographic inspectors.
"""

from __future__ import annotations
import streamlit as st
from typing import Optional


def render_header(title: str, current_user: dict, show_import: bool = True, breadcrumb: str = "") -> None:
    """
    Render clean minimal horizontal page header.
    Left: Clean Page Title
    Right: "+ Ingest Artifact" action when applicable
    """
    if show_import:
        col_left, col_right = st.columns([5, 1.3])
        with col_left:
            st.markdown(
                f'<div style="font-size: 22px; font-weight: 700; color: #252B2A; letter-spacing: -0.3px; margin-bottom: 8px;">{title}</div>',
                unsafe_allow_html=True
            )
        with col_right:
            if st.button("+ Ingest Artifact", type="primary", use_container_width=True, key=f"btn_hdr_import_{title}"):
                st.session_state["active_nav"] = "Intake & Ingestion"
                st.rerun()
    else:
        st.markdown(
            f'<div style="font-size: 22px; font-weight: 700; color: #252B2A; letter-spacing: -0.3px; margin-bottom: 8px;">{title}</div>',
            unsafe_allow_html=True
        )


def get_type_tag(category: str) -> str:
    """Map verbose evidence category to subtle textual forensic type label."""
    cat_lower = (category or "").lower()
    if "image" in cat_lower or "photo" in cat_lower or "cam" in cat_lower:
        return "IMAGE"
    elif "doc" in cat_lower or "pdf" in cat_lower or "contract" in cat_lower or "text" in cat_lower:
        return "DOCUMENT"
    elif "video" in cat_lower or "mp4" in cat_lower:
        return "VIDEO"
    elif "audio" in cat_lower or "voice" in cat_lower:
        return "AUDIO"
    elif "log" in cat_lower or "access" in cat_lower or "audit" in cat_lower:
        return "LOG"
    elif "archive" in cat_lower or "zip" in cat_lower or "tar" in cat_lower:
        return "ARCHIVE"
    elif "disk" in cat_lower or "raw" in cat_lower or "dd" in cat_lower or "iso" in cat_lower:
        return "DISK IMAGE"
    else:
        return "BINARY"


def get_format_icon(category: str) -> str:
    """Get clean icon representation for file format."""
    tag = get_type_tag(category)
    icons = {
        "IMAGE": "📷",
        "DOCUMENT": "📄",
        "VIDEO": "🎬",
        "AUDIO": "🎙️",
        "LOG": "📋",
        "ARCHIVE": "🗜️",
        "DISK IMAGE": "💾",
        "BINARY": "🔒"
    }
    return icons.get(tag, "📁")


def get_status_badge_html(status: str) -> str:
    """Format status as a clean HTML badge."""
    status_lower = (status or "").lower()
    if "verified" in status_lower and "not" not in status_lower and "fail" not in status_lower:
        return f'<span class="ks-badge-verified">&#x2713; {status}</span>'
    elif "not yet" in status_lower or "pending" in status_lower:
        return f'<span class="ks-badge-pending">&#x25CB; {status}</span>'
    elif "mismatch" in status_lower:
        return f'<span class="ks-badge-mismatch">&#x26A0; {status}</span>'
    else:
        return f'<span class="ks-badge-mismatch">&#x2715; {status}</span>'


def render_summary_metrics(total: int, verified: int, pending: int, mismatch: int) -> None:
    """Render the 4 primary summary metrics in restrained cards."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Cataloged Artifacts", total)
    with col2:
        st.metric("Verified Integrity", verified)
    with col3:
        st.metric("Pending Verification", pending)
    with col4:
        st.metric("Integrity Discrepancies", mismatch)


def render_hash_view(hash_str: str, label: Optional[str] = None) -> None:
    """Render a cryptographic hash in a monospace container with copy action."""
    if label:
        st.markdown(f"<span style='font-size: 11px; font-weight: 600; color: #527C78; text-transform: uppercase;'>{label}</span>", unsafe_allow_html=True)
    st.code(hash_str, language=None)
