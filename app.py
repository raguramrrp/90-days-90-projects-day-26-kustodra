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
    page_title="TRACEVAULT - Digital Evidence Integrity & Custody",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject visual design stylesheet
st.markdown(WORKSTATION_CSS, unsafe_allow_html=True)


def init_app_state(db: DatabaseManager) -> None:
    """Initialize session state defaults with neutral identities."""
    if "current_user" not in st.session_state:
        users = db.get_users()
        if users:
            st.session_state["current_user"] = users[0]
        else:
            st.session_state["current_user"] = {
                "user_id": "USR-101",
                "full_name": "Forensic Examiner",
                "role": "Lead Examiner",
                "organization": "Digital Forensics Unit"
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
    render_header(current_user)

    # Navigation options per specification
    nav_items = [
        ("Overview", "Overview"),
        ("Register Evidence", "Register Evidence"),
        ("Evidence Repository", "Evidence Repository"),
        ("Integrity Verification", "Integrity Verification"),
        ("Chain of Custody", "Chain of Custody"),
        ("Audit Reports", "Audit Reports"),
        ("Settings", "Settings"),
    ]

    current_nav = st.session_state.get("active_nav", "Overview")

    # Left Navigation Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="padding-bottom: 12px; margin-bottom: 16px; border-bottom: 1px solid #E1E6E3;">
            <div style="font-size: 16px; font-weight: 700; color: #315F50; letter-spacing: 0.5px;">TRACEVAULT</div>
            <div style="font-size: 11px; color: #68736F;">Evidence Integrity & Custody</div>
        </div>
        """, unsafe_allow_html=True)

        for label, nav_target in nav_items:
            is_active = (current_nav == nav_target)
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{nav_target}", type=btn_type, use_container_width=True):
                st.session_state["active_nav"] = nav_target
                st.rerun()

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 11px; color: #68736F; padding-top: 16px; border-top: 1px solid #E1E6E3; line-height: 1.6;">
            <b>Storage:</b> SQLite WAL Mode<br>
            <b>Hashing:</b> SHA-256 Bitstream<br>
            <b>Ledger:</b> Tamper-Evident Chain
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
        # Provide quick link back to repository
        if st.button("← Back to Evidence Repository", type="secondary"):
            st.session_state["active_nav"] = "Evidence Repository"
            st.rerun()
        page_details.render_page(db, current_user)
    elif active_page == "Integrity Verification":
        page_verify.render_page(db, current_user, samples_dir)
    elif active_page == "Chain of Custody":
        page_custody.render_page(db, current_user)
    elif active_page == "Audit Reports":
        page_reports.render_page(db, current_user)
    elif active_page == "Settings":
        page_settings.render_page(db, current_user, db_path)
    else:
        page_overview.render_page(db, current_user)


if __name__ == "__main__":
    main()
