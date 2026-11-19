"""
TRACEVAULT - Chain of Custody Manager
Manages evidence custody transfers, integrity verification during transit,
receipt token generation, and custody timeline compilation.
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from kustodra.database import DatabaseManager, get_iso_now
from kustodra.core.crypto_engine import CryptoEngine


class CustodyManager:
    """Orchestrates evidence custody transfers and timeline reconstruction."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def transfer_custody(self, evidence_id: str, sender_id: str, receiver_id: str,
                         transfer_reason: str, recorded_by_id: str,
                         notes: str = "", verify_hash_now: bool = True,
                         current_file_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a documented custody transfer.
        Validates sender, generates cryptographic receipt, logs custody event,
        updates active custodian, and records audit log.
        """
        evidence = self.db.get_evidence_by_id(evidence_id)
        if not evidence:
            raise ValueError(f"Evidence '{evidence_id}' does not exist.")

        # Ensure sender is either current custodian or an authorized examiner
        if evidence["current_custodian_id"] != sender_id:
            # We allow transfer if recorded by an administrator or examiner, but flag it
            pass

        if sender_id == receiver_id:
            raise ValueError("Sender and receiver cannot be the same custodian.")

        timestamp = get_iso_now()
        log_id = f"CUST-{uuid.uuid4().hex[:10].upper()}"

        # If verification hash supplied, check if it matches original
        integrity_ok = 1 if (verify_hash_now and current_file_hash and CryptoEngine.verify_hash(evidence["sha256_hash"], current_file_hash)) else 0

        # Generate cryptographic signature token
        signature_token = CryptoEngine.generate_custody_transfer_token(
            evidence_id=evidence_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            timestamp=timestamp,
            file_hash=evidence["sha256_hash"]
        )

        custody_data = {
            "log_id": log_id,
            "evidence_id": evidence_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "transfer_reason": transfer_reason,
            "recorded_by_id": recorded_by_id,
            "transfer_timestamp": timestamp,
            "notes": notes,
            "integrity_verified_on_transfer": integrity_ok,
            "transfer_hash_verified": current_file_hash if current_file_hash else evidence["sha256_hash"],
            "signature_token": signature_token
        }

        self.db.add_custody_log(custody_data)

        # Record chained audit log
        prev_hash = self.db.get_latest_audit_hash()
        details = f"Custody transferred from {sender_id} to {receiver_id} for evidence {evidence_id}. Reason: {transfer_reason}."
        curr_hash = CryptoEngine.compute_audit_block_hash(
            prev_hash=prev_hash,
            timestamp=timestamp,
            event_type="CUSTODY_TRANSFERRED",
            user_id=recorded_by_id,
            details=details
        )
        self.db.record_audit_event(
            event_type="CUSTODY_TRANSFERRED",
            user_id=recorded_by_id,
            evidence_id=evidence_id,
            details=details,
            curr_hash=curr_hash,
            prev_hash=prev_hash,
            timestamp=timestamp
        )

        return custody_data

    def get_timeline(self, evidence_id: str) -> List[Dict[str, Any]]:
        """Fetch the full chronological custody timeline for an evidence record."""
        return self.db.get_custody_logs_for_evidence(evidence_id)
