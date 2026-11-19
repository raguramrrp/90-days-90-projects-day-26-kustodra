# TRACEVAULT - Troubleshooting & FAQs

## Common Issues & Solutions

### 1. Port 8501 is already in use
**Error:** `Address already in use: 8501`  
**Solution:** Specify another port via command line:
```cmd
.\.venv\Scripts\streamlit.exe run app.py --server.port 8502
```

### 2. Streamlit prompts for email on first launch
**Cause:** Streamlit creates a prompt when `.streamlit/credentials.toml` is absent.  
**Solution:** A default configuration is provided in `.streamlit/config.toml` with `gatherUsageStats = false`. Running `setup.bat` initializes the configuration automatically.

### 3. Verification reports "Integrity Mismatch"
**Explanation:** This is an intentional security alert. It means the file being verified does not match the original SHA-256 hash recorded at registration.
- Verify whether the file was opened and re-saved in an editor (which alters line endings or metadata).
- If demonstrating the mismatch alert, this confirms the system detects tampered bitstreams.

### 4. Database reset needed
**Solution:** Go to **System Settings** in the application and click **Reset & Re-seed Forensic Database**, or run:
```cmd
.\.venv\Scripts\python scripts\seed_demo_data.py
```
