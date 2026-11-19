# TRACEVAULT - 90-Second Interview Demonstration Script

Follow this script to demonstrate TRACEVAULT during technical interviews:

### Step 1: Overview Dashboard (00:00 - 00:20)
- Launch the application: `run.bat`
- Point to the **Evidence Overview** screen:
  - Show the 4 summary metrics: Total Evidence (5), Verified (1), Pending (4), Discrepancies (0).
  - Note the clean, non-vibecoded design: restrained palette (`#F4F6F5` background, `#315F50` pine accent), monospace hashes, and clear information hierarchy.
  - Explain: *"TRACEVAULT manages digital evidence bitstream integrity and custody for forensics and compliance."*

### Step 2: Evidence Registration & Hashing (00:20 - 00:40)
- Navigate to **Register Evidence**.
- Drag and drop `data/sample_evidence/server_access_log.log`.
- Highlight live features:
  - Header inspection detects plain text / UTF-8 structure.
  - Automatic calculation of primary SHA-256 hash plus legacy MD5 and SHA-1.
  - Shannon Entropy computed at $4.12 / 8.0$ (indicating readable structured text).
  - Cross-case duplicate detector alerts if the exact file hash was seen in another case.

### Step 3: Integrity Verification & Tampering Detection (00:40 - 01:05)
- Navigate to **Integrity Verification**.
- Select exhibit `EV-2026-0001` (Compromised Gateway Access Log).
- Click **Forensic Sample Test** -> **Load Authentic Sample** -> **Execute Integrity Verification**:
  - Show the green **MATCH CONFIRMED (100% BIT-LEVEL INTEGRITY)** status.
- Now click **Load Tampered Sample (tampered_server_log.log)** -> **Execute Integrity Verification**:
  - Point out the red **INTEGRITY MISMATCH DETECTED (TAMPERING ALERT)** status.
  - Show the side-by-side hash comparison highlighting the differing SHA-256 digest.
  - Explain: *"Any single bit change alters the SHA-256 hash completely; the system immediately records an audit event and updates the evidence status."*

### Step 4: Chain of Custody & Tamper-Evident Audit Chain (01:05 - 01:30)
- Navigate to **Chain of Custody**:
  - View the chronological timeline of transfers between investigator and forensic lab.
  - Point to the cryptographic transfer receipt tokens.
- Navigate to **Audit Reports**:
  - Click **Compile Official PDF Certificate** to download the court-ready ReportLab document.
- Navigate to **System Settings**:
  - Click **Run Full Chain Validation**:
  - Show: *"The system validates all sequential SHA-256 audit blocks. If anyone modifies a database row directly in SQLite, the validator catches the broken block."*
