# KUSTODRA - User Guide

## Getting Started

1. Launch the application by double clicking `run.bat` or executing `.\run.ps1`.
2. Open your web browser at `http://localhost:8501`.

## Core Workflows

### 1. Ingesting Digital Artifacts
- Navigate to **Intake & Ingestion** in the navigation rail or click **+ Ingest Artifact** in the header.
- Upload any digital file (image, text log, document, video, or binary blob).
- Review the automatically extracted magic bytes, MIME type, and SHA-256 hash preview.
- Fill in the investigative case reference, title, collection location, and notes.
- Click **Seal Artifact into Vault**. The file is stored in vault storage and sealed with a unique ID (e.g. `ART-2026-XXXX`).

### 2. Verifying Bitstream Integrity
- Navigate to **Integrity Lab**.
- Select the cataloged artifact record you wish to audit.
- Choose your verification source:
  - **Stored Vault Bitstream:** Tests the stored file on disk.
  - **Upload Verification File:** Compares an external copy against the baseline hash.
  - **Validation Benchmark Suite:** Loads benchmark files for testing Match vs Mismatch.
- Click **Execute Verification**.
  - **Match:** Confirms bit-level identity.
  - **Mismatch:** Alerts you that file content was modified and highlights differing digests.

### 3. Transferring Custody
- Navigate to **Chain of Custody**.
- Select the artifact record to view its complete transfer history.
- Use the **Custody Transfer Authorization** form to select the receiving custodian and transfer reason.
- Check the legal certification box and submit to generate a verifiable transfer token.

### 4. Generating Audit & Compliance Reports
- Navigate to **Audit & Compliance**.
- Select an artifact item and click **Compile Official PDF Certificate**.
- Download the court-ready PDF certificate.
- Export case manifests or the full audit log in CSV or JSON format.

### 5. Validating Audit Chain Integrity
- Navigate to **System Configuration**.
- Click **Run Audit Chain Verification**.
- The engine recalculates sequential block hashes across all audit records and flags any manual row manipulation.
