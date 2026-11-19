"""
TRACEVAULT - Metadata Inspector Module
Performs multi-format header inspection, magic byte detection,
MIME spoofing analysis, image EXIF extraction, and text forensic metrics.
"""

from __future__ import annotations
import io
import json
import mimetypes
import os
from pathlib import Path
from typing import Any, BinaryIO, Dict, Optional, Tuple, Union

try:
    from PIL import Image, ExifTags
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


# Forensic Signature Database: Maps header byte prefixes to known formats and descriptions
FILE_SIGNATURES: Dict[str, Tuple[bytes, int, str, str]] = {
    # signature_id: (byte_sequence, byte_offset, formal_name, expected_mime)
    "PNG": (b"\x89PNG\r\n\x1a\n", 0, "Portable Network Graphics", "image/png"),
    "JPEG": (b"\xff\xd8\xff", 0, "JPEG Image", "image/jpeg"),
    "GIF87a": (b"GIF87a", 0, "GIF Image (v87a)", "image/gif"),
    "GIF89a": (b"GIF89a", 0, "GIF Image (v89a)", "image/gif"),
    "BMP": (b"BM", 0, "Windows Bitmap", "image/bmp"),
    "WEBP": (b"RIFF", 0, "RIFF Container (WebP/Audio)", "image/webp"),
    "PDF": (b"%PDF-", 0, "Adobe Portable Document Format", "application/pdf"),
    "ZIP": (b"PK\x03\x04", 0, "ZIP Archive / OpenDocument", "application/zip"),
    "7Z": (b"7z\xbc\xaf'\x1c", 0, "7-Zip Compressed Archive", "application/x-7z-compressed"),
    "RAR": (b"Rar!\x1a\x07", 0, "RAR Archive", "application/x-rar-compressed"),
    "GZIP": (b"\x1f\x8b", 0, "GZIP Compressed File", "application/gzip"),
    "SQLITE": (b"SQLite format 3\x00", 0, "SQLite Database File", "application/vnd.sqlite3"),
    "EXE_PE": (b"MZ", 0, "DOS / Windows Executable (PE)", "application/x-dosexec"),
    "ELF": (b"\x7fELF", 0, "Unix Executable (ELF)", "application/x-executable"),
    "MP4_FTYP": (b"ftyp", 4, "ISO Media / MP4 Video", "video/mp4"),
    "ID3_MP3": (b"ID3", 0, "MP3 Audio (ID3 Metadata)", "audio/mpeg"),
}


