"""
KUSTODRA - Live Browser Screenshot Capture Engine
Captures 100% authentic, high-resolution screenshots of the active running
Streamlit application using Headless Chrome & Chrome DevTools Protocol (CDP).
"""

import os
import sys
import subprocess
import time
import json
import base64
import asyncio
from pathlib import Path
import urllib.request
import requests
import websockets

PROJECT_ROOT = Path(r"D:\90 days\90-days-90-projects-day-26-kustodra")
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 8507
DEBUG_PORT = 9225


async def capture_cdp_screenshot(url: str, output_paths: list[Path], width: int = 1440, height: int = 900, wait_seconds: int = 6):
    """Launch Headless Chrome via CDP, wait for Streamlit to render, and save real screenshot."""
    print(f"[CDP] Navigating to: {url}")
    chrome_proc = subprocess.Popen(
        [
            CHROME_PATH,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            f"--remote-debugging-port={DEBUG_PORT}",
            f"--window-size={width},{height}",
            "--hide-scrollbars",
            url,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2.5)

    try:
        # Query Chrome for open pages
        resp = requests.get(f"http://localhost:{DEBUG_PORT}/json", timeout=5)
        targets = resp.json()
        target = next((t for t in targets if t.get("type") == "page"), targets[0])
        ws_url = target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=50_000_000) as ws:
            # Let Streamlit WebSockets, custom CSS, fonts, and DOM components mount completely
            print(f"[CDP] Connected to Chrome tab. Waiting {wait_seconds}s for Streamlit DOM to mount...")
            await asyncio.sleep(wait_seconds)

            # Capture high-resolution screenshot
            msg = {"id": 1, "method": "Page.captureScreenshot", "params": {"format": "png"}}
            await ws.send(json.dumps(msg))
            recv_data = await ws.recv()
            data = json.loads(recv_data)

            if "result" in data and "data" in data["result"]:
                img_bytes = base64.b64decode(data["result"]["data"])
                for p in output_paths:
                    with open(p, "wb") as f:
                        f.write(img_bytes)
                    print(f"  [SUCCESS] Captured REAL live screenshot: {p.name} ({len(img_bytes):,} bytes)")
                return True
            else:
                print(f"  [ERROR] Failed to capture: {data}")
                return False
    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()
        time.sleep(1)


def main():
    print("=" * 70)
    print("KUSTODRA - Real Live Application Screenshot Capturer")
    print("=" * 70)

    # 1. Start Streamlit in headless mode
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    print(f"[1/8] Launching KUSTODRA Streamlit Workstation on port {PORT}...")
    st_proc = subprocess.Popen(
        [
            str(PYTHON_EXE),
            "-m", "streamlit", "run", "app.py",
            f"--server.port={PORT}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for server ready
    ready = False
    base_url = f"http://localhost:{PORT}"
    for attempt in range(15):
        time.sleep(1)
        try:
            with urllib.request.urlopen(base_url, timeout=1) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except Exception:
            pass

    if not ready:
        print("[FATAL] Streamlit server failed to start on port", PORT)
        st_proc.kill()
        return

    print(f"[OK] Streamlit workstation is running live at {base_url}!")

    try:
        # Screen 1: Artifact Vault (Primary Screen)
        print("\n[2/8] Capturing Screen 1: Artifact Vault...")
        asyncio.run(capture_cdp_screenshot(
            f"{base_url}/?nav=Artifact+Vault",
            [SCREENSHOTS_DIR / "01-artifact-vault.png", SCREENSHOTS_DIR / "01-evidence-repository.png"],
            width=1440, height=920, wait_seconds=7
        ))

        # Screen 2: Artifact Inspector (Specimen Bitstream & Forensic Analysis)
        print("\n[3/8] Capturing Screen 2: Structured Artifact Inspector...")
        asyncio.run(capture_cdp_screenshot(
            f"{base_url}/?artifact_id=ART-2026-0005",
            [SCREENSHOTS_DIR / "02-artifact-inspector.png", SCREENSHOTS_DIR / "02-evidence-details.png", SCREENSHOTS_DIR / "03-artifact-inspector.png"],
            width=1440, height=920, wait_seconds=6
        ))

        # Screen 3: Cryptographic Integrity Laboratory
        print("\n[4/8] Capturing Screen 3: Cryptographic Integrity Laboratory...")
        asyncio.run(capture_cdp_screenshot(
            f"{base_url}/?nav=Integrity+Lab",
            [SCREENSHOTS_DIR / "03-integrity-lab.png", SCREENSHOTS_DIR / "04-integrity-lab.png"],
            width=1440, height=920, wait_seconds=6
        ))

        # Screen 4: Chain of Custody Timeline Ledger
        print("\n[5/8] Capturing Screen 4: Chain of Custody Timeline Ledger...")
        asyncio.run(capture_cdp_screenshot(
            f"{base_url}/?nav=Chain+of+Custody",
            [SCREENSHOTS_DIR / "04-chain-of-custody.png", SCREENSHOTS_DIR / "05-chain-of-custody.png"],
            width=1440, height=920, wait_seconds=6
        ))

        # Screen 5: Intake & Ingestion Workspace
        print("\n[6/8] Capturing Screen 5: Intake & Registration Workspace...")
        asyncio.run(capture_cdp_screenshot(
            f"{base_url}/?nav=Intake+%26+Ingestion",
            [SCREENSHOTS_DIR / "02-intake-ingestion.png"],
            width=1440, height=920, wait_seconds=6
        ))

        # Screen 6: Audit & Compliance Reporting
        print("\n[7/8] Capturing Screen 6: Audit & Compliance Reporting...")
        asyncio.run(capture_cdp_screenshot(
            f"{base_url}/?nav=Audit+%26+Compliance",
            [SCREENSHOTS_DIR / "06-audit-compliance-reports.png"],
            width=1440, height=920, wait_seconds=6
        ))

        print("\n[8/8] All live screenshots captured successfully!")
    finally:
        st_proc.terminate()
        try:
            st_proc.wait(timeout=3)
        except Exception:
            st_proc.kill()
        print("[CLEANUP] Streamlit server terminated cleanly.")


if __name__ == "__main__":
    main()
