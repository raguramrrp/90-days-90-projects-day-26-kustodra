# TRACEVAULT - Testing & Quality Assurance

## Test Suite Summary

The automated test suite contains 21 unit and end-to-end integration test cases located in `tests/`:

- `test_crypto_engine.py`:
  - `test_hash_calculation_known_vectors`: Verifies SHA-256, MD5, and SHA-1 against known string vectors.
  - `test_streaming_hash_calculation`: Verifies chunked 64KB calculation matches in-memory hashes.
  - `test_constant_time_verification`: Verifies case-insensitive constant-time digest comparison.
  - `test_shannon_entropy`: Verifies entropy bounds (0.0 for zeros, 3.5-5.0 for text, >7.5 for random bytes).
  - `test_audit_block_hash`: Verifies chained block hash determinism.
  - `test_custody_transfer_token`: Verifies digital transfer token structure.

- `test_metadata_inspector.py`:
  - `test_format_bytes`: Tests human-readable byte conversion.
  - `test_magic_signature_detection`: Validates PNG, JPEG, PDF, SQLite, PE executable, and text signatures.
  - `test_mime_spoofing_detection`: Verifies extension vs signature mismatch detection.
  - `test_text_forensic_metrics`: Verifies line count, blank line, and word count extraction.

- `test_forensic_analyzer.py`:
  - `test_classify_evidence`: Validates automated categorization rules.
  - `test_interpret_entropy`: Checks descriptive entropy levels.
  - `test_evaluate_risk`: Tests risk scoring and indicator calculation.
  - `test_generate_evidence_summary`: Tests forensic summary text generation.

- `test_database_and_custody.py`:
  - `test_add_and_get_evidence`: Tests evidence insertion and querying.
  - `test_duplicate_hash_detection`: Tests finding matching SHA-256 hashes across cases.
  - `test_custody_transfer_workflow`: Tests custody handovers and custodian updates.

- `test_audit_engine.py`:
  - `test_audit_chain_sequential_integrity`: Tests chain verification across sequential events.
  - `test_audit_chain_tamper_detection`: Proves that retroactive SQL row manipulation is caught.

- `test_report_generator.py`:
  - `test_generate_pdf_certificate`: Verifies ReportLab PDF generation and checks `%PDF-` header.

- `test_e2e_forensic_workflow.py`:
  - `test_complete_evidence_forensic_lifecycle`: Full end-to-end test simulating ingest, match, mismatch, custody transfer, audit validation, and PDF export.

## Running Tests

Execute via Windows batch script:
```cmd
test.bat
```
Or directly via Python:
```cmd
.\.venv\Scripts\python.exe -m pytest tests -v
```

**Status:** PASS (21/21 passed, 0.62 seconds execution time).
