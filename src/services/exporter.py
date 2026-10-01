import io
import re
from datetime import datetime
from typing import List
import pandas as pd
from src.models import Lead
from src.services.normalizer import sanitize_formula_injection

def create_safe_filename(category: str, area: str, city: str, extension: str = "xlsx") -> str:
    """Generates a clean, sanitized filename for exports."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    raw = f"{category}_{area}_{city}_{date_str}".lower()
    clean = re.sub(r"[^\w\-]+", "_", raw).strip("_")
    return f"{clean}.{extension}"

def export_to_excel(leads: List[Lead]) -> bytes:
    """
    Exports leads to an in-memory formatted Excel workbook (bytes).
    Uses xlsxwriter for professional styling with frozen headers and auto column widths.
    """
    output = io.BytesIO()

    # Prepare rows with formula injection safety
    data = []
    for lead in leads:
        d = lead.to_export_dict()
        safe_row = {col: sanitize_formula_injection(val) for col, val in d.items()}
        data.append(safe_row)

    df = pd.DataFrame(data)
    if df.empty:
        df = pd.DataFrame(columns=[
            "Business Name", "Phone", "Address", "Website", "Lead Score", 
            "Opportunity", "Suggested Service", "Pitch Angle", "Maps Link", "Category", "Source"
        ])

    # Write using xlsxwriter engine
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        sheet_name = "Leads"
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Header format
        header_format = workbook.add_format({
            "bold": True,
            "text_wrap": False,
            "valign": "middle",
            "fg_color": "#1E293B",  # Slate 800
            "font_color": "#FFFFFF",
            "border": 1
        })

        # Cell format
        cell_format = workbook.add_format({
            "valign": "middle",
            "border": 1,
            "border_color": "#E2E8F0"
        })

        # Write styled headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Freeze the top header row
        worksheet.freeze_panes(1, 0)

        # Auto-fit column widths
        for i, col in enumerate(df.columns):
            max_len = max(
                df[col].astype(str).map(len).max() if not df.empty else 0,
                len(col)
            ) + 4
            # Keep column widths readable (wider for Pitch Angle)
            max_cap = 65 if col == "Pitch Angle" else 50
            col_width = min(max(max_len, 14), max_cap)
            worksheet.set_column(i, i, col_width, cell_format)

    output.seek(0)
    return output.getvalue()

def export_to_csv(leads: List[Lead]) -> bytes:
    """
    Exports leads to in-memory UTF-8 CSV bytes.
    """
    data = []
    for lead in leads:
        d = lead.to_export_dict()
        safe_row = {col: sanitize_formula_injection(val) for col, val in d.items()}
        data.append(safe_row)

    df = pd.DataFrame(data)
    if df.empty:
        df = pd.DataFrame(columns=[
            "Business Name", "Phone", "Address", "Website", "Lead Score", 
            "Opportunity", "Suggested Service", "Pitch Angle", "Maps Link", "Category", "Source"
        ])

    csv_str = df.to_csv(index=False, encoding="utf-8-sig")
    return csv_str.encode("utf-8-sig")
