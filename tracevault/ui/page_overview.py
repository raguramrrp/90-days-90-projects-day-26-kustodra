"""
TRACEVAULT - Overview Dashboard Page
Presents concise evidence metrics, recent evidence repository summary,
and chronological forensic activity stream.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from tracevault.database import DatabaseManager
from tracevault.ui.components import render_metric_cards, render_status_badge


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the Overview Dashboard."""
    st.markdown("### Evidence Overview")
    st.markdown("<div style='font-size: 13px; color: #68736F; margin-bottom: 16px;'>Monitor registered evidence, integrity verification and custody activity across active cases.</div>", unsafe_allow_html=True)

    metrics = db.get_dashboard_metrics()
    render_metric_cards(
        total=metrics["total_evidence"],
        verified=metrics["verified_count"],
        pending=metrics["pending_count"],
        mismatch=metrics["mismatch_count"] + metrics["failed_count"]
    )

    col_btn, _ = st.columns([2, 5])
    with col_btn:
        if st.button("+ Register New Evidence", use_container_width=True):
            st.session_state["active_nav"] = "Register Evidence"
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 1. Recent Evidence Table
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("""
        <div class="tv-card">
            <div class="tv-card-header">
                <div>
                    <div class="tv-card-title">Recent Evidence</div>
                    <div class="tv-card-subtitle">Latest digital artifacts registered into vault custody</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        evidence_list = db.get_evidence_list()[:8]
        if evidence_list:
            rows_html = ""
            for ev in evidence_list:
                status_html = render_status_badge(ev["integrity_status"])
                reg_date = ev["created_at"][:10] if ev.get("created_at") else "N/A"
                rows_html += f"""
                <tr style="border-bottom: 1px solid #E1E6E3; font-size: 12px;">
                    <td style="padding: 8px 6px; font-weight: 600;">
                        <a href="?evidence_id={ev['evidence_id']}" style="color: #315F50; text-decoration: none;">{ev['evidence_id']}</a>
                    </td>
                    <td style="padding: 8px 6px;"><b>{ev['title']}</b><br><span style="color: #68736F; font-size: 11px;">{ev['original_filename']}</span></td>
                    <td style="padding: 8px 6px; color: #4A5653;">{ev['category']}</td>
                    <td style="padding: 8px 6px; color: #68736F;">{reg_date}</td>
                    <td style="padding: 8px 6px;">{ev.get('custodian_name', 'N/A')}</td>
                    <td style="padding: 8px 6px;">{status_html}</td>
                </tr>
                """
            st.markdown(f"""
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <thead>
                    <tr style="border-bottom: 2px solid #E1E6E3; font-size: 11px; color: #68736F; text-transform: uppercase;">
                        <th style="padding: 6px;">ID</th>
                        <th style="padding: 6px;">Evidence Name</th>
                        <th style="padding: 6px;">Category</th>
                        <th style="padding: 6px;">Registered</th>
                        <th style="padding: 6px;">Custodian</th>
                        <th style="padding: 6px;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.info("No evidence registered yet. Click 'Register New Evidence' to begin.")

        st.markdown("</div>", unsafe_allow_html=True)

    # 2. Recent Activity Chronological Stream
    with col_right:
        st.markdown("""
        <div class="tv-card">
            <div class="tv-card-header">
                <div>
                    <div class="tv-card-title">Recent Activity</div>
                    <div class="tv-card-subtitle">Chronological ledger of verified forensic events</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        audit_logs = db.get_audit_logs(limit=8)
        if audit_logs:
            for log in audit_logs:
                time_str = log["timestamp"][:19].replace("T", " ") if log.get("timestamp") else "N/A"
                event_name = log["event_type"].replace("_", " ").title()

                # Clean icon or tag based on event
                badge_color = "#315F50"
                if "MATCH" in log["event_type"]:
                    badge_color = "#287A54"
                elif "MISMATCH" in log["event_type"] or "TAMPER" in log["event_type"]:
                    badge_color = "#B74747"
                elif "CUSTODY" in log["event_type"]:
                    badge_color = "#B77B29"

                st.markdown(f"""
                <div class="tv-timeline-item">
                    <div class="tv-timeline-time">{time_str} UTC</div>
                    <div class="tv-timeline-title">
                        <span style="color: {badge_color}; font-weight: 700;">{event_name}</span>
                        {f"&bull; <span style='font-family: monospace; font-size: 11px;'>{log['evidence_id']}</span>" if log.get('evidence_id') else ''}
                    </div>
                    <div class="tv-timeline-desc">{log['details']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No activity recorded yet.")

        st.markdown("</div>", unsafe_allow_html=True)
