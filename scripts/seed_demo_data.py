"""
KUSTODRA - Database Baseline Seeding Script
Populates initial system users, investigative cases, cataloged artifacts,
custody transfer logs, integrity verification records, and chained audit logs.
"""

from __future__ import annotations
import shutil
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kustodra.database import DatabaseManager, get_iso_now
from kustodra.core.crypto_engine import CryptoEngine
from kustodra.core.metadata_inspector import MetadataInspector
from kustodra.core.forensic_analyzer import ForensicAnalyzer
from kustodra.core.custody_manager import CustodyManager
from kustodra.core.audit_engine import AuditEngine
from scripts.generate_sample_evidence import create_sample_files


def seed_database(db_path: str | Path | None = None,
                  storage_dir: str | Path | None = None,
                  samples_dir: str | Path | None = None) -> None:
    """Populate database with clean, realistic benchmark records."""
    db_file = Path(db_path) if db_path else PROJECT_ROOT / "data" / "kustodra.db"
    storage_path = Path(storage_dir) if storage_dir else PROJECT_ROOT / "data" / "vault_storage"
    samples_path = Path(samples_dir) if samples_dir else PROJECT_ROOT / "data" / "sample_evidence"

    db = DatabaseManager(db_file)
    audit = AuditEngine(db)
    custody = CustodyManager(db)

    # 1. Ensure sample files exist
    create_sample_files(samples_path)
    storage_path.mkdir(parents=True, exist_ok=True)

    print("[INFO] Seeding neutral system users...")
    users = [
        ("USR-101", "examiner", "Forensic Examiner", "Senior Examiner", "EX-01", "Digital Forensics Laboratory", "examiner@forensics.lab"),
        ("USR-102", "investigator", "Lead Investigator", "Case Investigator", "INV-01", "Cybercrime Investigation Unit", "investigator@investigations.unit"),
        ("USR-103", "custodian", "Vault Custodian", "Asset Custodian", "CUST-01", "Central Vault Depository", "custodian@vault.depository"),
        ("USR-104", "legal", "Legal Liaison", "Compliance Reviewer", "REV-01", "Legal Discovery Office", "legal@discovery.office"),
    ]
    for u in users:
        db.add_user(*u)

    print("[INFO] Seeding investigative cases...")
    cases = [
        ("CASE-2026-0842", "System Intrusion & Unauthorized Data Access", "Lead Investigator", "District Jurisdiction", "Active Investigation", "Investigation into gateway intrusion and data extraction attempts."),
        ("CASE-2026-0915", "Facility Access & Perimeter Security Breach", "Forensic Examiner", "Regional Jurisdiction", "Active Investigation", "Physical security alert investigation with perimeter footage inspection."),
        ("CASE-2026-0114", "Proprietary Data Arbitrage Audit", "Lead Investigator", "Commercial Arbitration", "Pending Trial", "Audit of proprietary specifications and access logs.")
    ]
    for c in cases:
        db.add_case(*c)

    # 2. Register initial artifact items
    print("[INFO] Cataloging forensic artifacts...")

    evidence_defs = [
        {
            "evidence_id": "ART-2026-0001",
            "case_id": "CASE-2026-0842",
            "title": "Gateway Server Access Log",
            "description": "HTTP server access log with authentication probe and extraction records.",
            "source_sample": "server_access_log.log",
            "category": "System & Audit Log",
            "collected_by": "Lead Investigator",
            "registered_by_id": "USR-102",
            "current_custodian_id": "USR-101",  # Transferred to examiner
            "collection_location": "Server Rack B-12, Data Center Alpha",
            "collection_date": "2026-11-18 04:45:00 UTC"
        },
        {
            "evidence_id": "ART-2026-0002",
            "case_id": "CASE-2026-0915",
            "title": "Perimeter Cam 04 Still Frame",
            "description": "Security camera still frame captured during perimeter alarm trigger.",
            "source_sample": "surveillance_cam4_frame109.png",
            "category": "Forensic Still Image",
            "collected_by": "Forensic Examiner",
            "registered_by_id": "USR-101",
            "current_custodian_id": "USR-103",  # In Vault Storage
            "collection_location": "Camera Sensor Network Gate 4",
            "collection_date": "2026-11-18 04:16:30 UTC"
        },
        {
            "evidence_id": "ART-2026-0003",
            "case_id": "CASE-2026-0842",
            "title": "Financial Transaction Audit Ledger",
            "description": "Exported transaction ledger detailing transfer records and account routing.",
            "source_sample": "financial_audit_ledger.csv",
            "category": "Digital Document",
            "collected_by": "Lead Investigator",
            "registered_by_id": "USR-102",
            "current_custodian_id": "USR-101",
            "collection_location": "Seized Workstation Drive",
            "collection_date": "2026-11-18 08:30:00 UTC"
        },
        {
            "evidence_id": "ART-2026-0004",
            "case_id": "CASE-2026-0114",
            "title": "Technical Specification Notes",
            "description": "Specification document outlining system parameters and hashing standards.",
            "source_sample": "confidential_asset_agreement.txt",
            "category": "Digital Document",
            "collected_by": "Lead Investigator",
            "registered_by_id": "USR-102",
            "current_custodian_id": "USR-102",
            "collection_location": "Internal File Share",
            "collection_date": "2026-11-17 16:00:00 UTC"
        },
        {
            "evidence_id": "ART-2026-0005",
            "case_id": "CASE-2026-0842",
            "title": "Suspicious Encrypted Binary Payload",
            "description": "High-entropy binary artifact discovered in system temporary directory.",
            "source_sample": "suspect_encrypted_payload.bin",
            "category": "Encrypted / Packed Payload",
            "collected_by": "Forensic Examiner",
            "registered_by_id": "USR-101",
            "current_custodian_id": "USR-103",
            "collection_location": "System /tmp partition",
            "collection_date": "2026-11-18 05:12:00 UTC"
        }
    ]

    for item in evidence_defs:
        src_file = samples_path / item["source_sample"]
        stored_file = storage_path / f"{item['evidence_id']}_{item['source_sample']}"
        shutil.copy2(src_file, stored_file)

        # Compute cryptographic hashes
        hashes = CryptoEngine.calculate_hashes_from_file(stored_file)
        entropy = CryptoEngine.calculate_shannon_entropy(stored_file)

        # Inspect metadata
        meta = MetadataInspector.inspect_file(stored_file, item["source_sample"])

        evidence_payload = {
            "evidence_id": item["evidence_id"],
            "case_id": item["case_id"],
            "title": item["title"],
            "description": item["description"],
            "category": item["category"],
            "original_filename": item["source_sample"],
            "file_extension": meta["file_extension"],
            "mime_type": meta["mime_type"],
            "magic_signature": meta["magic_signature"],
            "file_size_bytes": meta["file_size_bytes"],
            "sha256_hash": hashes["sha256"],
            "md5_hash": hashes["md5"],
            "sha1_hash": hashes["sha1"],
            "shannon_entropy": entropy,
            "collection_date": item["collection_date"],
            "collection_location": item["collection_location"],
            "collected_by": item["collected_by"],
            "registered_by_id": item["registered_by_id"],
            "current_custodian_id": item["current_custodian_id"],
            "integrity_status": "Not Yet Verified",
            "storage_rel_path": str(stored_file.as_posix()),
            "metadata": meta
        }

        db.add_evidence(evidence_payload)

        # Record chained audit log
        audit.log_event(
            event_type="ARTIFACT_REGISTERED",
            user_id=item["registered_by_id"],
            evidence_id=item["evidence_id"],
            details=f"Artifact {item['evidence_id']} ('{item['title']}') cataloged with SHA-256: {hashes['sha256'][:16]}..."
        )

    # 3. Seed verified status on ART-2026-0001
    print("[INFO] Executing initial baseline integrity check on ART-2026-0001...")
    ev1 = db.get_evidence_by_id("ART-2026-0001")
    if ev1:
        check_id = "CHK-INIT-0001"
        db.add_integrity_check({
            "check_id": check_id,
            "evidence_id": "ART-2026-0001",
            "checked_by_id": "USR-101",
            "check_timestamp": get_iso_now(),
            "expected_sha256": ev1["sha256_hash"],
            "calculated_sha256": ev1["sha256_hash"],
            "result_status": "Match",
            "tamper_details": None,
            "check_mode": "Vault Stored Baseline Check",
            "notes": "Intake verification performed. Bitstream hashes match."
        })
        audit.log_event(
            event_type="INTEGRITY_CHECK_MATCH",
            user_id="USR-101",
            evidence_id="ART-2026-0001",
            details="Cryptographic SHA-256 verification MATCH confirmed against intake baseline."
        )

    # 4. Record initial custody transfers
    print("[INFO] Logging custody transfer events...")
    custody.transfer_custody(
        evidence_id="ART-2026-0001",
        sender_id="USR-102",
        receiver_id="USR-101",
        transfer_reason="Forensic Lab Analysis",
        recorded_by_id="USR-102",
        notes="Transferred from intake to Forensic Laboratory for log parsing.",
        verify_hash_now=True,
        current_file_hash=ev1["sha256_hash"]
    )

    ev2 = db.get_evidence_by_id("ART-2026-0002")
    if ev2:
        custody.transfer_custody(
            evidence_id="ART-2026-0002",
            sender_id="USR-101",
            receiver_id="USR-103",
            transfer_reason="Secure Long-Term Vault Storage",
            recorded_by_id="USR-101",
            notes="Intake inspection completed. Transferred to Central Vault Depository.",
            verify_hash_now=True,
            current_file_hash=ev2["sha256_hash"]
        )

    print("[SUCCESS] Database seeded successfully with clean benchmark records!")


if __name__ == "__main__":
    seed_database()
