"""
Unit tests for KUSTODRA Tamper-Evident Chained Audit Engine.
"""

import tempfile
from pathlib import Path
import pytest
from kustodra.database import DatabaseManager
from kustodra.core.audit_engine import AuditEngine


@pytest.fixture
def audit_db():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = Path(tmp_dir) / "test_audit.db"
        manager = DatabaseManager(db_file)
        yield manager


def test_audit_chain_sequential_integrity(audit_db):
    """Verify that a sequence of audit events builds a 100% valid cryptographic chain."""
    audit = AuditEngine(audit_db)

    # Log several events
    audit.log_event("CASE_CREATED", "USR-01", "Case CASE-01 opened.")
    audit.log_event("EVIDENCE_REGISTERED", "USR-01", "Evidence EV-001 ingested.", evidence_id="EV-001")
    audit.log_event("CUSTODY_TRANSFERRED", "USR-01", "Custody handed over to USR-02.", evidence_id="EV-001")
    audit.log_event("INTEGRITY_CHECK_MATCH", "USR-02", "Verification match confirmed.", evidence_id="EV-001")

    res = audit.verify_audit_chain()
    assert res["is_valid"] is True
    assert res["total_blocks"] == 4
    assert res["verified_blocks"] == 4
    assert res["broken_at_id"] is None


def test_audit_chain_tamper_detection(audit_db):
    """Verify that altering a single field in a historical audit row is detected immediately."""
    audit = AuditEngine(audit_db)

    audit.log_event("EVENT_A", "USR-01", "Legitimate action A")
    audit.log_event("EVENT_B", "USR-01", "Legitimate action B")
    audit.log_event("EVENT_C", "USR-01", "Legitimate action C")

    # Manually tamper with block #2 directly in database
    with audit_db.get_connection() as conn:
        conn.execute("UPDATE audit_logs SET details = 'MALICIOUS_ALTERATION' WHERE audit_id = 2;")
        conn.commit()

    tamper_result = audit.verify_audit_chain()
    assert tamper_result["is_valid"] is False
    assert tamper_result["broken_at_id"] == 2
    assert "tampering detected" in tamper_result["error_details"].lower()
