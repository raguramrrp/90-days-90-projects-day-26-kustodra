# KUSTODRA — 90-Second Walkthrough & Technical Presentation
**Digital Asset Custody & Cryptographic Integrity Verification System**  
*Every artifact. Every transfer. Every verification. Documented.*

Follow this script to present KUSTODRA during technical interviews and architecture reviews:

### Step 1: Enterprise Artifact Vault (00:00 - 00:25)
- Launch the application: `run.bat`
- Point to the **Artifact Vault** screen (the default landing view):
  - Highlight the sleek enterprise design: 70px dark charcoal navigation rail with clear tooltips and mint active indicators, full-width search bar, compact filter toolbar with active count badge, and dense data grid.
  - Demonstrate thumbnail previews for images and crisp 48×48 format badges for documents, logs, and binaries.
  - Filter by category ("System & Audit Log") or search by ID (`ART-2026-0001`).
  - Explain: *"KUSTODRA is an enterprise digital asset custody and cryptographic integrity workstation designed for forensic laboratories, compliance auditors, and security operations."*

### Step 2: Artifact Intake & Cryptographic Hashing (00:25 - 00:45)
- Click **+ Ingest Artifact** in the top header.
- Drag and drop `data/sample_evidence/server_access_log.log`.
- Highlight live forensic features:
  - Header inspection detects plain text / UTF-8 structure via magic bytes.
  - Automatic calculation of primary SHA-256 bitstream hash plus legacy MD5 and SHA-1.
  - Shannon Entropy computed at $4.12 / 8.0$ (indicating readable structured text).
  - Cross-case duplicate detector alerts if the exact file hash was seen in another record.
  - Review & seal into KUSTODRA vault storage.

### Step 3: Integrity Lab & Tampering Detection (00:45 - 01:10)
- Navigate to **Integrity Lab** (microscope icon in rail).
- Select cataloged item `ART-2026-0001` (Gateway Server Access Log).
- Choose **Validation Benchmark Suite** -> **Authentic Reference Sample** -> **Execute Verification**:
  - Show the green **INTEGRITY MATCH (100% BIT-LEVEL AUTHENTICITY)** status.
- Now select **Tampered Specimen (1-Byte Alteration)** -> **Execute Verification**:
  - Point out the red **INTEGRITY MISMATCH DETECTED** alert.
  - Show the side-by-side hash comparison highlighting the divergent hexadecimal nibbles.
  - Explain: *"Even a 1-bit change alters the cryptographic digest completely due to the avalanche effect. KUSTODRA permanently logs the discrepancy to an immutable SQLite ledger."*

### Step 4: Chain of Custody & Tamper-Evident Audit Chain (01:10 - 01:30)
- Navigate to **Chain of Custody** (chain link icon):
  - View the chronological timeline of transfers between investigator and laboratory.
  - Point to the cryptographic transfer receipt tokens.
- Navigate to **Audit & Compliance** (document icon):
  - Click **Generate Official PDF Certificate** to download the court-ready ReportLab document.
- Navigate to **System Configuration** (gear icon):
  - Click **Run Audit Chain Verification**:
  - Show: *"The system validates all sequential SHA-256 audit blocks. If anyone modifies a database row directly in SQLite, the validator catches the broken block."*
