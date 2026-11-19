"""
TRACEVAULT - System Integrity & Settings Page
Cryptographic audit ledger validation, user profile switching,
and database health telemetry.
"""

from __future__ import annotations
import streamlit as st
from pathlib import Path

from tracevault.database import DatabaseManager
from tracevault.core.audit_engine import AuditEngine
from scripts.seed_demo_data import seed_database


def render_page(db: DatabaseManager, current_user: dict, db_path: Path) -> None:
    """Render System Settings and Audit Verification Tools."""
    st.markdown("### System Integrity & Settings")
    st.markdown("<div style='font-size: 13px; color: #68736F; margin-bottom: 16px;'>Workstation configuration, cryptographic audit ledger verification, and active examiner profiles.</div>", unsafe_allow_html=True)

    # 1. Cryptographic Audit Chain Validator
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">1. Cryptographic Audit Chain Integrity Validator</div>
                <div class="tv-card-subtitle">Verifies that no row in the system activity ledger has been modified, injected, or deleted</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    audit = AuditEngine(db)
    col_act, col_info = st.columns([2, 4])
    with col_act:
        if st.button("Run Full Chain Validation", type="primary", use_container_width=True):
            res = audit.verify_audit_chain()
            st.session_state["audit_chain_verification_result"] = res

    v_res = st.session_state.get("audit_chain_verification_result")
    if v_res:
        if v_res["is_valid"]:
            st.success(f"""
            **CHAIN INTEGRITY VALIDATED &bull; 100% UNTAMPERED**
            
            &bull; **Total Blocks Verified:** {v_res['total_blocks']} sequential cryptographic blocks  
            &bull; **Verification Status:** All SHA-256 block linkages match historical parent hashes  
            &bull; **Diagnostic Summary:** {v_res['error_details']}
            """)
        else:
            st.error(f"""
            **INTEGRITY BREACH DETECTED &bull; LEDGER TAMPERED**
            
            &bull; **Broken Block ID:** #{v_res['broken_at_id']}  
            &bull; **Verified Blocks Before Breach:** {v_res['verified_blocks']} of {v_res['total_blocks']}  
            &bull; **Diagnostic Summary:** {v_res['error_details']}
            """)

    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Examiner Profile Switcher
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">2. Active Forensic Examiner Profile</div>
                <div class="tv-card-subtitle">Switch active credential identity for custody handovers and verification signatures</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    users = db.get_users()
    user_dict = {u["user_id"]: u for u in users}
    active_uid = current_user["user_id"]

    new_uid = st.selectbox(
        "Current Operating Identity",
        options=list(user_dict.keys()),
        index=list(user_dict.keys()).index(active_uid) if active_uid in user_dict else 0,
        format_func=lambda x: f"{user_dict[x]['full_name']} &mdash; {user_dict[x]['role']} ({user_dict[x]['organization']})"
    )

    if new_uid != active_uid:
        st.session_state["current_user"] = user_dict[new_uid]
        st.success(f"Active identity switched to: {user_dict[new_uid]['full_name']}")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Workstation Storage & Database Health
    st.markdown("""
    <div class="tv-card">
        <div class="tv-card-header">
            <div>
                <div class="tv-card-title">3. Workstation Storage Telemetry</div>
                <div class="tv-card-subtitle">Local database parameters and secure vault partition status</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    db_size = db_path.stat().st_size if db_path.is_file() else 0
    metrics = db.get_dashboard_metrics()

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.metric("Database File Size", f"{db_size / 1024:.2f} KB")
    with col_t2:
        st.metric("Total Cases Managed", metrics["total_cases"])
    with col_t3:
        st.metric("Total Custody Transfers", metrics["total_transfers"])

    # Re-seed demo data option
    with st.expander("Forensic Workstation Factory Reset (Re-seed Demo Data)"):
        st.warning("This operation will reset the local database to the pristine forensic demonstration dataset.")
        if st.button("Reset & Re-seed Forensic Database", type="secondary"):
            seed_database()
            st.success("Database re-seeded successfully!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
