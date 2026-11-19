"""
KUSTODRA - UI Design System & Stylesheet
Exact reproduction of the reference enterprise evidence management workstation:
- Ultra-narrow vertical icon rail (~72px width)
- Center-aligned navigation glyphs and icons
- Compact horizontal top header with "+ Ingest artifact" action
- Wide prominent search bar
- Compact filter toolbar
- High-density enterprise evidence grid with thumbnail previews
- Neutral white and light-grey surfaces with thin 1px separators (#E1E4E3)
- Modern Plus Jakarta Sans typography and JetBrains Mono cryptographic displays
- Zero persistent tooltips or clutter
"""

WORKSTATION_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* Color Variables */
:root {
    --ks-bg: #F4F5F5;
    --ks-nav-bg: #111514;
    --ks-surface: #FFFFFF;
    --ks-text-primary: #252B2A;
    --ks-text-secondary: #777F7D;
    --ks-accent-forest: #315F50;
    --ks-accent-active: #263D36;
    --ks-border: #E1E4E3;
    --ks-row-hover: #F0F3F1;
    --ks-success: #32815A;
    --ks-warning: #B78032;
    --ks-danger: #BC4B4B;
}

/* Base typography — Premium Plus Jakarta Sans + JetBrains Mono */
html, body, .stApp, .main, [data-testid="stMain"], .stMain, p, h1, h2, h3, h4, h5, h6, label, input, button, select, textarea, .stSelectbox, .stTextInput, .stMarkdown {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
    color: #252B2A;
}

/* Strictly protect Streamlit Material Symbols / Icon ligatures from font-family override */
[data-testid="stIconMaterial"],
.material-symbols-rounded,
.material-symbols-outlined,
.material-icons,
[class*="material-symbols"],
[class*="material-icons"] {
    font-family: "Material Symbols Rounded", "Material Icons" !important;
    font-weight: normal !important;
    font-style: normal !important;
    line-height: 1 !important;
    display: inline-block !important;
    text-transform: none !important;
    letter-spacing: normal !important;
    word-wrap: normal !important;
    white-space: nowrap !important;
    direction: ltr !important;
    -webkit-font-smoothing: antialiased !important;
    -webkit-font-feature-settings: 'liga' !important;
}

code, kbd, samp, pre, .ks-mono, [data-testid="stCode"] {
    font-family: 'JetBrains Mono', Consolas, monospace !important;
}

.stApp {
    background-color: #F4F5F5 !important;
}

/* Content layout — flush next to 72px left rail */
.main,
[data-testid="stMain"],
.stMain {
    margin-left: 72px !important;
    width: calc(100% - 72px) !important;
}

.main .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}

/* Top App Header bar */
header[data-testid="stHeader"] {
    display: none !important;
}

/* Hide default streamlit toolbar to keep interface clean */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Hide collapse controls since rail is permanent */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

/* Hide floating tooltip bubbles without breaking dialogs or popovers */
div[data-testid="stTooltipContent"],
div[role="tooltip"],
.stTooltip {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* --- PERMANENT ULTRA-SLIM LEFT NAVIGATION RAIL (72px) --- */
section[data-testid="stSidebar"],
[data-testid="stSidebar"],
section[data-testid="stSidebar"][aria-expanded="false"],
[data-testid="stSidebar"][aria-expanded="false"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    margin: 0 !important;
    margin-left: 0 !important;
    left: 0 !important;
    top: 0 !important;
    bottom: 0 !important;
    position: fixed !important;
    min-width: 72px !important;
    max-width: 72px !important;
    width: 72px !important;
    height: 100vh !important;
    background-color: #111514 !important;
    border-right: 1px solid #202624 !important;
    border-top: none !important;
    padding: 0 !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    z-index: 99999 !important;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3) !important;
}

/* Sidebar Structural Containers */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
[data-testid="stSidebar"] [data-testid="stSidebarContent"],
[data-testid="stSidebar"] .stSidebarContent {
    background-color: #111514 !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 72px !important;
    min-width: 72px !important;
    max-width: 72px !important;
    overflow-x: hidden !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebar"] .stSidebarUserContent {
    padding: 12px 0 20px 0 !important;
    margin: 0 !important;
    width: 72px !important;
    min-width: 72px !important;
    max-width: 72px !important;
    overflow-x: hidden !important;
}

section[data-testid="stSidebar"] .block-container,
[data-testid="stSidebar"] .block-container {
    padding: 0 !important;
    margin: 0 auto !important;
    width: 72px !important;
    min-width: 72px !important;
    max-width: 72px !important;
}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 8px !important;
    padding: 0 !important;
    margin: 0 auto !important;
    width: 72px !important;
    min-width: 72px !important;
    max-width: 72px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: flex-start !important;
}

