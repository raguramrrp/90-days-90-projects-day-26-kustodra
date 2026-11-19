"""
TRACEVAULT - Forensic Analyzer & Classifier
Provides automated duplicate evidence detection, evidence categorization,
Shannon entropy interpretation, and intelligent metadata summarization.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pathlib import Path


class ForensicAnalyzer:
    """Heuristic and rule-based forensic classifier and metadata summarizer."""

    @staticmethod
    def classify_evidence(filename: str, signature_id: str, mime_type: str,
                          entropy: float, file_size: int) -> Dict[str, str]:
        """
        Classify evidence into a standardized digital forensic category.
        Returns a dictionary with 'category' and 'confidence_rationale'.
        """
        ext = Path(filename).suffix.lower()

        # 1. Executable / Malware Artifact
        if signature_id in ["EXE_PE", "ELF"] or ext in [".exe", ".dll", ".so", ".bin", ".scr", ".sys"]:
            return {
                "category": "Executable / Malware Artifact",
                "rationale": f"Identified by binary execution signature '{signature_id}' or executable extension."
            }

        # 2. Forensic Disk Image & Container
        if ext in [".e01", ".raw", ".dd", ".img", ".iso", ".vhd", ".vmdk"]:
            return {
                "category": "Forensic Disk Image",
                "rationale": f"Standard forensic bitstream storage extension '{ext}'."
            }

        # 3. Surveillance Video & Media
        if signature_id == "MP4_FTYP" or mime_type.startswith("video/") or ext in [".mp4", ".avi", ".mkv", ".mov", ".flv", ".ts"]:
            return {
                "category": "Surveillance Video",
                "rationale": "Video container or media stream identified by header and MIME type."
            }

        # 4. Audio Intercept / Voice Recording
        if signature_id == "ID3_MP3" or mime_type.startswith("audio/") or ext in [".mp3", ".wav", ".aac", ".m4a", ".ogg"]:
            return {
                "category": "Audio Recording",
                "rationale": "Audio stream or voice intercept format."
            }

        # 5. Forensic Still Image
        if signature_id in ["PNG", "JPEG", "GIF87a", "GIF89a", "BMP", "WEBP"] or mime_type.startswith("image/"):
            return {
                "category": "Forensic Still Image",
                "rationale": "Standard raster image format verified by magic bytes."
            }

        # 6. System / Network Log File
        if ext in [".log", ".evtx", ".pcap", ".cap", ".txt", ".audit"] or "log" in filename.lower():
            return {
                "category": "System & Audit Log",
                "rationale": "Log event stream or network telemetry artifact."
            }

        # 7. Digital Document / Financial Record
        if signature_id == "PDF" or ext in [".pdf", ".docx", ".xlsx", ".csv", ".doc", ".xls", ".rtf"]:
            return {
                "category": "Digital Document",
                "rationale": "Formatted office or evidentiary document container."
            }

        # 8. Encrypted / Compressed Archive
        if signature_id in ["ZIP", "7Z", "RAR", "GZIP"] or ext in [".zip", ".7z", ".rar", ".tar", ".gz"]:
            return {
                "category": "Compressed / Encrypted Archive",
                "rationale": f"Compressed multi-file archive container ({signature_id})."
            }

        # High entropy fallback
        if entropy > 7.6:
            return {
                "category": "Encrypted / Packed Payload",
                "rationale": f"High Shannon entropy ({entropy:.2f}/8.0) suggests encryption or packed compression."
            }

        return {
            "category": "Digital Evidentiary Artifact",
            "rationale": "General digital artifact categorized by system defaults."
        }

    @staticmethod
    def interpret_entropy(entropy: float, mime_type: str = "") -> Dict[str, str]:
        """
        Translate Shannon Entropy value into a forensic interpretation.
        Entropy scale: 0.0 to 8.0 bits per byte.
        """
        if entropy < 1.0:
            level = "Near Zero (Extremely Low)"
            assessment = "Repetitive or null-byte padded data; negligible information density."
            note = "Possible sparse file, memory wipe artifact, or zero-filled buffer."
        elif entropy < 4.5:
            level = "Low (Plain Text / Uncompressed Code)"
            assessment = "Consistent with natural language, source code, ASCII logs, or structured text."
            note = "High predictability; contents are readily readable and inspectable."
        elif entropy < 7.2:
            level = "Moderate (Structured Binary / Media)"
            assessment = "Typical of compiled binaries, structured databases, or loosely compressed media."
            note = "Normal operational range for standard multimedia and application data."
        else:
            level = "High (Cryptographic / Compressed / Packed)"
            assessment = "Consistent with AES/RSA ciphertext, high-ratio compression, or packed malware."
            note = "Near-uniform byte distribution; content cannot be visually parsed without decryption keys."

        return {
            "level": level,
            "type": level,
            "assessment": assessment,
            "implication": assessment,
            "security_note": note,
        }

    @classmethod
    def evaluate_risk(cls, *args, **kwargs) -> Dict[str, Any]:
        """
        Calculate an explainable Forensic Integrity Risk score (0 - 100) and indicators.
        Supports both positional arguments:
          evaluate_risk(is_spoofed, entropy, integrity_status, has_duplicates)
        or dictionary object:
          evaluate_risk(evidence_dict, duplicates_list=[])
        """
        is_spoofed = False
        entropy = 0.0
        integrity_status = "Verified"
        has_duplicates = False

        if args and isinstance(args[0], dict):
            ev = args[0]
            duplicates = args[1] if len(args) > 1 else kwargs.get("duplicates", [])
            entropy = float(ev.get("shannon_entropy", 0.0))
            integrity_status = str(ev.get("integrity_status", "Verified"))
            has_duplicates = bool(duplicates)
            is_spoofed = bool(ev.get("is_spoofed", False))
        else:
            if len(args) >= 1:
                is_spoofed = bool(args[0])
            else:
                is_spoofed = bool(kwargs.get("is_spoofed", False))

            if len(args) >= 2:
                entropy = float(args[1])
            else:
                entropy = float(kwargs.get("entropy", 0.0))

            if len(args) >= 3:
                integrity_status = str(args[2])
            else:
                integrity_status = str(kwargs.get("integrity_status", "Verified"))

            if len(args) >= 4:
                has_duplicates = bool(args[3])
            else:
                has_duplicates = bool(kwargs.get("has_duplicates", False))

        score = 0
        indicators: List[str] = []

        if integrity_status == "Integrity Mismatch":
            score += 60
            indicators.append("CRITICAL: Calculated SHA-256 does not match original registered hash (Tampering alert).")
        elif integrity_status == "Verification Failed":
            score += 30
            indicators.append("Verification could not be completed; file missing or unreadable.")
        elif integrity_status == "Not Yet Verified":
            score += 10
            indicators.append("Initial integrity verification has not yet been executed.")

        if is_spoofed:
            score += 35
            indicators.append("MIME/Extension mismatch: File extension conflicts with binary magic header signature.")

        if entropy > 7.75:
            score += 15
            indicators.append(f"Elevated Shannon entropy ({entropy:.2f}/8.0): High density indicates encryption or packing.")

        if has_duplicates:
            indicators.append("Identical cryptographic hash exists on other evidence records (Cross-case twin).")

        score = min(100, score)

        if score >= 60:
            level = "Critical Risk"
            color = "#B74747"
        elif score >= 25:
            level = "Caution / Review Required"
            color = "#B77B29"
        else:
            level = "Normal / Clean Integrity"
            color = "#287A54"

        return {
            "score": score,
            "level": level,
            "color": color,
            "indicators": indicators
        }

    @classmethod
    def generate_evidence_summary(cls, title: str, filename: str, category: str,
                                 size_formatted: str, mime_type: str,
                                 entropy: float, sha256_hash: str,
                                 is_spoofed: bool, duplicates_count: int) -> str:
        """
        Generate an intelligent forensic summary paragraph for the evidence detail card and reports.
        """
        entropy_info = cls.interpret_entropy(entropy)
        dup_text = f"Identified {duplicates_count} identical file hash match(es) in the repository." if duplicates_count > 0 else "Unique hash fingerprint with no duplicates detected across cases."

        summary = (
            f"Evidence record '{title}' ({filename}) is classified as a {category} with an exact payload size "
            f"of {size_formatted}. Forensic header inspection determined MIME type as '{mime_type}'. "
            f"Measured Shannon entropy is {entropy:.2f}/8.0 ({entropy_info['level']}), indicating {entropy_info['assessment'].lower()} "
            f"{dup_text} Cryptographic SHA-256 seal anchored at registration: {sha256_hash[:16]}...{sha256_hash[-8:]}."
        )

        if is_spoofed:
            summary += " ALERT: Detected header signature divergence from filename extension; forensic examiner review is required."

        return summary
