"""
TRACEVAULT - Database Management Module
Handles SQLite schema definition, migrations, and parameterized data access.
"""

from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple


def get_iso_now() -> str:
    """Return the current UTC timestamp formatted as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


class DatabaseManager:
    """Manages SQLite connection, schema initialization, and transactional queries."""

    def __init__(self, db_path: str | Path = "data/tracevault.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Create and yield a SQLite connection, automatically closing it on exit."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_schema(self) -> None:
        """Create database tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                badge_number TEXT,
                organization TEXT NOT NULL,
                email TEXT,
                created_at TEXT NOT NULL
            );
            """)

            # 2. Cases Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                case_title TEXT NOT NULL,
                investigator_lead TEXT NOT NULL,
                jurisdiction TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active Investigation',
                description TEXT,
                created_at TEXT NOT NULL
            );
            """)

            # 3. Evidence Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_extension TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                magic_signature TEXT,
                file_size_bytes INTEGER NOT NULL,
                sha256_hash TEXT NOT NULL,
                md5_hash TEXT NOT NULL,
                sha1_hash TEXT NOT NULL,
                shannon_entropy REAL NOT NULL,
                collection_date TEXT NOT NULL,
                collection_location TEXT,
                collected_by TEXT NOT NULL,
                registered_by_id TEXT NOT NULL,
                current_custodian_id TEXT NOT NULL,
                integrity_status TEXT NOT NULL DEFAULT 'Not Yet Verified',
                last_verified_at TEXT,
                last_verified_by TEXT,
                storage_rel_path TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases(case_id),
                FOREIGN KEY (registered_by_id) REFERENCES users(user_id),
                FOREIGN KEY (current_custodian_id) REFERENCES users(user_id)
            );
            """)

            # 4. Custody Logs Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS custody_logs (
                log_id TEXT PRIMARY KEY,
                evidence_id TEXT NOT NULL,
                sender_id TEXT NOT NULL,
                receiver_id TEXT NOT NULL,
                transfer_reason TEXT NOT NULL,
                recorded_by_id TEXT NOT NULL,
                transfer_timestamp TEXT NOT NULL,
                notes TEXT,
                integrity_verified_on_transfer INTEGER NOT NULL DEFAULT 0,
                transfer_hash_verified TEXT,
                signature_token TEXT NOT NULL,
                FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id) ON DELETE CASCADE,
                FOREIGN KEY (sender_id) REFERENCES users(user_id),
                FOREIGN KEY (receiver_id) REFERENCES users(user_id),
                FOREIGN KEY (recorded_by_id) REFERENCES users(user_id)
            );
            """)

            # 5. Integrity Checks Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS integrity_checks (
                check_id TEXT PRIMARY KEY,
                evidence_id TEXT NOT NULL,
                checked_by_id TEXT NOT NULL,
                check_timestamp TEXT NOT NULL,
                expected_sha256 TEXT NOT NULL,
                calculated_sha256 TEXT NOT NULL,
                result_status TEXT NOT NULL,
                tamper_details TEXT,
                check_mode TEXT NOT NULL DEFAULT 'File Upload Comparison',
                notes TEXT,
                FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id) ON DELETE CASCADE,
                FOREIGN KEY (checked_by_id) REFERENCES users(user_id)
            );
            """)

            # 6. Audit Logs Table (Tamper-evident cryptographically chained ledger)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                user_id TEXT NOT NULL,
                evidence_id TEXT,
                details TEXT NOT NULL,
                prev_hash TEXT NOT NULL,
                curr_hash TEXT NOT NULL
            );
            """)

            # Indices for rapid querying
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence(case_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evidence_sha256 ON evidence(sha256_hash);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evidence_status ON evidence(integrity_status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_custody_evidence ON custody_logs(evidence_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_integrity_evidence ON integrity_checks(evidence_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_event ON audit_logs(event_type);")

            conn.commit()

    # --- User Helpers ---

    def add_user(self, user_id: str, username: str, full_name: str, role: str,
                 badge_number: str, organization: str, email: str) -> None:
        """Insert or replace a system user."""
        with self.get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO users (user_id, username, full_name, role, badge_number, organization, email, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, full_name, role, badge_number, organization, email, get_iso_now()))
            conn.commit()

    def get_users(self) -> List[Dict[str, Any]]:
        """Fetch all system users."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT * FROM users ORDER BY full_name ASC;").fetchall()
            return [dict(r) for r in rows]

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute("SELECT * FROM users WHERE user_id = ?;", (user_id,)).fetchone()
            return dict(row) if row else None

    # --- Case Helpers ---

    def add_case(self, case_id: str, case_title: str, investigator_lead: str,
                 jurisdiction: str, status: str = "Active Investigation", description: str = "") -> None:
        """Insert or replace a forensic case file."""
        with self.get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO cases (case_id, case_title, investigator_lead, jurisdiction, status, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (case_id, case_title, investigator_lead, jurisdiction, status, description, get_iso_now()))
            conn.commit()

    def get_cases(self) -> List[Dict[str, Any]]:
        """Fetch all cases."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT * FROM cases ORDER BY created_at DESC;").fetchall()
            return [dict(r) for r in rows]

    def get_case_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific case."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute("SELECT * FROM cases WHERE case_id = ?;", (case_id,)).fetchone()
            return dict(row) if row else None

    # --- Evidence Helpers ---

    def add_evidence(self, data: Dict[str, Any]) -> None:
        """Insert a newly registered evidence record."""
        with self.get_connection() as conn:
            conn.execute("""
            INSERT INTO evidence (
                evidence_id, case_id, title, description, category,
                original_filename, file_extension, mime_type, magic_signature,
                file_size_bytes, sha256_hash, md5_hash, sha1_hash, shannon_entropy,
                collection_date, collection_location, collected_by,
                registered_by_id, current_custodian_id, integrity_status,
                last_verified_at, last_verified_by, storage_rel_path,
                metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["evidence_id"], data["case_id"], data["title"], data.get("description", ""),
                data["category"], data["original_filename"], data["file_extension"], data["mime_type"],
                data.get("magic_signature", ""), data["file_size_bytes"], data["sha256_hash"],
                data["md5_hash"], data["sha1_hash"], data["shannon_entropy"],
                data["collection_date"], data.get("collection_location", ""), data["collected_by"],
                data["registered_by_id"], data["current_custodian_id"], data.get("integrity_status", "Not Yet Verified"),
                data.get("last_verified_at"), data.get("last_verified_by"), data["storage_rel_path"],
                json.dumps(data.get("metadata", {})), data.get("created_at", get_iso_now())
            ))
            conn.commit()

    def get_evidence_list(self, search_query: str = "", category_filter: str = "All",
                          case_filter: str = "All", status_filter: str = "All") -> List[Dict[str, Any]]:
        """Search and filter registered evidence records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
            SELECT e.*, c.case_title, u.full_name as custodian_name, reg.full_name as registered_by_name
            FROM evidence e
            JOIN cases c ON e.case_id = c.case_id
            JOIN users u ON e.current_custodian_id = u.user_id
            JOIN users reg ON e.registered_by_id = reg.user_id
            WHERE 1=1
            """
            params: List[Any] = []

            if search_query:
                query += " AND (e.evidence_id LIKE ? OR e.title LIKE ? OR e.original_filename LIKE ? OR e.sha256_hash LIKE ?)"
                wildcard = f"%{search_query.strip()}%"
                params.extend([wildcard, wildcard, wildcard, wildcard])

            if category_filter and category_filter != "All":
                query += " AND e.category = ?"
                params.append(category_filter)

            if case_filter and case_filter != "All":
                query += " AND e.case_id = ?"
                params.append(case_filter)

            if status_filter and status_filter != "All":
                query += " AND e.integrity_status = ?"
                params.append(status_filter)

            query += " ORDER BY e.created_at DESC;"
            rows = cursor.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_evidence_by_id(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full details for a single evidence item."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
            SELECT e.*, c.case_title, c.jurisdiction,
                   u.full_name as custodian_name, u.role as custodian_role, u.badge_number as custodian_badge,
                   reg.full_name as registered_by_name, reg.role as registered_by_role
            FROM evidence e
            JOIN cases c ON e.case_id = c.case_id
            JOIN users u ON e.current_custodian_id = u.user_id
            JOIN users reg ON e.registered_by_id = reg.user_id
            WHERE e.evidence_id = ?;
            """
            row = cursor.execute(query, (evidence_id,)).fetchone()
            if not row:
                return None
            result = dict(row)
            try:
                result["metadata"] = json.loads(result.get("metadata_json", "{}"))
            except Exception:
                result["metadata"] = {}
            return result

    def update_evidence_custodian(self, evidence_id: str, new_custodian_id: str) -> None:
        """Update current custodian for an evidence record."""
        with self.get_connection() as conn:
            conn.execute("""
            UPDATE evidence SET current_custodian_id = ? WHERE evidence_id = ?;
            """, (new_custodian_id, evidence_id))
            conn.commit()

    def update_evidence_integrity_status(self, evidence_id: str, status: str, verified_by_name: str) -> None:
        """Update the integrity verification status of an evidence item."""
        with self.get_connection() as conn:
            conn.execute("""
            UPDATE evidence
            SET integrity_status = ?, last_verified_at = ?, last_verified_by = ?
            WHERE evidence_id = ?;
            """, (status, get_iso_now(), verified_by_name, evidence_id))
            conn.commit()

    def find_duplicates_by_hash(self, sha256_hash: str, exclude_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find any other evidence files that match the same SHA-256 hash."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if exclude_id:
                query = "SELECT evidence_id, title, original_filename, case_id, created_at FROM evidence WHERE sha256_hash = ? AND evidence_id != ?;"
                rows = cursor.execute(query, (sha256_hash, exclude_id)).fetchall()
            else:
                query = "SELECT evidence_id, title, original_filename, case_id, created_at FROM evidence WHERE sha256_hash = ?;"
                rows = cursor.execute(query, (sha256_hash,)).fetchall()
            return [dict(r) for r in rows]

    # --- Custody Log Helpers ---

    def add_custody_log(self, data: Dict[str, Any]) -> None:
        """Insert a custody transfer log and update the evidence's current custodian."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO custody_logs (
                log_id, evidence_id, sender_id, receiver_id, transfer_reason,
                recorded_by_id, transfer_timestamp, notes,
                integrity_verified_on_transfer, transfer_hash_verified, signature_token
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["log_id"], data["evidence_id"], data["sender_id"], data["receiver_id"],
                data["transfer_reason"], data["recorded_by_id"], data["transfer_timestamp"],
                data.get("notes", ""), data.get("integrity_verified_on_transfer", 0),
                data.get("transfer_hash_verified", ""), data["signature_token"]
            ))
            # Automatically update the evidence record's active custodian
            cursor.execute("""
            UPDATE evidence SET current_custodian_id = ? WHERE evidence_id = ?;
            """, (data["receiver_id"], data["evidence_id"]))
            conn.commit()

    def get_custody_logs_for_evidence(self, evidence_id: str) -> List[Dict[str, Any]]:
        """Retrieve chronological chain of custody events for an evidence file."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
            SELECT l.*,
                   s.full_name as sender_name, s.role as sender_role, s.badge_number as sender_badge,
                   r.full_name as receiver_name, r.role as receiver_role, r.badge_number as receiver_badge,
                   rec.full_name as recorded_by_name
            FROM custody_logs l
            JOIN users s ON l.sender_id = s.user_id
            JOIN users r ON l.receiver_id = r.user_id
            JOIN users rec ON l.recorded_by_id = rec.user_id
            WHERE l.evidence_id = ?
            ORDER BY l.transfer_timestamp ASC;
            """
            rows = cursor.execute(query, (evidence_id,)).fetchall()
            return [dict(r) for r in rows]

    def get_recent_custody_transfers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent transfers across all evidence files."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
            SELECT l.*, e.title as evidence_title, e.original_filename,
                   s.full_name as sender_name, r.full_name as receiver_name
            FROM custody_logs l
            JOIN evidence e ON l.evidence_id = e.evidence_id
            JOIN users s ON l.sender_id = s.user_id
            JOIN users r ON l.receiver_id = r.user_id
            ORDER BY l.transfer_timestamp DESC
            LIMIT ?;
            """
            rows = cursor.execute(query, (limit,)).fetchall()
            return [dict(r) for r in rows]

    # --- Integrity Check Helpers ---

    def add_integrity_check(self, data: Dict[str, Any]) -> None:
        """Record an integrity verification check result and update evidence status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO integrity_checks (
                check_id, evidence_id, checked_by_id, check_timestamp,
                expected_sha256, calculated_sha256, result_status,
                tamper_details, check_mode, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["check_id"], data["evidence_id"], data["checked_by_id"],
                data["check_timestamp"], data["expected_sha256"], data["calculated_sha256"],
                data["result_status"], data.get("tamper_details"),
                data.get("check_mode", "File Upload Comparison"), data.get("notes", "")
            ))

            # Map check result to evidence status
            new_status = "Verified" if data["result_status"] == "Match" else "Integrity Mismatch" if data["result_status"] == "Mismatch" else "Verification Failed"
            user_row = cursor.execute("SELECT full_name FROM users WHERE user_id = ?;", (data["checked_by_id"],)).fetchone()
            examiner_name = user_row["full_name"] if user_row else data["checked_by_id"]

            cursor.execute("""
            UPDATE evidence
            SET integrity_status = ?, last_verified_at = ?, last_verified_by = ?
            WHERE evidence_id = ?;
            """, (new_status, data["check_timestamp"], examiner_name, data["evidence_id"]))
            conn.commit()

    def get_integrity_checks_for_evidence(self, evidence_id: str) -> List[Dict[str, Any]]:
        """Retrieve all integrity check logs for an evidence file."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
            SELECT c.*, u.full_name as checked_by_name, u.role as checked_by_role
            FROM integrity_checks c
            JOIN users u ON c.checked_by_id = u.user_id
            WHERE c.evidence_id = ?
            ORDER BY c.check_timestamp DESC;
            """
            rows = cursor.execute(query, (evidence_id,)).fetchall()
            return [dict(r) for r in rows]

    # --- Audit Log Chaining Helpers ---

    def get_latest_audit_hash(self) -> str:
        """Return the curr_hash of the most recent audit row, or genesis string if empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute("SELECT curr_hash FROM audit_logs ORDER BY audit_id DESC LIMIT 1;").fetchone()
            if row and row["curr_hash"]:
                return row["curr_hash"]
            # Genesis hash for the initial block
            return "0000000000000000000000000000000000000000000000000000000000000000"

    def record_audit_event(self, event_type: str, user_id: str, details: str,
                           curr_hash: str, prev_hash: str, timestamp: Optional[str] = None,
                           evidence_id: Optional[str] = None) -> int:
        """Insert a cryptographically chained audit event."""
        event_time = timestamp if timestamp else get_iso_now()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO audit_logs (timestamp, event_type, user_id, evidence_id, details, prev_hash, curr_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (event_time, event_type, user_id, evidence_id, details, prev_hash, curr_hash))
            conn.commit()
            return cursor.lastrowid

    def get_audit_logs(self, limit: int = 50, event_filter: str = "All") -> List[Dict[str, Any]]:
        """Retrieve audit logs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if event_filter and event_filter != "All":
                query = "SELECT * FROM audit_logs WHERE event_type = ? ORDER BY audit_id DESC LIMIT ?;"
                rows = cursor.execute(query, (event_filter, limit)).fetchall()
            else:
                query = "SELECT * FROM audit_logs ORDER BY audit_id DESC LIMIT ?;"
                rows = cursor.execute(query, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def get_all_audit_logs_ascending(self) -> List[Dict[str, Any]]:
        """Retrieve all audit logs in chronological order for chain integrity verification."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT * FROM audit_logs ORDER BY audit_id ASC;").fetchall()
            return [dict(r) for r in rows]

    # --- Dashboard Summary Metrics ---

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Compute key summary counts for the workstation dashboard."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            total_evidence = cursor.execute("SELECT COUNT(*) FROM evidence;").fetchone()[0]
            verified_count = cursor.execute("SELECT COUNT(*) FROM evidence WHERE integrity_status = 'Verified';").fetchone()[0]
            pending_count = cursor.execute("SELECT COUNT(*) FROM evidence WHERE integrity_status = 'Not Yet Verified';").fetchone()[0]
            mismatch_count = cursor.execute("SELECT COUNT(*) FROM evidence WHERE integrity_status = 'Integrity Mismatch';").fetchone()[0]
            failed_count = cursor.execute("SELECT COUNT(*) FROM evidence WHERE integrity_status = 'Verification Failed';").fetchone()[0]
            total_cases = cursor.execute("SELECT COUNT(*) FROM cases;").fetchone()[0]
            total_transfers = cursor.execute("SELECT COUNT(*) FROM custody_logs;").fetchone()[0]

            return {
                "total_evidence": total_evidence,
                "verified_count": verified_count,
                "pending_count": pending_count,
                "mismatch_count": mismatch_count,
                "failed_count": failed_count,
                "total_cases": total_cases,
                "total_transfers": total_transfers
            }