section[data-testid="stSidebar"] [data-testid="stElementContainer"],
[data-testid="stSidebar"] [data-testid="stElementContainer"] {
    width: 72px !important;
    min-width: 72px !important;
    max-width: 72px !important;
    margin: 0 auto !important;
    padding: 0 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

section[data-testid="stSidebar"] div.stButton,
[data-testid="stSidebar"] div.stButton {
    width: 72px !important;
    min-width: 72px !important;
    max-width: 72px !important;
    margin: 0 auto !important;
    padding: 0 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

/* Rail Logo Icon at top — Exactly 44x44px centered */
.ks-rail-logo {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    max-width: 44px !important;
    min-height: 44px !important;
    max-height: 44px !important;
    margin: 4px auto 14px auto !important;
    background-color: #1A2220 !important;
    border: 1px solid #283532 !important;
    border-radius: 10px !important;
    color: #32815A !important;
    font-weight: 800 !important;
    font-size: 20px !important;
    line-height: 1 !important;
    text-align: center !important;
    user-select: none !important;
    box-sizing: border-box !important;
}

/* Sidebar Nav Buttons: Base Geometry (44x44 square with rounded corners) */
[data-testid="stSidebar"] button,
section[data-testid="stSidebar"] button,
[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] button[data-testid*="baseButton"],
section[data-testid="stSidebar"] button[data-testid*="baseButton"] {
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    max-width: 44px !important;
    min-height: 44px !important;
    max-height: 44px !important;
    padding: 0 !important;
    margin: 0 auto !important;
    border-radius: 10px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
    outline: none !important;
    transition: all 0.15s ease-in-out !important;
    cursor: pointer !important;
}

/* Inactive Sidebar Buttons: Transparent Charcoal, NEVER WHITE PILLS */
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] button[kind="secondary"],
[data-testid="stSidebar"] .stButton > button[kind="secondary"],
section[data-testid="stSidebar"] button[kind="secondary"],
section[data-testid="stSidebar"] .stButton > button[kind="secondary"],
[data-testid="stSidebar"] button[data-testid*="baseButton-secondary"],
section[data-testid="stSidebar"] button[data-testid*="baseButton-secondary"] {
    background-color: transparent !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    color: #9AA5A1 !important;
}

/* Inactive Hover State */
[data-testid="stSidebar"] button:hover,
[data-testid="stSidebar"] button[kind="secondary"]:hover,
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover,
section[data-testid="stSidebar"] button[kind="secondary"]:hover,
section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background-color: #1A2220 !important;
    background: #1A2220 !important;
    border: 1px solid #283532 !important;
    color: #FFFFFF !important;
}

/* Active Primary Button: Deep Emerald Active State */
[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] button[data-testid*="primary"],
section[data-testid="stSidebar"] button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] button[data-testid*="primary"] {
    background-color: #263D36 !important;
    background: #263D36 !important;
    border: 1px solid #365C50 !important;
    box-shadow: 0 0 10px rgba(50, 129, 90, 0.45) !important;
    color: #5ED49F !important;
}

/* Icon Glyphs inside all sidebar buttons */
[data-testid="stSidebar"] button [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span,
[data-testid="stSidebar"] button div,
section[data-testid="stSidebar"] button [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] button p,
section[data-testid="stSidebar"] button span,
section[data-testid="stSidebar"] button div {
    font-size: 20px !important;
    line-height: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    width: auto !important;
    height: auto !important;
    color: inherit !important;
}

/* --- HORIZONTAL PAGE HEADER --- */
.ks-top-header {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E1E4E3;
    padding: 12px 20px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 6px;
}

.ks-header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.ks-page-title {
    font-size: 20px;
    font-weight: 700;
    color: #252B2A;
    letter-spacing: -0.3px;
    margin: 0;
}

.ks-breadcrumb {
    font-size: 11px;
    font-weight: 600;
    color: #777F7D;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.ks-header-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

/* User Account Tag */
.ks-user-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background-color: #F4F5F5;
    border: 1px solid #E1E4E3;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    color: #252B2A;
}

/* --- PROMINENT SEARCH BAR --- */
.ks-search-container {
    background-color: #FFFFFF;
    border: 1px solid #E1E4E3;
    border-radius: 6px;
    padding: 2px 8px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
}

/* --- FILTER TOOLBAR --- */
.ks-filter-toolbar {
    background-color: #FFFFFF;
    border: 1px solid #E1E4E3;
    border-radius: 6px;
    padding: 8px 14px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
}

/* Results Count */
.ks-results-count {
    font-size: 12px;
    font-weight: 600;
    color: #777F7D;
    margin-bottom: 8px;
    letter-spacing: 0.2px;
}

/* --- ENTERPRISE TABLE STYLING --- */
.stDataFrame {
    background-color: #FFFFFF !important;
    border: 1px solid #E1E4E3 !important;
    border-radius: 6px !important;
}

/* Native buttons styling */
div.stButton > button {
    border-radius: 4px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 6px 14px !important;
}

.main div.stButton > button[kind="primary"],
[data-testid="stMain"] div.stButton > button[kind="primary"] {
    background-color: #315F50 !important;
    border: 1px solid #264B3F !important;
    color: #FFFFFF !important;
}

.main div.stButton > button[kind="primary"]:hover,
[data-testid="stMain"] div.stButton > button[kind="primary"]:hover {
    background-color: #264B3F !important;
    border-color: #1A352D !important;
}

.main div.stButton > button[kind="secondary"],
[data-testid="stMain"] div.stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #252B2A !important;
    border: 1px solid #E1E4E3 !important;
}

