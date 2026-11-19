"""
Unit tests for TRACEVAULT Report Generator (ReportLab PDF & Markdown).
"""

import pytest
from tracevault.core.report_generator import ReportGenerator


@pytest.fixture
def evidence_mock():
    return {
        "evidence_id": "EV-2026-9901",
        "case_id": "CASE-2026-CR-0842",
        "case_title": "Network Intrusion Investigation",
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
        "collected_by": "Forensic Examiner",
        "current_custodian_id": "USR-101",
        "custodian_name": "Lead Forensic Examiner",
        "integrity_status": "Verified"
    }


@pytest.fixture
def custody_logs_mock():
    return [
        {
            "transfer_timestamp": "2026-11-19T10:30:00Z",
            "sender_name": "Field Officer",
            "receiver_name": "Lead Forensic Examiner",
            "transfer_reason": "Forensic Lab Analysis",
            "signature_token": "a1b2c3d4e5f60718293a4b5c6d7e8f90"
        }
    ]


@pytest.fixture
def integrity_checks_mock():
    return [
        {
            "check_timestamp": "2026-11-19T11:00:00Z",
            "checked_by_name": "Lead Forensic Examiner",
            "check_mode": "Vault Stored Baseline Check",
            "result_status": "Match",
            "calculated_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }
    ]


def test_generate_pdf_certificate(evidence_mock, custody_logs_mock, integrity_checks_mock):
    """Verify that ReportLab generator outputs valid PDF byte stream when available."""
    if not ReportGenerator.is_available():
        pytest.skip("ReportLab not installed in test environment")

    pdf_bytes = ReportGenerator.generate_evidence_certificate(
        evidence=evidence_mock,
        custody_logs=custody_logs_mock,
        integrity_checks=integrity_checks_mock,
        generated_by_name="Lead Forensic Examiner",
        agency_name="Forensics Laboratory"
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")


def test_generate_markdown_report(evidence_mock, custody_logs_mock, integrity_checks_mock):
    """Verify that Markdown report generator produces formatted documentation."""
    md_report = ReportGenerator.generate_markdown_report(
        evidence=evidence_mock,
        custody_logs=custody_logs_mock,
        integrity_checks=integrity_checks_mock,
        generated_by_name="Lead Forensic Examiner",
        agency_name="Forensics Laboratory"
    )

    assert isinstance(md_report, str)
    assert "EV-2026-9901" in md_report
    assert "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" in md_report
    assert "Chain of Custody Timeline" in md_report
    assert "Integrity Verification Log" in md_report


def test_report_generator_is_available():
    """Verify availability checker returns boolean."""
    assert isinstance(ReportGenerator.is_available(), bool)
