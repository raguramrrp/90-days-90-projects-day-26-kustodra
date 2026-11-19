"""
TRACEVAULT - Audit Reports & Documentation Page
Generates court-ready PDF certificates via ReportLab and tabular forensic exports (CSV/JSON).
"""

from __future__ import annotations
import io
import json
import streamlit as st
import pandas as pd
from datetime import datetime, timezone

from tracevault.database import DatabaseManager, get_iso_now
from tracevault.core.report_generator import ReportGenerator
from tracevault.core.audit_engine import AuditEngine


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Forensic Reporting & Audit Export workspace."""
    st.markdown("### Forensic Audit Reports")
    st.markdown("<div style='font-size: 13px; color: #68736F; margin-bottom: 16px;'>Generate certified PDF chain-of-custody documentation, case dossiers, and immutable audit logs.</div>", unsafe_allow_html=True)

    all_evidence = db.get_evidence_list()
    if not all_evidence:
        st.info("No evidence registered to generate reports for.")
        return

    tab_pdf, tab_case, tab_audit = st.tabs([
        "Individual Evidence Certificate (PDF)",
        "Case Dossier Summary (CSV / JSON)",
        "System Audit Trail Export"
    ])

    # Tab 1: Individual Evidence PDF Certificate
    with tab_pdf:
        st.markdown("""
        <div class="tv-card">
            <div class="tv-card-header">
                <div>
                    <div class="tv-card-title">Evidence & Chain-of-Custody Certificate Generator</div>
                    <div class="tv-card-subtitle">Official court-admissible PDF document compiled using ReportLab</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        selected_id = st.session_state.get("selected_evidence_id", all_evidence[0]["evidence_id"])
        evidence_options = [e["evidence_id"] for e in all_evidence]
        if selected_id not in evidence_options:
            selected_id = evidence_options[0]

        col_ev_sel, col_agency = st.columns(2)
        with col_ev_sel:
            chosen_id = st.selectbox(
                "Select Evidence Record *",
                options=evidence_options,
                index=evidence_options.index(selected_id),
                format_func=lambda x: f"{x} &mdash; {[e['title'] for e in all_evidence if e['evidence_id'] == x][0]}"
            )
        with col_agency:
            agency_name = st.text_input("Agency / Department Name", value="Digital Forensics & Evidence Integrity Workstation")

        ev = db.get_evidence_by_id(chosen_id)
        custody_logs = db.get_custody_logs_for_evidence(chosen_id)
        integrity_checks = db.get_integrity_checks_for_evidence(chosen_id)

        # Generate PDF Button
        if st.button("Compile Official PDF Certificate", type="primary"):
            with st.spinner("Compiling publication-grade PDF certificate..."):
                pdf_bytes = ReportGenerator.generate_evidence_certificate(
                    evidence=ev,
                    custody_logs=custody_logs,
                    integrity_checks=integrity_checks,
                    generated_by_name=current_user["full_name"],
                    agency_name=agency_name
                )
                st.session_state["generated_pdf_bytes"] = pdf_bytes
                st.session_state["generated_pdf_id"] = chosen_id

                # Record audit log event
                audit = AuditEngine(db)
                audit.log_event(
                    event_type="REPORT_GENERATED",
                    user_id=current_user["user_id"],
                    evidence_id=chosen_id,
                    details=f"Official PDF Evidence Certificate compiled for {chosen_id} by {current_user['full_name']}."
                )

        if "generated_pdf_bytes" in st.session_state and st.session_state.get("generated_pdf_id") == chosen_id:
            pdf_data = st.session_state["generated_pdf_bytes"]
            filename = f"TRACEVAULT_CERTIFICATE_{chosen_id}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"
            st.success(f"PDF Document Ready ({len(pdf_data):,} bytes). Download below:")
            st.download_button(
                label=f"Download {filename}",
                data=pdf_data,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # Tab 2: Case Dossier Summary
    with tab_case:
        st.markdown("""
        <div class="tv-card">
            <div class="tv-card-header">
                <div>
                    <div class="tv-card-title">Case Evidence Dossier Export</div>
                    <div class="tv-card-subtitle">Complete manifest of all exhibits registered to an active case file</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        cases = db.get_cases()
        case_options = {c["case_id"]: f"{c['case_id']} &mdash; {c['case_title']}" for c in cases}
        selected_case_id = st.selectbox("Select Case to Export", options=list(case_options.keys()), format_func=lambda x: case_options[x])

        case_items = db.get_evidence_list(case_filter=selected_case_id)
        if case_items:
            df_case = pd.DataFrame(case_items)
            display_cols = ["evidence_id", "title", "original_filename", "category", "sha256_hash", "integrity_status", "custodian_name", "created_at"]
            available_cols = [c for c in display_cols if c in df_case.columns]
            st.dataframe(df_case[available_cols], use_container_width=True, hide_index=True)

            col_csv, col_json = st.columns(2)
            with col_csv:
                csv_bytes = df_case.to_csv(index=False).encode("utf-8")
                st.download_button("Export Manifest (CSV)", data=csv_bytes, file_name=f"{selected_case_id}_manifest.csv", mime="text/csv", use_container_width=True)
            with col_json:
                json_bytes = json.dumps(case_items, indent=2).encode("utf-8")
                st.download_button("Export Manifest (JSON)", data=json_bytes, file_name=f"{selected_case_id}_manifest.json", mime="application/json", use_container_width=True)
        else:
            st.info("No evidence registered under this case file.")

        st.markdown("</div>", unsafe_allow_html=True)

    # Tab 3: System Audit Trail Export
    with tab_audit:
        st.markdown("""
        <div class="tv-card">
            <div class="tv-card-header">
                <div>
                    <div class="tv-card-title">Immutable Audit Trail Export</div>
                    <div class="tv-card-subtitle">Full system activity ledger including chained block hashes</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        audit_logs = db.get_all_audit_logs_ascending()
        if audit_logs:
            df_audit = pd.DataFrame(audit_logs)
            st.dataframe(df_audit, use_container_width=True, hide_index=True)

            audit_csv = df_audit.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Export Complete Chained Audit Ledger (CSV)",
                data=audit_csv,
                file_name=f"tracevault_audit_chain_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No audit logs available.")

        st.markdown("</div>", unsafe_allow_html=True)
