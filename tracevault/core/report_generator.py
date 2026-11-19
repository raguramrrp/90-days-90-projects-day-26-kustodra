"""
TRACEVAULT - Forensic Report Generator
Produces court-ready, publication-grade Digital Evidence & Chain-of-Custody
certificates and audit reports in PDF format using ReportLab.
"""

from __future__ import annotations
import io
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

from tracevault.database import get_iso_now


class ReportGenerator:
    """Generates standardized PDF and tabular evidence documentation."""

    @staticmethod
    def generate_evidence_certificate(evidence: Dict[str, Any],
                                     custody_logs: List[Dict[str, Any]],
                                     integrity_checks: List[Dict[str, Any]],
                                     generated_by_name: str,
                                     agency_name: str = "Digital Forensics & Evidence Integrity Workstation") -> bytes:
        """
        Build an official, publication-quality PDF Evidence Custody & Integrity Certificate.
        Returns PDF bytes suitable for browser download or disk saving.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Typography Styles matching workstation aesthetics
        primary_accent = colors.HexColor("#315F50")
        dark_text = colors.HexColor("#202927")
        secondary_text = colors.HexColor("#68736F")
        border_color = colors.HexColor("#E1E6E3")
        muted_bg = colors.HexColor("#F4F6F5")
        success_green = colors.HexColor("#287A54")
        danger_red = colors.HexColor("#B74747")

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=primary_accent
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=secondary_text
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=primary_accent,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=dark_text
        )

        mono_style = ParagraphStyle(
            "Mono",
            parent=styles["Normal"],
            fontName="Courier",
            fontSize=7.5,
            leading=10,
            textColor=dark_text
        )

        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7,
            leading=10,
            textColor=secondary_text
        )

        story = []

        # 1. Header Banner
        report_ref = f"REP-{evidence['evidence_id']}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"
        story.append(Paragraph("TRACEVAULT &bull; FORENSIC EVIDENCE & CHAIN-OF-CUSTODY CERTIFICATE", title_style))
        story.append(Paragraph(f"{agency_name} | Document Reference: <b>{report_ref}</b>", subtitle_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=primary_accent, spaceAfter=10))

        # 2. General Case & Evidence Identity Table
        story.append(Paragraph("1. EVIDENCE RECORD & CASE IDENTITY", section_heading))
        identity_data = [
            [
                Paragraph("<b>Evidence ID:</b>", body_style),
                Paragraph(f"<b>{evidence['evidence_id']}</b>", body_style),
                Paragraph("<b>Case Reference:</b>", body_style),
                Paragraph(f"{evidence['case_id']} &mdash; {evidence.get('case_title', 'N/A')}", body_style)
            ],
            [
                Paragraph("<b>Evidence Title:</b>", body_style),
                Paragraph(evidence["title"], body_style),
                Paragraph("<b>Forensic Category:</b>", body_style),
                Paragraph(evidence["category"], body_style)
            ],
            [
                Paragraph("<b>Original Filename:</b>", body_style),
                Paragraph(evidence["original_filename"], body_style),
                Paragraph("<b>Detected MIME / Signature:</b>", body_style),
                Paragraph(f"{evidence['mime_type']} ({evidence.get('magic_signature', 'N/A')})", body_style)
            ],
            [
                Paragraph("<b>Exact File Size:</b>", body_style),
                Paragraph(f"{evidence['file_size_bytes']:,} Bytes", body_style),
                Paragraph("<b>Current Custodian:</b>", body_style),
                Paragraph(f"{evidence.get('custodian_name', evidence['current_custodian_id'])}", body_style)
            ],
            [
                Paragraph("<b>Collection Date:</b>", body_style),
                Paragraph(str(evidence["collection_date"]), body_style),
                Paragraph("<b>Current Status:</b>", body_style),
                Paragraph(f"<b>{evidence['integrity_status']}</b>", body_style)
            ]
        ]

        t_identity = Table(identity_data, colWidths=[110, 160, 120, 150])
        t_identity.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t_identity)
        story.append(Spacer(1, 10))

        # 3. Cryptographic Hashes (Registration Baseline)
        story.append(Paragraph("2. CRYPTOGRAPHIC BASELINE FINGERPRINTS (RECORDED AT INGESTION)", section_heading))
        hash_data = [
            [Paragraph("<b>Algorithm</b>", body_style), Paragraph("<b>Cryptographic Digest Value (Hex)</b>", body_style)],
            [Paragraph("<b>SHA-256</b>", body_style), Paragraph(evidence["sha256_hash"], mono_style)],
            [Paragraph("<b>MD5</b>", body_style), Paragraph(evidence["md5_hash"], mono_style)],
            [Paragraph("<b>SHA-1</b>", body_style), Paragraph(evidence["sha1_hash"], mono_style)],
            [Paragraph("<b>Shannon Entropy</b>", body_style), Paragraph(f"{evidence['shannon_entropy']:.4f} / 8.0000 bits per byte", body_style)],
        ]
        t_hash = Table(hash_data, colWidths=[110, 430])
        t_hash.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), muted_bg),
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t_hash)
        story.append(Spacer(1, 10))

        # 4. Chain of Custody Ledger Table
        story.append(Paragraph("3. CHAIN-OF-CUSTODY TRANSFER TIMELINE", section_heading))
        if custody_logs:
            custody_headers = [
                Paragraph("<b>Date / UTC Time</b>", body_style),
                Paragraph("<b>Released By (Sender)</b>", body_style),
                Paragraph("<b>Received By</b>", body_style),
                Paragraph("<b>Transfer Reason</b>", body_style),
                Paragraph("<b>Receipt Token</b>", body_style)
            ]
            custody_rows = [custody_headers]
            for log in custody_logs:
                token_snip = log.get("signature_token", "N/A")[:16] + "..." if log.get("signature_token") else "N/A"
                sender_display = log.get("sender_name") or log.get("sender_id", "N/A")
                receiver_display = log.get("receiver_name") or log.get("receiver_id", "N/A")
                custody_rows.append([
                    Paragraph(log.get("transfer_timestamp", "")[:19].replace("T", " "), body_style),
                    Paragraph(sender_display, body_style),
                    Paragraph(receiver_display, body_style),
                    Paragraph(log.get("transfer_reason", "Transfer"), body_style),
                    Paragraph(token_snip, mono_style)
                ])
            t_custody = Table(custody_rows, colWidths=[90, 110, 110, 130, 100])
            t_custody.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), muted_bg),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(t_custody)
        else:
            story.append(Paragraph("<i>No custody transfers recorded. Evidence remains with initial collecting custodian.</i>", body_style))
        story.append(Spacer(1, 10))

        # 5. Integrity Verification Log
        story.append(Paragraph("4. INTEGRITY VERIFICATION AUDIT TRAIL", section_heading))
        if integrity_checks:
            verif_headers = [
                Paragraph("<b>Verification Timestamp</b>", body_style),
                Paragraph("<b>Examiner</b>", body_style),
                Paragraph("<b>Mode</b>", body_style),
                Paragraph("<b>Result</b>", body_style),
                Paragraph("<b>Calculated SHA-256 Digest</b>", body_style)
            ]
            verif_rows = [verif_headers]
            for chk in integrity_checks:
                status_color = success_green if chk.get("result_status") == "Match" else danger_red
                status_text = f"<font color='{status_color.hexval()}'><b>{chk.get('result_status', 'Unknown')}</b></font>"
                calc_hash = chk.get("calculated_sha256", "")
                calc_hash_display = calc_hash[:20] + "..." if len(calc_hash) > 20 else calc_hash
                examiner_display = chk.get("checked_by_name") or chk.get("checked_by_id", "Examiner")
                timestamp_display = str(chk.get("check_timestamp", ""))[:19].replace("T", " ")
                verif_rows.append([
                    Paragraph(timestamp_display, body_style),
                    Paragraph(examiner_display, body_style),
                    Paragraph(chk.get("check_mode", "Upload"), body_style),
                    Paragraph(status_text, body_style),
                    Paragraph(calc_hash_display, mono_style)
                ])
            t_verif = Table(verif_rows, colWidths=[95, 95, 80, 80, 190])
            t_verif.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), muted_bg),
                ('GRID', (0, 0), (-1, -1), 0.5, border_color),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(t_verif)
        else:
            story.append(Paragraph("<i>No formal verification checks executed on this evidence item.</i>", body_style))
        story.append(Spacer(1, 12))

        # 6. Legal & Forensic Disclaimers (Required by Specification)
        story.append(Paragraph("5. FORENSIC NOTICE & DISCLOSURE STATEMENT", section_heading))
        disclaimer_text = (
            "<b>Cryptographic Integrity Scope:</b> A SHA-256 hash proves mathematically whether file contents "
            "match a previously recorded hash; it does not independently prove who created the file or whether "
            "the original evidence was authentic. Integrity is contingent on custody continuity, secure registry "
            "access, and tamper-evident audit logging. This document was generated automatically by the TRACEVAULT "
            "workstation and reflects state recorded in the immutable database ledger at time of generation."
        )
        story.append(Paragraph(disclaimer_text, disclaimer_style))
        story.append(Spacer(1, 8))

        cert_footer = (
            f"Report Generated: <b>{get_iso_now()} UTC</b> &bull; Examiner: <b>{generated_by_name}</b> &bull; "
            f"Workstation: TRACEVAULT v1.0 &bull; Page 1 of 1"
        )
        story.append(Paragraph(cert_footer, subtitle_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
