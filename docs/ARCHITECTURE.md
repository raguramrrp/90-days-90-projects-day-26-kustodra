# TRACEVAULT - System Architecture

## Component Overview

```
                                  +--------------------------------------------------+
                                  |            Streamlit Workstation UI              |
                                  |  (Overview, Register, Repository, Verification,  |
                                  |   Chain of Custody, Audit Reports, Settings)    |
                                  +------------------------+-------------------------+
                                                           |
                                                           v
                                  +--------------------------------------------------+
                                  |             TRACEVAULT Core Engines              |
                                  |                                                  |
                                  |  - CryptoEngine (Streaming SHA-256 / Entropy)    |
                                  |  - MetadataInspector (Signatures / Spoof Check)  |
                                  |  - ForensicAnalyzer (Heuristics / Risk Scoring)  |
                                  |  - CustodyManager (Transfers / Receipts)         |
                                  |  - AuditEngine (Cryptographically Chained Logs)  |
                                  |  - ReportGenerator (ReportLab PDF Certificates)  |
                                  +------------------------+-------------------------+
                                                           |
                                  +------------------------+-------------------------+
                                  |                                                  |
                                  v                                                  v
                    +---------------------------+                      +---------------------------+
                    |      SQLite Database      |                      |    Vault Storage Engine   |
                    | (users, cases, evidence,  |                      |  (Air-gapped bitstream    |
                    |  custody_logs, audit_logs)|                      |   copies on local disk)   |
                    +---------------------------+                      +---------------------------+
```

## Data Schema & Relationships

- `users`: Represents verified forensic examiners, investigators, custodians, and prosecutors.
- `cases`: Master investigative case records (`case_id`, `case_title`, `jurisdiction`).
- `evidence`: Evidentiary artifacts, baseline hashes (`sha256_hash`, `md5_hash`, `sha1_hash`), Shannon entropy, and storage pointers.
- `custody_logs`: Handovers linking `sender_id`, `receiver_id`, `transfer_reason`, and `signature_token`.
- `integrity_checks`: Check logs recording calculated hashes, timestamp, examiner, and match/mismatch determinations.
- `audit_logs`: Chained activity ledger linking `curr_hash = SHA256(prev_hash + data)`.
