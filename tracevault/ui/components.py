"""
TRACEVAULT - Reusable UI Components
Provides styled headers, status indicators, hash formatters, and cards.
"""

from __future__ import annotations
import streamlit as st
from typing import Optional


def render_header(current_user: dict, workspace_name: str = "TraceVault Digital Forensics Workstation") -> None:
    """Render the compact top header bar."""
    st.markdown(f"""
    <div class="tv-header-bar">
        <div>
            <div class="tv-logo-title">
                <span>TRACEVAULT</span>
                <span style="font-size: 11px; font-weight: 500; background: #EDF1EE; color: #315F50; padding: 2px 7px; border-radius: 3px; border: 1px solid #E1E6E3;">EVIDENCE INTEGRITY WORKSTATION</span>
            </div>
            <div class="tv-header-meta">
                Workspace: <b>{workspace_name}</b> &bull; Environment: Secure Offline Node
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 13px; font-weight: 600; color: #202927;">
                {current_user.get('full_name', 'Lead Examiner')}
            </div>
            <div style="font-size: 11px; color: #68736F;">
                {current_user.get('role', 'Forensic Examiner')} &bull; Badge: <b>{current_user.get('badge_number', 'FE-8842')}</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    """Return HTML string for consistent security status badges."""
    status_lower = status.lower()
    if "verified" in status_lower and "not" not in status_lower and "fail" not in status_lower:
        return f'<span class="tv-status-badge tv-status-verified">&#x2713; {status}</span>'
    elif "not yet" in status_lower or "pending" in status_lower:
        return f'<span class="tv-status-badge tv-status-pending">&#x25CB; {status}</span>'
    elif "mismatch" in status_lower:
        return f'<span class="tv-status-badge tv-status-mismatch">&#x26A0; {status}</span>'
    else:
        return f'<span class="tv-status-badge tv-status-mismatch">&#x2715; {status}</span>'


def render_hash_view(hash_str: str, label: Optional[str] = None) -> None:
    """Display a cryptographic hash in a clean monospace container."""
    if label:
        st.markdown(f"<div style='font-size: 11px; font-weight: 600; color: #68736F; margin-bottom: 2px;'>{label}</div>", unsafe_allow_html=True)
    st.markdown(f'<div class="tv-hash-box">{hash_str}</div>', unsafe_allow_html=True)


def render_metric_cards(total: int, verified: int, pending: int, mismatch: int) -> None:
    """Render the 4 primary workstation metrics."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="tv-metric-box">
            <div class="tv-metric-label">Total Registered Evidence</div>
            <div class="tv-metric-val">{total}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="tv-metric-box" style="border-left: 3px solid #287A54;">
            <div class="tv-metric-label">Verified Integrity</div>
            <div class="tv-metric-val" style="color: #287A54;">{verified}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="tv-metric-box" style="border-left: 3px solid #B77B29;">
            <div class="tv-metric-label">Pending Verification</div>
            <div class="tv-metric-val" style="color: #B77B29;">{pending}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="tv-metric-box" style="border-left: 3px solid #B74747;">
            <div class="tv-metric-label">Integrity Discrepancies</div>
            <div class="tv-metric-val" style="color: #B74747;">{mismatch}</div>
        </div>
        """, unsafe_allow_html=True)
