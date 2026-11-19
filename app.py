"""
KUSTODRA — Main Streamlit Application Entrypoint
Digital Asset Custody & Cryptographic Integrity Verification System
Forensic Asset Management Workstation
"""

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from kustodra.database import DatabaseManager
from kustodra.ui.styles import WORKSTATION_CSS
from kustodra.ui import (
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
    page_title="KUSTODRA — Digital Asset Management System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject visual identity stylesheet
st.markdown(WORKSTATION_CSS, unsafe_allow_html=True)


def init_app_state(db: DatabaseManager) -> None:
    """Initialize session state defaults with neutral forensic identities."""
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

    # Primary default landing view is Artifact Vault matching enterprise reference
    if "active_nav" not in st.session_state:
        st.session_state["active_nav"] = "Artifact Vault"


@st.dialog("KUSTODRA — Workstation User Guide", width="large")
def show_help_dialog() -> None:
    """Comprehensive interactive user guide for the digital asset custody workstation."""
    st.markdown("### 🛡️ Digital Asset Custody & Forensic Verification Guide")
    st.markdown(
        "**KUSTODRA** is an enterprise-grade Digital Evidence Integrity & Chain-of-Custody Management System. "
        "It provides mathematical certainty that digital artifacts (logs, disk images, media, documents) remain "
        "**unmodified, authentic, and court-admissible** throughout their lifecycle."
    )

    st.markdown("---")
    st.markdown("#### 🚀 Operational Modules")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        **🗄️ Artifact Vault**  
        Central registry of all cataloged evidence items. Filter by custodian, format, or verification state, and search by SHA-256 hash, title, or artifact ID.

        **📥 Intake & Ingestion**  
        Acquire new specimens. Computes streaming SHA-256, SHA-1, MD5, detects magic byte signatures to catch file spoofing, and calculates Shannon Entropy.

        **📊 System Intelligence**  
        Real-time telemetry on vault health, entropy risk distribution, and custodian activity timelines.

        **🔬 Integrity Lab**  
        Perform constant-time cryptographic verification (`hmac.compare_digest`) comparing suspect or stored copies against immutable baseline hashes.
        """)
    with c2:
        st.markdown("""
        **⛓️ Chain of Custody**  
        Track legal handovers between examiners, analysts, and vault storage. Every transfer generates a verifiable HMAC receipt token.

        **📄 Audit & Compliance**  
        Compile formal, publication-ready PDF evidence certificates and Markdown dossiers admissible in judicial or compliance proceedings.

        **⚙️ System Configuration**  
        Inspect database schema, run cryptographic chain validations, export database backups, or reset demo seed records.
        """)

    st.markdown("---")
    st.markdown("#### 📐 Cryptographic & Forensic Standards")
    st.markdown("""
    - **NIST FIPS 180-4:** SHA-256 & SHA-1 Secure Hash Standards
    - **RFC 2104 / FIPS 198-1:** HMAC Keyed-Hashing for Custody Handover Receipts
    - **ISO/IEC 27037:** Digital Evidence Handling, Identification, Collection & Preservation
    - **Constant-Time Verification:** Immune to side-channel timing attacks
    """)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("Close Guide", type="primary", use_container_width=True, key="btn_close_help"):
        st.rerun()


@st.dialog("Active Custodian Identity & Session", width="medium")
def show_profile_dialog(db: DatabaseManager, current_user: dict) -> None:
    """Display active forensic examiner credentials and allow identity switching."""
    st.markdown("### 👤 Active Custodian Profile")
    st.caption("Cryptographic identity used to sign custody transfers, ingest artifacts, and seal verification checks.")

    name = current_user.get("full_name", "Forensic Examiner")
    role = current_user.get("role", "Vault Custodian")
    uid = current_user.get("user_id", "USR-101")
    org = current_user.get("organization", "Digital Forensics Unit")

    st.markdown(f"""
    <div style="background-color: #FAFCFB; border: 1px solid #E1E4E3; border-radius: 8px; padding: 16px; margin: 12px 0;">
        <div style="font-size: 18px; font-weight: 700; color: #252B2A;">{name}</div>
        <div style="font-size: 13px; color: #315F50; font-weight: 600; margin-top: 2px;">{role} &bull; ID: <code>{uid}</code></div>
        <div style="font-size: 12px; color: #777F7D; margin-top: 6px;">Organization: <b>{org}</b></div>
        <div style="font-size: 12px; color: #32815A; font-weight: 600; margin-top: 6px;">🟢 Active Session &bull; Clearance: Full Vault Access</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Switch Custodian Profile")
    users = db.get_users()
    if users:
        user_names = [u["full_name"] for u in users]
        curr_idx = user_names.index(name) if name in user_names else 0

        selected_name = st.selectbox("Select Active Examiner / Custodian", options=user_names, index=curr_idx)
        if selected_name != name:
            if st.button("Switch Identity", type="primary", use_container_width=True, key="btn_switch_identity"):
                new_u = next(u for u in users if u["full_name"] == selected_name)
                st.session_state["current_user"] = new_u
                st.toast(f"Active Custodian switched to {selected_name}", icon="👤")
                st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("Close", type="secondary", use_container_width=True, key="btn_close_profile"):
        st.rerun()


def main() -> None:
    """Main workstation controller and router."""
    db_path = PROJECT_ROOT / "data" / "kustodra.db"
    vault_dir = PROJECT_ROOT / "data" / "vault_storage"
    samples_dir = PROJECT_ROOT / "data" / "sample_evidence"

    # Auto-initialize database if missing
    db = DatabaseManager(db_path)
    init_app_state(db)

    # Check URL parameters for direct artifact linking (e.g. ?artifact_id=ART-2026-0001)
    query_params = st.query_params
    target_id = query_params.get("artifact_id") or query_params.get("evidence_id")
    if target_id:
        st.session_state["selected_evidence_id"] = target_id
        st.session_state["active_nav"] = "Artifact Inspector"

    current_user = st.session_state["current_user"]

    # 7 Workstation Navigation Targets (Rendered as single-icon buttons in the narrow rail)
    nav_items = [
        ("Artifact Vault", "Artifact Vault", "🗄️"),
        ("Intake & Ingestion", "Intake & Ingestion", "📥"),
        ("System Intelligence", "System Intelligence", "📊"),
        ("Integrity Lab", "Integrity Lab", "🔬"),
        ("Chain of Custody", "Chain of Custody", "⛓️"),
        ("Audit & Compliance", "Audit & Compliance", "📄"),
        ("System Configuration", "System Configuration", "⚙️"),
    ]

    current_nav = st.session_state.get("active_nav", "Artifact Vault")

    # Left Vertical Navigation Rail (~72px wide dark charcoal rail)
    with st.sidebar:
        # Minimal top logo glyph matching the reference design
        st.markdown('<div class="ks-rail-logo">▲</div>', unsafe_allow_html=True)

        for label, nav_target, icon in nav_items:
            is_active = (current_nav == nav_target)
            btn_type = "primary" if is_active else "secondary"
            # Icon button without persistent tooltip
            if st.button(icon, key=f"nav_{nav_target}", type=btn_type):
                st.session_state["active_nav"] = nav_target
                st.rerun()

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # Bottom utility icons — triggers interactive modals
        if st.button("❓", key="nav_help", type="secondary"):
            show_help_dialog()
        if st.button("👤", key="nav_profile", type="secondary"):
            show_profile_dialog(db, current_user)

    # Route to Selected Forensic Workspace
    active_page = st.session_state["active_nav"]

    if active_page == "Artifact Vault":
        page_repository.render_page(db, current_user)
    elif active_page == "Intake & Ingestion":
        page_register.render_page(db, current_user, vault_dir)
    elif active_page == "System Intelligence":
        page_overview.render_page(db, current_user)
    elif active_page == "Artifact Inspector":
        col_back, _ = st.columns([1, 4])
        with col_back:
            if st.button("← Back to Vault", type="secondary"):
                st.session_state["active_nav"] = "Artifact Vault"
                st.rerun()
        page_details.render_page(db, current_user)
    elif active_page == "Integrity Lab":
        page_verify.render_page(db, current_user, samples_dir)
    elif active_page == "Chain of Custody":
        page_custody.render_page(db, current_user)
    elif active_page == "Audit & Compliance":
        page_reports.render_page(db, current_user)
    elif active_page == "System Configuration":
        page_settings.render_page(db, current_user, db_path)
    else:
        page_repository.render_page(db, current_user)


if __name__ == "__main__":
    main()
