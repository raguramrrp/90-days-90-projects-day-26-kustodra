"""
KUSTODRA - Artifact Vault (Primary Screen)
Exact enterprise data grid interface inspired by the reference evidence management system:
- Wide prominent search bar
- Compact filter toolbar with active count
- High-density enterprise evidence grid with thumbnail previews
- Multi-criteria filtering (ID, Custodian, Date Range, Category, Status)
- Interactive row selection and detail opening
"""

from __future__ import annotations
import base64
from io import BytesIO
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from kustodra.database import DatabaseManager
from kustodra.ui.components import render_header, get_type_tag, get_format_icon, get_status_badge_html


@st.cache_data(show_spinner=False)
def generate_preview_data_uri(file_path_str: str, category: str, filename: str) -> str:
    """Generate high-fidelity, realistic 64x64 visual thumbnail previews for artifacts."""
    cat_lower = (category or "").lower()
    fn_lower = (filename or "").lower()
    resolved_path = DatabaseManager.resolve_file_path(file_path_str) if file_path_str else None
    font_tiny = ImageFont.load_default()

    # 1. Surveillance / Forensic Camera Still
    if "cam" in fn_lower or "surveillance" in fn_lower or "image" in cat_lower or (resolved_path and resolved_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]):
        if resolved_path and resolved_path.is_file():
            try:
                base = Image.open(resolved_path).convert("RGB")
                enh = ImageEnhance.Contrast(base)
                base = enh.enhance(1.6)
                enh2 = ImageEnhance.Brightness(base)
                base = enh2.enhance(1.3)
                base = base.resize((64, 64), Image.Resampling.LANCZOS)
            except Exception:
                base = Image.new("RGB", (64, 64), color=(20, 35, 30))
        else:
            base = Image.new("RGB", (64, 64), color=(20, 35, 30))

        d = ImageDraw.Draw(base)
        # Scanlines overlay
        for y in range(0, 64, 4):
            d.line([(0, y), (63, y)], fill=(34, 197, 94), width=1)
        # Target brackets
        d.line([(8, 14), (16, 14)], fill=(34, 197, 94), width=1)
        d.line([(8, 14), (8, 22)], fill=(34, 197, 94), width=1)
        d.line([(55, 14), (47, 14)], fill=(34, 197, 94), width=1)
        d.line([(55, 14), (55, 22)], fill=(34, 197, 94), width=1)
        # Center reticle
        d.line([(29, 32), (35, 32)], fill=(34, 197, 94), width=1)
        d.line([(32, 29), (32, 35)], fill=(34, 197, 94), width=1)
        # REC indicator
        d.ellipse([4, 4, 8, 8], fill=(239, 68, 68))
        d.text((12, 1), "REC", fill=(239, 68, 68), font=font_tiny)
        # Bottom timecode bar
        d.rectangle([0, 52, 63, 63], fill=(0, 0, 0))
        d.text((3, 52), "CAM-04 04:12", fill=(34, 197, 94), font=font_tiny)
        d.rectangle([0, 0, 63, 63], outline=(34, 197, 94), width=1)

        buf = BytesIO()
        base.save(buf, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"

    # 2. Spreadsheet / CSV / Financial Ledger
    if "csv" in fn_lower or "ledger" in fn_lower or "financial" in cat_lower or "sheet" in fn_lower:
        img = Image.new("RGB", (64, 64), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        # Green Excel header bar
        d.rectangle([0, 0, 63, 14], fill=(22, 101, 52))
        d.text((5, 1), "CSV", fill=(255, 255, 255), font=font_tiny)
        d.text((36, 1), "$$$", fill=(134, 239, 172), font=font_tiny)
        # Column headers
        d.rectangle([0, 15, 63, 23], fill=(240, 253, 244))
        d.line([(0, 23), (63, 23)], fill=(187, 247, 208), width=1)
        # Data rows
        for r, y in enumerate([24, 34, 44, 54]):
            bg = (248, 250, 252) if r % 2 == 1 else (255, 255, 255)
            d.rectangle([0, y, 63, y+9], fill=bg)
            d.line([(0, y+9), (63, y+9)], fill=(226, 232, 240), width=1)
            # Data cells
            d.rectangle([4, y+3, 18, y+6], fill=(100, 116, 139))
            d.rectangle([24, y+3, 40, y+6], fill=(71, 85, 105))
            d.rectangle([46, y+3, 58, y+6], fill=(22, 101, 52))
        # Column separators
        d.line([(21, 15), (21, 63)], fill=(226, 232, 240), width=1)
        d.line([(43, 15), (43, 63)], fill=(226, 232, 240), width=1)
        d.rectangle([0, 0, 63, 63], outline=(187, 247, 208), width=1)

        buf = BytesIO()
        img.save(buf, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"

    # 3. Log / Console Terminal File
    if "log" in fn_lower or "access" in fn_lower or "log" in cat_lower or "audit" in cat_lower:
        img = Image.new("RGB", (64, 64), color=(15, 23, 42))
        d = ImageDraw.Draw(img)
        # Window top bar
        d.rectangle([0, 0, 63, 14], fill=(30, 41, 59))
        d.ellipse([4, 4, 8, 8], fill=(239, 68, 68))
        d.ellipse([11, 4, 15, 8], fill=(234, 179, 8))
        d.ellipse([18, 4, 22, 8], fill=(34, 197, 94))
        d.text((28, 2), "LOG", fill=(148, 163, 184), font=font_tiny)
        # Multi-color log lines
        colors = [(56, 189, 248), (74, 222, 128), (251, 146, 60), (148, 163, 184)]
        y = 18
        lines = [
            [(5, 25), (28, 48), (51, 58)],
            [(5, 20), (23, 42), (45, 60)],
            [(5, 30), (33, 50)],
            [(5, 18), (21, 35), (38, 55)],
            [(5, 26), (29, 46)]
        ]
        for i, line_segments in enumerate(lines):
            for j, seg in enumerate(line_segments):
                c = colors[(i + j) % len(colors)]
                d.rectangle([seg[0], y, seg[1], y+2], fill=c)
            y += 7
        d.rectangle([5, 54, 9, 58], fill=(34, 197, 94))
        d.rectangle([0, 0, 63, 63], outline=(51, 65, 85), width=1)

        buf = BytesIO()
        img.save(buf, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"

    # 4. Binary / Encrypted / Packed Payload / Malware
    if "bin" in fn_lower or "payload" in fn_lower or "encrypted" in cat_lower or "binary" in cat_lower or "malware" in cat_lower:
        img = Image.new("RGB", (64, 64), color=(15, 23, 42))
        d = ImageDraw.Draw(img)
        # Top bar
        d.rectangle([0, 0, 63, 13], fill=(30, 41, 59))
        d.text((4, 1), "0xBIN", fill=(251, 191, 36), font=font_tiny)
        d.text((38, 1), "ENC", fill=(239, 68, 68), font=font_tiny)
        # Hex rows
        hex_rows = [
            ("7F 45 4C", (56, 189, 248)),
            ("00 2A F1", (244, 114, 182)),
            ("8B E5 C3", (74, 222, 128)),
            ("FF 09 3A", (251, 191, 36)),
            ("1C 89 ED", (167, 139, 250))
        ]
        y = 16
        for code, color in hex_rows:
            d.text((4, y), code, fill=color, font=font_tiny)
            for x in range(46, 60, 4):
                d.ellipse([x, y+3, x+1, y+4], fill=(100, 116, 139))
            y += 9
        # Gold lock badge
        d.rectangle([40, 42, 60, 60], fill=(245, 158, 11), outline=(180, 83, 9), width=1)
        d.rectangle([45, 48, 55, 57], fill=(15, 23, 42))
        d.arc([46, 44, 54, 50], start=180, end=0, fill=(15, 23, 42), width=1)
        d.rectangle([0, 0, 63, 63], outline=(51, 65, 85), width=1)

        buf = BytesIO()
        img.save(buf, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"

    # 5. Default / Legal Document / Specification Notes
    img = Image.new("RGB", (64, 64), color=(241, 245, 249))
    d = ImageDraw.Draw(img)
    # Sheet shadow
    d.rectangle([7, 5, 59, 61], fill=(203, 213, 225))
    # Paper sheet with folded dog-ear corner
    d.polygon([(6, 4), (50, 4), (58, 12), (58, 60), (6, 60)], fill=(255, 255, 255))
    d.polygon([(50, 4), (58, 12), (50, 12)], fill=(226, 232, 240))
    d.line([(50, 4), (50, 12), (58, 12)], fill=(148, 163, 184), width=1)
    # Title bar
    d.rectangle([11, 10, 44, 14], fill=(30, 41, 59))
    # Formatted text lines
    for y in [18, 25, 32, 39, 46]:
        d.rectangle([11, y, 52, y+2], fill=(148, 163, 184))
        d.rectangle([11, y+3, 38, y+4], fill=(203, 213, 225))
    # Red forensic wax seal / stamp
    d.ellipse([42, 44, 54, 56], fill=(220, 38, 38), outline=(153, 27, 27), width=1)
    d.line([(45, 50), (51, 50)], fill=(255, 255, 255), width=1)
    d.rectangle([0, 0, 63, 63], outline=(203, 213, 225), width=1)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"


def render_page(db: DatabaseManager, current_user: dict) -> None:
    """Render the primary Artifact Vault screen."""
    render_header(
        title="Artifact Vault",
        current_user=current_user,
        show_import=True,
        breadcrumb="ASSET MANAGEMENT"
    )

    # 1. Wide Search Bar (Positioned directly beneath header)
    if search_query := st.text_input(
        "Search artifacts",
        placeholder="🔍 Search artifacts by title, ID (e.g. ART-2026-0001), SHA-256 hash, case reference, or custodian...",
        key="ks_main_search_query",
        label_visibility="collapsed"
    ):
        col_sq_txt, col_sq_clr = st.columns([6, 1])
        with col_sq_clr:
            if st.button("Clear Search", key="btn_clear_search", use_container_width=True):
                st.session_state["ks_main_search_query"] = ""
                st.rerun()

    # 2. Compact Filter Toolbar
    with st.container(border=True):
        col_f1, col_f2, col_f3, col_f4, col_views, col_cnt = st.columns([1.8, 2.0, 1.8, 1.8, 1.5, 1.1])

        active_filters = 0
        if search_query:
            active_filters += 1

        with col_f1:
            users = db.get_users()
            user_opts = ["All Custodians"] + [u["full_name"] for u in users]
            owner_filter = st.selectbox("Custodian", options=user_opts, label_visibility="collapsed")
            if owner_filter != "All Custodians":
                active_filters += 1

        with col_f2:
            cat_opts = [
                "All Categories",
                "System & Audit Log",
                "Forensic Still Image",
                "Surveillance Video",
                "Digital Document",
                "Audio Recording",
                "Forensic Disk Image",
                "Encrypted / Packed Payload",
                "Compressed / Encrypted Archive",
                "Executable / Malware Artifact"
            ]
            category_filter = st.selectbox("Category", options=cat_opts, label_visibility="collapsed")
            if category_filter != "All Categories":
                active_filters += 1

        with col_f3:
            stat_opts = ["All Statuses", "Verified", "Not Yet Verified", "Integrity Mismatch", "Verification Failed"]
            status_filter = st.selectbox("Status", options=stat_opts, label_visibility="collapsed")
            if status_filter != "All Statuses":
                active_filters += 1

        with col_f4:
            sort_by = st.selectbox("Sort", options=["Newest First", "Oldest First", "Title A-Z", "Size Large-Small"], label_visibility="collapsed")

        with col_views:
            view_mode = st.segmented_control("View Mode", options=["Table", "Grid"], default="Table", label_visibility="collapsed")

        with col_cnt:
            badge_color = "#315F50" if active_filters > 0 else "#777F7D"
            st.markdown(f"<div style='text-align: right; font-size: 11px; font-weight: 600; color: {badge_color}; margin-top: 8px;'>Filters: <b>{active_filters}</b></div>", unsafe_allow_html=True)

    # Apply database query filters
    effective_search = search_query.strip() if search_query else None

    filter_cat = None if category_filter == "All Categories" else category_filter
    filter_stat = None if status_filter == "All Statuses" else status_filter

    evidence_list = db.get_evidence_list(
        search_query=effective_search,
        category_filter=filter_cat,
        status_filter=filter_stat
    )

    # Filter by owner if selected
    if owner_filter != "All Custodians":
        evidence_list = [e for e in evidence_list if e.get("custodian_name") == owner_filter]

    # Apply sorting
    if sort_by == "Newest First":
        evidence_list = sorted(evidence_list, key=lambda x: str(x.get("created_at", "")), reverse=True)
    elif sort_by == "Oldest First":
        evidence_list = sorted(evidence_list, key=lambda x: str(x.get("created_at", "")))
    elif sort_by == "Title A-Z":
        evidence_list = sorted(evidence_list, key=lambda x: str(x.get("title", "")).lower())
    elif sort_by == "Size Large-Small":
        evidence_list = sorted(evidence_list, key=lambda x: x.get("file_size_bytes", 0), reverse=True)

    # 3. Artifact Count Headline
    st.markdown(f"<div style='font-size: 11px; color: #777F7D; margin-top: 8px; margin-bottom: 8px;'><b>{len(evidence_list)}</b> artifacts cataloged</div>", unsafe_allow_html=True)

    if not evidence_list:
        st.info("No artifacts match the specified search or filter criteria.")
        return

    # 4. View Mode: Dense Enterprise Table vs Grid
    if view_mode == "Table":
        table_rows = []
        for e in evidence_list:
            size_bytes = e["file_size_bytes"]
            size_str = f"{size_bytes / 1024:.1f} KB" if size_bytes < 1024 * 1024 else f"{size_bytes / (1024 * 1024):.2f} MB" if size_bytes >= 1024 * 1024 else f"{size_bytes} B"
            tag = get_type_tag(e.get("category", ""))
            icon = get_format_icon(e.get("category", ""))

            # Resolve disk file path for thumbnail
            file_path = e.get("storage_rel_path") or e.get("storage_path") or ""
            thumb_uri = generate_preview_data_uri(file_path, e.get("category", ""), e.get("original_filename", ""))

            # Format timestamp cleanly
            raw_ts = str(e.get("created_at") or e.get("collection_date") or "")
            ts_clean = raw_ts[:16].replace("T", " ") if raw_ts else "N/A"

            table_rows.append({
                "Artifact ID": e["evidence_id"],
                "Preview": thumb_uri,
                "Artifact Title": f"{icon}  {e['title']}",
                "Format": tag,
                "Custodian": e.get("custodian_name") or e.get("current_custodian_id", "Unknown"),
                "Ingested At": ts_clean,
                "Size": size_str,
                "Integrity State": e["integrity_status"]
            })

        df_display = pd.DataFrame(table_rows)

        # Interactive selection table (SINGLE native checkbox column provided by on_select="rerun")
        grid_event = st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            column_config={
                "Artifact ID": st.column_config.TextColumn("Artifact ID", width=120),
                "Preview": st.column_config.ImageColumn("Preview", width=80),
                "Artifact Title": st.column_config.TextColumn("Artifact Title", width="large"),
                "Format": st.column_config.TextColumn("Format", width=100),
                "Custodian": st.column_config.TextColumn("Custodian", width=160),
                "Ingested At": st.column_config.TextColumn("Ingested At", width=150),
                "Size": st.column_config.TextColumn("Size", width=90),
                "Integrity State": st.column_config.TextColumn("Integrity State", width=140)
            }
        )

        # Handle row selection
        selected_rows = grid_event.selection.rows if grid_event and hasattr(grid_event, "selection") else []
        if selected_rows:
            clicked_ev_id = df_display.iloc[selected_rows[0]]["Artifact ID"]
            st.session_state["selected_evidence_id"] = clicked_ev_id

        # Quick Action Bar for Selected Artifact
        current_choice = st.session_state.get("selected_evidence_id", evidence_list[0]["evidence_id"])
        selected_item = next((e for e in evidence_list if e["evidence_id"] == current_choice), evidence_list[0])
        selected_id = selected_item["evidence_id"]

        with st.container(border=True):
            col_sel_info, col_act1, col_act2, col_act3 = st.columns([3.5, 1.3, 1.3, 1.3])
            with col_sel_info:
                st.markdown(
                    f"**Active Artifact:** `{selected_id}` &bull; **{selected_item['title']}** "
                    f"&bull; {get_status_badge_html(selected_item['integrity_status'])}",
                    unsafe_allow_html=True
                )
            with col_act1:
                if st.button("Inspect Details →", type="primary", use_container_width=True):
                    st.session_state["selected_evidence_id"] = selected_id
                    st.session_state["active_nav"] = "Artifact Inspector"
                    st.rerun()
            with col_act2:
                if st.button("🔬 Verify in Lab", type="secondary", use_container_width=True):
                    st.session_state["selected_evidence_id"] = selected_id
                    st.session_state["active_nav"] = "Integrity Lab"
                    st.rerun()
            with col_act3:
                if st.button("⛓️ Custody", type="secondary", use_container_width=True):
                    st.session_state["selected_evidence_id"] = selected_id
                    st.session_state["active_nav"] = "Chain of Custody"
                    st.rerun()

    else:
        # Grid Card View (Alternative view from switcher)
        cols_per_row = 3
        for i in range(0, len(evidence_list), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(evidence_list):
                    ev = evidence_list[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            file_path = ev.get("storage_rel_path") or ev.get("storage_path") or ""
                            thumb_uri = generate_preview_data_uri(file_path, ev.get("category", ""), ev.get("original_filename", ""))
                            if thumb_uri:
                                st.image(thumb_uri, use_container_width=True)
                            st.markdown(f"**{ev['title']}**")
                            st.caption(f"ID: `{ev['evidence_id']}` &bull; {ev['category']}")
                            st.caption(f"Custodian: **{ev.get('custodian_name', 'N/A')}**")
                            st.markdown(get_status_badge_html(ev['integrity_status']), unsafe_allow_html=True)
                            if st.button(f"Inspect {ev['evidence_id']}", key=f"btn_grid_{ev['evidence_id']}", use_container_width=True):
                                st.session_state["selected_evidence_id"] = ev["evidence_id"]
                                st.session_state["active_nav"] = "Artifact Inspector"
                                st.rerun()
