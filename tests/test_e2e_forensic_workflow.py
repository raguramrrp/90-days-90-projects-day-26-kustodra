"""
End-to-end integration test simulating complete forensic investigation lifecycle:
Ingest -> Inspect -> Verify Match -> Verify Tampered Mismatch -> Custody Transfer -> Audit Chain -> PDF Export.
"""

import tempfile
from pathlib import Path
import pytest

from kustodra.database import DatabaseManager, get_iso_now
from kustodra.core.crypto_engine import CryptoEngine
from kustodra.core.metadata_inspector import MetadataInspector
from kustodra.core.forensic_analyzer import ForensicAnalyzer
from kustodra.core.custody_manager import CustodyManager
from kustodra.core.audit_engine import AuditEngine
from kustodra.core.report_generator import ReportGenerator


def test_complete_evidence_forensic_lifecycle():
    """Execute complete end-to-end evidence ingestion, verification, transfer, and reporting flow."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        db_file = tmp_path / "forensic_vault.db"
        storage_dir = tmp_path / "vault_storage"
        storage_dir.mkdir()

        db = DatabaseManager(db_file)
        audit = AuditEngine(db)
        custody = CustodyManager(db)

        # 1. Setup Users and Case
        db.add_user("USR-101", "rram", "Special Agent Ragu Ram", "Lead Examiner", "FE-8842", "Digital Forensics Lab", "rram@test.internal")
        db.add_user("USR-102", "svance", "Detective Sarah Vance", "Cyber Investigator", "INV-2201", "Taskforce", "svance@test.internal")
        db.add_case("CASE-2026-CR-0842", "Operation Silver Lattice", "Detective Sarah Vance", "Federal Court")

        # 2. Ingest Evidence File
        evidence_content = b"CRITICAL_INCIDENT_NETWORK_PACKET_TRACE_DUMP_2026"
        hashes = CryptoEngine.calculate_hashes_from_bytes(evidence_content)
        entropy = CryptoEngine.calculate_shannon_entropy(evidence_content)
        meta = MetadataInspector.inspect_file(evidence_content, "capture.log")

        ev_id = "EV-2026-E2E"
        target_vault_file = storage_dir / f"{ev_id}_capture.log"
        target_vault_file.write_bytes(evidence_content)

        db.add_evidence({
            "evidence_id": ev_id,
            "case_id": "CASE-2026-CR-0842",
            "title": "Network Packet Dump",
            "description": "Seized network telemetry capture",
            "category": "System & Audit Log",
            "original_filename": "capture.log",
            "file_extension": ".log",
            "mime_type": meta["mime_type"],
            "magic_signature": meta["magic_signature"],
            "file_size_bytes": len(evidence_content),
            "sha256_hash": hashes["sha256"],
            "md5_hash": hashes["md5"],
            "sha1_hash": hashes["sha1"],
            "shannon_entropy": entropy,
            "collection_date": "2026-11-19 08:00:00 UTC",
            "collection_location": "Server Switch Eth0",
            "collected_by": "Detective Sarah Vance",
            "registered_by_id": "USR-102",
            "current_custodian_id": "USR-102",
            "integrity_status": "Not Yet Verified",
            "storage_rel_path": str(target_vault_file.as_posix()),
            "metadata": meta
        })
        audit.log_event("EVIDENCE_REGISTERED", "USR-102", f"Evidence {ev_id} registered.", evidence_id=ev_id)

        # 3. Test Match Verification
        is_match = CryptoEngine.verify_hash(hashes["sha256"], hashes["sha256"])
        assert is_match is True
        db.add_integrity_check({
            "check_id": "CHK-MATCH-1",
            "evidence_id": ev_id,
            "checked_by_id": "USR-101",
            "check_timestamp": get_iso_now(),
            "expected_sha256": hashes["sha256"],
            "calculated_sha256": hashes["sha256"],
            "result_status": "Match",
            "tamper_details": None,
            "check_mode": "Vault Stored Baseline Check",
            "notes": "Intake verification identical match."
        })
        audit.log_event("INTEGRITY_CHECK_MATCH", "USR-101", f"Match confirmed for {ev_id}.", evidence_id=ev_id)

        ev_record = db.get_evidence_by_id(ev_id)
        assert ev_record["integrity_status"] == "Verified"

        # 4. Test Deliberate Tampering Detection (Mismatch)
        tampered_content = b"CRITICAL_INCIDENT_NETWORK_PACKET_TRACE_DUMP_TAMPERED"
        tampered_hashes = CryptoEngine.calculate_hashes_from_bytes(tampered_content)
        assert tampered_hashes["sha256"] != hashes["sha256"]

        is_tampered_match = CryptoEngine.verify_hash(hashes["sha256"], tampered_hashes["sha256"])
        assert is_tampered_match is False

        db.add_integrity_check({
            "check_id": "CHK-MISMATCH-1",
            "evidence_id": ev_id,
            "checked_by_id": "USR-101",
            "check_timestamp": get_iso_now(),
            "expected_sha256": hashes["sha256"],
            "calculated_sha256": tampered_hashes["sha256"],
            "result_status": "Mismatch",
            "tamper_details": "Bitstream altered. Differing SHA-256.",
            "check_mode": "Tampered Sample Test",
            "notes": "Tampering detected in exhibit payload."
        })
        audit.log_event("INTEGRITY_CHECK_MISMATCH", "USR-101", f"MISMATCH alert on {ev_id}!", evidence_id=ev_id)

        ev_tampered = db.get_evidence_by_id(ev_id)
        assert ev_tampered["integrity_status"] == "Integrity Mismatch"

        # 5. Custody Transfer
        custody.transfer_custody(
            evidence_id=ev_id,
            sender_id="USR-102",
            receiver_id="USR-101",
            transfer_reason="Forensic Lab Analysis",
            recorded_by_id="USR-101",
            notes="Transferred to Lab Examiner for forensic timeline reconstruction.",
            verify_hash_now=True,
            current_file_hash=hashes["sha256"]
        )
        ev_transferred = db.get_evidence_by_id(ev_id)
        assert ev_transferred["current_custodian_id"] == "USR-101"

        # 6. Verify Complete Cryptographic Audit Chain
        chain_res = audit.verify_audit_chain()
        assert chain_res["is_valid"] is True
        assert chain_res["total_blocks"] >= 4

        # 7. Compile Official Court PDF Certificate
        custody_logs = db.get_custody_logs_for_evidence(ev_id)
        integrity_checks = db.get_integrity_checks_for_evidence(ev_id)
        pdf_bytes = ReportGenerator.generate_evidence_certificate(
            evidence=ev_transferred,
            custody_logs=custody_logs,
            integrity_checks=integrity_checks,
            generated_by_name="Special Agent Ragu Ram",
            agency_name="Federal Digital Forensics Lab"
        )
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 2000
