# KUSTODRA - Project Overview

## 1. Executive Summary
**KUSTODRA** is a Digital Asset Custody & Cryptographic Integrity Verification System designed for cybersecurity specialists, forensic examiners, and compliance auditors. It provides a secure workstation to catalog digital artifacts, extract deep metadata, calculate multi-algorithm cryptographic digests (SHA-256, MD5, SHA-1), detect tampering, manage custody handovers, maintain a tamper-evident audit ledger, and generate official documentation.

## 2. Core Problem
Digital files (documents, disk images, network traces, and CCTV video) are vulnerable to accidental corruption or intentional alteration during transit and investigation. Proving mathematical continuity and chain of custody is essential for court admissibility and internal compliance.

## 3. Core Objectives
- **Cryptographic Hashing:** Compute deterministic SHA-256, MD5, and SHA-1 hashes using memory-bounded chunked streaming (64KB buffers).
- **Integrity Verification:** Compare current file bitstreams with registered baselines using constant-time comparisons (`hmac.compare_digest`).
- **Chain of Custody Tracking:** Maintain an immutable record of every custodian handover, complete with cryptographic receipt tokens.
- **Tamper-Evident Audit Logging:** Chain each system activity log with the hash of the preceding record to immediately detect retroactive SQL modifications.
- **Reporting:** Compile publication-quality PDF artifact certificates and custody reports using ReportLab.
