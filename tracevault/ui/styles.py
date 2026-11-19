"""
TRACEVAULT - Professional UI Stylesheet
Clean, minimal CSS system adhering strictly to the workstation color palette
and respecting native Streamlit layout rendering.
"""

WORKSTATION_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Base Font & Theme */
html, body, [class*="css"], .stMarkdown, p, div {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #202927;
}

.stApp {
    background-color: #F4F6F5;
}

/* Tighter, balanced main block container */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1240px;
}

/* Sidebar Styling: Clean, narrow, restrained */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E1E6E3;
    padding-top: 0.5rem;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1rem;
    padding-left: 0.75rem;
    padding-right: 0.75rem;
}

/* Sidebar navigation buttons */
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
    background-color: #F4F6F5;
    border: 1px solid #E1E6E3;
    color: #202927;
}

div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background-color: #315F50;
    border: 1px solid #315F50;
    color: #FFFFFF;
    font-weight: 600;
}

/* Top App Header Banner */
.tv-app-header {
    background-color: #FFFFFF;
    border: 1px solid #E1E6E3;
    border-radius: 4px;
    padding: 10px 16px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.tv-app-title {
    font-size: 16px;
    font-weight: 700;
    color: #315F50;
    letter-spacing: 0.3px;
}

.tv-app-subtitle {
    font-size: 11px;
    color: #68736F;
}

.tv-user-tag {
    font-size: 12px;
    font-weight: 600;
    color: #202927;
    text-align: right;
}

.tv-user-role {
    font-size: 11px;
    color: #68736F;
    text-align: right;
}

/* Native buttons styling */
div.stButton > button {
    border-radius: 4px;
    font-size: 13px;
    font-weight: 500;
    padding: 5px 14px;
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
    color: #202927;
    border: 1px solid #E1E6E3;
}

div.stButton > button[kind="secondary"]:hover {
    background-color: #F4F6F5;
    border-color: #789487;
}

/* Status Badges */
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

/* Streamlit Native Container override */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF;
    border-color: #E1E6E3 !important;
    border-radius: 4px;
}
</style>
"""
