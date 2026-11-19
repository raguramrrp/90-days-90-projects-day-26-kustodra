"""
Unit tests for KUSTODRA Database and Custody Management.
"""

import tempfile
from pathlib import Path
import pytest
from kustodra.database import DatabaseManager, get_iso_now
from kustodra.core.custody_manager import CustodyManager


@pytest.fixture
def test_db():
    """Create an isolated test database in a temporary directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = Path(tmp_dir) / "test_kustodra.db"
        manager = DatabaseManager(db_file)
        # Add basic test user and case
        manager.add_user("USR-01", "testuser", "Examiner Alice", "Lead Examiner", "FE-100", "Cyber Unit", "alice@test.org")
        manager.add_user("USR-02", "bob", "Detective Bob", "Investigator", "INV-200", "Police Taskforce", "bob@test.org")
        manager.add_case("CASE-01", "Test Incident", "Detective Bob", "Central Court")
        yield manager


def test_add_and_get_evidence(test_db):
    """Test registering evidence and querying it back."""
    ev_data = {
        "evidence_id": "EV-TEST-001",
        "case_id": "CASE-01",
        "title": "Seized USB Drive Dump",
        "description": "Raw memory capture",
        "category": "Forensic Disk Image",
        "original_filename": "dump.raw",
        "file_extension": ".raw",
        "mime_type": "application/octet-stream",
        "magic_signature": "RAW Container",
        "file_size_bytes": 1048576,
        "sha256_hash": "a" * 64,
        "md5_hash": "b" * 32,
        "sha1_hash": "c" * 40,
        "shannon_entropy": 7.42,
        "collection_date": "2026-11-19 10:00:00 UTC",
        "collection_location": "Office Room 302",
        "collected_by": "Detective Bob",
        "registered_by_id": "USR-01",
        "current_custodian_id": "USR-01",
        "integrity_status": "Not Yet Verified",
        "storage_rel_path": "data/vault_storage/EV-TEST-001_dump.raw",
        "metadata": {"test": "val"}
    }
    test_db.add_evidence(ev_data)

    retrieved = test_db.get_evidence_by_id("EV-TEST-001")
    assert retrieved is not None
    assert retrieved["title"] == "Seized USB Drive Dump"
    assert retrieved["sha256_hash"] == "a" * 64
    assert retrieved["current_custodian_id"] == "USR-01"


def test_duplicate_hash_detection(test_db):
    """Test identifying identical hashes across evidence records."""
    common_hash = "d" * 64
    ev1 = {
        "evidence_id": "EV-DUP-001",
        "case_id": "CASE-01",
        "title": "Original Capture",
        "category": "Digital Document",
        "original_filename": "file1.txt",
        "file_extension": ".txt",
        "mime_type": "text/plain",
        "file_size_bytes": 100,
        "sha256_hash": common_hash,
        "md5_hash": "m1" * 16,
        "sha1_hash": "s1" * 20,
        "shannon_entropy": 3.5,
        "collection_date": "2026-11-19 10:00:00 UTC",
        "collected_by": "Detective Bob",
        "registered_by_id": "USR-01",
        "current_custodian_id": "USR-01",
        "storage_rel_path": "path1",
        "metadata": {}
    }
    ev2 = dict(ev1, evidence_id="EV-DUP-002", title="Identical Exhibit", original_filename="copy.txt")

    test_db.add_evidence(ev1)
    test_db.add_evidence(ev2)

    dups = test_db.find_duplicates_by_hash(common_hash, exclude_id="EV-DUP-001")
    assert len(dups) == 1
    assert dups[0]["evidence_id"] == "EV-DUP-002"


def test_custody_transfer_workflow(test_db):
    """Test transferring evidence custody from Alice to Bob."""
    ev_data = {
        "evidence_id": "EV-CUST-001",
        "case_id": "CASE-01",
        "title": "Network Log",
        "category": "System & Audit Log",
        "original_filename": "net.log",
        "file_extension": ".log",
        "mime_type": "text/plain",
        "file_size_bytes": 500,
        "sha256_hash": "f" * 64,
        "md5_hash": "m" * 32,
        "sha1_hash": "s" * 40,
        "shannon_entropy": 4.0,
        "collection_date": "2026-11-19 10:00:00 UTC",
        "collected_by": "Alice",
        "registered_by_id": "USR-01",
        "current_custodian_id": "USR-01",
        "storage_rel_path": "path",
        "metadata": {}
    }
    test_db.add_evidence(ev_data)

    custody_mgr = CustodyManager(test_db)
    custody_mgr.transfer_custody(
        evidence_id="EV-CUST-001",
        sender_id="USR-01",
        receiver_id="USR-02",
        transfer_reason="Courtroom Presentation",
        recorded_by_id="USR-01",
        notes="Transferred for hearing exhibit marking.",
        verify_hash_now=True,
        current_file_hash="f" * 64
    )

    updated_ev = test_db.get_evidence_by_id("EV-CUST-001")
    assert updated_ev["current_custodian_id"] == "USR-02"

    logs = custody_mgr.get_timeline("EV-CUST-001")
    assert len(logs) == 1
    assert logs[0]["sender_id"] == "USR-01"
    assert logs[0]["receiver_id"] == "USR-02"
    assert logs[0]["integrity_verified_on_transfer"] == 1
    assert len(logs[0]["signature_token"]) == 64
