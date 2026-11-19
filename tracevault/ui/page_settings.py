"""
TRACEVAULT - Settings & Audit Verification Page
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
    """Render Settings and Audit Verification Tools."""
    st.markdown("### Settings")
    st.caption("Workstation configuration, cryptographic audit chain verification, and operating identity.")

    # 1. Cryptographic Audit Chain Validator
    with st.container(border=True):
        st.markdown("#### Cryptographic Audit Chain Validator")
        st.caption("Verifies that every activity block in the SQLite ledger is cryptographically linked and untampered.")

        audit = AuditEngine(db)
        if st.button("Run Audit Chain Verification", type="primary"):
            res = audit.verify_audit_chain()
            st.session_state["audit_chain_verification_result"] = res

        v_res = st.session_state.get("audit_chain_verification_result")
        if v_res:
            if v_res["is_valid"]:
                st.success(
                    f"**Audit Chain Verified Intact**\n\n"
                    f"- **Total Blocks Verified:** {v_res['total_blocks']} sequential cryptographic blocks\n"
                    f"- **Status:** All SHA-256 block linkages match historical parent hashes\n"
                    f"- **Details:** {v_res['error_details']}"
                )
            else:
                st.error(
                    f"**Integrity Breach Detected**\n\n"
                    f"- **Broken Block ID:** #{v_res['broken_at_id']}\n"
                    f"- **Verified Prior Blocks:** {v_res['verified_blocks']} of {v_res['total_blocks']}\n"
                    f"- **Details:** {v_res['error_details']}"
                )

    # 2. Operating Identity Switcher
    with st.container(border=True):
        st.markdown("#### Operating Identity")
        st.caption("Select the active system identity used for custody transfers, integrity audits, and event signatures.")

        users = db.get_users()
        user_dict = {u["user_id"]: u for u in users}
        active_uid = current_user.get("user_id")

        if user_dict:
            new_uid = st.selectbox(
                "Active User",
                options=list(user_dict.keys()),
                index=list(user_dict.keys()).index(active_uid) if active_uid in user_dict else 0,
                format_func=lambda x: f"{user_dict[x]['full_name']} — {user_dict[x]['role']} ({user_dict[x]['organization']})"
            )

            if new_uid != active_uid:
                st.session_state["current_user"] = user_dict[new_uid]
                st.success(f"Operating identity switched to: {user_dict[new_uid]['full_name']}")
                st.rerun()

    # 3. Workstation Storage Telemetry
    with st.container(border=True):
        st.markdown("#### Storage & Database Telemetry")
        st.caption("Local database file parameters and repository statistics.")

        db_size = db_path.stat().st_size if db_path.is_file() else 0
        metrics = db.get_dashboard_metrics()

        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.metric("Database File Size", f"{db_size / 1024:.1f} KB")
        with col_t2:
            st.metric("Total Cases Managed", metrics["total_cases"])
        with col_t3:
            st.metric("Total Custody Transfers", metrics["total_transfers"])

        with st.expander("Reset Demonstration Data", expanded=False):
            st.warning("This will reset the local SQLite database to the pristine forensic demonstration dataset.")
            if st.button("Reset Database", type="secondary"):
                seed_database()
                st.success("Database re-seeded successfully.")
                st.rerun()
