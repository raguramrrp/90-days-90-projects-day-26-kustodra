"""
TRACEVAULT - Sample Evidence Generator
Creates digital test artifacts across multiple forensic categories.
"""

from __future__ import annotations
import random
from pathlib import Path
from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def create_sample_files(target_dir: str | Path | None = None) -> None:
    """Generate forensic test files."""
    if target_dir is None:
        dest = PROJECT_ROOT / "data" / "sample_evidence"
    else:
        dest = Path(target_dir)
        if not dest.is_absolute():
            dest = PROJECT_ROOT / dest
    dest.mkdir(parents=True, exist_ok=True)

    # 1. Server Access Log
    log_content = (
        "192.168.1.105 - - [18/Nov/2026:04:12:01 +0000] \"GET /admin/login HTTP/1.1\" 200 4821\n"
        "192.168.1.105 - - [18/Nov/2026:04:12:15 +0000] \"POST /admin/auth HTTP/1.1\" 401 1204\n"
        "192.168.1.105 - - [18/Nov/2026:04:12:44 +0000] \"POST /admin/auth HTTP/1.1\" 401 1204\n"
        "10.0.4.88 - - [18/Nov/2026:04:15:22 +0000] \"GET /api/v1/customers?id=1 HTTP/1.1\" 400 312\n"
        "10.0.4.88 - - [18/Nov/2026:04:15:39 +0000] \"POST /api/v1/upload HTTP/1.1\" 200 8920\n"
        "172.16.0.12 - - [18/Nov/2026:04:22:10 +0000] \"GET /vault/records/export.csv HTTP/1.1\" 200 45192\n"
        "192.168.1.105 - - [18/Nov/2026:04:30:00 +0000] \"POST /admin/logout HTTP/1.1\" 302 0\n"
    )
    (dest / "server_access_log.log").write_text(log_content, encoding="utf-8")

    # 2. Tampered Server Access Log
    tampered_content = log_content.replace("10.0.4.88", "127.0.0.1")
    (dest / "tampered_server_log.log").write_text(tampered_content, encoding="utf-8")

    # 3. Surveillance Still Image
    img = Image.new("RGB", (640, 480), color=(35, 45, 42))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 600, 440], outline=(120, 148, 135), width=2)
    draw.text((50, 50), "PERIMETER MONITOR - CAM 04", fill=(240, 240, 240))
    draw.text((50, 70), "UTC 2026-11-18 04:15:22", fill=(200, 200, 200))
    img.save(dest / "surveillance_cam4_frame109.png", format="PNG")

    # 4. Financial Audit Ledger
    csv_content = (
        "transaction_id,timestamp,source_account,destination_account,amount_usd,auth_token\n"
        "TX-9901,2026-11-17T14:22:00Z,ACC-4081-992,EXT-CH-8821,245000.00,AUTH_SIG_882910\n"
        "TX-9902,2026-11-17T15:10:11Z,ACC-4081-992,EXT-US-1029,12000.00,AUTH_SIG_882911\n"
    )
    (dest / "financial_audit_ledger.csv").write_text(csv_content, encoding="utf-8")

    # 5. Technical Note Document
    note_content = (
        "Project Alpha technical specification notes.\n"
        "Date: 2026-11-10.\n"
        "File digest reference: DOC-EXP-2026-884.\n"
        "Test sample document for cryptographic integrity verification.\n"
    )
    (dest / "confidential_asset_agreement.txt").write_text(note_content, encoding="utf-8")

    # 6. High Entropy Binary Payload
    random.seed(42)
    entropy_bytes = bytes([random.randint(0, 255) for _ in range(8192)])
    (dest / "suspect_encrypted_payload.bin").write_bytes(entropy_bytes)

    print(f"[SUCCESS] Sample evidence files generated in: {dest.resolve()}")


if __name__ == "__main__":
    create_sample_files()
