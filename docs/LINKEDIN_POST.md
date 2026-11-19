# LinkedIn Post Content — Day 26: KUSTODRA

Copy and paste the text below directly into LinkedIn:

---

🚀 **Day 26 of 90 Days — 90 Projects Challenge!**

Can you prove in court that a digital evidence file wasn’t modified in Notepad right before the trial?

In digital forensics and cyber incident response, **digital artifacts are fragile**. If an investigator seizes a server access log, a surveillance video, or an encrypted binary, opposing counsel will always ask:
1️⃣ *How do we know someone didn't edit this file after seizure?*
2️⃣ *Who had custody of this file at every single minute?*
3️⃣ *Can you mathematically prove this file is 100% bit-for-bit identical to the one collected on day one?*

If that chain of authenticity is broken, the evidence gets thrown out.

To solve this, I built **KUSTODRA** — an enterprise-grade **Digital Evidence Integrity & Chain-of-Custody Management System**.

---

### 🛡️ Think of it as a High-Tech Digital Evidence Locker:
* **The Tamper-Evident Seal ➔ SHA-256 Bitstream Fingerprinting:** The moment a file is acquired, immutable cryptographic digests (SHA-256, MD5, SHA-1) are calculated. If even 1 single bit changes, the hash changes completely.
* **The Evidence Tag ➔ Automated Metadata & Magic Byte Inspection:** Reads raw file headers (magic bytes) to catch extension spoofing (e.g., malware disguised as `.txt` or `.png`) and computes **Shannon Entropy** to detect encrypted or packed payloads.
* **The Chain-of-Custody Sign-Out Sheet ➔ Cryptographic Handover Tokens:** Tracks every custody transfer between examiners, analysts, and vault storage, sealing each transaction with a verifiable HMAC receipt token.
* **The Inspection Bench ➔ Cryptographic Integrity Lab:** Conducts constant-time verification (`hmac.compare_digest`) to prevent timing attacks, flagging any tampering down to the exact divergent byte.
* **The Courtroom Affidavit ➔ Automated Forensic PDF Certificates:** Compiles publication-ready, court-admissible audit reports and case manifests using ReportLab.

---

### 💻 System Architecture & Technical Stack:
* **Core Backend:** Python 3.12 & SQLite (WAL Mode for high-concurrency ACID transactions)
* **Cryptographic Engine:** `hashlib` & `hmac` (constant-time verification, HMAC tokenized receipts)
* **Forensic Analytics:** Magic signature extraction, Shannon Entropy calculation, and heuristic risk scoring
* **Interface & UX:** Modern Streamlit workstation featuring a **sleek 72px vertical navigation rail**, full-width responsive layout, and high-density enterprise data grids
* **Reporting:** ReportLab PDF compilation & Markdown/CSV export
* **Reliability:** 24 comprehensive unit and end-to-end integration tests (`pytest`)

Building this project deepened my understanding of security engineering, cryptographic baselines, side-channel attack prevention, and building audit-compliant enterprise systems.

GitHub Repository: [Link in comments]

I’d love to hear your thoughts on how your security or forensics teams handle digital chain of custody! 👇

#90Days90Projects #Cybersecurity #DigitalForensics #SecurityEngineering #Python #Streamlit #Cryptography #SoftwareEngineering #StudentsWhoCode #Placements #BuildInPublic
