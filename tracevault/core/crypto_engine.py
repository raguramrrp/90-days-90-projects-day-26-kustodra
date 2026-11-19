"""
TRACEVAULT - Cryptographic Forensics Engine
Provides streaming multi-hash computation (SHA-256, MD5, SHA-1),
constant-time hash comparison, Shannon entropy measurement,
and tamper-evident chained audit hashing.
"""

from __future__ import annotations
import hashlib
import hmac
import math
from pathlib import Path
from typing import BinaryIO, Dict, Tuple, Union


CHUNK_SIZE = 65536  # 64 KB streaming buffer for high throughput and bounded memory


class CryptoEngine:
    """Core cryptographic routines for forensic file integrity and chained logging."""

    @staticmethod
    def calculate_hashes_from_stream(stream: BinaryIO) -> Dict[str, str]:
        """
        Compute SHA-256, MD5, and SHA-1 concurrently over a readable binary stream.
        Resets stream pointer to 0 before and after hashing if seekable.
        """
        sha256 = hashlib.sha256()
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()

        if hasattr(stream, "seek") and stream.seekable():
            stream.seek(0)

        while True:
            chunk = stream.read(CHUNK_SIZE)
            if not chunk:
                break
            sha256.update(chunk)
            md5.update(chunk)
            sha1.update(chunk)

        if hasattr(stream, "seek") and stream.seekable():
            stream.seek(0)

        return {
            "sha256": sha256.hexdigest().lower(),
            "md5": md5.hexdigest().lower(),
            "sha1": sha1.hexdigest().lower()
        }

    @classmethod
    def calculate_hashes_from_file(cls, file_path: Union[str, Path]) -> Dict[str, str]:
        """Compute cryptographic hashes for a file on disk using streaming chunks."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Target evidence file does not exist: {path}")

        with path.open("rb") as f:
            return cls.calculate_hashes_from_stream(f)

    @classmethod
    def calculate_hashes_from_bytes(cls, data: bytes) -> Dict[str, str]:
        """Compute cryptographic hashes for raw bytes in memory."""
        sha256 = hashlib.sha256(data).hexdigest().lower()
        md5 = hashlib.md5(data).hexdigest().lower()
        sha1 = hashlib.sha1(data).hexdigest().lower()
        return {
            "sha256": sha256,
            "md5": md5,
            "sha1": sha1
        }

    @staticmethod
    def verify_hash(expected_hash: str, calculated_hash: str) -> bool:
        """
        Compare two hashes using constant-time comparison to prevent timing attacks.
        Returns True if identical (case-insensitive), False otherwise.
        """
        if not expected_hash or not calculated_hash:
            return False
        return hmac.compare_digest(expected_hash.strip().lower(), calculated_hash.strip().lower())

    @staticmethod
    def calculate_shannon_entropy(data_or_stream: Union[bytes, BinaryIO, str, Path]) -> float:
        """
        Calculate the Shannon Entropy of binary data.
        Returns a float between 0.0 (completely predictable) and 8.0 (pure randomness / encrypted / compressed).
        Formula: H = - sum(p_i * log2(p_i)) for each byte value 0..255.
        """
        byte_counts = [0] * 256
        total_bytes = 0

        if isinstance(data_or_stream, (str, Path)):
            path = Path(data_or_stream)
            if not path.is_file():
                return 0.0
            with path.open("rb") as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    for byte in chunk:
                        byte_counts[byte] += 1
        elif isinstance(data_or_stream, bytes):
            total_bytes = len(data_or_stream)
            for byte in data_or_stream:
                byte_counts[byte] += 1
        elif hasattr(data_or_stream, "read"):
            # Binary stream
            stream = data_or_stream
            if hasattr(stream, "seek") and stream.seekable():
                stream.seek(0)
            while True:
                chunk = stream.read(CHUNK_SIZE)
                if not chunk:
                    break
                total_bytes += len(chunk)
                for byte in chunk:
                    byte_counts[byte] += 1
            if hasattr(stream, "seek") and stream.seekable():
                stream.seek(0)
        else:
            return 0.0

        if total_bytes == 0:
            return 0.0

        entropy = 0.0
        for count in byte_counts:
            if count > 0:
                p_i = count / total_bytes
                entropy -= p_i * math.log2(p_i)

        return round(entropy, 4)

    @staticmethod
    def compute_audit_block_hash(prev_hash: str, timestamp: str, event_type: str,
                                 user_id: str, details: str) -> str:
        """
        Compute a chained cryptographic block hash for audit events.
        Ensures any retroactive modification or row deletion invalidates the chain.
        """
        payload = f"{prev_hash}|{timestamp}|{event_type}|{user_id}|{details}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest().lower()

    @staticmethod
    def generate_custody_transfer_token(evidence_id: str, sender_id: str,
                                        receiver_id: str, timestamp: str,
                                        file_hash: str) -> str:
        """
        Generate a verifiable digital token representing a custody transfer operation.
        """
        token_payload = f"CUSTODY-TRANSFER:{evidence_id}:{sender_id}->{receiver_id}:{timestamp}:{file_hash}".encode("utf-8")
        return hashlib.sha256(token_payload).hexdigest().lower()
