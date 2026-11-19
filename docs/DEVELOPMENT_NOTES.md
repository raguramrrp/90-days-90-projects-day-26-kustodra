# TRACEVAULT - Development Notes

## Design & Engineering Decisions

### 1. Memory-Bounded Cryptographic Streaming
Forensic disk images and video files can reach gigabytes in size. Loading entire files into memory can cause Out-Of-Memory (OOM) crashes. `CryptoEngine.calculate_hashes_from_stream` uses a 64KB chunk buffer to compute SHA-256, MD5, and SHA-1 in a single streaming pass.

### 2. Constant-Time Hash Comparison
Standard string equality (`==`) terminates early on the first differing character, creating a potential timing side-channel attack. We enforce `hmac.compare_digest()` for constant-time comparisons.

### 3. Shannon Entropy Calculation
Entropy ($H = -\sum p_i \log_2 p_i$) measures bit randomness on a 0.0 to 8.0 scale. Plain ASCII logs typically show $H \approx 3.5 - 4.5$, while encrypted archives or packed malware exhibit $H > 7.6$. This gives examiners immediate visibility into file structure without executing code.

### 4. Cryptographically Chained Audit Ledger
To protect against insider threat or SQL tampering, each audit entry records:
$$\text{curr\_hash} = \text{SHA256}(\text{prev\_hash} + \text{timestamp} + \text{event\_type} + \text{user\_id} + \text{details})$$
If any row in the SQLite database is edited or deleted, `AuditEngine.verify_audit_chain()` detects the broken link and pinpoints the exact row.

### 5. Robust Connection Lifecycle on Windows
To avoid SQLite `PermissionError` on Windows during temporary file deletion, `DatabaseManager.get_connection()` is implemented as a context manager yielding connections with automatic commit, rollback, and `conn.close()` in `finally`.
