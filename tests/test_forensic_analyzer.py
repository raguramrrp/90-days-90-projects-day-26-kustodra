"""
Unit tests for TRACEVAULT Forensic Analyzer and Classifier.
"""

import pytest
from tracevault.core.forensic_analyzer import ForensicAnalyzer


def test_classify_evidence():
    """Verify evidence categorization heuristic rules."""
    # Forensic disk image
    c1 = ForensicAnalyzer.classify_evidence("disk.raw", "UNKNOWN", "application/octet-stream", 6.5, 1000)
    assert c1["category"] == "Forensic Disk Image"

    # Surveillance Video
    c2 = ForensicAnalyzer.classify_evidence("cctv_feed.mp4", "MP4_FTYP", "video/mp4", 7.1, 5000)
    assert c2["category"] == "Surveillance Video"

    # System & Audit Log
    c3 = ForensicAnalyzer.classify_evidence("auth_server.log", "PLAIN_TEXT", "text/plain", 3.8, 1200)
    assert c3["category"] == "System & Audit Log"

    # Executable Artifact
    c4 = ForensicAnalyzer.classify_evidence("payload.exe", "EXE_PE", "application/x-dosexec", 6.9, 8000)
    assert c4["category"] == "Executable / Malware Artifact"


def test_interpret_entropy():
    """Verify entropy interpretation levels."""
    zero_eval = ForensicAnalyzer.interpret_entropy(0.0)
    assert "Zero" in zero_eval["level"]

    text_eval = ForensicAnalyzer.interpret_entropy(4.1)
    assert "Low" in text_eval["level"]

    crypto_eval = ForensicAnalyzer.interpret_entropy(7.9)
    assert "High" in crypto_eval["level"]


def test_evaluate_risk():
    """Verify explainable risk score calculation."""
    # Clean verified evidence
    clean_risk = ForensicAnalyzer.evaluate_risk(
        is_spoofed=False,
        entropy=4.2,
        integrity_status="Verified",
        has_duplicates=False
    )
    assert clean_risk["score"] < 25
    assert clean_risk["level"] == "Normal / Clean Integrity"

    # Compromised evidence with mismatch and spoofed header
    tampered_risk = ForensicAnalyzer.evaluate_risk(
        is_spoofed=True,
        entropy=7.8,
        integrity_status="Integrity Mismatch",
        has_duplicates=True
    )
    assert tampered_risk["score"] >= 80
    assert tampered_risk["level"] == "Critical Risk"
    assert len(tampered_risk["indicators"]) >= 3


def test_generate_evidence_summary():
    """Verify intelligent forensic summary text generation."""
    summary = ForensicAnalyzer.generate_evidence_summary(
        title="Web Server Log",
        filename="access.log",
        category="System & Audit Log",
        size_formatted="12.50 KB",
        mime_type="text/plain",
        entropy=4.12,
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        is_spoofed=False,
        duplicates_count=0
    )
    assert "Web Server Log" in summary
    assert "System & Audit Log" in summary
    assert "Unique hash fingerprint" in summary
