"""
Unit tests for TRACEVAULT ReportLab PDF Certificate Generator.
"""

import pytest
from tracevault.core.report_generator import ReportGenerator


def test_generate_pdf_certificate():
    """Verify that the ReportLab generator outputs valid PDF byte stream with proper structure."""
    evidence_mock = {
        "evidence_id": "EV-2026-9901",
        "case_id": "CASE-2026-CR-0842",
        "case_title": "Operation Silver Lattice",
        "title": "Compromised Access Log",
        "category": "System & Audit Log",
        "original_filename": "access.log",
        "mime_type": "text/plain",
        "magic_signature": "Plain ASCII Text",
        "file_size_bytes": 1024,
        "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "md5_hash": "d41d8cd98f00b204e9800998ecf8427e",
        "sha1_hash": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
        "shannon_entropy": 4.12,
        "collection_date": "2026-11-19 10:00:00 UTC",
        "collection_location": "Server Rack B-12",
        "collected_by": "Special Agent Ragu Ram",
        "current_custodian_id": "USR-101",
        "custodian_name": "Special Agent Ragu Ram",
        "integrity_status": "Verified"
    }

    custody_logs_mock = [
        {
            "transfer_timestamp": "2026-11-19T10:30:00Z",
            "sender_name": "Detective Sarah Vance",
            "receiver_name": "Special Agent Ragu Ram",
            "transfer_reason": "Forensic Lab Analysis",
            "signature_token": "a1b2c3d4e5f60718293a4b5c6d7e8f90"
        }
    ]

    integrity_checks_mock = [
        {
            "check_timestamp": "2026-11-19T11:00:00Z",
            "checked_by_name": "Special Agent Ragu Ram",
            "check_mode": "Vault Stored Baseline Check",
            "result_status": "Match",
            "calculated_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }
    ]

    pdf_bytes = ReportGenerator.generate_evidence_certificate(
        evidence=evidence_mock,
        custody_logs=custody_logs_mock,
        integrity_checks=integrity_checks_mock,
        generated_by_name="Special Agent Ragu Ram",
        agency_name="Test Digital Forensics Laboratory"
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # Standard PDF header check (%PDF-)
    assert pdf_bytes.startswith(b"%PDF-")
