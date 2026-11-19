"""
Unit tests for KUSTODRA Metadata Inspector.
"""

import io
import pytest
from kustodra.core.metadata_inspector import MetadataInspector


def test_format_bytes():
    """Verify human-readable byte conversion formatting."""
    assert "500 Bytes" in MetadataInspector.format_bytes(500)
    assert "1.50 KB" in MetadataInspector.format_bytes(1536)
    assert "2.00 MB" in MetadataInspector.format_bytes(2 * 1024 * 1024)
    assert "1.00 GB" in MetadataInspector.format_bytes(1024 * 1024 * 1024)


def test_magic_signature_detection():
    """Verify signature header detection across binary and text formats."""
    # PNG
    sig_id, name, mime = MetadataInspector.detect_magic_signature(b"\x89PNG\r\n\x1a\n\x00\x00")
    assert sig_id == "PNG"
    assert mime == "image/png"

    # JPEG
    sig_id, name, mime = MetadataInspector.detect_magic_signature(b"\xff\xd8\xff\xe0\x00\x10JFIF")
    assert sig_id == "JPEG"
    assert mime == "image/jpeg"

    # PDF
    sig_id, name, mime = MetadataInspector.detect_magic_signature(b"%PDF-1.4\n%...")
    assert sig_id == "PDF"
    assert mime == "application/pdf"

    # SQLite
    sig_id, name, mime = MetadataInspector.detect_magic_signature(b"SQLite format 3\x00\x10\x00")
    assert sig_id == "SQLITE"
    assert mime == "application/vnd.sqlite3"

    # Windows Executable (PE / MZ)
    sig_id, name, mime = MetadataInspector.detect_magic_signature(b"MZ\x90\x00\x03\x00\x00\x00")
    assert sig_id == "EXE_PE"
    assert mime == "application/x-dosexec"

    # Plain text
    sig_id, name, mime = MetadataInspector.detect_magic_signature(b"Simple log output timestamp=2026-11-19")
    assert sig_id == "PLAIN_TEXT"
    assert mime == "text/plain"


def test_mime_spoofing_detection():
    """Verify that file extension vs header signature mismatch is flagged as spoofed."""
    # An executable payload disguised as an image file
    fake_image_bytes = b"MZ\x90\x00\x03\x00\x00\x00SomeFakeExecutablePayload"
    result = MetadataInspector.inspect_file(fake_image_bytes, "innocent_photo.jpg")

    assert result["is_spoofed"] is True
    assert "CRITICAL" in result["spoof_warning"]
    assert "executable" in result["spoof_warning"].lower()


def test_text_forensic_metrics():
    """Verify line, word, and character counting for text files."""
    text_content = b"Line 1 with five words\nLine 2 with four words\n\nLine 4"
    result = MetadataInspector.inspect_file(text_content, "sample.txt")

    assert "text" in result["details"]
    text_info = result["details"]["text"]
    assert text_info["total_lines"] == 4
    assert text_info["blank_lines"] == 1
    assert text_info["word_count"] == 12
