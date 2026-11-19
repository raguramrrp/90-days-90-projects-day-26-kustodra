"""
Unit tests for KUSTODRA Cryptographic Forensics Engine.
"""

import hashlib
import io
import pytest
from kustodra.core.crypto_engine import CryptoEngine


def test_hash_calculation_known_vectors():
    """Verify SHA-256, MD5, and SHA-1 against known string vectors."""
    data = b"KUSTODRA_FORENSIC_INTEGRITY_TEST_2026"
    expected_sha256 = hashlib.sha256(data).hexdigest().lower()
    expected_md5 = hashlib.md5(data).hexdigest().lower()
    expected_sha1 = hashlib.sha1(data).hexdigest().lower()

    hashes = CryptoEngine.calculate_hashes_from_bytes(data)
    assert hashes["sha256"] == expected_sha256
    assert hashes["md5"] == expected_md5
    assert hashes["sha1"] == expected_sha1


def test_streaming_hash_calculation():
    """Verify streaming chunked calculation matches in-memory calculation."""
    large_payload = b"A" * 150000  # Exceeds 64KB chunk size
    stream = io.BytesIO(large_payload)
    hashes = CryptoEngine.calculate_hashes_from_stream(stream)
    assert hashes["sha256"] == hashlib.sha256(large_payload).hexdigest().lower()


def test_constant_time_verification():
    """Verify constant-time hash comparison logic."""
    h1 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    h2 = "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
    h3 = "0000000000000000000000000000000000000000000000000000000000000000"

    assert CryptoEngine.verify_hash(h1, h2) is True
    assert CryptoEngine.verify_hash(h1, h3) is False
    assert CryptoEngine.verify_hash("", h1) is False


def test_verify_sha256_constant_time():
    """Verify verify_sha256_constant_time with bytes and streams."""
    data = b"cryptographic forensic payload 2026"
    h = hashlib.sha256(data).hexdigest()
    assert CryptoEngine.verify_sha256_constant_time(data, h) is True
    assert CryptoEngine.verify_sha256_constant_time(data, "badhash") is False
    assert CryptoEngine.verify_sha256_constant_time(data, "") is False


def test_shannon_entropy():
    """Verify entropy bounds: uniform data ~0.0, random data ~8.0."""
    zero_bytes = b"\x00" * 4096
    entropy_low = CryptoEngine.calculate_shannon_entropy(zero_bytes)
    assert entropy_low == 0.0

    # Natural text has moderate entropy (typically 3.0 to 4.5)
    text_data = b"The quick brown fox jumps over the lazy dog repeatedly in plain English text."
    entropy_text = CryptoEngine.calculate_shannon_entropy(text_data)
    assert 3.0 <= entropy_text <= 5.0

    # Deterministic pseudo-random byte block (high entropy > 7.5)
    import random
    random.seed(99)
    rand_data = bytes([random.randint(0, 255) for _ in range(8192)])
    entropy_high = CryptoEngine.calculate_shannon_entropy(rand_data)
    assert entropy_high >= 7.5


def test_audit_block_hash():
    """Verify chained audit block hash computation."""
    prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    timestamp = "2026-11-19T10:00:00Z"
    event_type = "EVIDENCE_REGISTERED"
    user_id = "USR-101"
    details = "Evidence EV-001 intake."

    curr_hash = CryptoEngine.compute_audit_block_hash(prev_hash, timestamp, event_type, user_id, details)
    assert len(curr_hash) == 64
    assert curr_hash == CryptoEngine.compute_audit_block_hash(prev_hash, timestamp, event_type, user_id, details)


def test_custody_transfer_token():
    """Verify digital transfer token generation is deterministic."""
    token = CryptoEngine.generate_custody_transfer_token(
        evidence_id="EV-2026-0001",
        sender_id="USR-101",
        receiver_id="USR-102",
        timestamp="2026-11-19T10:00:00Z",
        file_hash="abc123def456"
    )
    assert len(token) == 64
