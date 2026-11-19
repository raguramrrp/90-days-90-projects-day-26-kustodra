# Data Directory Guide

This folder contains storage directories and forensic artifacts used by TRACEVAULT.

## Subdirectories

- `sample_evidence/`: Synthetic, realistic test files used for intake verification and tampering demonstrations:
  - `server_access_log.log`: Web server log with HTTP requests and IPs.
  - `tampered_server_log.log`: Altered copy with modified IP addresses for 1-click mismatch verification.
  - `surveillance_cam4_frame109.png`: Raster security camera still frame.
  - `financial_audit_ledger.csv`: Structured tabular transaction log.
  - `confidential_asset_agreement.txt`: Text document for text metadata inspection.
  - `suspect_encrypted_payload.bin`: High-entropy pseudo-random binary block for encryption analysis.
  - `TRACEVAULT_SAMPLE_CERTIFICATE.pdf`: Compiled ReportLab PDF certificate sample.

- `vault_storage/`: Local repository storing bitstream copies of registered evidence with immutable filenames (`<EVIDENCE_ID>_<ORIGINAL_NAME>`).

- `tracevault.db`: SQLite database file operating in WAL (Write-Ahead Logging) mode.
