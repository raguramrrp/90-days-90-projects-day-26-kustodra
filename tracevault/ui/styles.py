"""
TRACEVAULT - Forensic Workstation Stylesheet
Implements the Forensic Evidence Workbench visual identity:
Calm, precise, archival aesthetic combining forensic laboratory, digital evidence archive,
and cryptographic workstation influences.
"""

WORKSTATION_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Color System */
:root {
    --tv-bg: #F2F4F1;
    --tv-surface: #FFFFFF;
    --tv-surface-subtle: #E9EEEA;
    --tv-text: #202A27;
    --tv-text-muted: #697570;
    --tv-forest: #315F50;
    --tv-sage: #91AA9D;
    --tv-tech: #527C78;
    --tv-border: #DCE3DE;
    --tv-verified: #287A54;
    --tv-pending: #B77B29;
    --tv-mismatch: #B74747;
}

/* Base Font & Theme */
html, body, [class*="css"], .stMarkdown, p, div {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #202A27;
}

.stApp {
    background-color: #F2F4F1;
}

/* Content Area Grid */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 2.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1240px;
}

/* Headings Hierarchy */
h1 {
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #202A27 !important;
    letter-spacing: -0.3px !important;
    margin-bottom: 4px !important;
}

h2, h3 {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #202A27 !important;
    letter-spacing: -0.2px !important;
    margin-top: 0px !important;
    margin-bottom: 6px !important;
}

h4 {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #315F50 !important;
    margin-bottom: 6px !important;
}

/* Sidebar Styling: Archival & Compact */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #DCE3DE;
    padding-top: 0.5rem;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1rem;
    padding-left: 0.75rem;
    padding-right: 0.75rem;
}

/* Sidebar Navigation Buttons */
div[data-testid="stSidebar"] div.stButton > button {
    text-align: left;
    justify-content: flex-start;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 12px;
    margin-bottom: 3px;
    width: 100%;
}

div[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background-color: transparent;
    border: 1px solid transparent;
    color: #4A5653;
}

div[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
    background-color: #E9EEEA;
    border: 1px solid #DCE3DE;
    color: #202A27;
}

div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background-color: #315F50;
    border: 1px solid #315F50;
    color: #FFFFFF;
    font-weight: 600;
}

/* Top Application Shell Header */
.tv-app-header {
    background-color: #FFFFFF;
    border: 1px solid #DCE3DE;
    border-radius: 4px;
    padding: 10px 18px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.tv-app-title {
    font-size: 17px;
    font-weight: 700;
    color: #315F50;
    letter-spacing: 0.4px;
}

.tv-app-descriptor {
    font-size: 10px;
    font-weight: 600;
    color: #697570;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

.tv-user-tag {
    font-size: 12px;
    font-weight: 600;
    color: #202A27;
    text-align: right;
}

.tv-user-role {
    font-size: 11px;
    color: #697570;
    text-align: right;
}

/* Native Buttons */
div.stButton > button {
    border-radius: 4px;
    font-size: 13px;
    font-weight: 500;
    padding: 6px 14px;
}

div.stButton > button[kind="primary"] {
    background-color: #315F50;
    color: #FFFFFF;
    border: 1px solid #274D40;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #274D40;
    border-color: #1E3B31;
    color: #FFFFFF;
}

div.stButton > button[kind="secondary"] {
    background-color: #FFFFFF;
    color: #202A27;
    border: 1px solid #DCE3DE;
}

div.stButton > button[kind="secondary"]:hover {
    background-color: #E9EEEA;
    border-color: #91AA9D;
}

/* Streamlit Native Container Override */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF;
    border-color: #DCE3DE !important;
    border-radius: 4px;
}

/* Monospace Elements (JetBrains Mono / Consolas) */
code, pre, .tv-mono {
    font-family: 'JetBrains Mono', Consolas, 'Courier New', monospace !important;
}

/* Textual File-Type Badges */
.tv-type-tag {
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 3px;
    text-transform: uppercase;
    display: inline-block;
    border: 1px solid #DCE3DE;
    background-color: #E9EEEA;
    color: #202A27;
}

/* Integrity Status Badges */
.tv-badge-verified {
    background-color: #EBF5F0;
    color: #287A54;
    border: 1px solid #C4E3D4;
    padding: 2px 7px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
}

.tv-badge-pending {
    background-color: #FBF6EB;
    color: #B77B29;
    border: 1px solid #F0DFC0;
    padding: 2px 7px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
}

.tv-badge-mismatch {
    background-color: #FBEFEF;
    color: #B74747;
    border: 1px solid #F2C7C7;
    padding: 2px 7px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
}

/* Technical Hash Fingerprint Panel */
.tv-hash-box {
    background-color: #E9EEEA;
    border: 1px solid #DCE3DE;
    border-radius: 4px;
    padding: 10px 14px;
    margin-top: 6px;
    margin-bottom: 12px;
}

.tv-hash-label {
    font-size: 11px;
    font-weight: 600;
    color: #527C78;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.tv-hash-value {
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 12px;
    color: #202A27;
    word-break: break-all;
}

/* Comparison Diff Panels */
.tv-compare-panel {
    background-color: #FFFFFF;
    border: 1px solid #DCE3DE;
    border-radius: 4px;
    padding: 12px 16px;
}

.tv-diff-match {
    background-color: #EBF5F0;
    border: 1px solid #C4E3D4;
    color: #287A54;
    border-radius: 4px;
    padding: 12px 16px;
    margin-bottom: 12px;
}

.tv-diff-mismatch {
    background-color: #FBEFEF;
    border: 1px solid #F2C7C7;
    color: #B74747;
    border-radius: 4px;
    padding: 12px 16px;
    margin-bottom: 12px;
}

/* Compact Activity Stream Item */
.tv-stream-item {
    padding-bottom: 8px;
    margin-bottom: 8px;
    border-bottom: 1px solid #DCE3DE;
    font-size: 12px;
}

.tv-stream-item:last-child {
    border-bottom: none;
    margin-bottom: 0px;
    padding-bottom: 0px;
}
</style>
"""
