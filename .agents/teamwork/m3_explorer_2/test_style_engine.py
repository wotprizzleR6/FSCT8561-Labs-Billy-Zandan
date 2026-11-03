"""
Test script for python-docx styling engine.
Verifies XML manipulation helpers, table formatting, callout boxes, and code styling.
"""

import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_styled_document():
    doc = docx.Document()

    # Configure Margins (1.0 inch on all sides)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

        # Configure Header & Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hr = hp.add_run("FSCT 8561 — Digital Media Forensics & Incident Response | Lab 6 Report")
        hr.font.name = "Calibri"
        hr.font.size = Pt(8.5)
        hr.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        fr1 = fp.add_run("Student: Billy Zandan (A01371854)")
        fr1.font.name = "Calibri"
        fr1.font.size = Pt(8.5)
        fr1.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Style Helpers
    def set_cell_shading(cell, color_hex):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
        # top/bottom in dxa (20 dxa = 1 pt; 120 dxa = 6 pt; 150 dxa = 7.5 pt)
        tcMar = parse_xml(
            f'<w:tcMar {nsdecls("w")}>'
            f'<w:top w:w="{top}" w:type="dxa"/>'
            f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
            f'<w:left w:w="{left}" w:type="dxa"/>'
            f'<w:right w:w="{right}" w:type="dxa"/>'
            f'</w:tcMar>'
        )
        cell._tc.get_or_add_tcPr().append(tcMar)

    def set_cell_borders(cell, top="D1D5DB", bottom="D1D5DB", left=None, right=None, sz="4"):
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="{"single" if top else "none"}" w:sz="{sz}" w:space="0" w:color="{top or "auto"}"/>'
            f'<w:bottom w:val="{"single" if bottom else "none"}" w:sz="{sz}" w:space="0" w:color="{bottom or "auto"}"/>'
            f'<w:left w:val="{"single" if left else "none"}" w:sz="{sz}" w:space="0" w:color="{left or "auto"}"/>'
            f'<w:right w:val="{"single" if right else "none"}" w:sz="{sz}" w:space="0" w:color="{right or "auto"}"/>'
            f'</w:tcBorders>'
        )
        cell._tc.get_or_add_tcPr().append(tcBorders)

    def set_cell_width(cell, width_in_inches):
        cell.width = Inches(width_in_inches)
        tcW = parse_xml(f'<w:tcW {nsdecls("w")} w:w="{int(width_in_inches * 1440)}" w:type="dxa"/>')
        cell._tc.get_or_add_tcPr().append(tcW)

    def set_table_header_repeat_and_cant_split(row):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    def set_row_cant_split(row):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    # Add Heading
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("LAB 6: COVERT CHANNELS IN IMAGE METADATA")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(20)
    r_title.font.color.rgb = RGBColor(0x00, 0x2B, 0x49) # BCIT Navy

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Forensic Investigation Deliverable & Incident Reconstruction | Billy Zandan (A01371854)")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(10.5)
    r_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Add Table
    headers = ["Filename", "Format", "Metadata Layer", "Suspected Field", "Encoding", "Risk", "Incident Stage"]
    col_widths = [1.0, 0.5, 1.0, 1.0, 0.8, 0.5, 1.7] # Sum = 6.5 in

    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    header_row = table.rows[0]
    set_table_header_repeat_and_cant_split(header_row)
    for idx, (title, width) in enumerate(zip(headers, col_widths)):
        cell = header_row.cells[idx]
        set_cell_width(cell, width)
        set_cell_shading(cell, "002B49") # BCIT Navy
        set_cell_margins(cell, top=140, bottom=140, left=140, right=140)
        set_cell_borders(cell, top="002B49", bottom="002B49", left=None, right=None)
        cell.text = title
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in (1, 4, 5) else WD_ALIGN_PARAGRAPH.LEFT
        r = p.runs[0]
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Test Data Row
    sample_data = [
        ("Brain.png", "PNG", "tEXt chunk", "Software", "Plain text", "10", "RECON: DNS harvesting"),
        ("Activation.png", "PNG", "ExifOffset Sub-IFD", "UserComment", "ASCII header", "15", "VULN: Unpatched CVE"),
    ]

    for row_idx, row_values in enumerate(sample_data):
        row = table.add_row()
        set_row_cant_split(row)
        bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for idx, (val, width) in enumerate(zip(row_values, col_widths)):
            cell = row.cells[idx]
            set_cell_width(cell, width)
            set_cell_shading(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            set_cell_borders(cell, top="E2E8F0", bottom="E2E8F0", left=None, right=None)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in (1, 4, 5) else WD_ALIGN_PARAGRAPH.LEFT
            r = p.runs[0]
            r.font.name = "Calibri"
            r.font.size = Pt(8.0)
            r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
            if idx == 5: # Risk score
                r.bold = True
                r.font.color.rgb = RGBColor(0xDC, 0x26, 0x26) if int(val) >= 15 else RGBColor(0xD9, 0x77, 0x06)

    # Add Callout Box / Code Box
    p_code_intro = doc.add_paragraph()
    p_code_intro.paragraph_format.space_before = Pt(12)
    p_code_intro.paragraph_format.space_after = Pt(4)
    r_intro = p_code_intro.add_run("Code Block Demonstration:")
    r_intro.bold = True
    r_intro.font.name = "Calibri"

    def add_code_block(document, code_lines, title=None):
        box_table = document.add_table(rows=1, cols=1)
        box_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        box_table.autofit = False

        cell = box_table.cell(0, 0)
        set_cell_width(cell, 6.5)
        set_cell_shading(cell, "F1F5F9") # Slate 100
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        # Left border: thick 24 (3pt) BCIT Navy (002B49), others subtle
        set_cell_borders(cell, top="CBD5E1", bottom="CBD5E1", left="002B49", right="CBD5E1", sz="24")

        # Cell paragraph
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0

        if title:
            r_head = p.add_run(f"# --- {title} ---\n")
            r_head.bold = True
            r_head.font.name = "Consolas"
            r_head.font.size = Pt(8.0)
            r_head.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)

        for line in code_lines:
            r = p.add_run(line + "\n")
            r.font.name = "Consolas"
            r.font.size = Pt(7.5)
            if line.startswith("#"):
                r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B) # Comment gray
            elif line.startswith("def ") or line.startswith("class ") or line.startswith("import ") or line.startswith("from "):
                r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) # Keyword dark
                r.bold = True
            else:
                r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    sample_code = [
        "import base64",
        "from PIL import Image, ExifTags",
        "",
        "# Extract EXIF from image file",
        "def inspect_exif(image_path):",
        "    with Image.open(image_path) as img:",
        "        exif = img.getexif()",
        "        return dict(exif.items())",
    ]
    add_code_block(doc, sample_code, "Metadata Inspection Helper")

    out_file = Path(__file__).parent / "test_styled_output.docx"
    doc.save(str(out_file))
    print(f"Successfully generated styled test document at: {out_file}")

if __name__ == "__main__":
    create_styled_document()
