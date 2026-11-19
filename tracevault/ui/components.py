"""
TRACEVAULT - Forensic Workstation UI Components
Provides standard headers, metric formatters, status badges, and cryptographic fingerprint inspectors.
"""

from __future__ import annotations
import streamlit as st
from typing import Optional


def render_header(current_user: dict) -> None:
    """Render the compact, professional forensic workbench header."""
    user_name = current_user.get("full_name", "Forensic Examiner")
    user_role = current_user.get("role", "Examiner")
    user_org = current_user.get("organization", "Digital Forensics Unit")

    st.markdown(f"""
    <div class="tv-app-header">
        <div>
            <div class="tv-app-title">TRACEVAULT</div>
            <div class="tv-app-descriptor">DIGITAL FORENSICS &bull; EVIDENCE MANAGEMENT</div>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <div>
                <div class="tv-user-tag">{user_name}</div>
                <div class="tv-user-role">{user_role} &bull; {user_org}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


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


def get_status_badge_html(status: str) -> str:
    """Format status as a clean HTML badge."""
    status_lower = (status or "").lower()
    if "verified" in status_lower and "not" not in status_lower and "fail" not in status_lower:
        return f'<span class="tv-badge-verified">&#x2713; {status}</span>'
    elif "not yet" in status_lower or "pending" in status_lower:
        return f'<span class="tv-badge-pending">&#x25CB; {status}</span>'
    elif "mismatch" in status_lower:
        return f'<span class="tv-badge-mismatch">&#x26A0; {status}</span>'
    else:
        return f'<span class="tv-badge-mismatch">&#x2715; {status}</span>'


def render_summary_metrics(total: int, verified: int, pending: int, mismatch: int) -> None:
    """
    Render the 4 primary summary metrics per specification:
    - Registered Evidence
    - Verified Integrity
    - Pending Verification
    - Integrity Discrepancies
    """
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Registered Evidence", total)
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
