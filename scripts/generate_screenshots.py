"""
TRACEVAULT - High-Resolution Screenshot Generator
Generates clean, professional UI screenshots directly reflecting
the visual design system and forensic workstation screens.
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Visual Design Palette
BG_COLOR = (244, 246, 245)      # #F4F6F5
SURFACE_COLOR = (255, 255, 255) # #FFFFFF
TEXT_DARK = (32, 41, 39)        # #202927
TEXT_MUTED = (104, 115, 111)    # #68736F
PRIMARY_ACCENT = (49, 95, 80)   # #315F50
BORDER_COLOR = (225, 230, 227)  # #E1E6E3
MUTED_BG = (237, 241, 238)      # #EDF1EE
SUCCESS_GREEN = (40, 122, 84)   # #287A54
DANGER_RED = (183, 71, 71)      # #B74747
WARNING_AMBER = (183, 123, 41)  # #B77B29


def get_font(size: int = 14, bold: bool = False):
    """Load standard font or fallback."""
    try:
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except Exception:
        return ImageFont.load_default()


def get_mono_font(size: int = 12):
    """Load monospace font or fallback."""
    try:
        return ImageFont.truetype("consola.ttf", size)
    except Exception:
        return ImageFont.load_default()


def create_base_canvas(active_nav: str = "Overview", title: str = "Evidence Overview", subtitle: str = "") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Create the workstation window frame with sidebar and top header."""
    img = Image.new("RGB", (1280, 800), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 1. Sidebar (Width: 240px)
    draw.rectangle([0, 0, 240, 800], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    
    # Sidebar Header
    draw.text((24, 28), "TRACEVAULT", fill=PRIMARY_ACCENT, font=get_font(18, bold=True))
    draw.text((24, 52), "Digital Forensics & Custody", fill=TEXT_MUTED, font=get_font(11))
    draw.line([(24, 75), (216, 75)], fill=BORDER_COLOR, width=1)

    # Nav items
    nav_items = [
        "Overview",
        "Register Evidence",
        "Evidence Repository",
        "Evidence Details & Metadata",
        "Integrity Verification",
        "Chain of Custody",
        "Audit Reports",
        "System Settings"
    ]
    y_pos = 95
    for item in nav_items:
        is_active = (item == active_nav)
        if is_active:
            draw.rectangle([16, y_pos - 4, 224, y_pos + 26], fill=MUTED_BG, outline=BORDER_COLOR, width=1)
            draw.rectangle([16, y_pos - 4, 20, y_pos + 26], fill=PRIMARY_ACCENT)
            draw.text((28, y_pos + 2), item, fill=PRIMARY_ACCENT, font=get_font(13, bold=True))
        else:
            draw.text((28, y_pos + 2), item, fill=TEXT_DARK, font=get_font(13))
        y_pos += 38

    # Sidebar Footer Telemetry
    draw.line([(24, 680), (216, 680)], fill=BORDER_COLOR, width=1)
    draw.text((24, 695), "NODE: TRACE-NODE-41", fill=TEXT_MUTED, font=get_mono_font(11))
    draw.text((24, 715), "LEDGER: SHA-256 SEALED", fill=SUCCESS_GREEN, font=get_mono_font(11))
    draw.text((24, 735), "STORAGE: SQLite WAL (Active)", fill=TEXT_MUTED, font=get_mono_font(11))

    # 2. Main Content Top Bar
    draw.rectangle([240, 0, 1280, 60], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((264, 16), "TRACEVAULT EVIDENCE WORKSTATION", fill=PRIMARY_ACCENT, font=get_font(14, bold=True))
    draw.text((264, 34), "Node Alpha-01 &bull; Secure Digital Evidence Depository", fill=TEXT_MUTED, font=get_font(11))

    draw.text((1050, 16), "Special Agent Ragu Ram", fill=TEXT_DARK, font=get_font(13, bold=True))
    draw.text((1050, 34), "Lead Forensic Examiner (FE-8842)", fill=TEXT_MUTED, font=get_font(11))

    # Main Area Heading
    draw.text((264, 85), title, fill=TEXT_DARK, font=get_font(22, bold=True))
    if subtitle:
        draw.text((264, 115), subtitle, fill=TEXT_MUTED, font=get_font(13))

    return img, draw


def generate_screenshot_01_overview():
    """Screenshot 1: Overview Dashboard."""
    img, draw = create_base_canvas("Overview", "Evidence Overview", "Monitor registered evidence, integrity verification and custody activity across active cases.")

    # 4 Metric Cards
    metrics = [
        ("TOTAL REGISTERED EVIDENCE", "5", PRIMARY_ACCENT),
        ("VERIFIED INTEGRITY", "1", SUCCESS_GREEN),
        ("PENDING VERIFICATION", "4", WARNING_AMBER),
        ("INTEGRITY DISCREPANCIES", "0", DANGER_RED)
    ]
    card_x = 264
    for label, val, color in metrics:
        draw.rectangle([card_x, 145, card_x + 225, 215], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
        draw.rectangle([card_x, 145, card_x + 4, 215], fill=color)
        draw.text((card_x + 14, 155), label, fill=TEXT_MUTED, font=get_font(10, bold=True))
        draw.text((card_x + 14, 175), val, fill=color, font=get_font(24, bold=True))
        card_x += 245

    # Button
    draw.rectangle([264, 230, 440, 265], fill=PRIMARY_ACCENT, outline=PRIMARY_ACCENT)
    draw.text((284, 240), "+ Register New Evidence", fill=(255, 255, 255), font=get_font(12, bold=True))

    # Left Card: Recent Evidence
    draw.rectangle([264, 280, 830, 750], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((280, 295), "Recent Evidence", fill=TEXT_DARK, font=get_font(15, bold=True))
    draw.text((280, 315), "Latest digital artifacts registered into vault custody", fill=TEXT_MUTED, font=get_font(12))
    draw.line([(280, 335), (814, 335)], fill=BORDER_COLOR, width=1)

    # Table Header
    draw.text((280, 345), "EVIDENCE ID", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.text((390, 345), "TITLE", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.text((570, 345), "CATEGORY", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.text((710, 345), "STATUS", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.line([(280, 365), (814, 365)], fill=BORDER_COLOR, width=1)

    # Sample rows
    rows = [
        ("EV-2026-0001", "Gateway Server Access Log", "System & Audit Log", "Verified", SUCCESS_GREEN),
        ("EV-2026-0002", "Perimeter Cam 04 Still Frame", "Forensic Still Image", "Pending", WARNING_AMBER),
        ("EV-2026-0003", "Offshore Wire Transfer CSV", "Digital Document", "Pending", WARNING_AMBER),
        ("EV-2026-0004", "Confidential Asset Agreement", "Digital Document", "Pending", WARNING_AMBER),
        ("EV-2026-0005", "Encrypted Payload Binary", "Encrypted / Packed", "Pending", WARNING_AMBER)
    ]
    r_y = 380
    for eid, title, cat, status, color in rows:
        draw.text((280, r_y), eid, fill=PRIMARY_ACCENT, font=get_mono_font(11))
        draw.text((390, r_y), title, fill=TEXT_DARK, font=get_font(12, bold=True))
        draw.text((570, r_y), cat, fill=TEXT_MUTED, font=get_font(11))
        # Status pill
        draw.rectangle([710, r_y - 2, 780, r_y + 16], fill=MUTED_BG, outline=color)
        draw.text((720, r_y), status, fill=color, font=get_font(10, bold=True))
        draw.line([(280, r_y + 24), (814, r_y + 24)], fill=BORDER_COLOR, width=1)
        r_y += 38

    # Right Card: Recent Activity
    draw.rectangle([850, 280, 1240, 750], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((866, 295), "Recent Activity", fill=TEXT_DARK, font=get_font(15, bold=True))
    draw.text((866, 315), "Chronological ledger of verified forensic events", fill=TEXT_MUTED, font=get_font(12))
    draw.line([(866, 335), (1224, 335)], fill=BORDER_COLOR, width=1)

    events = [
        ("INTEGRITY CHECK MATCH", "EV-2026-0001", "Baseline SHA-256 verified identical match.", SUCCESS_GREEN),
        ("CUSTODY TRANSFERRED", "EV-2026-0001", "Released from Det. Vance to Agent Ragu Ram.", WARNING_AMBER),
        ("CUSTODY TRANSFERRED", "EV-2026-0002", "Transferred to Vault Custodian Marcus Chen.", WARNING_AMBER),
        ("EVIDENCE REGISTERED", "EV-2026-0005", "High-entropy binary artifact ingested.", PRIMARY_ACCENT),
        ("EVIDENCE REGISTERED", "EV-2026-0001", "Apache access log bitstream sealed.", PRIMARY_ACCENT)
    ]
    e_y = 355
    for etype, eid, desc, col in events:
        draw.ellipse([870, e_y + 3, 878, e_y + 11], fill=col)
        draw.line([(874, e_y + 11), (874, e_y + 60)], fill=BORDER_COLOR, width=2)
        draw.text((890, e_y), f"{etype} &bull; {eid}", fill=col, font=get_font(11, bold=True))
        draw.text((890, e_y + 18), desc, fill=TEXT_MUTED, font=get_font(10))
        e_y += 55

    img.save(SCREENSHOTS_DIR / "01-overview-dashboard.png")


def generate_screenshot_02_register():
    """Screenshot 2: Register New Evidence."""
    img, draw = create_base_canvas("Register Evidence", "Register New Evidence", "Ingest digital artifacts into secure vault custody with automatic SHA-256 hashing.")

    # Upload Card
    draw.rectangle([264, 150, 1240, 260], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 165), "Step 1 — Select Evidence File", fill=TEXT_DARK, font=get_font(14, bold=True))
    draw.rectangle([284, 195, 1220, 245], fill=MUTED_BG, outline=BORDER_COLOR, width=1)
    draw.text((304, 212), "Selected File: server_access_log.log (8,920 Bytes) — Detected: Plain ASCII / UTF-8 Text", fill=PRIMARY_ACCENT, font=get_font(12, bold=True))

    # Details Card
    draw.rectangle([264, 275, 1240, 520], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 290), "Step 2 — Evidence Details & Case Association", fill=TEXT_DARK, font=get_font(14, bold=True))

    draw.text((284, 325), "Case Reference: CASE-2026-CR-0842 (Operation Silver Lattice)", fill=TEXT_DARK, font=get_font(12))
    draw.text((284, 360), "Evidence Title: Gateway Server Access Log", fill=TEXT_DARK, font=get_font(12, bold=True))
    draw.text((284, 395), "Forensic Category: System & Audit Log", fill=TEXT_DARK, font=get_font(12))
    draw.text((284, 430), "Seized By: Detective Sarah Vance", fill=TEXT_DARK, font=get_font(12))
    draw.text((284, 465), "Seizure Location: Server Rack B-12, IP 10.0.4.1", fill=TEXT_DARK, font=get_font(12))

    # Cryptographic Hash Preview Card
    draw.rectangle([264, 535, 1240, 680], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 550), "Step 3 — Cryptographic Baseline Fingerprints", fill=TEXT_DARK, font=get_font(14, bold=True))
    draw.text((284, 575), "PRIMARY SHA-256 HASH SEAL:", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.rectangle([284, 595, 1220, 630], fill=MUTED_BG, outline=BORDER_COLOR, width=1)
    draw.text((294, 608), "8f2b3a1c904e5d6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a", fill=TEXT_DARK, font=get_mono_font(12))

    draw.rectangle([264, 700, 440, 740], fill=PRIMARY_ACCENT)
    draw.text((310, 712), "Register Evidence", fill=(255, 255, 255), font=get_font(13, bold=True))

    img.save(SCREENSHOTS_DIR / "02-register-evidence.png")


def generate_screenshot_03_verification_mismatch():
    """Screenshot 3: Integrity Verification - Tampering Detected."""
    img, draw = create_base_canvas("Integrity Verification", "Integrity Verification Engine", "Cryptographic file comparison engine. Calculate current SHA-256 against baseline.")

    # Status Alert: Mismatch
    draw.rectangle([264, 150, 1240, 240], fill=(251, 239, 239), outline=DANGER_RED, width=2)
    draw.text((284, 165), "INTEGRITY MISMATCH DETECTED (TAMPERING ALERT)", fill=DANGER_RED, font=get_font(15, bold=True))
    draw.text((284, 192), "The calculated SHA-256 hash does not match the registered hash.", fill=TEXT_DARK, font=get_font(13))
    draw.text((284, 212), "The file contents differ from the registered version. Verification ID: CHK-MISMATCH-001 &bull; Severity: Critical", fill=TEXT_MUTED, font=get_font(11))

    # Side-by-side hash comparison
    draw.rectangle([264, 255, 1240, 430], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 270), "Cryptographic Comparison Details", fill=TEXT_DARK, font=get_font(14, bold=True))

    draw.text((284, 300), "EXPECTED SHA-256 (REGISTERED INTAKE BASELINE):", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.rectangle([284, 320, 1220, 355], fill=MUTED_BG, outline=BORDER_COLOR, width=1)
    draw.text((294, 332), "9a4f61e88d401c29e612cb723508b98127394ba0210e7b8a7f0129bc4123de45", fill=SUCCESS_GREEN, font=get_mono_font(12))

    draw.text((284, 365), "CALCULATED CURRENT SHA-256 (PAYLOAD TESTED):", fill=DANGER_RED, font=get_font(11, bold=True))
    draw.rectangle([284, 385, 1220, 420], fill=(251, 239, 239), outline=DANGER_RED, width=1)
    draw.text((294, 397), "7c1d09ab22ef1489012356bcdef98120348712a091823746bcde091234567890", fill=DANGER_RED, font=get_mono_font(12))

    # Historical checks
    draw.rectangle([264, 450, 1240, 750], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 465), "Verification History for EV-2026-0001", fill=TEXT_DARK, font=get_font(14, bold=True))

    draw.text((284, 500), "2026-11-19 14:15:00 UTC &bull; Examiner: Special Agent Ragu Ram &bull; Mode: Tampered Sample Test", fill=TEXT_DARK, font=get_font(12))
    draw.text((1150, 500), "Mismatch", fill=DANGER_RED, font=get_font(12, bold=True))
    draw.line([(284, 525), (1220, 525)], fill=BORDER_COLOR, width=1)

    draw.text((284, 540), "2026-11-19 04:45:00 UTC &bull; Examiner: Special Agent Ragu Ram &bull; Mode: Vault Baseline Check", fill=TEXT_DARK, font=get_font(12))
    draw.text((1150, 540), "Match", fill=SUCCESS_GREEN, font=get_font(12, bold=True))

    img.save(SCREENSHOTS_DIR / "03-integrity-verification-mismatch.png")


def generate_screenshot_04_custody_timeline():
    """Screenshot 4: Chain of Custody Timeline."""
    img, draw = create_base_canvas("Chain of Custody", "Chain-of-Custody Timeline", "Forensic accountability ledger. Track, transfer, and verify legal possession.")

    # Active Custodian Banner
    draw.rectangle([264, 150, 1240, 220], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.rectangle([264, 150, 268, 220], fill=PRIMARY_ACCENT)
    draw.text((284, 165), "ACTIVE LEGAL CUSTODIAN", fill=TEXT_MUTED, font=get_font(10, bold=True))
    draw.text((284, 185), "Special Agent Ragu Ram (Lead Forensic Examiner)", fill=TEXT_DARK, font=get_font(15, bold=True))
    draw.text((1100, 165), "EV-2026-0001", fill=PRIMARY_ACCENT, font=get_mono_font(13))
    draw.text((1100, 185), "Status: Verified", fill=SUCCESS_GREEN, font=get_font(12, bold=True))

    # Left: Timeline (Width: 600px)
    draw.rectangle([264, 235, 830, 750], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 250), "Chronological Transfer History", fill=TEXT_DARK, font=get_font(14, bold=True))
    draw.line([(284, 275), (810, 275)], fill=BORDER_COLOR, width=1)

    # Timeline entry 1
    draw.ellipse([290, 300, 298, 308], fill=PRIMARY_ACCENT)
    draw.line([(294, 308), (294, 400)], fill=PRIMARY_ACCENT, width=2)
    draw.text((310, 295), "2026-11-18 04:45:00 UTC", fill=TEXT_MUTED, font=get_font(10))
    draw.text((310, 312), "INITIAL SEIZURE & INTAKE", fill=PRIMARY_ACCENT, font=get_font(12, bold=True))
    draw.text((310, 332), "Collected by Detective Sarah Vance from Server Rack B-12.", fill=TEXT_DARK, font=get_font(11))
    draw.text((310, 350), "Cryptographic SHA-256 seal anchored.", fill=TEXT_MUTED, font=get_font(10))

    # Timeline entry 2
    draw.ellipse([290, 410, 298, 418], fill=SUCCESS_GREEN)
    draw.text((310, 405), "2026-11-18 06:10:00 UTC", fill=TEXT_MUTED, font=get_font(10))
    draw.text((310, 422), "Det. Sarah Vance &rarr; Special Agent Ragu Ram", fill=TEXT_DARK, font=get_font(12, bold=True))
    draw.text((310, 442), "Reason: Forensic Lab Analysis [Integrity Verified on Transfer]", fill=SUCCESS_GREEN, font=get_font(11))
    draw.text((310, 460), "Receipt Token: c9f1a238b0123... Sealed in SQLite Ledger", fill=TEXT_MUTED, font=get_mono_font(10))

    # Right: Transfer Form
    draw.rectangle([850, 235, 1240, 750], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((870, 250), "Transfer Custody Form", fill=TEXT_DARK, font=get_font(14, bold=True))
    draw.text((870, 270), "Authorize release to another certified custodian", fill=TEXT_MUTED, font=get_font(11))
    draw.line([(870, 290), (1220, 290)], fill=BORDER_COLOR, width=1)

    draw.text((870, 310), "Releasing Custodian: Special Agent Ragu Ram", fill=TEXT_DARK, font=get_font(11))
    draw.text((870, 350), "Recipient: Marcus Chen (Evidence Vault Custodian)", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.text((870, 390), "Transfer Reason: Secure Long-Term Vault Storage", fill=TEXT_DARK, font=get_font(11))
    draw.text((870, 430), "Notes: Post-examination lockbox transfer.", fill=TEXT_DARK, font=get_font(11))
    draw.text((870, 470), "[X] Perform immediate SHA-256 verification upon release", fill=PRIMARY_ACCENT, font=get_font(11))
    draw.text((870, 500), "[X] I legally certify this custody transfer", fill=PRIMARY_ACCENT, font=get_font(11, bold=True))

    draw.rectangle([870, 540, 1100, 580], fill=PRIMARY_ACCENT)
    draw.text((900, 552), "Record Custody Transfer", fill=(255, 255, 255), font=get_font(12, bold=True))

    img.save(SCREENSHOTS_DIR / "04-chain-of-custody-timeline.png")


def main():
    print("[INFO] Generating high-resolution UI screenshots...")
    generate_screenshot_01_overview()
    generate_screenshot_02_register()
    generate_screenshot_03_verification_mismatch()
    generate_screenshot_04_custody_timeline()
    print(f"[SUCCESS] All screenshots saved in: {SCREENSHOTS_DIR.resolve()}")


if __name__ == "__main__":
    main()
