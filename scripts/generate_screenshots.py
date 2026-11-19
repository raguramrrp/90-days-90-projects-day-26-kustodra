"""
KUSTODRA - High-Resolution Screenshot Generator
Generates clean, professional UI screenshots directly reflecting
the KUSTODRA Enterprise Asset Vault design system with left vertical rail.
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
    """Load clean modern typography (Plus Jakarta Sans / Segoe UI / Arial)."""
    candidates = [
        "PlusJakartaSans-Bold.ttf" if bold else "PlusJakartaSans-Regular.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "arialbd.ttf" if bold else "arial.ttf"
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    return ImageFont.load_default()


def get_mono_font(size: int = 12):
    """Load crisp monospace font (JetBrains Mono / Consolas)."""
    candidates = [
        "JetBrainsMono-Regular.ttf",
        "consola.ttf",
        "cour.ttf"
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    return ImageFont.load_default()


def create_base_canvas(active_icon: str = "📁", title: str = "Artifact Vault") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Create the KUSTODRA enterprise workstation window frame with left vertical rail and clean header."""
    img = Image.new("RGB", (1280, 800), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 1. Left Vertical Navigation Rail (Width: 68px)
    draw.rectangle([0, 0, 68, 800], fill=RAIL_BG)
    draw.line([(68, 0), (68, 800)], fill=(32, 38, 36), width=1)

    # Rail Delta Logo Mark at top
    draw.rectangle([12, 12, 56, 56], fill=(26, 34, 32), outline=(40, 53, 50), width=1)
    draw.text((26, 20), "▲", fill=SUCCESS_GREEN, font=get_font(18, bold=True))

    # Icon buttons
    icons = ["📁", "📥", "📊", "🔬", "⛓️", "📄", "⚙️"]
    y_pos = 78
    for ic in icons:
        is_active = (ic == active_icon)
        if is_active:
            draw.rectangle([12, y_pos, 56, y_pos + 44], fill=ACTIVE_ACCENT, outline=(54, 92, 80), width=1)
            draw.text((24, y_pos + 12), ic, fill=ACTIVE_GREEN, font=get_font(16))
        else:
            draw.text((24, y_pos + 12), ic, fill=(140, 150, 147), font=get_font(16))
        y_pos += 48

    # Bottom utility icons
    draw.text((24, 715), "❓", fill=(140, 150, 147), font=get_font(16))
    draw.text((24, 755), "👤", fill=(140, 150, 147), font=get_font(16))

    # 2. Main Horizontal Header (Top, x=88 to 1260)
    draw.text((88, 16), title, fill=TEXT_DARK, font=get_font(22, bold=True))

    # + Ingest Artifact Button on right
    draw.rectangle([1140, 14, 1260, 44], fill=PRIMARY_ACCENT)
    draw.text((1152, 22), "+ Ingest artifact", fill=(255, 255, 255), font=get_font(11, bold=True))

    return img, draw


def generate_screenshot_01_repository():
    """Screenshot 1: Primary Artifact Vault Screen."""
    img, draw = create_base_canvas("📁", "Artifact Vault")

    # 1. Wide Prominent Search Bar
    draw.rectangle([88, 62, 1150, 98], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((104, 72), "🔍  Search by artifact title, ID, hash, case reference, or custodian...", fill=TEXT_MUTED, font=get_font(12))

    draw.rectangle([1165, 62, 1260, 98], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((1180, 72), "Saved ▾", fill=TEXT_DARK, font=get_font(12))

    # 2. Compact Filter Toolbar
    draw.rectangle([88, 108, 1260, 150], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.rectangle([98, 116, 175, 142], fill=SECONDARY_SURFACE, outline=BORDER_COLOR, width=1)
    draw.text((106, 122), "⚙ Filters", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.rectangle([155, 120, 169, 138], fill=PRIMARY_ACCENT)
    draw.text((159, 122), "3", fill=(255, 255, 255), font=get_font(10, bold=True))

    draw.rectangle([185, 116, 285, 142], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((195, 122), "ID / ART-...", fill=TEXT_MUTED, font=get_font(11))

    draw.rectangle([295, 116, 450, 142], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((305, 122), "Custodian: All ▾", fill=TEXT_DARK, font=get_font(11))

    draw.rectangle([460, 116, 610, 142], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((470, 122), "Category: All ▾", fill=TEXT_DARK, font=get_font(11))

    draw.rectangle([620, 116, 755, 142], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((630, 122), "Status: Verified ▾", fill=TEXT_DARK, font=get_font(11))

    draw.rectangle([1120, 116, 1180, 142], fill=ACTIVE_ACCENT, outline=PRIMARY_ACCENT, width=1)
    draw.text((1130, 122), "▦ Table", fill=(255, 255, 255), font=get_font(11, bold=True))

    draw.rectangle([1190, 116, 1250, 142], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((1205, 122), "⊞ Grid", fill=TEXT_DARK, font=get_font(11))

    draw.text((88, 160), "5 artifacts cataloged • Sorted by Newest First", fill=TEXT_MUTED, font=get_font(11))

    # 3. Dense Enterprise Evidence Table
    draw.rectangle([88, 180, 1260, 780], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)

    draw.rectangle([88, 180, 1260, 218], fill=SECONDARY_SURFACE)
    draw.line([(88, 218), (1260, 218)], fill=BORDER_COLOR, width=1)

    draw.text((100, 192), "☐", fill=TEXT_MUTED, font=get_font(13))
    draw.text((128, 192), "ARTIFACT ID", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.text((230, 192), "PREVIEW", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.text((310, 192), "ARTIFACT TITLE", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.text((580, 192), "CUSTODIAN", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.text((760, 192), "INGESTED AT", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.text((880, 192), "SIZE", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.text((960, 192), "FORMAT", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.text((1120, 192), "INTEGRITY STATE", fill=TEXT_DARK, font=get_font(11, bold=True))

    rows = [
        ("ART-2026-0001", "LOG", "Gateway Server Access Log", "Forensic Examiner", "2026-11-19 14:31", "8.9 KB", "LOG", "✓ Verified", SUCCESS_GREEN, (230, 245, 235)),
        ("ART-2026-0002", "IMG", "Perimeter Cam 04 Still Frame", "Vault Custodian", "2026-11-19 14:31", "3.2 MB", "IMAGE", "✓ Verified", SUCCESS_GREEN, (230, 245, 235)),
        ("ART-2026-0003", "CSV", "Financial Transaction Audit Ledger", "Forensic Examiner", "2026-11-19 14:31", "14.2 KB", "DOCUMENT", "✓ Verified", SUCCESS_GREEN, (230, 245, 235)),
        ("ART-2026-0004", "TXT", "Technical Specification Notes", "Lead Investigator", "2026-11-19 14:31", "4.8 KB", "DOCUMENT", "✓ Verified", SUCCESS_GREEN, (230, 245, 235)),
        ("ART-2026-0005", "BIN", "Suspicious Encrypted Binary Payload", "Vault Custodian", "2026-11-19 14:31", "64.0 KB", "BINARY", "○ Not Verified", WARNING_AMBER, (253, 248, 235))
    ]

    r_y = 225
    for eid, tag_badge, title, owner, rec_on, size, cat, status, stat_col, stat_bg in rows:
        if eid == "ART-2026-0001":
            draw.rectangle([89, r_y - 4, 1259, r_y + 44], fill=(240, 245, 242))

        draw.text((100, r_y + 10), "☑" if eid == "ART-2026-0001" else "☐", fill=PRIMARY_ACCENT if eid == "ART-2026-0001" else TEXT_MUTED, font=get_font(13))
        draw.text((128, r_y + 10), eid, fill=PRIMARY_ACCENT, font=get_mono_font(12))

        # Rich visual thumbnail preview
        px_box = [228, r_y + 2, 266, r_y + 40]
        if tag_badge == "LOG":
            draw.rectangle(px_box, fill=(15, 23, 42), outline=(51, 65, 85))
            draw.rectangle([228, r_y + 2, 266, r_y + 10], fill=(30, 41, 59))
            draw.ellipse([231, r_y + 4, 234, r_y + 7], fill=(239, 68, 68))
            draw.ellipse([236, r_y + 4, 239, r_y + 7], fill=(234, 179, 8))
            draw.ellipse([241, r_y + 4, 244, r_y + 7], fill=(34, 197, 94))
            draw.rectangle([232, r_y + 14, 248, r_y + 16], fill=(56, 189, 248))
            draw.rectangle([250, r_y + 14, 262, r_y + 16], fill=(74, 222, 128))
            draw.rectangle([232, r_y + 20, 244, r_y + 22], fill=(148, 163, 184))
            draw.rectangle([246, r_y + 20, 260, r_y + 22], fill=(251, 146, 60))
            draw.rectangle([232, r_y + 26, 255, r_y + 28], fill=(56, 189, 248))
            draw.rectangle([232, r_y + 32, 236, r_y + 36], fill=(34, 197, 94))
        elif tag_badge == "IMG":
            draw.rectangle(px_box, fill=(20, 35, 30), outline=(34, 197, 94))
            for ly in range(r_y + 6, r_y + 36, 4):
                draw.line([(229, ly), (265, ly)], fill=(34, 197, 94, 60))
            draw.line([(233, r_y + 10), (237, r_y + 10)], fill=(34, 197, 94))
            draw.line([(233, r_y + 10), (233, r_y + 14)], fill=(34, 197, 94))
            draw.line([(261, r_y + 10), (257, r_y + 10)], fill=(34, 197, 94))
            draw.line([(261, r_y + 10), (261, r_y + 14)], fill=(34, 197, 94))
            draw.ellipse([231, r_y + 4, 234, r_y + 7], fill=(239, 68, 68))
            draw.rectangle([229, r_y + 32, 265, r_y + 39], fill=(0, 0, 0))
            draw.text((230, r_y + 30), "CAM-4", fill=(34, 197, 94), font=get_font(8, bold=True))
        elif tag_badge == "CSV":
            draw.rectangle(px_box, fill=(255, 255, 255), outline=(187, 247, 208))
            draw.rectangle([228, r_y + 2, 266, r_y + 11], fill=(22, 101, 52))
            draw.text((231, r_y + 2), "CSV", fill=(255, 255, 255), font=get_font(7, bold=True))
            for ry_off in [15, 22, 29, 36]:
                draw.line([(228, r_y + ry_off), (266, r_y + ry_off)], fill=(226, 232, 240))
                draw.rectangle([231, r_y + ry_off - 4, 242, r_y + ry_off - 2], fill=(100, 116, 139))
                draw.rectangle([245, r_y + ry_off - 4, 262, r_y + ry_off - 2], fill=(22, 101, 52))
            draw.line([(243, r_y + 11), (243, r_y + 40)], fill=(226, 232, 240))
        elif tag_badge == "TXT":
            draw.rectangle([232, r_y + 4, 266, r_y + 40], fill=(203, 213, 225))
            draw.polygon([(230, r_y + 2), (258, r_y + 2), (264, r_y + 8), (264, r_y + 39), (230, r_y + 39)], fill=(255, 255, 255))
            draw.polygon([(258, r_y + 2), (264, r_y + 8), (258, r_y + 8)], fill=(226, 232, 240))
            draw.rectangle([234, r_y + 6, 255, r_y + 9], fill=(30, 41, 59))
            for ly in [13, 18, 23, 28, 33]:
                draw.rectangle([234, r_y + ly, 260, r_y + ly + 2], fill=(148, 163, 184))
            draw.ellipse([254, r_y + 28, 262, r_y + 36], fill=(220, 38, 38))
        else:  # BIN
            draw.rectangle(px_box, fill=(15, 23, 42), outline=(51, 65, 85))
            draw.rectangle([228, r_y + 2, 266, r_y + 11], fill=(30, 41, 59))
            draw.text((231, r_y + 2), "0xBIN", fill=(251, 191, 36), font=get_font(7, bold=True))
            hex_samples = [("7F 45", (56, 189, 248)), ("2A F1", (244, 114, 182)), ("8B E5", (74, 222, 128)), ("FF 09", (251, 191, 36))]
            hy = r_y + 13
            for hcode, hcol in hex_samples:
                draw.text((231, hy), hcode, fill=hcol, font=get_font(7))
                hy += 6
            draw.rectangle([252, r_y + 26, 264, r_y + 38], fill=(245, 158, 11))

        draw.text((310, r_y + 10), title, fill=TEXT_DARK, font=get_font(12, bold=True))
        draw.text((580, r_y + 10), owner, fill=TEXT_DARK, font=get_font(12))
        draw.text((760, r_y + 10), rec_on, fill=TEXT_MUTED, font=get_font(11))
        draw.text((880, r_y + 10), size, fill=TEXT_DARK, font=get_font(11))

        draw.rectangle([960, r_y + 6, 1030, r_y + 30], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
        draw.text((970, r_y + 10), cat, fill=TEXT_DARK, font=get_font(10, bold=True))

        draw.rectangle([1120, r_y + 6, 1220, r_y + 30], fill=stat_bg, outline=stat_col)
        draw.text((1130, r_y + 10), status, fill=stat_col, font=get_font(11, bold=True))

        draw.line([(88, r_y + 44), (1260, r_y + 44)], fill=BORDER_COLOR, width=1)
        r_y += 48

    out_file = SCREENSHOTS_DIR / "01-evidence-repository.png"
    img.save(out_file)
    print(f"[OK] Saved {out_file.name}")


def generate_screenshot_02_details():
    """Screenshot 2: Artifact Inspector & Metadata."""
    img, draw = create_base_canvas("📁", "Artifact Inspector")

    # Header strip
    draw.rectangle([88, 60, 1260, 110], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((104, 70), "Gateway Server Access Log", fill=TEXT_DARK, font=get_font(16, bold=True))
    draw.text((104, 90), "ART-2026-0001 • CASE-2026-ALPHA • text/plain • Ingested: 2026-11-19", fill=TEXT_MUTED, font=get_font(11))

    draw.rectangle([1110, 68, 1245, 102], fill=(230, 245, 235), outline=SUCCESS_GREEN)
    draw.text((1125, 76), "✓ VERIFIED INTACT", fill=SUCCESS_GREEN, font=get_font(11, bold=True))

    # Tabs
    draw.rectangle([88, 120, 1260, 156], fill=SECONDARY_SURFACE, outline=BORDER_COLOR, width=1)
    tabs = ["Overview", "Metadata", "Integrity", "Custody History", "Audit History"]
    t_x = 98
    for t in tabs:
        if t == "Metadata":
            draw.rectangle([t_x, 122, t_x + 90, 154], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
            draw.text((t_x + 16, 130), t, fill=PRIMARY_ACCENT, font=get_font(11, bold=True))
        else:
            draw.text((t_x + 16, 130), t, fill=TEXT_MUTED, font=get_font(11))
        t_x += 105

    # Metadata cards
    draw.rectangle([88, 170, 660, 780], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((108, 186), "File System & Magic Bytes", fill=TEXT_DARK, font=get_font(14, bold=True))
    draw.text((108, 220), "Original Filename:  server_access_log.log", fill=TEXT_DARK, font=get_font(12))
    draw.text((108, 250), "File Size:          8,912 Bytes (8.7 KB)", fill=TEXT_DARK, font=get_font(12))
    draw.text((108, 280), "Detected MIME:      text/plain", fill=TEXT_DARK, font=get_font(12))
    draw.text((108, 310), "Magic Signature:    ASCII plain text log file", fill=TEXT_DARK, font=get_font(12))
    draw.text((108, 340), "Extension Check:    CONFIRMED MATCH (No spoofing)", fill=SUCCESS_GREEN, font=get_font(12, bold=True))
    draw.text((108, 370), "Shannon Entropy:    3.8410 / 8.0000 (Low / Natural Language)", fill=TEXT_DARK, font=get_font(12))

    draw.rectangle([680, 170, 1260, 780], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((700, 186), "Cryptographic Baseline Fingerprints", fill=TEXT_DARK, font=get_font(14, bold=True))
    draw.text((700, 220), "SHA-256 (Baseline):", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.rectangle([700, 240, 1240, 275], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
    draw.text((710, 248), "06ff016b5eacdcc135104acf3fe0cd1299d5e9ac9466b6449ba2a57b4a481597", fill=TEXT_DARK, font=get_mono_font(11))

    draw.text((700, 290), "MD5 Digest:", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.rectangle([700, 310, 1240, 345], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
    draw.text((710, 318), "f89b12a3cd01e4a9082f6e521034ba91", fill=TEXT_DARK, font=get_mono_font(11))

    draw.text((700, 360), "SHA-1 Digest:", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.rectangle([700, 380, 1240, 415], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
    draw.text((710, 388), "2a7b8890cf25e11409ab44d0382e66f912ca8701", fill=TEXT_DARK, font=get_mono_font(11))

    out_file = SCREENSHOTS_DIR / "02-evidence-details.png"
    img.save(out_file)
    print(f"[OK] Saved {out_file.name}")


def generate_screenshot_03_verify():
    """Screenshot 3: Integrity Verification Lab."""
    img, draw = create_base_canvas("🔬", "Integrity Lab")

    draw.rectangle([88, 60, 1260, 780], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((108, 76), "Cryptographic Verification & Bitstream Comparison", fill=TEXT_DARK, font=get_font(16, bold=True))

    # Segmented buttons
    draw.rectangle([108, 110, 570, 146], fill=(235, 240, 237), outline=BORDER_COLOR)
    draw.rectangle([110, 112, 240, 144], fill=PRIMARY_ACCENT)
    draw.text((125, 120), "Vault Stored Copy", fill=(255, 255, 255), font=get_font(11, bold=True))
    draw.text((255, 120), "Upload External Copy", fill=TEXT_DARK, font=get_font(11))
    draw.text((415, 120), "Validation Benchmark Suite", fill=TEXT_DARK, font=get_font(11))

    # Side-by-side comparison
    draw.rectangle([108, 170, 670, 320], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
    draw.text((124, 186), "REGISTERED SHA-256 FINGERPRINT (REFERENCE)", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.text((124, 215), "06ff016b5eacdcc135104acf3fe0cd1299d5e9ac9466b6449ba2a57b4a481597", fill=TEXT_DARK, font=get_mono_font(11))
    draw.text((124, 255), "Baseline Size: 8,912 Bytes • Intake Date: 2026-11-19 14:31:46 UTC", fill=TEXT_MUTED, font=get_font(11))

    draw.rectangle([690, 170, 1240, 320], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
    draw.text((706, 186), "CALCULATED SHA-256 FINGERPRINT (ACTIVE COPY)", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.text((706, 215), "06ff016b5eacdcc135104acf3fe0cd1299d5e9ac9466b6449ba2a57b4a481597", fill=TEXT_DARK, font=get_mono_font(11))
    draw.text((706, 255), "Instance Size: 8,912 Bytes • Source: Vault Archive (server_access_log.log)", fill=TEXT_MUTED, font=get_font(11))

    # Match banner
    draw.rectangle([108, 340, 1240, 410], fill=(235, 248, 240), outline=SUCCESS_GREEN, width=1)
    draw.text((124, 355), "✓  INTEGRITY MATCH CONFIRMED", fill=SUCCESS_GREEN, font=get_font(14, bold=True))
    draw.text((124, 380), "The calculated SHA-256 bitstream fingerprint matches the registered immutable reference. Zero tampering or bit-rot detected.", fill=TEXT_DARK, font=get_font(12))

    out_file = SCREENSHOTS_DIR / "03-integrity-lab.png"
    img.save(out_file)
    print(f"[OK] Saved {out_file.name}")


def generate_screenshot_04_custody():
    """Screenshot 4: Chain of Custody Timeline."""
    img, draw = create_base_canvas("⛓️", "Chain of Custody")

    draw.rectangle([88, 60, 1260, 780], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((108, 76), "Chronological Custody Ledger & Handover Receipts", fill=TEXT_DARK, font=get_font(16, bold=True))

    events = [
        ("Event #0: Initial Seizure & Registration", "2026-11-19 14:31 UTC", "Collected by Lead Investigator at Primary Datacenter Rack 3. Ingested into vault archive."),
        ("Event #1: Forensic Examiner → Lead Analyst", "2026-11-19 15:45 UTC", "Reason: Forensic Lab Analysis • Receipt Token: a4f910e28b... • Verified: YES"),
        ("Event #2: Lead Analyst → Secure Vault Custodian", "2026-11-19 18:20 UTC", "Reason: Secure Long-Term Vault Storage • Receipt Token: bc7712df90... • Verified: YES")
    ]

    c_y = 120
    for title, ts, details in events:
        draw.rectangle([108, c_y, 1240, c_y + 80], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
        draw.text((124, c_y + 12), title, fill=TEXT_DARK, font=get_font(12, bold=True))
        draw.text((1060, c_y + 12), ts, fill=TEXT_MUTED, font=get_font(11))
        draw.text((124, c_y + 40), details, fill=TEXT_DARK, font=get_font(11))
        c_y += 95

    out_file = SCREENSHOTS_DIR / "04-chain-of-custody.png"
    img.save(out_file)
    print(f"[OK] Saved {out_file.name}")


def generate_screenshot_05_intake():
    """Screenshot 5: Ingestion & Forensic Intake Workspace."""
    img, draw = create_base_canvas("📥", "Intake & Ingestion")

    # Outer panel
    draw.rectangle([88, 60, 1260, 780], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((108, 76), "Register New Digital Specimen & Compute Baselines", fill=TEXT_DARK, font=get_font(16, bold=True))
    draw.text((108, 98), "Files are hashed in streaming chunks the moment they are uploaded to ensure bitstream immutability.", fill=TEXT_MUTED, font=get_font(11))

    # Form layout (2 columns)
    # Left column: Dropzone & File details
    draw.rectangle([108, 130, 660, 360], fill=(250, 252, 251), outline=(197, 204, 200), width=1)
    draw.text((310, 200), "📁", font=get_font(28))
    draw.text((220, 240), "Drag and drop specimen file here or Browse", fill=TEXT_DARK, font=get_font(12, bold=True))
    draw.text((235, 265), "Selected: suspect_encrypted_payload.bin (8,192 Bytes)", fill=PRIMARY_ACCENT, font=get_font(11))

    # Form fields
    draw.text((108, 385), "Artifact Title *", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.rectangle([108, 405, 660, 440], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((118, 415), "Suspicious Encrypted Binary Payload", fill=TEXT_DARK, font=get_font(11))

    draw.text((108, 455), "Evidence Category *", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.rectangle([108, 475, 660, 510], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((118, 485), "Encrypted / Packed Payload ▾", fill=TEXT_DARK, font=get_font(11))

    draw.text((108, 525), "Case Reference Number *", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.rectangle([108, 545, 660, 580], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((118, 555), "CASE-2026-ALPHA-09", fill=TEXT_DARK, font=get_font(11))

    draw.text((108, 595), "Initial Custodian & Incident Notes", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.rectangle([108, 615, 660, 690], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((118, 625), "Recovered from encrypted USB volume during incident response triage.", fill=TEXT_DARK, font=get_font(11))

    draw.rectangle([108, 715, 660, 755], fill=PRIMARY_ACCENT)
    draw.text((310, 727), "+ Ingest & Seal Specimen", fill=(255, 255, 255), font=get_font(12, bold=True))

    # Right column: Live Forensic Analysis & Baseline Calculation
    draw.rectangle([680, 130, 1240, 755], fill=SECONDARY_SURFACE, outline=BORDER_COLOR, width=1)
    draw.text((700, 146), "Real-Time Cryptographic Seal & Forensic Triage", fill=TEXT_DARK, font=get_font(14, bold=True))

    draw.text((700, 185), "SHA-256 Bitstream Fingerprint:", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.rectangle([700, 205, 1220, 240], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((710, 215), "8355c88711331b0d4750d2f9495b1d69f2e3c093e039583c3105ae7876a77680", fill=TEXT_DARK, font=get_mono_font(10))

    draw.text((700, 255), "MD5 & SHA-1 Baseline Digests:", fill=TEXT_MUTED, font=get_font(11, bold=True))
    draw.rectangle([700, 275, 1220, 310], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((710, 285), "MD5: e10adc3949ba59abbe56e057f20f883e • SHA-1: 7c4a8d09ca3762af61e59520943dc2", fill=TEXT_DARK, font=get_mono_font(10))

    # Magic byte inspection card
    draw.rectangle([700, 330, 1220, 420], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((715, 345), "Raw Magic Signature Inspection", fill=TEXT_DARK, font=get_font(12, bold=True))
    draw.text((715, 370), "Header Bytes:  39 0C 8C 7D 72 47 34 2C (High-Entropy Binary Header)", fill=TEXT_DARK, font=get_mono_font(10))
    draw.text((715, 395), "MIME Check:    application/octet-stream (No spoofing detected)", fill=SUCCESS_GREEN, font=get_font(11, bold=True))

    # Shannon Entropy gauge
    draw.rectangle([700, 440, 1220, 560], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((715, 455), "Shannon Entropy Analysis (Randomness / Packing)", fill=TEXT_DARK, font=get_font(12, bold=True))
    draw.text((715, 480), "Calculated Entropy:  7.9892 / 8.0000", fill=TEXT_DARK, font=get_font(13, bold=True))
    draw.rectangle([715, 505, 1205, 520], fill=(225, 228, 227))
    draw.rectangle([715, 505, 1180, 520], fill=DANGER_RED) # High entropy bar
    draw.text((715, 532), "HIGH ENTROPY: Cryptographically Encrypted or Strongly Compressed Payload", fill=DANGER_RED, font=get_font(11, bold=True))

    # Risk summary
    draw.rectangle([700, 580, 1220, 735], fill=(254, 242, 242), outline=(252, 165, 165))
    draw.text((715, 595), "Forensic Risk Evaluation: ELEVATED RISK (25/100)", fill=DANGER_RED, font=get_font(12, bold=True))
    draw.text((715, 625), "• Specimen contains near-maximal Shannon Entropy (7.9892)", fill=TEXT_DARK, font=get_font(11))
    draw.text((715, 650), "• High probability of packed executable, encrypted ransomware, or encrypted vault", fill=TEXT_DARK, font=get_font(11))
    draw.text((715, 675), "• Recommendation: Maintain in isolated air-gapped quarantine vault for static analysis", fill=TEXT_DARK, font=get_font(11))

    out_file = SCREENSHOTS_DIR / "02-intake-ingestion.png"
    img.save(out_file)
    print(f"[OK] Saved {out_file.name}")


def generate_screenshot_06_reports():
    """Screenshot 6: Audit & Compliance PDF Certificates."""
    img, draw = create_base_canvas("📄", "Audit & Compliance")

    draw.rectangle([88, 60, 1260, 780], fill=SURFACE_COLOR, outline=BORDER_COLOR, width=1)
    draw.text((108, 76), "Court-Ready Forensic Certificates & Case Manifests", fill=TEXT_DARK, font=get_font(16, bold=True))
    draw.text((108, 98), "Generate formally admissible affidavits documenting bitstream fingerprints, chain of custody, and integrity tests.", fill=TEXT_MUTED, font=get_font(11))

    # Form card
    draw.rectangle([108, 130, 1240, 310], fill=SECONDARY_SURFACE, outline=BORDER_COLOR)
    draw.text((128, 148), "Artifact Integrity Certificate Generator", fill=TEXT_DARK, font=get_font(14, bold=True))

    draw.text((128, 185), "Target Artifact Record *", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.rectangle([128, 205, 660, 240], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((140, 215), "ART-2026-0005 — Suspicious Encrypted Binary Payload", fill=TEXT_DARK, font=get_font(11))

    draw.text((680, 185), "Issuing Agency / Forensic Laboratory", fill=TEXT_DARK, font=get_font(11, bold=True))
    draw.rectangle([680, 205, 1220, 240], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((692, 215), "KUSTODRA Digital Asset Management & Forensic Laboratory", fill=TEXT_DARK, font=get_font(11))

    draw.rectangle([128, 255, 660, 292], fill=PRIMARY_ACCENT)
    draw.text((310, 267), "Compile Court-Ready PDF Certificate", fill=(255, 255, 255), font=get_font(11, bold=True))

    draw.rectangle([680, 255, 1220, 292], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.text((870, 267), "Generate Markdown Dossier", fill=TEXT_DARK, font=get_font(11, bold=True))

    # Certificate preview card
    draw.rectangle([108, 335, 1240, 755], fill=SURFACE_COLOR, outline=BORDER_COLOR)
    draw.rectangle([108, 335, 1240, 375], fill=(240, 245, 243))
    draw.text((128, 348), "CERTIFICATE PREVIEW: KUSTODRA-CERT-ART-2026-0005.PDF", fill=PRIMARY_ACCENT, font=get_font(11, bold=True))

    draw.rectangle([340, 395, 1000, 735], fill=(255, 255, 255), outline=BORDER_COLOR, width=2)
    # Mini PDF sheet
    draw.text((380, 420), "OFFICIAL FORENSIC EVIDENCE CERTIFICATE", fill=(30, 41, 59), font=get_font(15, bold=True))
    draw.line([(380, 445), (960, 445)], fill=PRIMARY_ACCENT, width=2)
    draw.text((380, 460), "ISSUING AUTHORITY: Digital Forensics Incident Response Unit", fill=TEXT_MUTED, font=get_font(10))
    draw.text((380, 480), "CERTIFICATE UUID: 9b104a3e-7c18-42f1-bb03-0182746c109e", fill=TEXT_MUTED, font=get_font(10))
    draw.text((380, 510), "SPECIMEN TITLE: Suspicious Encrypted Binary Payload", fill=TEXT_DARK, font=get_font(12, bold=True))
    draw.text((380, 535), "SHA-256 DIGEST: 8355c88711331b0d4750d2f9495b1d69f2e3c093e039583c3105ae7876a77680", fill=TEXT_DARK, font=get_mono_font(9))
    draw.text((380, 560), "INTEGRITY STATUS: VERIFIED UNMODIFIED & COURT-ADMISSIBLE", fill=SUCCESS_GREEN, font=get_font(11, bold=True))
    draw.text((380, 590), "CUSTODY CHAIN RECORD: 3 Transfers Verified • HMAC Tokens Validated", fill=TEXT_DARK, font=get_font(10))
    draw.text((380, 615), "AFFIDAVIT: Bitstream calculated via constant-time verification algorithm adhering to ISO/IEC 27037.", fill=TEXT_MUTED, font=get_font(10))
    # Seal at bottom
    draw.ellipse([870, 640, 940, 710], fill=(240, 253, 244), outline=SUCCESS_GREEN, width=2)
    draw.text((885, 665), "SEALED", fill=SUCCESS_GREEN, font=get_font(10, bold=True))

    out_file = SCREENSHOTS_DIR / "06-audit-compliance-reports.png"
    img.save(out_file)
    print(f"[OK] Saved {out_file.name}")


def generate_screenshot_07_process_flow():
    """Screenshot 7: End-to-End Forensic Process Flow & Architectural Lifecycle."""
    img = Image.new("RGB", (1280, 800), color=(17, 21, 20)) # Dark sleek forensic command theme
    draw = ImageDraw.Draw(img)

    # Top Header Banner
    draw.rectangle([0, 0, 1280, 90], fill=(22, 28, 26))
    draw.line([(0, 90), (1280, 90)], fill=(40, 53, 50), width=1)

    draw.rectangle([36, 22, 76, 62], fill=(26, 34, 32), outline=(50, 129, 90), width=1)
    draw.text((49, 30), "▲", fill=(94, 212, 159), font=get_font(20, bold=True))

    draw.text((92, 24), "KUSTODRA — Digital Asset Custody & Forensic Process Flow", fill=(255, 255, 255), font=get_font(18, bold=True))
    draw.text((92, 52), "End-to-End Cryptographic Chain-of-Custody Lifecycle, Verification Architecture & Court Admissibility", fill=(148, 163, 184), font=get_font(11))

    # 6 Process Stage Boxes (Arranged in a clear 2x3 workflow grid)
    stages = [
        ("01", "DIGITAL ACQUISITION & INTAKE", "📥", [
            "• Raw specimen acquired from incident or field seizure",
            "• Automated file lock (No write operations allowed)",
            "• Streaming bitstream ingest into isolated quarantine",
            "• Capture provenance metadata (collector, timestamp, location)"
        ], (49, 95, 80)),
        ("02", "CRYPTOGRAPHIC FINGERPRINTING", "🔒", [
            "• Streaming calculation of SHA-256, SHA-1, and MD5",
            "• Raw Magic Byte inspection to catch extension spoofing",
            "• Shannon Entropy analysis to detect packed/encrypted payloads",
            "• Duplicate fingerprint detection against database"
        ], (38, 61, 54)),
        ("03", "IMMUTABLE VAULT ARCHIVAL", "🗄️", [
            "• Specimen saved to tamper-evident vault storage",
            "• Cataloged in SQLite WAL database with ACID guarantees",
            "• Cryptographic audit block-hash linking state sequentially",
            "• Initial custody ownership established and locked"
        ], (30, 41, 59)),
        ("04", "CUSTODIAL HANDOVER & HMAC TOKENS", "⛓️", [
            "• Examiner-to-Examiner or Examiner-to-Vault transfer",
            "• Mandatory operational justification logged",
            "• Each handover signed with a verifiable HMAC-SHA256 token",
            "• Chronological timeline creates unbroken legal chain of custody"
        ], (51, 65, 85)),
        ("05", "CRYPTOGRAPHIC INTEGRITY LAB", "🔬", [
            "• Constant-time verification prevents side-channel timing attacks",
            "• Compares active/suspect instance against registered baseline",
            "• Single-bit divergence detection (identifies bit-rot or tampering)",
            "• Verified status recorded in immutable historical ledger"
        ], (22, 101, 52)),
        ("06", "COURT-ADMISSIBLE AFFIDAVITS", "📄", [
            "• Automated ReportLab compilation of formal PDF certificates",
            "• Detailed case dossiers with complete custody receipts",
            "• Adheres to NIST SP 800-86 and ISO/IEC 27037 standards",
            "• Tamper-proof evidence ready for trial submission"
        ], (50, 129, 90))
    ]

    # Grid positions: 3 columns x 2 rows
    box_w = 370
    box_h = 280
    xs = [40, 455, 870]
    ys = [120, 450]

    for idx, (num, title, icon, bullets, accent) in enumerate(stages):
        col = idx % 3
        row = idx // 3
        bx = xs[col]
        by = ys[row]

        # Outer card
        draw.rectangle([bx, by, bx + box_w, by + box_h], fill=(22, 28, 26), outline=(40, 53, 50), width=1)

        # Stage number pill & title bar
        draw.rectangle([bx, by, bx + box_w, by + 46], fill=(26, 34, 32))
        draw.line([(bx, by + 46), (bx + box_w, by + 46)], fill=(40, 53, 50), width=1)

        draw.rectangle([bx + 12, by + 10, bx + 42, by + 36], fill=accent, outline=(94, 212, 159), width=1)
        draw.text((bx + 18, by + 16), num, fill=(255, 255, 255), font=get_font(10, bold=True))

        draw.text((bx + 52, by + 14), title, fill=(255, 255, 255), font=get_font(11, bold=True))
        draw.text((bx + box_w - 36, by + 12), icon, font=get_font(14))

        # Bullets
        ly = by + 65
        for b in bullets:
            draw.text((bx + 16, ly), b, fill=(203, 213, 225), font=get_font(11))
            ly += 45

        # Horizontal connecting arrows
        if col < 2:
            arr_x = bx + box_w + 5
            arr_y = by + 140
            draw.line([(arr_x, arr_y), (arr_x + 35, arr_y)], fill=(94, 212, 159), width=2)
            draw.polygon([(arr_x + 35, arr_y), (arr_x + 27, arr_y - 5), (arr_x + 27, arr_y + 5)], fill=(94, 212, 159))

    # Vertical loopback arrow from Stage 3 down to Stage 4
    draw.line([(1055, 400), (1055, 440)], fill=(94, 212, 159), width=2)
    draw.polygon([(1055, 440), (1050, 432), (1060, 432)], fill=(94, 212, 159))

    # Bottom Architecture Summary Bar
    draw.rectangle([40, 745, 1240, 785], fill=(22, 28, 26), outline=(40, 53, 50))
    draw.text((55, 757), "FORENSIC SECURITY PRINCIPLES:", fill=(94, 212, 159), font=get_font(10, bold=True))
    draw.text((260, 757), "Constant-Time Verification • Avalanche Effect • HMAC Signed Transfers • ISO/IEC 27037 Compliance", fill=(203, 213, 225), font=get_font(10))

    out_file = SCREENSHOTS_DIR / "07-process-flow-architecture.png"
    img.save(out_file)
    print(f"[OK] Saved {out_file.name}")


def main():
    print("[INFO] Generating complete suite of high-resolution KUSTODRA screenshots...")
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
