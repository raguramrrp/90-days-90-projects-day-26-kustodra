"""
TRACEVAULT - Professional UI Stylesheet
Implements the exact visual design system: restrained palette, Inter font,
thin borders, monospace cryptographic hashes, and zero vibecoded styling.
"""

WORKSTATION_CSS = """
<style>
/* Import Inter Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global Root Configuration */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #202927;
    background-color: #F4F6F5;
}

/* Streamlit Header & Top Padding */
header[data-testid="stHeader"] {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E1E6E3;
}

.stApp {
    background-color: #F4F6F5;
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}

/* Sidebar Customization */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E1E6E3;
    padding-top: 1rem;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}

/* Workstation Top Header Banner */
.tv-header-bar {
    background-color: #FFFFFF;
    border: 1px solid #E1E6E3;
    border-radius: 4px;
    padding: 12px 18px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.tv-logo-title {
    font-size: 19px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #315F50;
    margin: 0;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.tv-header-meta {
    font-size: 12px;
    color: #68736F;
    margin: 0;
}

/* Professional Surface Cards */
.tv-card {
    background-color: #FFFFFF;
    border: 1px solid #E1E6E3;
    border-radius: 4px;
    padding: 16px 20px;
    margin-bottom: 16px;
}

.tv-card-header {
    border-bottom: 1px solid #E1E6E3;
    padding-bottom: 10px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.tv-card-title {
    font-size: 15px;
    font-weight: 600;
    color: #202927;
    margin: 0;
}

.tv-card-subtitle {
    font-size: 12px;
    color: #68736F;
    margin-top: 2px;
}

/* Metric Display Blocks */
.tv-metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
}

.tv-metric-box {
    background-color: #FFFFFF;
    border: 1px solid #E1E6E3;
    border-radius: 4px;
    padding: 14px 18px;
}

.tv-metric-label {
    font-size: 12px;
    font-weight: 500;
    color: #68736F;
    margin-bottom: 4px;
}

.tv-metric-val {
    font-size: 24px;
    font-weight: 700;
    color: #202927;
    margin: 0;
}

/* Monospace Cryptographic Hash Boxes */
.tv-hash-box {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 12px;
    background-color: #EDF1EE;
    border: 1px solid #E1E6E3;
    border-radius: 3px;
    padding: 8px 12px;
    word-break: break-all;
    color: #202927;
    line-height: 1.4;
    user-select: all;
}

.tv-hash-box-small {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 11px;
    background-color: #EDF1EE;
    padding: 2px 6px;
    border-radius: 3px;
    border: 1px solid #E1E6E3;
    display: inline-block;
}

/* Status Indicators */
.tv-status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
}

.tv-status-verified {
    background-color: #EBF5F0;
    color: #287A54;
    border: 1px solid #C4E3D4;
}

.tv-status-pending {
    background-color: #FBF6EB;
    color: #B77B29;
    border: 1px solid #F0DFC0;
}

.tv-status-mismatch {
    background-color: #FBEFEF;
    color: #B74747;
    border: 1px solid #F2C7C7;
}

/* Tables */
.tv-table-container {
    border: 1px solid #E1E6E3;
    border-radius: 4px;
    background: #FFFFFF;
    overflow-x: auto;
}

/* Streamlit Native Button Overrides */
div.stButton > button {
    background-color: #315F50;
    color: #FFFFFF;
    font-weight: 500;
    font-size: 13px;
    border: 1px solid #274D40;
    border-radius: 3px;
    padding: 6px 14px;
    transition: all 0.15s ease;
}

div.stButton > button:hover {
    background-color: #274D40;
    border-color: #1E3B31;
    color: #FFFFFF;
}

div.stButton > button:active {
    background-color: #1E3B31;
}

/* Secondary Button Styling */
div.stDownloadButton > button {
    background-color: #FFFFFF;
    color: #315F50;
    font-weight: 500;
    font-size: 13px;
    border: 1px solid #315F50;
    border-radius: 3px;
    padding: 6px 14px;
}

div.stDownloadButton > button:hover {
    background-color: #EDF1EE;
    border-color: #274D40;
    color: #274D40;
}

/* Timeline Components */
.tv-timeline-item {
    border-left: 2px solid #315F50;
    padding-left: 16px;
    margin-left: 8px;
    margin-bottom: 18px;
    position: relative;
}

.tv-timeline-item::before {
    content: '';
    position: absolute;
    left: -6px;
    top: 4px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #315F50;
}

.tv-timeline-time {
    font-size: 11px;
    font-weight: 600;
    color: #68736F;
    margin-bottom: 2px;
}

.tv-timeline-title {
    font-size: 13px;
    font-weight: 600;
    color: #202927;
    margin-bottom: 4px;
}

.tv-timeline-desc {
    font-size: 12px;
    color: #4A5653;
    line-height: 1.4;
}
</style>
"""
