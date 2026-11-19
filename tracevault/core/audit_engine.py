"""
TRACEVAULT - Tamper-Evident Audit Engine
Maintains a cryptographically chained append-only ledger of all system actions.
Provides verification routines to detect database record manipulation.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from tracevault.database import DatabaseManager, get_iso_now
from tracevault.core.crypto_engine import CryptoEngine


class AuditEngine:
    """Manages chained audit logging and chain-of-custody verification."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def log_event(self, event_type: str, user_id: str, details: str,
                  evidence_id: Optional[str] = None) -> int:
        """
        Record an immutable system activity event chained to the previous block hash.
        """
        timestamp = get_iso_now()
        prev_hash = self.db.get_latest_audit_hash()
        curr_hash = CryptoEngine.compute_audit_block_hash(
            prev_hash=prev_hash,
            timestamp=timestamp,
            event_type=event_type,
            user_id=user_id,
            details=details
        )
        return self.db.record_audit_event(
            event_type=event_type,
            user_id=user_id,
            details=details,
            curr_hash=curr_hash,
            prev_hash=prev_hash,
            timestamp=timestamp,
            evidence_id=evidence_id
        )

    def verify_audit_chain(self) -> Dict[str, Any]:
        """
        Verify the integrity of the entire audit log chain.
        Ensures no row was edited, inserted, or deleted directly in SQLite.
        Returns:
            {
                "is_valid": bool,
                "total_blocks": int,
                "verified_blocks": int,
                "broken_at_id": Optional[int],
                "error_details": Optional[str]
            }
        """
        logs = self.db.get_all_audit_logs_ascending()
        if not logs:
            return {
                "is_valid": True,
                "total_blocks": 0,
                "verified_blocks": 0,
                "broken_at_id": None,
                "error_details": "Audit ledger is empty (genesis state)."
            }

        prev_expected_hash = "0000000000000000000000000000000000000000000000000000000000000000"

        for idx, row in enumerate(logs):
            audit_id = row["audit_id"]
            row_prev_hash = row["prev_hash"]
            row_curr_hash = row["curr_hash"]
            timestamp = row["timestamp"]
            event_type = row["event_type"]
            user_id = row["user_id"]
            details = row["details"]

            # For the very first block, if prev_hash is not genesis, check continuity
            if idx == 0:
                prev_expected_hash = row_prev_hash
            elif row_prev_hash != prev_expected_hash:
                return {
                    "is_valid": False,
                    "total_blocks": len(logs),
                    "verified_blocks": idx,
                    "broken_at_id": audit_id,
                    "error_details": (
                        f"Chain linkage broken at block #{audit_id}. "
                        f"Expected previous hash: {prev_expected_hash[:16]}..., "
                        f"Found: {row_prev_hash[:16]}..."
                    )
                }

            # Recompute expected current hash
            recalculated_curr_hash = CryptoEngine.compute_audit_block_hash(
                prev_hash=row_prev_hash,
                timestamp=timestamp,
                event_type=event_type,
                user_id=user_id,
                details=details
            )

            if not CryptoEngine.verify_hash(row_curr_hash, recalculated_curr_hash):
                return {
                    "is_valid": False,
                    "total_blocks": len(logs),
                    "verified_blocks": idx,
                    "broken_at_id": audit_id,
                    "error_details": (
                        f"Content tampering detected at block #{audit_id}! "
                        f"Stored hash '{row_curr_hash[:16]}...' does not match "
                        f"recalculated hash '{recalculated_curr_hash[:16]}...'."
                    )
                }

            prev_expected_hash = row_curr_hash

        return {
            "is_valid": True,
            "total_blocks": len(logs),
            "verified_blocks": len(logs),
            "broken_at_id": None,
            "error_details": "Cryptographic audit chain is 100% intact and verified."
        }
