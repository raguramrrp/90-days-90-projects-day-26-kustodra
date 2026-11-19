"""
TRACEVAULT - Database Seeding Script
Populates initial users, forensic cases, registered evidence,
custody transfers, integrity checks, and chained audit logs.
"""

from __future__ import annotations
import shutil
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tracevault.database import DatabaseManager, get_iso_now
from tracevault.core.crypto_engine import CryptoEngine
from tracevault.core.metadata_inspector import MetadataInspector
from tracevault.core.forensic_analyzer import ForensicAnalyzer
from tracevault.core.custody_manager import CustodyManager
from tracevault.core.audit_engine import AuditEngine
from scripts.generate_sample_evidence import create_sample_files


def seed_database(db_path: str | Path | None = None,
                  storage_dir: str | Path | None = None,
                  samples_dir: str | Path | None = None) -> None:
    """Populate database with reproducible, realistic forensic demo records."""
    db_file = Path(db_path) if db_path else PROJECT_ROOT / "data" / "tracevault.db"
    storage_path = Path(storage_dir) if storage_dir else PROJECT_ROOT / "data" / "vault_storage"
    samples_path = Path(samples_dir) if samples_dir else PROJECT_ROOT / "data" / "sample_evidence"

    db = DatabaseManager(db_file)
    audit = AuditEngine(db)
    custody = CustodyManager(db)

    # 1. Ensure sample files exist
    create_sample_files(samples_path)

    storage_path.mkdir(parents=True, exist_ok=True)

    print("[INFO] Seeding forensic system users...")
    users = [
        ("USR-101", "rram", "Special Agent Ragu Ram", "Lead Forensic Examiner", "FE-8842", "Digital Forensics & Cyber Defense Lab", "rram@tracevault.internal"),
        ("USR-102", "svance", "Detective Sarah Vance", "Senior Cyber Investigator", "INV-2201", "Financial Crimes Task Force", "svance@taskforce.gov"),
        ("USR-103", "mchen", "Marcus Chen", "Evidence Vault Custodian", "CUST-4419", "Central Evidence Depository", "mchen@vault.internal"),
        ("USR-104", "erostova", "Elena Rostova", "Digital Evidence Prosecutor", "PROS-1092", "Office of the State Attorney", "erostova@justice.gov"),
    ]
    for u in users:
        db.add_user(*u)

    print("[INFO] Seeding investigative cases...")
    cases = [
        ("CASE-2026-CR-0842", "Operation Silver Lattice: Offshore Exfiltration & Wire Fraud", "Detective Sarah Vance", "Eastern Judicial District", "Active Investigation", "Investigation into unauthorized wire transfers and API key theft."),
        ("CASE-2026-CR-0915", "Incident Sentinel: Perimeter CCTV Tampering & Breach", "Special Agent Ragu Ram", "Metro Security Command", "Active Investigation", "Physical perimeter penetration combined with attempted CCTV log wiping."),
        ("CASE-2026-CV-0114", "Aura Holdings vs Pacific Capital: Code Leak Arbitration", "Detective Sarah Vance", "Commercial Arbitration Tribunal", "Pending Trial", "Proprietary algorithmic model misappropriation claim.")
    ]
    for c in cases:
        db.add_case(*c)

    # 2. Register initial evidence items
    print("[INFO] Registering forensic evidence artifacts...")

    evidence_defs = [
        {
            "evidence_id": "EV-2026-0001",
            "case_id": "CASE-2026-CR-0842",
            "title": "Compromised Gateway Server Access Log",
            "description": "Raw Apache HTTP access log containing SQL injection probe and exfiltration requests.",
            "source_sample": "server_access_log.log",
            "category": "System & Audit Log",
            "collected_by": "Detective Sarah Vance",
            "registered_by_id": "USR-102",
            "current_custodian_id": "USR-101",  # Transferred to examiner
            "collection_location": "Server Rack B-12, Data Center Alpha, Rack Mount IP 10.0.4.1",
            "collection_date": "2026-11-18 04:45:00 UTC"
        },
        {
            "evidence_id": "EV-2026-0002",
            "case_id": "CASE-2026-CR-0915",
            "title": "Perimeter Cam 04 High-Resolution Still Frame",
            "description": "Security camera still frame captured at perimeter sector 4 during alarm trigger.",
            "source_sample": "surveillance_cam4_frame109.png",
            "category": "Forensic Still Image",
            "collected_by": "Special Agent Ragu Ram",
            "registered_by_id": "USR-101",
            "current_custodian_id": "USR-103",  # In Vault Storage
            "collection_location": "Security Network Gateway 192.168.1.105",
            "collection_date": "2026-11-18 04:16:30 UTC"
        },
        {
            "evidence_id": "EV-2026-0003",
            "case_id": "CASE-2026-CR-0842",
            "title": "Suspect Offshore Wire Transfer CSV Ledger",
            "description": "Exported transaction ledger detailing illicit bank transfers to offshore accounts.",
            "source_sample": "financial_audit_ledger.csv",
            "category": "Digital Document",
            "collected_by": "Detective Sarah Vance",
            "registered_by_id": "USR-102",
            "current_custodian_id": "USR-101",
            "collection_location": "Seized Laptop Workstation DESKTOP-FC89",
            "collection_date": "2026-11-18 08:30:00 UTC"
        },
        {
            "evidence_id": "EV-2026-0004",
            "case_id": "CASE-2026-CV-0114",
            "title": "Technical Architecture Specification Note",
            "description": "Technical document outlining security parameters and hashing standards.",
            "source_sample": "confidential_asset_agreement.txt",
            "category": "Digital Document",
            "collected_by": "Detective Sarah Vance",
            "registered_by_id": "USR-102",
            "current_custodian_id": "USR-102",
            "collection_location": "Workstation File Share",
            "collection_date": "2026-11-17 16:00:00 UTC"
        },
        {
            "evidence_id": "EV-2026-0005",
            "case_id": "CASE-2026-CR-0842",
            "title": "Unidentified Encrypted Payload Binary",
            "description": "High-entropy binary artifact discovered in root directory /tmp/cache_sys.bin.",
            "source_sample": "suspect_encrypted_payload.bin",
            "category": "Encrypted / Packed Payload",
            "collected_by": "Special Agent Ragu Ram",
            "registered_by_id": "USR-101",
            "current_custodian_id": "USR-103",
            "collection_location": "Server /tmp partition root",
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
            event_type="EVIDENCE_REGISTERED",
            user_id=item["registered_by_id"],
            evidence_id=item["evidence_id"],
            details=f"Evidence {item['evidence_id']} ('{item['title']}') registered with SHA-256: {hashes['sha256'][:16]}..."
        )

    # 3. Seed verified status on EV-2026-0001
    print("[INFO] Executing initial baseline integrity check on EV-2026-0001...")
    ev1 = db.get_evidence_by_id("EV-2026-0001")
    if ev1:
        check_id = "CHK-INIT-0001"
        db.add_integrity_check({
            "check_id": check_id,
            "evidence_id": "EV-2026-0001",
            "checked_by_id": "USR-101",
            "check_timestamp": get_iso_now(),
            "expected_sha256": ev1["sha256_hash"],
            "calculated_sha256": ev1["sha256_hash"],
            "result_status": "Match",
            "tamper_details": None,
            "check_mode": "Vault Stored Baseline Check",
            "notes": "Initial intake cryptographic verification performed by Lead Examiner. Hashes match identically."
        })
        audit.log_event(
            event_type="INTEGRITY_CHECK_MATCH",
            user_id="USR-101",
            evidence_id="EV-2026-0001",
            details="Cryptographic SHA-256 verification MATCH confirmed against intake baseline."
        )

    # 4. Record initial custody transfers for EV-2026-0001 and EV-2026-0002
    print("[INFO] Logging custody transfer events...")
    custody.transfer_custody(
        evidence_id="EV-2026-0001",
        sender_id="USR-102",
        receiver_id="USR-101",
        transfer_reason="Forensic Lab Analysis",
        recorded_by_id="USR-102",
        notes="Transferred from crime scene intake to Cyber Forensics Lab workstation for deep packet and log parsing.",
        verify_hash_now=True,
        current_file_hash=ev1["sha256_hash"]
    )

    ev2 = db.get_evidence_by_id("EV-2026-0002")
    if ev2:
        custody.transfer_custody(
            evidence_id="EV-2026-0002",
            sender_id="USR-101",
            receiver_id="USR-103",
            transfer_reason="Secure Long-Term Vault Storage",
            recorded_by_id="USR-101",
            notes="Intake and image EXIF verification complete; transferred to Central Vault for court lockbox custody.",
            verify_hash_now=True,
            current_file_hash=ev2["sha256_hash"]
        )

    print("[SUCCESS] Database seeded successfully with realistic forensic records!")


if __name__ == "__main__":
    seed_database()