.main div.stButton > button[kind="secondary"]:hover,
[data-testid="stMain"] div.stButton > button[kind="secondary"]:hover {
    background-color: #F0F3F1 !important;
    border-color: #C5CCC8 !important;
}

/* Native Container override */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border-color: #E1E4E3 !important;
    border-radius: 6px !important;
}

/* --- FILE UPLOADER CLEAN RENDERING (NO TEXT OVERLAP) --- */
[data-testid="stFileUploader"] {
    width: 100% !important;
}

[data-testid="stFileUploaderDropzone"] {
    background-color: #FAFCFB !important;
    border: 1px dashed #C5CCC8 !important;
    border-radius: 6px !important;
    padding: 16px 20px !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
}

/* --- SEGMENTED CONTROLS (PILL / TAB BUTTONS - NO CIRCLES) --- */
[data-testid="stSegmentedControl"] {
    background-color: #EBF0ED !important;
    border-radius: 8px !important;
    padding: 3px !important;
    border: 1px solid #D8DFDB !important;
    display: inline-flex !important;
    gap: 4px !important;
    width: auto !important;
}

[data-testid="stSegmentedControl"] button {
    border-radius: 6px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #252B2A !important;
    background-color: transparent !important;
    border: none !important;
    padding: 6px 14px !important;
    box-shadow: none !important;
    transition: all 0.15s ease-in-out !important;
}

[data-testid="stSegmentedControl"] button:hover {
    background-color: rgba(49, 95, 80, 0.08) !important;
}

[data-testid="stSegmentedControl"] button[aria-selected="true"],
[data-testid="stSegmentedControl"] button[data-checked="true"] {
    background-color: #315F50 !important;
    color: #FFFFFF !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12) !important;
}

/* Monospace fonts */
code, pre, .ks-mono {
    font-family: 'JetBrains Mono', Consolas, monospace !important;
}

/* Status Badges */
.ks-badge-verified {
    background-color: #EBF5F0;
    color: #32815A;
    border: 1px solid #C4E3D4;
    padding: 2px 7px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
}

.ks-badge-pending {
    background-color: #FBF6EB;
    color: #B78032;
    border: 1px solid #F0DFC0;
    padding: 2px 7px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
}

.ks-badge-mismatch {
    background-color: #FBEFEF;
    color: #BC4B4B;
    border: 1px solid #F2C7C7;
    padding: 2px 7px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
    display: inline-block;
}

/* Category Pill */
.ks-cat-pill {
    background-color: #E9EEEA;
    border: 1px solid #DCE3DE;
    color: #252B2A;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 3px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

/* Compact Hash Box */
.ks-hash-box {
    background-color: #F8F9F9;
    border: 1px solid #E1E4E3;
    border-radius: 4px;
    padding: 8px 12px;
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 12px;
    color: #252B2A;
    word-break: break-all;
}

/* Diff panels */
.tv-compare-panel {
    background-color: #F8F9F9;
    border: 1px solid #E1E4E3;
    border-radius: 4px;
    padding: 10px 14px;
}

.tv-diff-match {
    background-color: #EBF5F0;
    border: 1px solid #C4E3D4;
    color: #32815A;
    border-radius: 4px;
    padding: 12px 16px;
    margin-bottom: 12px;
}

.tv-diff-mismatch {
    background-color: #FBEFEF;
    border: 1px solid #F2C7C7;
    color: #BC4B4B;
    border-radius: 4px;
    padding: 12px 16px;
    margin-bottom: 12px;
}

.ks-stream-item {
    padding: 8px 0;
    border-bottom: 1px solid #E1E4E3;
}
</style>
"""