class MetadataInspector:
    """Extracts forensic metadata from evidence files without executing or altering them."""

    @staticmethod
    def format_bytes(size_bytes: int) -> str:
        """Format raw byte count into human-readable string with units."""
        if size_bytes < 1024:
            return f"{size_bytes} Bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB ({size_bytes:,} B)"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB ({size_bytes:,} B)"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB ({size_bytes:,} B)"

    @classmethod
    def detect_magic_signature(cls, header_bytes: bytes) -> Tuple[str, str, str]:
        """
        Inspect the binary header (first 512 bytes) and match against forensic signature table.
        Returns: (signature_id, formal_name, expected_mime)
        """
        if not header_bytes:
            return ("EMPTY", "Empty 0-Byte File", "application/x-empty")

        for sig_id, (prefix, offset, name, mime) in FILE_SIGNATURES.items():
            if len(header_bytes) >= offset + len(prefix):
                if header_bytes[offset:offset + len(prefix)] == prefix:
                    return (sig_id, name, mime)

        # Check for plain ASCII / UTF-8 text characteristics
        try:
            sample_text = header_bytes[:256].decode("utf-8")
            # If decodable and doesn't contain non-printable control characters (except \r, \n, \t)
            printable_ratio = sum(1 for c in sample_text if c.isprintable() or c in "\r\n\t") / len(sample_text)
            if printable_ratio > 0.95:
                if sample_text.strip().startswith("{") or sample_text.strip().startswith("["):
                    return ("JSON", "JSON Structured Data", "application/json")
                if sample_text.strip().startswith("<?xml") or sample_text.strip().startswith("<html"):
                    return ("XML_HTML", "XML / Markup Document", "text/xml")
                if "," in sample_text and "\n" in sample_text:
                    return ("CSV", "Comma-Separated Text (CSV)", "text/csv")
                return ("PLAIN_TEXT", "Plain ASCII / UTF-8 Text", "text/plain")
        except UnicodeDecodeError:
            pass

        return ("UNKNOWN_BINARY", "Generic Binary Data / Unrecognized Magic", "application/octet-stream")

    @classmethod
    def inspect_file(cls, file_path_or_stream: Union[str, Path, BinaryIO],
                     filename: str) -> Dict[str, Any]:
        """
        Comprehensive forensic inspection of an evidence file.
        Extracts size, extension, MIME, magic signature, spoof flags, and format-specific attributes.
        """
        file_bytes: Optional[bytes] = None
        size_bytes = 0
        header_sample = b""

        if isinstance(file_path_or_stream, (str, Path)):
            path = Path(file_path_or_stream)
            if not path.is_file():
                raise FileNotFoundError(f"File not found for inspection: {path}")
            size_bytes = path.stat().st_size
            with path.open("rb") as f:
                header_sample = f.read(1024)
                f.seek(0)
                # Read complete bytes only if file is relatively small (< 10MB) for image/text deep inspect
                if size_bytes <= 10 * 1024 * 1024:
                    file_bytes = f.read()
        elif isinstance(file_path_or_stream, bytes):
            file_bytes = file_path_or_stream
            size_bytes = len(file_bytes)
            header_sample = file_bytes[:1024]
        elif hasattr(file_path_or_stream, "read"):
            stream = file_path_or_stream
            if hasattr(stream, "seek") and stream.seekable():
                stream.seek(0)
            file_bytes = stream.read()
            size_bytes = len(file_bytes)
            header_sample = file_bytes[:1024]
            if hasattr(stream, "seek") and stream.seekable():
                stream.seek(0)

        # 1. Extension and Guessed MIME
        ext = Path(filename).suffix.lower()
        guessed_mime, _ = mimetypes.guess_type(filename)
        if not guessed_mime:
            guessed_mime = "application/octet-stream"

        # 2. Magic signature detection
        sig_id, formal_name, signature_mime = cls.detect_magic_signature(header_sample)

        # 3. Extension vs Signature Spoofing Check
        is_spoofed = False
        spoof_warning = ""

        # Flag dangerous discrepancies
        if sig_id == "EXE_PE" and ext not in [".exe", ".dll", ".sys", ".scr", ".com"]:
            is_spoofed = True
            spoof_warning = f"CRITICAL: File named '{filename}' has extension '{ext}' but header contains executable (MZ/PE) signature!"
        elif sig_id == "ELF" and ext in [".txt", ".pdf", ".jpg", ".png"]:
            is_spoofed = True
            spoof_warning = f"CRITICAL: File named '{filename}' has extension '{ext}' but header contains Linux ELF binary signature!"
        elif sig_id in ["PNG", "JPEG", "GIF87a", "GIF89a"] and ext in [".exe", ".txt", ".sh", ".py"]:
            is_spoofed = True
            spoof_warning = f"NOTE: Extension '{ext}' diverges from detected image header '{formal_name}'."
        elif sig_id == "PDF" and ext not in [".pdf", ".ai"]:
            is_spoofed = True
            spoof_warning = f"WARNING: File header matches PDF signature but filename extension is '{ext}'."

        result: Dict[str, Any] = {
            "filename": filename,
            "file_extension": ext if ext else "None",
            "file_size_bytes": size_bytes,
            "file_size_formatted": cls.format_bytes(size_bytes),
            "mime_type": signature_mime if signature_mime != "application/octet-stream" else guessed_mime,
            "guessed_mime_type": guessed_mime,
            "signature_id": sig_id,
            "magic_signature": formal_name,
            "is_spoofed": is_spoofed,
            "spoof_warning": spoof_warning,
            "details": {}
        }

        # 4. Format-Specific Detailed Inspection
        if file_bytes is not None:
            # Check Image Formats
            if HAS_PILLOW and sig_id in ["PNG", "JPEG", "GIF87a", "GIF89a", "BMP", "WEBP"]:
                image_details = cls._inspect_image(file_bytes)
                if image_details:
                    result["details"]["image"] = image_details

            # Check Text & Log Formats
            if sig_id in ["PLAIN_TEXT", "CSV", "JSON", "XML_HTML"] or ext in [".txt", ".log", ".csv", ".json", ".xml", ".ini", ".conf"]:
                text_details = cls._inspect_text(file_bytes)
                if text_details:
                    result["details"]["text"] = text_details

        return result

    @classmethod
    def _inspect_image(cls, data: bytes) -> Optional[Dict[str, Any]]:
        """Extract image dimensions, mode, and EXIF tags safely."""
        if not HAS_PILLOW:
            return None
        try:
            with Image.open(io.BytesIO(data)) as img:
                details: Dict[str, Any] = {
                    "dimensions": f"{img.width} x {img.height} pixels",
                    "width": img.width,
                    "height": img.height,
                    "color_mode": img.mode,
                    "image_format": img.format or "Unknown",
                    "has_transparency": "A" in img.mode or "transparency" in img.info,
                }

                # Extract EXIF if present
                exif_data = img.getexif() if hasattr(img, "getexif") else None
                if exif_data:
                    clean_exif: Dict[str, str] = {}
                    for tag_id, value in exif_data.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        # Filter out raw byte arrays or non-serializable objects
                        if isinstance(value, (str, int, float)):
                            clean_exif[tag_name] = str(value)
                        elif isinstance(value, bytes):
                            clean_exif[tag_name] = f"<binary {len(value)} bytes>"
                    if clean_exif:
                        details["exif"] = clean_exif

                return details
        except Exception:
            return None

    @classmethod
    def _inspect_text(cls, data: bytes) -> Optional[Dict[str, Any]]:
        """Extract line counts, encoding detection, and sample preview from text evidence."""
        try:
            # Attempt UTF-8 first, fallback to latin-1
            text = ""
            encoding_used = "utf-8"
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("latin-1")
                encoding_used = "latin-1"

            lines = text.splitlines()
            total_lines = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())
            word_count = sum(len(line.split()) for line in lines)

            preview_lines = lines[:10]
            preview = "\n".join(preview_lines)
            if len(lines) > 10:
                preview += f"\n... [+{len(lines) - 10} more lines]"

            return {
                "encoding": encoding_used,
                "total_lines": total_lines,
                "blank_lines": blank_lines,
                "word_count": word_count,
                "character_count": len(text),
                "preview": preview
            }
        except Exception:
            return None
