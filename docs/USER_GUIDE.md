# TRACEVAULT - User Guide

## Getting Started

1. Launch the application by double clicking `run.bat` or executing `streamlit run app.py`.
2. Open your web browser at `http://localhost:8501`.

## Core Workflows

### 1. Ingesting Evidence
- Navigate to **Register Evidence** in the sidebar.
- Upload any digital file (image, text log, document, video, or binary blob).
- Review the automatically extracted magic bytes, MIME type, and SHA-256 hash preview.
- Fill in the investigative case reference, title, seizure location, and notes.
- Click **Register Evidence**. The file is stored in vault storage and sealed with a unique ID (e.g. `EV-2026-XXXX`).

### 2. Verifying File Integrity
- Navigate to **Integrity Verification**.
- Select the evidence record you wish to audit.
- Choose your verification source:
  - **Stored Vault Copy:** Tests the stored file on disk.
  - **Upload File:** Compares an external copy against the baseline hash.
  - **Forensic Sample Test:** Loads sample files for testing Match vs Mismatch.
- Click **Execute Integrity Verification**.
  - **Match:** Confirms bit-level identity.
  - **Mismatch:** Alerts you that file content was modified and highlights differing digests.

### 3. Transferring Custody
- Navigate to **Chain of Custody**.
- Select the evidence record to view its complete transfer history.
- Use the **Transfer Custody** form to select the receiving custodian and transfer reason.
- Check the legal certification box and submit to generate a verifiable transfer token.

### 4. Generating Audit Reports
- Navigate to **Audit Reports**.
- Select an evidence item and click **Compile Official PDF Certificate**.
- Download the resulting PDF certificate.
- Export case manifests or the full audit log in CSV or JSON format.

### 5. Validating Audit Chain Integrity
- Navigate to **System Settings**.
- Click **Run Full Chain Validation**.
- The engine recalculates sequential block hashes across all audit records and flags any manual row manipulation.
