"""
KUSTODRA - High-Resolution Screenshot Generator
Generates pixel-perfect, hyper-realistic UI screenshots directly reflecting
the live KUSTODRA Enterprise Asset Vault workstation with left vertical rail,
rich miniature previews, and active custody controls.
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# KUSTODRA Color Palette
BG_COLOR = (244, 245, 245)          # #F4F5F5
RAIL_BG = (17, 21, 20)              # #111514
SURFACE_COLOR = (255, 255, 255)     # #FFFFFF
SECONDARY_SURFACE = (235, 239, 237) # #EBEFED
TEXT_DARK = (37, 43, 42)            # #252B2A
TEXT_MUTED = (119, 127, 125)        # #777F7D
PRIMARY_ACCENT = (49, 95, 80)       # #315F50
ACTIVE_ACCENT = (38, 61, 54)        # #263D36
ACTIVE_GREEN = (94, 212, 159)       # #5ED49F
BORDER_COLOR = (225, 228, 227)      # #E1E4E3
SUCCESS_GREEN = (50, 129, 90)       # #32815A
DANGER_RED = (188, 75, 75)          # #BC4B4B
WARNING_AMBER = (183, 128, 50)      # #B78032


def get_font(size: int = 14, bold: bool = False):
    """Load clean modern typography (Segoe UI / Arial)."""
    candidates = [
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "arialbd.ttf" if bold else "arial.ttf"
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    return ImageFont.load_default()


def get_mono_font(size: int = 12, bold: bool = False):
    """Load crisp monospace font (Consolas / Courier)."""
    candidates = [
        "consolab.ttf" if bold else "consola.ttf",
        "courbd.ttf" if bold else "cour.ttf"
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    return ImageFont.load_default()


def create_base_canvas(active_icon: str = "🗄️", title: str = "Artifact Vault") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Create the KUSTODRA enterprise workstation window frame with 72px left vertical rail."""
    img = Image.new("RGB", (1400, 880), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 1. Left Vertical Navigation Rail (Width: 72px, Dark Charcoal)
    draw.rectangle([0, 0, 72, 880], fill=RAIL_BG)
    draw.line([(72, 0), (72, 880)], fill=(32, 38, 36), width=1)

    # Rail Delta Logo Mark at top
    draw.rectangle([14, 16, 58, 58], fill=(26, 34, 32), outline=(40, 53, 50), width=1)
    draw.text((28, 24), "▲", fill=SUCCESS_GREEN, font=get_font(18, bold=True))

    # 7 Core Workstation Icons matching app.py
    icons = [
        ("🗄️", "Artifact Vault"),
        ("📥", "Intake & Ingestion"),
        ("📊", "System Intelligence"),
        ("🔬", "Integrity Lab"),
        ("⛓️", "Chain of Custody"),
        ("📄", "Audit & Compliance"),
        ("⚙️", "System Configuration"),
    ]
    y_pos = 85
    for ic, name in icons:
        is_active = (ic == active_icon)
        if is_active:
            draw.rectangle([14, y_pos, 58, y_pos + 44], fill=PRIMARY_ACCENT, outline=(94, 212, 159), width=1)
            draw.text((25, y_pos + 12), ic, font=get_font(16))
        else:
            draw.rectangle([14, y_pos, 58, y_pos + 44], fill=(26, 32, 30), outline=(36, 44, 42), width=1)
            draw.text((25, y_pos + 12), ic, font=get_font(16))
        y_pos += 52

    # Bottom Utility Icons: Help ❓ and Custodian Profile 👤
    draw.rectangle([14, 765, 58, 805], fill=(26, 32, 30), outline=(36, 44, 42), width=1)
    draw.text((25, 775), "❓", font=get_font(16))

    draw.rectangle([14, 815, 58, 855], fill=(26, 32, 30), outline=(36, 44, 42), width=1)
    draw.text((25, 825), "👤", font=get_font(16))

    # 2. Main Workstation Header (Top, x=96 to 1370)
    draw.text((96, 20), title, fill=TEXT_DARK, font=get_font(24, bold=True))

    # + Ingest Artifact Button on top right
    draw.rectangle([1230, 20, 1370, 54], fill=PRIMARY_ACCENT)
    draw.text((1248, 28), "+ Ingest Artifact", fill=(255, 255, 255), font=get_font(12, bold=True))

    return img, draw


def generate_screenshot_01_repository():
    """Screenshot 1: Primary Enterprise Artifact Vault Screen."""
    img, draw = create_base_canvas("🗄️", "Artifact Vault")

    # 1. Search Bar
    draw.rectangle([96, 75, 1370, 115], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((114, 86), "🔍  Search artifacts by title, ID (e.g. ART-2026-0001), SHA-256 hash, case reference, or custodian...", fill=TEXT_MUTED, font=get_font(12))

    # 2. Filter Toolbar
    f_y = 130
    draw.rectangle([96, f_y, 310, f_y + 40], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((112, f_y + 11), "All Custodians ▾", fill=TEXT_DARK, font=get_font(12))

    draw.rectangle([325, f_y, 520, f_y + 40], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((340, f_y + 11), "All Categories ▾", fill=TEXT_DARK, font=get_font(12))

    draw.rectangle([535, f_y, 730, f_y + 40], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((550, f_y + 11), "All Statuses ▾", fill=TEXT_DARK, font=get_font(12))

    draw.rectangle([745, f_y, 940, f_y + 40], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((760, f_y + 11), "Newest First ▾", fill=TEXT_DARK, font=get_font(12))

    draw.rectangle([955, f_y, 1025, f_y + 40], fill=PRIMARY_ACCENT)
    draw.text((970, f_y + 11), "Table", fill=(255, 255, 255), font=get_font(12, bold=True))

    draw.rectangle([1035, f_y, 1105, f_y + 40], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((1055, f_y + 11), "Grid", fill=TEXT_DARK, font=get_font(12))

    draw.text((1315, f_y + 12), "Filters: 0", fill=TEXT_MUTED, font=get_font(11))

    # Count
    draw.text((96, 185), "5 artifacts cataloged", fill=TEXT_MUTED, font=get_font(11))

    # 3. Dense Artifact Table
    t_y = 205
    draw.rectangle([96, t_y, 1370, 680], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)

    # Table Header Row
    draw.rectangle([96, t_y, 1370, t_y + 42], fill=(249, 250, 250))
    draw.line([(96, t_y + 42), (1370, t_y + 42)], fill=BORDER_COLOR, width=1)

    draw.text((110, t_y + 13), "☐", fill=TEXT_MUTED, font=get_font(13))
    draw.text((140, t_y + 13), "Artifact ID", fill=TEXT_MUTED, font=get_font(12, bold=True))
    draw.text((260, t_y + 13), "Preview", fill=TEXT_MUTED, font=get_font(12, bold=True))
    draw.text((360, t_y + 13), "Artifact Title", fill=TEXT_MUTED, font=get_font(12, bold=True))
    draw.text((720, t_y + 13), "Format", fill=TEXT_MUTED, font=get_font(12, bold=True))
    draw.text((830, t_y + 13), "Custodian", fill=TEXT_MUTED, font=get_font(12, bold=True))
    draw.text((1040, t_y + 13), "Ingested At", fill=TEXT_MUTED, font=get_font(12, bold=True))
    draw.text((1180, t_y + 13), "Size", fill=TEXT_MUTED, font=get_font(12, bold=True))
    draw.text((1245, t_y + 13), "Integrity State", fill=TEXT_MUTED, font=get_font(12, bold=True))

    rows = [
        ("ART-2026-0005", "BIN", "🔒 Suspicious Encrypted Binary Payload", "BINARY", "Central Vault Custodian", "2026-11-19 14:31", "8.0 KB", "Not Yet Verified", WARNING_AMBER, True),
        ("ART-2026-0004", "DOC", "📄 Technical Specification Notes", "DOCUMENT", "Lead Investigator", "2026-11-19 14:31", "0.2 KB", "Not Yet Verified", WARNING_AMBER, False),
        ("ART-2026-0003", "CSV", "📄 Financial Transaction Audit Ledger", "DOCUMENT", "Forensic Examiner", "2026-11-19 14:31", "0.2 KB", "Verified", SUCCESS_GREEN, False),
        ("ART-2026-0002", "CAM", "📷 Perimeter Cam 04 Still Frame", "IMAGE", "Central Vault Custodian", "2026-11-19 14:31", "4.8 KB", "Not Yet Verified", WARNING_AMBER, False),
        ("ART-2026-0001", "LOG", "📋 Gateway Server Access Log", "LOG", "Forensic Examiner", "2026-11-19 14:31", "0.6 KB", "Verified", SUCCESS_GREEN, False),
    ]

    r_y = t_y + 44
    for aid, ptype, title, fmt, cust, ing_time, sz, status, st_col, is_selected in rows:
        if is_selected:
            draw.rectangle([97, r_y - 2, 1369, r_y + 50], fill=(244, 248, 246))

        draw.text((110, r_y + 14), "☑" if is_selected else "☐", fill=PRIMARY_ACCENT if is_selected else TEXT_MUTED, font=get_font(13))
        draw.text((140, r_y + 14), aid, fill=PRIMARY_ACCENT, font=get_mono_font(12))

        # Rich miniature preview badges
        bx = 262
        by = r_y + 4
        if ptype == "BIN":
            draw.rectangle([bx, by, bx + 52, by + 40], fill=(15, 23, 42), outline=(51, 65, 85))
            draw.rectangle([bx + 4, by + 4, bx + 48, by + 12], fill=(30, 41, 59))
            draw.text((bx + 12, by + 16), "0xBIN", fill=(251, 191, 36), font=get_font(8, bold=True))
            draw.text((bx + 8, by + 28), "7F 45 2A", fill=(56, 189, 248), font=get_mono_font(7))
        elif ptype == "DOC":
            draw.rectangle([bx, by, bx + 52, by + 40], fill=(248, 250, 252), outline=(203, 213, 225))
            draw.rectangle([bx + 6, by + 6, bx + 36, by + 8], fill=(100, 116, 139))
            draw.rectangle([bx + 6, by + 12, bx + 44, by + 14], fill=(148, 163, 184))
            draw.rectangle([bx + 6, by + 18, bx + 40, by + 20], fill=(148, 163, 184))
            draw.rectangle([bx + 6, by + 24, bx + 32, by + 26], fill=(148, 163, 184))
            draw.ellipse([bx + 34, by + 24, bx + 44, by + 34], fill=(220, 38, 38))
        elif ptype == "CSV":
            draw.rectangle([bx, by, bx + 52, by + 40], fill=(240, 253, 244), outline=(134, 239, 172))
            draw.rectangle([bx, by, bx + 52, by + 12], fill=(22, 101, 52))
            draw.text((bx + 8, by + 2), "CSV $$$", fill=(255, 255, 255), font=get_font(7, bold=True))
            for ly in [16, 23, 30]:
                draw.line([(bx + 2, by + ly), (bx + 50, by + ly)], fill=(187, 247, 208))
            draw.line([(bx + 26, by + 12), (bx + 26, by + 38)], fill=(187, 247, 208))
        elif ptype == "CAM":
            draw.rectangle([bx, by, bx + 52, by + 40], fill=(10, 20, 15), outline=(34, 197, 94))
            for scan in range(by + 3, by + 38, 5):
                draw.line([(bx + 2, scan), (bx + 50, scan)], fill=(20, 50, 30))
            draw.text((bx + 10, by + 10), "[ + ]", fill=(34, 197, 94), font=get_mono_font(8, bold=True))
            draw.rectangle([bx + 2, by + 28, bx + 50, by + 38], fill=(0, 0, 0))
            draw.text((bx + 6, by + 28), "CAM-04", fill=(34, 197, 94), font=get_mono_font(7))
        else:  # LOG
            draw.rectangle([bx, by, bx + 52, by + 40], fill=(15, 23, 42), outline=(51, 65, 85))
            draw.rectangle([bx, by, bx + 52, by + 10], fill=(30, 41, 59))
            draw.ellipse([bx + 4, by + 3, bx + 7, by + 6], fill=(239, 68, 68))
            draw.ellipse([bx + 10, by + 3, bx + 13, by + 6], fill=(234, 179, 8))
            draw.ellipse([bx + 16, by + 3, bx + 19, by + 6], fill=(34, 197, 94))
            draw.text((bx + 4, by + 12), "$ [AUTH]", fill=(56, 189, 248), font=get_mono_font(6))
            draw.text((bx + 4, by + 20), "> 200 OK", fill=(74, 222, 128), font=get_mono_font(6))
            draw.text((bx + 4, by + 28), "ERR:401", fill=(248, 113, 113), font=get_mono_font(6))

        draw.text((360, r_y + 14), title, fill=TEXT_DARK, font=get_font(12, bold=True))
        draw.text((720, r_y + 14), fmt, fill=TEXT_DARK, font=get_font(11))
        draw.text((830, r_y + 14), cust, fill=TEXT_DARK, font=get_font(11))
        draw.text((1040, r_y + 14), ing_time, fill=TEXT_MUTED, font=get_font(11))
        draw.text((1180, r_y + 14), sz, fill=TEXT_DARK, font=get_font(11))

        # Status text with badge style
        draw.text((1245, r_y + 14), ("✓ " if status == "Verified" else "○ ") + status, fill=st_col, font=get_font(11, bold=True))

        draw.line([(96, r_y + 50), (1370, r_y + 50)], fill=BORDER_COLOR, width=1)
        r_y += 52

    # 4. Prominent Bottom Action Card (Active Artifact)
    ac_y = 705
    draw.rectangle([96, ac_y, 1370, 795], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)

    draw.text((116, ac_y + 20), "Active Artifact: ART-2026-0005 • Suspicious Encrypted Binary Payload •", fill=TEXT_DARK, font=get_font(13, bold=True))
    draw.text((116, ac_y + 48), "○ Not Yet Verified", fill=WARNING_AMBER, font=get_font(11, bold=True))

    # Action Buttons
    draw.rectangle([680, ac_y + 22, 880, ac_y + 64], fill=PRIMARY_ACCENT)
    draw.text((720, ac_y + 34), "Inspect Details →", fill=(255, 255, 255), font=get_font(12, bold=True))

    draw.rectangle([900, ac_y + 22, 1100, ac_y + 64], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((945, ac_y + 34), "🔬 Verify in Lab", fill=TEXT_DARK, font=get_font(12, bold=True))

    draw.rectangle([1120, ac_y + 22, 1340, ac_y + 64], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((1185, ac_y + 34), "⛓️ Custody", fill=TEXT_DARK, font=get_font(12, bold=True))

    out_file1 = SCREENSHOTS_DIR / "01-artifact-vault.png"
    out_file2 = SCREENSHOTS_DIR / "01-evidence-repository.png"
    img.save(out_file1)
    img.save(out_file2)
    print(f"[OK] Saved {out_file1.name} & {out_file2.name}")


def generate_screenshot_02_details():
    """Screenshot 2: Structured Artifact Inspector Screen."""
    img, draw = create_base_canvas("🗄️", "Artifact Inspector")

    # Header strip
    draw.rectangle([96, 75, 1370, 140], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((116, 88), "ART-2026-0005: Suspicious Encrypted Binary Payload", fill=TEXT_DARK, font=get_font(18, bold=True))
    draw.text((116, 114), "Case: CASE-2026-CYBER • Format: BINARY • Ingested: 2026-11-19 14:31:46 UTC • Custodian: Central Vault Custodian", fill=TEXT_MUTED, font=get_font(11))

    draw.rectangle([1220, 88, 1350, 124], fill=(254, 243, 199), outline=WARNING_AMBER)
    draw.text((1235, 98), "○ NOT VERIFIED", fill=WARNING_AMBER, font=get_font(11, bold=True))

    # Tabs Row
    draw.rectangle([96, 155, 1370, 195], fill=(244, 246, 245), outline=BORDER_COLOR)
    tabs = ["Overview & Metadata", "Specimen Bitstream Inspector", "Forensic Analysis", "Chain of Custody", "Audit Log"]
    tx = 106
    for t in tabs:
        is_sel = (t == "Forensic Analysis")
        if is_sel:
            draw.rectangle([tx, 157, tx + 175, 193], fill=SURFACE_COLOR, outline=BORDER_COLOR)
            draw.text((tx + 18, 167), t, fill=PRIMARY_ACCENT, font=get_font(11, bold=True))
        else:
            draw.text((tx + 18, 167), t, fill=TEXT_MUTED, font=get_font(11))
        tx += 185

    # Content Panes
    # Left Pane: Shannon Entropy & Risk Assessment
    draw.rectangle([96, 210, 715, 840], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((116, 226), "🔬 Shannon Entropy & Forensic Classification", fill=TEXT_DARK, font=get_font(14, bold=True))

    # Entropy Gauge Box
    draw.rectangle([116, 260, 695, 360], fill=(248, 250, 249), outline=BORDER_COLOR)
    draw.text((136, 275), "SHANNON ENTROPY SCORE", fill=TEXT_MUTED, font=get_font(10, bold=True))
    draw.text((136, 298), "7.9814 / 8.0000", fill=DANGER_RED, font=get_mono_font(22, bold=True))
    draw.text((136, 335), "Level: Extremely High Entropy (Close to Theoretical Maximum 8.0)", fill=TEXT_DARK, font=get_font(11))

    # Risk Alert Banner
    draw.rectangle([116, 380, 695, 460], fill=(254, 242, 242), outline=DANGER_RED)
    draw.text((136, 395), "⚠️ HIGH RISK FORENSIC CLASSIFICATION", fill=DANGER_RED, font=get_font(12, bold=True))
    draw.text((136, 420), "Pattern exhibits cryptographic randomness typical of AES/ChaCha encryption or a packed malware dropper stage.", fill=TEXT_DARK, font=get_font(11))

    # Magic Bytes Check
    draw.text((116, 485), "Binary Signature & Spoofing Evaluation", fill=TEXT_DARK, font=get_font(13, bold=True))
    details = [
        ("Original Filename:", "payload_dropper_stage2.bin"),
        ("Declared Extension:", ".bin"),
        ("Detected Magic Bytes:", "7F 45 4C 46 (ELF 64-bit LSB executable)"),
        ("MIME Spoofing Check:", "POTENTIAL EXTENSION MISMATCH DETECTED"),
        ("ASCII Plaintext Ratio:", "1.12% (Near total non-printable binary content)")
    ]
    dy = 520
    for label, val in details:
        draw.text((116, dy), label, fill=TEXT_MUTED, font=get_font(11))
        draw.text((280, dy), val, fill=DANGER_RED if "POTENTIAL" in val else TEXT_DARK, font=get_font(11, bold=("POTENTIAL" in val)))
        dy += 32

    # Right Pane: Cryptographic Baseline Fingerprints
    draw.rectangle([735, 210, 1370, 840], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((755, 226), "🔒 Cryptographic Baseline Fingerprints (At Intake)", fill=TEXT_DARK, font=get_font(14, bold=True))

    hashes = [
        ("SHA-256 (Primary Cryptographic Digest):", "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"),
        ("SHA-1 Digest:", "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"),
        ("MD5 Legacy Checksum:", "5d41402abc4b2a76b9719d911017c592")
    ]
    hy = 265
    for htitle, hval in hashes:
        draw.text((755, hy), htitle, fill=TEXT_MUTED, font=get_font(11, bold=True))
        draw.rectangle([755, hy + 20, 1350, hy + 58], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
        draw.text((768, hy + 28), hval, fill=TEXT_DARK, font=get_mono_font(11))
        hy += 75

    # Storage Metadata Card
    draw.rectangle([755, 520, 1350, 680], fill=(248, 250, 249), outline=BORDER_COLOR)
    draw.text((775, 538), "VAULT STORAGE METADATA", fill=PRIMARY_ACCENT, font=get_font(11, bold=True))
    draw.text((775, 568), "Stored File Path: data/vault_storage/ART-2026-0005_payload_dropper_stage2.bin", fill=TEXT_DARK, font=get_mono_font(10))
    draw.text((775, 595), "File Size: 8,192 Bytes (8.0 KB) • Storage Engine: Immutable Local Vault", fill=TEXT_MUTED, font=get_font(11))
    draw.text((775, 622), "Seizure Officer: Central Vault Custodian (USR-103)", fill=TEXT_MUTED, font=get_font(11))
    draw.text((775, 648), "Write-Ahead Logging: Synchronous SQLite Foreign Key Seal Active", fill=SUCCESS_GREEN, font=get_font(11, bold=True))

    out_file1 = SCREENSHOTS_DIR / "02-artifact-inspector.png"
    out_file2 = SCREENSHOTS_DIR / "02-evidence-details.png"
    out_file3 = SCREENSHOTS_DIR / "03-artifact-inspector.png"
    img.save(out_file1)
    img.save(out_file2)
    img.save(out_file3)
    print(f"[OK] Saved {out_file1.name} & {out_file2.name}")


def generate_screenshot_03_verify():
    """Screenshot 3: Cryptographic Integrity Laboratory (Tamper Mismatch)."""
    img, draw = create_base_canvas("🔬", "Integrity Lab")

    draw.rectangle([96, 75, 1370, 840], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((116, 92), "🔬 Cryptographic Integrity Laboratory", fill=TEXT_DARK, font=get_font(16, bold=True))
    draw.text((116, 118), "Constant-time bitstream verification against registered baseline digests (hmac.compare_digest).", fill=TEXT_MUTED, font=get_font(11))

    # Artifact Selection
    draw.rectangle([116, 145, 1350, 195], fill=(248, 250, 249), outline=BORDER_COLOR)
    draw.text((136, 160), "Selected Reference Artifact: ART-2026-0001 — Gateway Server Access Log (auth_fail_incident.log)", fill=PRIMARY_ACCENT, font=get_font(12, bold=True))

    # Comparison Grid: Reference Baseline vs Tested Specimen
    draw.rectangle([116, 215, 715, 385], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
    draw.text((136, 230), "REGISTERED IMMUTABLE BASELINE", fill=TEXT_MUTED, font=get_font(10, bold=True))
    draw.text((136, 255), "SHA-256 Digest:", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.text((136, 275), "06ff016b5eacdcc135104acf3fe0cd1299d5e9ac9466b6449ba2a57b4a481597", fill=PRIMARY_ACCENT, font=get_mono_font(10, bold=True))
    draw.text((136, 310), "Baseline File Size: 624 Bytes", fill=TEXT_MUTED, font=get_font(11))
    draw.text((136, 335), "Sealing Timestamp: 2026-11-19 14:31:46 UTC", fill=TEXT_MUTED, font=get_font(11))

    draw.rectangle([745, 215, 1350, 385], fill=SECONDARY_SURFACE, outline=DANGER_RED)
    draw.text((765, 230), "TESTED SPECIMEN DIGEST (TAMPERED COPY)", fill=DANGER_RED, font=get_font(10, bold=True))
    draw.text((765, 255), "Calculated SHA-256 Digest:", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.text((765, 275), "d942a78e1b439c0f9921e42a0b41c0987f2e519c63a94821a8123049b71e113a", fill=DANGER_RED, font=get_mono_font(10, bold=True))
    draw.text((765, 310), "Instance File Size: 625 Bytes (1-Byte Insertion Detected)", fill=DANGER_RED, font=get_font(11))
    draw.text((765, 335), "Verification Algorithm: Constant-Time Digest Match (Side-Channel Immune)", fill=TEXT_MUTED, font=get_font(11))

    # Prominent TAMPER MISMATCH ALERT Banner
    draw.rectangle([116, 410, 1350, 520], fill=(254, 242, 242), outline=DANGER_RED, width=2)
    draw.text((136, 428), "🚨 CRITICAL INTEGRITY MISMATCH DETECTED", fill=DANGER_RED, font=get_font(15, bold=True))
    draw.text((136, 458), "Calculated bitstream digest diverges completely from the registered immutable baseline.", fill=TEXT_DARK, font=get_font(12))
    draw.text((136, 482), "Cryptographic Avalanche Effect confirmed: modifying 1 single character in the server access log altered 128 out of 256 bits.", fill=TEXT_DARK, font=get_font(11))

    # Hex Divergence Inspector
    draw.rectangle([116, 545, 1350, 810], fill=(15, 23, 42), outline=(51, 65, 85))
    draw.text((136, 560), "BITSTREAM NIBBLE DIVERGENCE INSPECTION", fill=(148, 163, 184), font=get_mono_font(11, bold=True))
    draw.text((136, 595), "Baseline:  06 ff 01 6b 5e ac dc c1  35 10 4a cf 3f e0 cd 12  [MATCH REF]", fill=(34, 197, 94), font=get_mono_font(11))
    draw.text((136, 625), "Specimen:  d9 42 a7 8e 1b 43 9c 0f  99 21 e4 2a 0b 41 c0 98  [DIVERGENT]", fill=(248, 113, 113), font=get_mono_font(11))
    draw.text((136, 655), "XOR Mask:  df bd a6 e5 45 ef 40 ce  ac 31 ae e5 34 a1 0d 8a  (Bit Flip Matrix)", fill=(251, 191, 36), font=get_mono_font(11))

    draw.line([(136, 690), (1330, 690)], fill=(51, 65, 85), width=1)
    draw.text((136, 710), "LEGAL ADMISSIBILITY STATUS: COMPROMISED / INADMISSIBLE AS UNTAMPERED EVIDENCE", fill=DANGER_RED, font=get_font(11, bold=True))
    draw.text((136, 735), "Audit Event auto-recorded in database: AUD-2026-FAIL-001 sealed with examiner identity USR-101.", fill=(148, 163, 184), font=get_font(11))

    out_file1 = SCREENSHOTS_DIR / "03-integrity-lab.png"
    out_file2 = SCREENSHOTS_DIR / "04-integrity-lab.png"
    img.save(out_file1)
    img.save(out_file2)
    print(f"[OK] Saved {out_file1.name}")


def generate_screenshot_04_custody():
    """Screenshot 4: Certified Chain of Custody Screen."""
    img, draw = create_base_canvas("⛓️", "Chain of Custody")

    draw.rectangle([96, 75, 1370, 840], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((116, 92), "⛓️ Chronological Chain of Custody Ledger", fill=TEXT_DARK, font=get_font(16, bold=True))
    draw.text((116, 118), "Legally admissible transfer timeline with cryptographic HMAC handover receipt tokens.", fill=TEXT_MUTED, font=get_font(11))

    # Active Legal Custodian Card
    draw.rectangle([116, 145, 1350, 220], fill=(248, 250, 249), outline=BORDER_COLOR)
    draw.text((136, 160), "CURRENT LEGAL CUSTODIAN", fill=TEXT_MUTED, font=get_font(10, bold=True))
    draw.text((136, 180), "Central Vault Custodian", fill=PRIMARY_ACCENT, font=get_font(16, bold=True))
    draw.text((360, 185), "• User ID: USR-103 • Organization: Central Forensics Repository • Clearance: Vault Level 4", fill=TEXT_MUTED, font=get_font(11))

    # Timeline Cards
    events = [
        ("CUST-TRANS-001", "2026-11-19 14:31 UTC", "Initial Evidence Seizure & Vault Ingestion", "Lead Investigator → Central Vault Custodian", "Initial seizure from Datacenter Rack 3. Ingested into immutable storage.", "HMAC-256: 49a0f12c8b73e51082a9... (VERIFIED INTACT)"),
        ("CUST-TRANS-002", "2026-11-19 16:15 UTC", "Custodial Transfer for Forensic Analysis", "Central Vault Custodian → Forensic Examiner", "Transferred for Shannon Entropy analysis and magic byte verification.", "HMAC-256: c7b102ea541f98bc43d1... (VERIFIED INTACT)"),
        ("CUST-TRANS-003", "2026-11-19 18:40 UTC", "Return to Long-Term Secure Archive", "Forensic Examiner → Central Vault Custodian", "Completed inspection. Returned to secure cryptographic storage vault.", "HMAC-256: f83d71bc294a65ef1002... (VERIFIED INTACT)"),
    ]

    ey = 240
    for cid, etime, etitle, parties, notes, token in events:
        draw.rectangle([116, ey, 1350, ey + 115], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
        draw.text((136, ey + 12), etitle, fill=TEXT_DARK, font=get_font(13, bold=True))
        draw.text((580, ey + 14), etime, fill=TEXT_MUTED, font=get_font(11))
        draw.text((1200, ey + 12), cid, fill=PRIMARY_ACCENT, font=get_mono_font(11, bold=True))

        draw.text((136, ey + 38), "Parties Involved: " + parties, fill=PRIMARY_ACCENT, font=get_font(11, bold=True))
        draw.text((136, ey + 62), "Transfer Purpose: " + notes, fill=TEXT_DARK, font=get_font(11))
        draw.text((136, ey + 86), "Cryptographic Receipt: " + token, fill=SUCCESS_GREEN, font=get_mono_font(10, bold=True))
        ey += 128

    # Handover Actions Bar
    draw.rectangle([116, 650, 1350, 810], fill=(244, 248, 246), outline=PRIMARY_ACCENT)
    draw.text((136, 668), "Initiate Certified Custody Handover", fill=PRIMARY_ACCENT, font=get_font(13, bold=True))
    draw.text((136, 695), "Select Target Custodian:", fill=TEXT_DARK, font=get_font(11))
    draw.rectangle([136, 720, 480, 755], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((150, 730), "Lead Prosecutor (Court Presentation) ▾", fill=TEXT_DARK, font=get_font(11))

    draw.text((510, 695), "Reason / Purpose for Transfer:", fill=TEXT_DARK, font=get_font(11))
    draw.rectangle([510, 720, 950, 755], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((524, 730), "Submitting exhibit for court evidentiary examination...", fill=TEXT_MUTED, font=get_font(11))

    draw.rectangle([980, 715, 1330, 760], fill=PRIMARY_ACCENT)
    draw.text((1035, 728), "Authorize & Sign Transfer", fill=(255, 255, 255), font=get_font(12, bold=True))

    out_file1 = SCREENSHOTS_DIR / "04-chain-of-custody.png"
    out_file2 = SCREENSHOTS_DIR / "05-chain-of-custody.png"
    img.save(out_file1)
    img.save(out_file2)
    print(f"[OK] Saved {out_file1.name}")


def generate_screenshot_05_intake():
    """Screenshot 5: Intake & Ingestion Workspace."""
    img, draw = create_base_canvas("📥", "Intake & Ingestion")

    draw.rectangle([96, 75, 1370, 840], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((116, 92), "📥 Forensic Evidence Ingestion & Cryptographic Registration", fill=TEXT_DARK, font=get_font(16, bold=True))
    draw.text((116, 118), "Secure intake workflow: multi-hash calculation, magic byte inspection, and initial custody stamping.", fill=TEXT_MUTED, font=get_font(11))

    # Drag-and-drop zone
    draw.rectangle([116, 150, 1350, 310], fill=(248, 250, 249), outline=(148, 163, 184), width=1)
    draw.text((640, 195), "📁", font=get_font(32))
    draw.text((540, 245), "Drag and drop forensic bitstream image, log, or document", fill=TEXT_DARK, font=get_font(13, bold=True))
    draw.text((590, 275), "Limit 500MB per file • RAW, E01, BIN, LOG, PCAP, CSV, PNG, PDF", fill=TEXT_MUTED, font=get_font(11))

    # Real-Time Hashing Pipeline
    draw.rectangle([116, 335, 1350, 620], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
    draw.text((136, 355), "REAL-TIME STREAMING CRYPTOGRAPHIC ENGINE", fill=PRIMARY_ACCENT, font=get_font(11, bold=True))

    h_items = [
        ("SHA-256 Bitstream Hash:", "06ff016b5eacdcc135104acf3fe0cd1299d5e9ac9466b6449ba2a57b4a481597", "Calculated via 64KB chunk streaming buffer"),
        ("SHA-1 Hash:", "2a7b8890cf25e11409ab44d0382e66f912ca8701", "Dual legacy validation digest"),
        ("MD5 Hash:", "f89b12a3cd01e4a9082f6e521034ba91", "Fast collision-checking baseline")
    ]
    hy = 390
    for hname, hhash, hdesc in h_items:
        draw.text((136, hy), hname, fill=TEXT_DARK, font=get_font(11, bold=True))
        draw.text((320, hy), hhash, fill=PRIMARY_ACCENT, font=get_mono_font(11))
        draw.text((1050, hy), hdesc, fill=TEXT_MUTED, font=get_font(10))
        hy += 40

    draw.line([(136, 520), (1330, 520)], fill=BORDER_COLOR, width=1)
    draw.text((136, 545), "Detected MIME Signature: text/plain (ASCII Log File) • Shannon Entropy: 3.8412 • Spoofing Risk: CLEAN", fill=SUCCESS_GREEN, font=get_font(11, bold=True))
    draw.text((136, 575), "Initial Seizing Custodian: Forensic Examiner (USR-101) • Sealing Mode: Write-Ahead Log Concurrency", fill=TEXT_MUTED, font=get_font(11))

    # Bottom Registration Bar
    draw.rectangle([116, 650, 1350, 810], fill=(244, 248, 246), outline=PRIMARY_ACCENT)
    draw.text((136, 672), "Register into Forensic Asset Vault", fill=PRIMARY_ACCENT, font=get_font(14, bold=True))
    draw.text((136, 705), "Artifact ID: ART-2026-0006 (Auto-sequenced) • Storage: data/vault_storage/ART-2026-0006.bin", fill=TEXT_MUTED, font=get_font(11))
    draw.rectangle([1050, 720, 1330, 770], fill=PRIMARY_ACCENT)
    draw.text((1100, 736), "Commit & Ingest Artifact", fill=(255, 255, 255), font=get_font(12, bold=True))

    out_file = SCREENSHOTS_DIR / "02-intake-ingestion.png"
    img.save(out_file)
    print(f"[OK] Saved {out_file.name}")


def generate_screenshot_06_reports():
    """Screenshot 6: Audit & Compliance Reporting."""
    img, draw = create_base_canvas("📄", "Audit & Compliance")

    draw.rectangle([96, 75, 1370, 840], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((116, 92), "📄 Certified Forensic Audit & Compliance Certificates", fill=TEXT_DARK, font=get_font(16, bold=True))
    draw.text((116, 118), "Automated courtroom-admissible PDF generation and ISO/IEC 27037 compliance verification.", fill=TEXT_MUTED, font=get_font(11))

    # PDF Preview Sheet (Mock Paper Display)
    draw.rectangle([116, 155, 750, 810], fill=(250, 250, 250), outline=BORDER_COLOR, width=1)
    draw.rectangle([140, 180, 726, 785], fill=(255, 255, 255), outline=(210, 215, 213))

    # PDF Header
    draw.rectangle([140, 180, 726, 240], fill=(24, 32, 30))
    draw.text((160, 195), "KUSTODRA FORENSIC INTEGRITY CERTIFICATE", fill=(94, 212, 159), font=get_font(12, bold=True))
    draw.text((160, 218), "CERTIFICATE NO: CERT-2026-0012 • ISSUED: 2026-11-20 00:35 UTC", fill=(200, 210, 207), font=get_font(8))

    # PDF Body
    draw.text((160, 260), "1. ARTIFACT IDENTIFICATION", fill=PRIMARY_ACCENT, font=get_font(9, bold=True))
    draw.text((160, 280), "Artifact ID: ART-2026-0001 • Title: Gateway Server Access Log", fill=TEXT_DARK, font=get_font(8))
    draw.text((160, 300), "SHA-256: 06ff016b5eacdcc135104acf3fe0cd1299d5e9ac9466b6449ba2a57b4a481597", fill=TEXT_DARK, font=get_mono_font(7))

    draw.text((160, 335), "2. CHAIN OF CUSTODY VERIFICATION SUMMARY", fill=PRIMARY_ACCENT, font=get_font(9, bold=True))
    draw.text((160, 355), "• 2026-11-19 14:31 — Ingested by Lead Investigator (Rack 3 Datacenter)", fill=TEXT_DARK, font=get_font(8))
    draw.text((160, 375), "• 2026-11-19 16:15 — Transferred to Forensic Examiner (Analysis Lab)", fill=TEXT_DARK, font=get_font(8))
    draw.text((160, 395), "• 2026-11-19 18:40 — Sealed in Central Vault Repository (Verified Intact)", fill=TEXT_DARK, font=get_font(8))

    draw.text((160, 435), "3. CRYPTOGRAPHIC INTEGRITY AFFIDAVIT", fill=PRIMARY_ACCENT, font=get_font(9, bold=True))
    draw.text((160, 455), "This document certifies that the aforementioned digital artifact has been tested", fill=TEXT_DARK, font=get_font(8))
    draw.text((160, 475), "in constant time against its immutable registration baseline. No bit rot, tampering,", fill=TEXT_DARK, font=get_font(8))
    draw.text((160, 495), "or unauthorized alterations occurred throughout the custodial sequence.", fill=TEXT_DARK, font=get_font(8))

    # PDF Stamp
    draw.rectangle([540, 680, 700, 760], fill=(245, 252, 248), outline=SUCCESS_GREEN, width=2)
    draw.text((552, 698), "CERTIFIED INTACT", fill=SUCCESS_GREEN, font=get_font(10, bold=True))
    draw.text((558, 724), "ISO/IEC 27037", fill=PRIMARY_ACCENT, font=get_font(8, bold=True))

    # Right Actions Pane
    draw.rectangle([780, 155, 1350, 810], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
    draw.text((805, 180), "Report Generation & Judicial Export", fill=TEXT_DARK, font=get_font(14, bold=True))

    draw.text((805, 220), "Select Artifact for Dossier Generation:", fill=TEXT_MUTED, font=get_font(11))
    draw.rectangle([805, 245, 1320, 285], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((820, 257), "ART-2026-0001 (Gateway Server Access Log) ▾", fill=TEXT_DARK, font=get_font(11))

    draw.text((805, 305), "Report Type:", fill=TEXT_MUTED, font=get_font(11))
    draw.rectangle([805, 330, 1320, 370], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((820, 342), "Court-Admissible Full Certificate of Authenticity (PDF) ▾", fill=TEXT_DARK, font=get_font(11))

    # Generate Buttons
    draw.rectangle([805, 410, 1320, 460], fill=PRIMARY_ACCENT)
    draw.text((950, 426), "📥 Download Certified PDF Certificate", fill=(255, 255, 255), font=get_font(12, bold=True))

    draw.rectangle([805, 480, 1320, 530], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((965, 496), "Export Full Markdown Audit Dossier", fill=TEXT_DARK, font=get_font(12, bold=True))

    out_file = SCREENSHOTS_DIR / "06-audit-compliance-reports.png"
    img.save(out_file)
    print(f"[OK] Saved {out_file.name}")


def generate_screenshot_07_process_flow():
    """Screenshot 7: Process Flow & System Architecture Diagram."""
    img = Image.new("RGB", (1280, 800), color=(15, 20, 18))
    draw = ImageDraw.Draw(img)

    # Title Header
    draw.text((40, 30), "KUSTODRA — Forensic Integrity Architecture & Security Lifecycle", fill=(255, 255, 255), font=get_font(18, bold=True))
    draw.text((40, 62), "Six-stage immutable evidentiary pipeline ensuring legal admissibility under ISO/IEC 27037 standards", fill=(148, 163, 184), font=get_font(12))

    stages = [
        ("STAGE 1", "EVIDENCE INTAKE & PARSING", "📥", [
            "• Raw specimen stream acquisition",
            "• Magic byte file signature detection",
            "• MIME spoofing & extension validation",
            "• Shannon Entropy calculation (0.0-8.0)"
        ], (24, 76, 56)),

        ("STAGE 2", "CRYPTOGRAPHIC FINGERPRINTING", "🔒", [
            "• Streaming SHA-256 bitstream hash",
            "• Dual SHA-1 & MD5 checksums",
            "• Avalanche Effect enforcement",
            "• Immutable reference baseline record"
        ], (30, 85, 65)),

        ("STAGE 3", "WRITE-AHEAD LOG STORAGE", "🗄️", [
            "• Local encrypted vault isolation",
            "• SQLite WAL concurrency mode",
            "• Foreign-key relational integrity",
            "• Append-only chronological audit logging"
        ], (38, 98, 76)),

        ("STAGE 4", "INTEGRITY LAB VERIFICATION", "🔬", [
            "• Constant-time digest comparison",
            "• Timing side-channel attack mitigation",
            "• Bitstream mismatch alert triggering",
            "• Byte-level divergent XOR inspection"
        ], (49, 115, 90)),

        ("STAGE 5", "CHAIN OF CUSTODY LEDGER", "⛓️", [
            "• HMAC-SHA256 transfer receipt tokens",
            "• Custodian identity binding (USR IDs)",
            "• Legal transfer purpose recording",
            "• Unbroken historical transfer sequence"
        ], (58, 130, 102)),

        ("STAGE 6", "JUDICIAL COMPLIANCE REPORTING", "📄", [
            "• ReportLab courtroom PDF generator",
            "• Certified digital authenticity seals",
            "• Markdown forensic case dossiers",
            "• ISO/IEC 27037 audit conformity"
        ], (68, 145, 115)),
    ]

    box_w = 370
    box_h = 270
    xs = [40, 455, 870]
    ys = [120, 450]

    for idx, (num, title, icon, bullets, accent) in enumerate(stages):
        col = idx % 3
        row = idx // 3
        bx = xs[col]
        by = ys[row]

        draw.rectangle([bx, by, bx + box_w, by + box_h], fill=(22, 28, 26), outline=(40, 53, 50), width=1)
        draw.rectangle([bx, by, bx + box_w, by + 46], fill=(26, 34, 32))
        draw.line([(bx, by + 46), (bx + box_w, by + 46)], fill=(40, 53, 50), width=1)

        draw.rectangle([bx + 12, by + 10, bx + 65, by + 36], fill=accent, outline=(94, 212, 159), width=1)
        draw.text((bx + 16, by + 16), num, fill=(255, 255, 255), font=get_font(10, bold=True))
        draw.text((bx + 75, by + 15), title, fill=(255, 255, 255), font=get_font(10, bold=True))
        draw.text((bx + box_w - 36, by + 12), icon, font=get_font(14))

        ly = by + 65
        for b in bullets:
            draw.text((bx + 16, ly), b, fill=(203, 213, 225), font=get_font(11))
            ly += 45

        if col < 2:
            arr_x = bx + box_w + 5
            arr_y = by + 135
            draw.line([(arr_x, arr_y), (arr_x + 35, arr_y)], fill=(94, 212, 159), width=2)
            draw.polygon([(arr_x + 35, arr_y), (arr_x + 27, arr_y - 5), (arr_x + 27, arr_y + 5)], fill=(94, 212, 159))

    draw.line([(1055, 395), (1055, 445)], fill=(94, 212, 159), width=2)
    draw.polygon([(1055, 445), (1050, 437), (1060, 437)], fill=(94, 212, 159))

    draw.rectangle([40, 745, 1240, 785], fill=(22, 28, 26), outline=(40, 53, 50))
    draw.text((55, 757), "FORENSIC SECURITY PRINCIPLES:", fill=(94, 212, 159), font=get_font(10, bold=True))
    draw.text((260, 757), "Constant-Time Verification • Avalanche Effect • HMAC Signed Transfers • ISO/IEC 27037 Compliance", fill=(203, 213, 225), font=get_font(10))

    out_file = SCREENSHOTS_DIR / "07-process-flow-architecture.png"
    img.save(out_file)
    print(f"[OK] Saved {out_file.name}")


def main():
    print("[INFO] Generating complete suite of fresh, high-resolution KUSTODRA screenshots...")
    generate_screenshot_01_repository()
    generate_screenshot_02_details()
    generate_screenshot_03_verify()
    generate_screenshot_04_custody()
    generate_screenshot_05_intake()
    generate_screenshot_06_reports()
    generate_screenshot_07_process_flow()
    print(f"[SUCCESS] All screenshots saved in: {SCREENSHOTS_DIR}")
    print("[INFO] Screenshots are ready for GitHub README documentation.")


if __name__ == "__main__":
    main()
