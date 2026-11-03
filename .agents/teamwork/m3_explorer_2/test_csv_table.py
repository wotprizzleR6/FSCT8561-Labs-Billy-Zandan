"""
Test dynamic CSV table loading and rendering.
"""

import csv
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def test_csv_table():
    csv_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1.0)

    # Styling helpers
    def set_cell_shading(cell, color_hex):
        cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'))

    def set_cell_margins(cell, top=100, bottom=100, left=100, right=100):
        cell._tc.get_or_add_tcPr().append(parse_xml(
            f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>'
        ))

    def set_cell_borders(cell, top="E2E8F0", bottom="E2E8F0"):
        cell._tc.get_or_add_tcPr().append(parse_xml(
            f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="{top}"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="{bottom}"/><w:left w:val="none"/><w:right w:val="none"/></w:tcBorders>'
        ))

    def set_cell_width(cell, width_inches):
        cell.width = Inches(width_inches)
        cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:tcW {nsdecls("w")} w:w="{int(width_inches * 1440)}" w:type="dxa"/>'))

    headers = [
        "Filename",
        "Format",
        "Discovered Metadata Fields",
        "Suspected Field",
        "Encoding",
        "Risk",
        "Risk Heuristic Justification",
    ]
    widths = [0.95, 0.45, 1.15, 0.95, 0.85, 0.45, 1.70] # Sum = 6.50 in

    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    header_row = table.rows[0]
    header_row._tr.get_or_add_trPr().append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    header_row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    for idx, (h, w) in enumerate(zip(headers, widths)):
        cell = header_row.cells[idx]
        set_cell_width(cell, w)
        set_cell_shading(cell, "002B49")
        set_cell_margins(cell, top=140, bottom=140, left=100, right=100)
        set_cell_borders(cell, top="002B49", bottom="002B49")
        cell.text = h
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in (1, 5) else WD_ALIGN_PARAGRAPH.LEFT
        r = p.runs[0]
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(8.0)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, rec in enumerate(records):
        row = table.add_row()
        row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"

        values = [
            rec["filename"],
            rec["format"],
            rec["metadata_fields"],
            rec["suspected_field"],
            rec["encoding"],
            rec["risk_score"],
            rec["reason"],
        ]

        for c_idx, (val, w) in enumerate(zip(values, widths)):
            cell = row.cells[c_idx]
            set_cell_width(cell, w)
            set_cell_shading(cell, bg)
            set_cell_margins(cell, top=90, bottom=90, left=90, right=90)
            set_cell_borders(cell, top="E2E8F0", bottom="E2E8F0")
            cell.text = str(val)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in (1, 5) else WD_ALIGN_PARAGRAPH.LEFT
            r = p.runs[0]
            r.font.name = "Calibri"
            r.font.size = Pt(7.0) if c_idx in (2, 6) else Pt(7.5)
            r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
            if c_idx == 0:
                r.bold = True
                r.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)
            elif c_idx == 5:
                r.bold = True
                r.font.color.rgb = RGBColor(0xDC, 0x26, 0x26) if int(val) >= 15 else RGBColor(0xD9, 0x77, 0x06)

    out = Path(__file__).parent / "test_csv_table.docx"
    doc.save(str(out))
    print(f"Saved CSV table docx to: {out}")

if __name__ == "__main__":
    test_csv_table()
