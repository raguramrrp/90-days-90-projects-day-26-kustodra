"""
TRACEVAULT - Main Streamlit Application Entrypoint
Digital Evidence Integrity & Chain-of-Custody Management System
"""

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tracevault.database import DatabaseManager
from tracevault.ui.styles import WORKSTATION_CSS
from tracevault.ui.components import render_header
from tracevault.ui import (
    page_overview,
    page_register,
    page_repository,
    page_details,
    page_verify,
    page_custody,
    page_reports,
    page_settings
)

# Page configuration
st.set_page_config(
    page_title="TRACEVAULT - Digital Evidence Integrity & Custody System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject visual design stylesheet
st.markdown(WORKSTATION_CSS, unsafe_allow_html=True)


def init_app_state(db: DatabaseManager) -> None:
    """Initialize session state defaults."""
    if "current_user" not in st.session_state:
        users = db.get_users()
        if users:
            st.session_state["current_user"] = users[0]
        else:
            st.session_state["current_user"] = {
                "user_id": "USR-101",
                "full_name": "Special Agent Ragu Ram",
                "role": "Lead Forensic Examiner",
                "badge_number": "FE-8842",
                "organization": "Digital Forensics & Cyber Defense Lab"
            }

    if "active_nav" not in st.session_state:
        st.session_state["active_nav"] = "Overview"


def main() -> None:
    """Main workstation controller and router."""
    db_path = PROJECT_ROOT / "data" / "tracevault.db"
    vault_dir = PROJECT_ROOT / "data" / "vault_storage"
    samples_dir = PROJECT_ROOT / "data" / "sample_evidence"

    # Auto-initialize database if missing
    db = DatabaseManager(db_path)
    init_app_state(db)

    # Check URL parameters for direct evidence linking (e.g. ?evidence_id=EV-2026-0001)
    query_params = st.query_params
    if "evidence_id" in query_params:
        st.session_state["selected_evidence_id"] = query_params["evidence_id"]
        st.session_state["active_nav"] = "Evidence Details & Metadata"

    current_user = st.session_state["current_user"]

    # Top Header Bar
    render_header(current_user, workspace_name="Cyber Forensics Workstation Alpha-01")

    # Left Navigation Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="padding-bottom: 12px; margin-bottom: 16px; border-bottom: 1px solid #E1E6E3;">
            <div style="font-size: 16px; font-weight: 700; color: #315F50; letter-spacing: 0.5px;">TRACEVAULT</div>
            <div style="font-size: 11px; color: #68736F;">Digital Forensics & Evidence Management</div>
        </div>
        """, unsafe_allow_html=True)

        nav_options = [
            "Overview",
            "Register Evidence",
            "Evidence Repository",
            "Evidence Details & Metadata",
            "Integrity Verification",
            "Chain of Custody",
            "Audit Reports",
            "System Settings"
        ]

        current_nav = st.session_state.get("active_nav", "Overview")
        current_idx = nav_options.index(current_nav) if current_nav in nav_options else 0

        selected_nav = st.radio(
            "Navigation",
            options=nav_options,
            index=current_idx,
            label_visibility="collapsed"
        )

        if selected_nav != current_nav:
            st.session_state["active_nav"] = selected_nav
            st.rerun()

        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 11px; color: #68736F; padding-top: 20px; border-top: 1px solid #E1E6E3; line-height: 1.5;">
            <b>Node ID:</b> TRACE-NODE-41<br>
            <b>Storage:</b> SQLite WAL Mode<br>
            <b>Audit Chain:</b> Active / Sealed<br>
            <b>Engine:</b> SHA-256 Bitstream
        </div>
        """, unsafe_allow_html=True)

    # Route to Selected Page
    active_page = st.session_state["active_nav"]

    if active_page == "Overview":
        page_overview.render_page(db, current_user)
    elif active_page == "Register Evidence":
        page_register.render_page(db, current_user, vault_dir)
    elif active_page == "Evidence Repository":
        page_repository.render_page(db, current_user)
    elif active_page == "Evidence Details & Metadata":
        page_details.render_page(db, current_user)
    elif active_page == "Integrity Verification":
        page_verify.render_page(db, current_user, samples_dir)
    elif active_page == "Chain of Custody":
        page_custody.render_page(db, current_user)
    elif active_page == "Audit Reports":
        page_reports.render_page(db, current_user)
    elif active_page == "System Settings":
        page_settings.render_page(db, current_user, db_path)


if __name__ == "__main__":
    main()
