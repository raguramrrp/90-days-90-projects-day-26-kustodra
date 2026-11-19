"""
TRACEVAULT - Clean UI Components
Provides small, neutral application headers, native metric formatters,
and status badges without fictional identities or broken markup.
"""

from __future__ import annotations
import streamlit as st
from typing import Optional


def render_header(current_user: dict) -> None:
    """Render a minimal, neutral top application header."""
    user_name = current_user.get("full_name", "Forensic Examiner")
    user_role = current_user.get("role", "Examiner")

    st.markdown(f"""
    <div class="tv-app-header">
        <div>
            <div class="tv-app-title">TRACEVAULT</div>
            <div class="tv-app-subtitle">Digital Evidence Integrity & Chain-of-Custody System</div>
        </div>
        <div>
            <div class="tv-user-tag">{user_name}</div>
            <div class="tv-user-role">{user_role}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_status_badge_html(status: str) -> str:
    """Format status as a clean HTML badge."""
    status_lower = status.lower()
    if "verified" in status_lower and "not" not in status_lower and "fail" not in status_lower:
        return f'<span class="tv-badge-verified">&#x2713; {status}</span>'
    elif "not yet" in status_lower or "pending" in status_lower:
        return f'<span class="tv-badge-pending">&#x25CB; {status}</span>'
    elif "mismatch" in status_lower:
        return f'<span class="tv-badge-mismatch">&#x26A0; {status}</span>'
    else:
        return f'<span class="tv-badge-mismatch">&#x2715; {status}</span>'


def render_summary_metrics(total: int, verified: int, pending: int, mismatch: int) -> None:
    """Render the 4 primary summary metrics using native Streamlit metric cards."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Registered Evidence", total)
    with col2:
        st.metric("Verified", verified)
    with col3:
        st.metric("Pending Verification", pending)
    with col4:
        st.metric("Integrity Mismatches", mismatch)


def render_hash_view(hash_str: str, label: Optional[str] = None) -> None:
    """Render a cryptographic hash in a native monospace container with built-in copy."""
    if label:
        st.markdown(f"<span style='font-size: 11px; font-weight: 600; color: #68736F;'>{label}</span>", unsafe_allow_html=True)
    st.code(hash_str, language=None)
