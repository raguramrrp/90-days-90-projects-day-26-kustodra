"""
TRACEVAULT - High-Resolution Screenshot Generator
Generates clean, professional UI screenshots directly reflecting
the Forensic Evidence Workbench visual design system.
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Forensic Color Palette
BG_COLOR = (242, 244, 241)          # #F2F4F1
SURFACE_COLOR = (255, 255, 255)     # #FFFFFF
SECONDARY_SURFACE = (233, 238, 234) # #E9EEEA
TEXT_DARK = (32, 42, 39)            # #202A27
TEXT_MUTED = (105, 117, 112)        # #697570
PRIMARY_ACCENT = (49, 95, 80)       # #315F50
BORDER_COLOR = (220, 227, 222)      # #DCE3DE
SUCCESS_GREEN = (40, 122, 84)       # #287A54
DANGER_RED = (183, 71, 71)          # #B74747
WARNING_AMBER = (183, 123, 41)      # #B77B29


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


def create_base_canvas(active_nav: str = "Overview", title: str = "Evidence Intelligence", subtitle: str = "") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Create the workstation window frame with sidebar and top header."""
    img = Image.new("RGB", (1280, 800), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 1. Sidebar (Width: 240px)
    draw.rectangle([0, 0, 240, 800], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    
    # Sidebar Brand
    draw.text((24, 26), "TRACEVAULT", fill=PRIMARY_ACCENT, font=get_font(18, bold=True))
    draw.text((24, 48), "FORENSIC WORKSTATION", fill=TEXT_MUTED, font=get_font(10, bold=True))
    draw.line([(24, 68), (216, 68)], fill=BORDER_COLOR, width=1)

    # Nav items
    nav_items = [
        ("Overview", "📋"),
        ("Evidence Intake", "📥"),
        ("Evidence Repository", "🗄️"),
        ("Integrity Lab", "🔬"),
        ("Chain of Custody", "⛓️"),
        ("Audit & Reports", "📄"),
        ("Settings", "⚙️")
    ]
    y_pos = 85
    for item, icon in nav_items:
        is_active = (item == active_nav)
        if is_active:
            draw.rectangle([16, y_pos - 4, 224, y_pos + 28], fill=PRIMARY_ACCENT, outline=PRIMARY_ACCENT)
            draw.text((28, y_pos + 2), f"{icon}  {item}", fill=(255, 255, 255), font=get_font(13, bold=True))
        else:
            draw.text((28, y_pos + 2), f"{icon}  {item}", fill=TEXT_DARK, font=get_font(13))
        y_pos += 40

    # Sidebar Footer Telemetry
    draw.line([(24, 685), (216, 685)], fill=BORDER_COLOR, width=1)
    draw.text((24, 700), "STORAGE: SQLite WAL Mode", fill=TEXT_MUTED, font=get_mono_font(11))
    draw.text((24, 720), "HASHING: SHA-256 Bitstream", fill=PRIMARY_ACCENT, font=get_mono_font(11))
    draw.text((24, 740), "LEDGER: Chained / Immutable", fill=SUCCESS_GREEN, font=get_mono_font(11))

    # 2. Main Content Top Header
    draw.rectangle([240, 0, 1280, 56], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((264, 14), "TRACEVAULT", fill=PRIMARY_ACCENT, font=get_font(15, bold=True))
    draw.text((264, 32), "DIGITAL FORENSICS • EVIDENCE MANAGEMENT", fill=TEXT_MUTED, font=get_font(9, bold=True))

    draw.text((1050, 14), "Forensic Examiner", fill=TEXT_DARK, font=get_font(13, bold=True))
    draw.text((1050, 32), "Lead Examiner • Digital Forensics Unit", fill=TEXT_MUTED, font=get_font(10))

    # Main Area Heading
    draw.text((264, 78), title, fill=TEXT_DARK, font=get_font(22, bold=True))
    if subtitle:
        draw.text((264, 108), subtitle, fill=TEXT_MUTED, font=get_font(12))

    return img, draw


def generate_screenshot_01_overview():
    """Screenshot 1: Evidence Intelligence Overview."""
    img, draw = create_base_canvas("Overview", "Evidence Intelligence", "Monitor evidence records, cryptographic integrity and chain-of-custody activity.")

    # 4 Summary Strip Blocks
    metrics = [
        ("REGISTERED EVIDENCE", "5", PRIMARY_ACCENT),
        ("VERIFIED INTEGRITY", "4", SUCCESS_GREEN),
        ("PENDING VERIFICATION", "1", WARNING_AMBER),
        ("INTEGRITY DISCREPANCIES", "0", DANGER_RED)
    ]
    card_x = 264
    for label, val, color in metrics:
        draw.rectangle([card_x, 138, card_x + 225, 205], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
        draw.text((card_x + 14, 148), label, fill=TEXT_MUTED, font=get_font(10, bold=True))
        draw.text((card_x + 14, 168), val, fill=color, font=get_font(22, bold=True))
        card_x += 245

    # Register Button in header area
    draw.rectangle([1100, 78, 1240, 110], fill=PRIMARY_ACCENT)
    draw.text((1115, 87), "+ Register Evidence", fill=(255, 255, 255), font=get_font(11, bold=True))

    # Left Section: Evidence Register
    draw.rectangle([264, 225, 830, 520], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((280, 238), "Evidence Register", fill=TEXT_DARK, font=get_font(15, bold=True))
    draw.text((280, 256), "Active digital artifacts in custody", fill=TEXT_MUTED, font=get_font(11))
    draw.line([(280, 274), (814, 274)], fill=BORDER_COLOR, width=1)

    draw.text((280, 282), "ID", fill=TEXT_MUTED, font=get_font(10, bold=True))
    draw.text((370, 282), "EVIDENCE NAME", fill=TEXT_MUTED, font=get_font(10, bold=True))
    draw.text((580, 282), "TYPE", fill=TEXT_MUTED, font=get_font(10, bold=True))
    draw.text((680, 282), "STATUS", fill=TEXT_MUTED, font=get_font(10, bold=True))
    draw.line([(280, 298), (814, 298)], fill=BORDER_COLOR, width=1)

    rows = [
        ("EV-2026-0001", "Gateway Server Access Log", "LOG", "Verified", SUCCESS_GREEN),
        ("EV-2026-0002", "Perimeter Cam Still Frame", "IMAGE", "Verified", SUCCESS_GREEN),
        ("EV-2026-0003", "Offshore Wire Transfer CSV", "DOCUMENT", "Verified", SUCCESS_GREEN),
        ("EV-2026-0004", "Confidential Asset Agreement", "DOCUMENT", "Verified", SUCCESS_GREEN),
        ("EV-2026-0005", "Encrypted Payload Binary", "BINARY", "Pending", WARNING_AMBER)
    ]
    r_y = 310
    for eid, title, cat, status, color in rows:
        draw.text((280, r_y), eid, fill=PRIMARY_ACCENT, font=get_mono_font(11))
        draw.text((370, r_y), title, fill=TEXT_DARK, font=get_font(11, bold=True))
        draw.rectangle([580, r_y - 2, 630, r_y + 14], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
        draw.text((586, r_y), cat, fill=TEXT_DARK, font=get_mono_font(9))
        draw.rectangle([680, r_y - 2, 750, r_y + 14], fill=SECONDARY_SURFACE, outline=color)
        draw.text((690, r_y), status, fill=color, font=get_font(10, bold=True))
        draw.line([(280, r_y + 20), (814, r_y + 20)], fill=BORDER_COLOR, width=1)
        r_y += 32

    # Right Section: Custody Activity
    draw.rectangle([850, 225, 1240, 520], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((866, 238), "Custody Activity", fill=TEXT_DARK, font=get_font(15, bold=True))
    draw.text((866, 256), "Chronological timeline of custody events", fill=TEXT_MUTED, font=get_font(11))
    draw.line([(866, 274), (1224, 274)], fill=BORDER_COLOR, width=1)

    events = [
        ("Integrity Check Match", "EV-2026-0001", "Baseline SHA-256 verified identical match.", SUCCESS_GREEN),
        ("Custody Transferred", "EV-2026-0001", "Released from Lead Investigator to Forensic Examiner.", WARNING_AMBER),
        ("Custody Transferred", "EV-2026-0002", "Transferred to Vault Evidence Custodian.", WARNING_AMBER),
        ("Evidence Registered", "EV-2026-0005", "High-entropy binary artifact ingested.", PRIMARY_ACCENT),
        ("Evidence Registered", "EV-2026-0001", "Server access log bitstream sealed.", PRIMARY_ACCENT)
    ]
    e_y = 290
    for etype, eid, desc, col in events:
        draw.text((866, e_y), etype, fill=col, font=get_font(11, bold=True))
        draw.text((1150, e_y), eid, fill=TEXT_MUTED, font=get_mono_font(10))
        draw.text((866, e_y + 16), desc, fill=TEXT_DARK, font=get_font(10))
        draw.line([(866, e_y + 34), (1224, e_y + 34)], fill=BORDER_COLOR, width=1)
        e_y += 42

    # Bottom Section: Integrity Activity
    draw.rectangle([264, 540, 1240, 770], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((280, 555), "Integrity Activity", fill=TEXT_DARK, font=get_font(15, bold=True))
    draw.text((280, 575), "Recent cryptographic hash verifications and authenticity checks", fill=TEXT_MUTED, font=get_font(11))
    draw.line([(280, 595), (1224, 595)], fill=BORDER_COLOR, width=1)

    draw.text((280, 610), "EV-2026-0001", fill=PRIMARY_ACCENT, font=get_mono_font(11))
    draw.text((400, 610), "2026-11-19 14:15:00 UTC", fill=TEXT_MUTED, font=get_font(11))
    draw.text((580, 610), "Forensic Examiner", fill=TEXT_DARK, font=get_font(11))
    draw.text((750, 610), "Match", fill=SUCCESS_GREEN, font=get_font(11, bold=True))
    draw.text((850, 610), "e3b0c44298fc1c14...855", fill=TEXT_DARK, font=get_mono_font(11))

    img.save(SCREENSHOTS_DIR / "01-overview-dashboard.png")


def generate_screenshot_02_intake():
    """Screenshot 2: Evidence Intake."""
    img, draw = create_base_canvas("Evidence Intake", "Evidence Intake", "Register a digital artifact and establish its initial integrity reference.")

    # Section A
    draw.rectangle([264, 140, 1240, 240], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 155), "Section A — File Acquisition", fill=PRIMARY_ACCENT, font=get_font(14, bold=True))
    draw.text((284, 175), "Acquire the digital artifact into secure memory. Cryptographic hashing executes automatically.", fill=TEXT_MUTED, font=get_font(11))
    draw.rectangle([284, 195, 1220, 225], fill=SECONDARY_SURFACE, outline=BORDER_COLOR, width=1)
    draw.text((294, 203), "Acquired: server_access_log.log • Ext: .log • MIME: text/plain • Size: 8,920 Bytes • Header: Plain ASCII Text", fill=PRIMARY_ACCENT, font=get_mono_font(11))

    # Section B
    draw.rectangle([264, 255, 1240, 430], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 270), "Section B — Evidence Description & Provenance", fill=PRIMARY_ACCENT, font=get_font(14, bold=True))
    draw.text((284, 300), "Case Reference: CASE-2026-CR-0842 — Network Intrusion Investigation", fill=TEXT_DARK, font=get_font(12))
    draw.text((284, 330), "Evidence Title: Gateway Server Access Log", fill=TEXT_DARK, font=get_font(12, bold=True))
    draw.text((284, 360), "Category: System & Audit Log", fill=TEXT_DARK, font=get_font(12))
    draw.text((284, 390), "Collected By: Forensic Examiner • Location: Primary Server Rack 3", fill=TEXT_DARK, font=get_font(12))

    # Section C
    draw.rectangle([264, 445, 1240, 580], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 460), "Section C — Cryptographic Fingerprint", fill=PRIMARY_ACCENT, font=get_font(14, bold=True))
    draw.text((284, 485), "SHA-256 PRIMARY REFERENCE DIGEST:", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.rectangle([284, 505, 1220, 535], fill=SECONDARY_SURFACE, outline=BORDER_COLOR, width=1)
    draw.text((294, 514), "8f2b3a1c904e5d6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a", fill=TEXT_DARK, font=get_mono_font(12))
    draw.text((284, 545), "Entropy: 4.1200 / 8.0000 bits/byte • MD5 & SHA-1 Calculated • Status: Ready to Anchor", fill=TEXT_MUTED, font=get_font(11))

    # Section D
    draw.rectangle([264, 595, 1240, 680], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 610), "Section D — Registration Review", fill=PRIMARY_ACCENT, font=get_font(14, bold=True))
    draw.rectangle([284, 635, 460, 665], fill=PRIMARY_ACCENT)
    draw.text((310, 644), "Register Evidence", fill=(255, 255, 255), font=get_font(12, bold=True))

    img.save(SCREENSHOTS_DIR / "02-register-evidence.png")


def generate_screenshot_03_integrity_lab():
    """Screenshot 3: Integrity Laboratory Comparison."""
    img, draw = create_base_canvas("Integrity Lab", "Integrity Laboratory", "Compare cryptographic fingerprints to identify changes in digital evidence.")

    # Status Alert: Mismatch
    draw.rectangle([264, 140, 1240, 225], fill=(251, 239, 239), outline=DANGER_RED, width=1)
    draw.text((284, 155), "⚠️ INTEGRITY MISMATCH", fill=DANGER_RED, font=get_font(15, bold=True))
    draw.text((284, 180), "The calculated fingerprint differs from the registered reference. The file contents are not identical.", fill=TEXT_DARK, font=get_font(13))
    draw.text((284, 200), "Divergence: 14 of 64 hexadecimal characters differ • Verification permanently recorded to ledger.", fill=TEXT_MUTED, font=get_font(11))

    # Side-by-side hash comparison
    draw.rectangle([264, 240, 740, 420], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 255), "REGISTERED SHA-256 (REFERENCE)", fill=PRIMARY_ACCENT, font=get_font(12, bold=True))
    draw.rectangle([284, 280, 720, 340], fill=SECONDARY_SURFACE, outline=BORDER_COLOR, width=1)
    draw.text((294, 295), "9a4f61e88d401c29e612cb723508b981", fill=SUCCESS_GREEN, font=get_mono_font(11))
    draw.text((294, 315), "27394ba0210e7b8a7f0129bc4123de45", fill=SUCCESS_GREEN, font=get_mono_font(11))
    draw.text((284, 360), "Size: 8,920 Bytes • Ingestion Baseline Sealed", fill=TEXT_MUTED, font=get_font(11))

    draw.rectangle([760, 240, 1240, 420], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((780, 255), "CALCULATED SHA-256 (INSTANCE TESTED)", fill=DANGER_RED, font=get_font(12, bold=True))
    draw.rectangle([780, 280, 1220, 340], fill=(251, 239, 239), outline=DANGER_RED, width=1)
    draw.text((790, 295), "7c1d09ab22ef1489012356bcdef98120", fill=DANGER_RED, font=get_mono_font(11))
    draw.text((790, 315), "348712a091823746bcde091234567890", fill=DANGER_RED, font=get_mono_font(11))
    draw.text((780, 360), "Size: 8,924 Bytes • Source: Tampered File Instance", fill=TEXT_MUTED, font=get_font(11))

    # History Ledger
    draw.rectangle([264, 435, 1240, 740], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 450), "Historical Verification Ledger for EV-2026-0001", fill=TEXT_DARK, font=get_font(14, bold=True))
    draw.line([(284, 475), (1220, 475)], fill=BORDER_COLOR, width=1)

    draw.text((284, 490), "2026-11-19 14:15:00 UTC • Examiner: Forensic Examiner • Mode: Tampered Test", fill=TEXT_DARK, font=get_font(12))
    draw.text((1150, 490), "Mismatch", fill=DANGER_RED, font=get_font(12, bold=True))
    draw.line([(284, 515), (1220, 515)], fill=BORDER_COLOR, width=1)

    draw.text((284, 530), "2026-11-19 04:45:00 UTC • Examiner: Forensic Examiner • Mode: Vault Baseline Check", fill=TEXT_DARK, font=get_font(12))
    draw.text((1150, 530), "Match", fill=SUCCESS_GREEN, font=get_font(12, bold=True))

    img.save(SCREENSHOTS_DIR / "03-integrity-verification-mismatch.png")


def generate_screenshot_04_custody():
    """Screenshot 4: Chain of Custody."""
    img, draw = create_base_canvas("Chain of Custody", "Chain of Custody", "Review the documented possession and transfer history of digital evidence.")

    # Current Custodian Banner
    draw.rectangle([264, 140, 1240, 205], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 155), "CURRENT ACTIVE CUSTODIAN: Forensic Examiner (Lead Examiner)", fill=TEXT_DARK, font=get_font(14, bold=True))
    draw.text((284, 178), "Evidence: EV-2026-0001 — Gateway Server Access Log • Status: Verified", fill=TEXT_MUTED, font=get_font(11))

    # Left: Timeline Ledger
    draw.rectangle([264, 220, 800, 740], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((284, 235), "Chronological Custody Ledger", fill=TEXT_DARK, font=get_font(14, bold=True))
    draw.line([(284, 260), (780, 260)], fill=BORDER_COLOR, width=1)

    draw.text((284, 275), "Event #0: Initial Seizure & Registration", fill=PRIMARY_ACCENT, font=get_font(12, bold=True))
    draw.text((284, 295), "Collected by Forensic Examiner at Server Rack 3 • Baseline Sealed", fill=TEXT_MUTED, font=get_font(11))
    draw.line([(284, 320), (780, 320)], fill=BORDER_COLOR, width=1)

    draw.text((284, 335), "Event #1: Transfer to Evidence Custodian", fill=TEXT_DARK, font=get_font(12, bold=True))
    draw.text((284, 355), "Reason: Secure Long-Term Vault Storage • Token: c9f1a238b012... • Verified", fill=TEXT_MUTED, font=get_font(11))

    # Right: Transfer Form
    draw.rectangle([820, 220, 1240, 740], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((840, 235), "Record Custody Transfer", fill=TEXT_DARK, font=get_font(14, bold=True))
    draw.line([(840, 260), (1220, 260)], fill=BORDER_COLOR, width=1)

    draw.text((840, 280), "Releasing Custodian: Forensic Examiner", fill=TEXT_DARK, font=get_font(11))
    draw.text((840, 315), "Receiving Custodian: Evidence Custodian", fill=TEXT_DARK, font=get_font(11))
    draw.text((840, 350), "Transfer Reason: Forensic Lab Analysis", fill=TEXT_DARK, font=get_font(11))
    draw.text((840, 385), "[X] Verify SHA-256 integrity on release", fill=PRIMARY_ACCENT, font=get_font(11))
    draw.text((840, 415), "[X] I authorize and certify this legal custody transfer", fill=PRIMARY_ACCENT, font=get_font(11, bold=True))
    draw.rectangle([840, 450, 1050, 485], fill=PRIMARY_ACCENT)
    draw.text((865, 460), "Authorize Transfer", fill=(255, 255, 255), font=get_font(11, bold=True))

    img.save(SCREENSHOTS_DIR / "04-chain-of-custody-timeline.png")


def main():
    print("[INFO] Generating high-resolution UI screenshots...")
    generate_screenshot_01_overview()
    generate_screenshot_02_intake()
    generate_screenshot_03_integrity_lab()
    generate_screenshot_04_custody()
    print(f"[SUCCESS] All screenshots saved in: {SCREENSHOTS_DIR.resolve()}")


if __name__ == "__main__":
    main()
