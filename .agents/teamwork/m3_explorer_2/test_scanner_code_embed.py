"""
Test embedding full metadata_scanner.py source code.
"""

from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def test_code_embed():
    scanner_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py")
    code_text = scanner_path.read_text(encoding="utf-8")

    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1.0)

    # Style helper
    def set_cell_shading(cell, color_hex):
        cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'))

    def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
        cell._tc.get_or_add_tcPr().append(parse_xml(
            f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>'
        ))

    def set_cell_borders(cell):
        cell._tc.get_or_add_tcPr().append(parse_xml(
            f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/><w:left w:val="single" w:sz="24" w:space="0" w:color="002B49"/><w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/></w:tcBorders>'
        ))

    def set_cell_width(cell, width_inches):
        cell.width = Inches(width_inches)
        cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:tcW {nsdecls("w")} w:w="{int(width_inches * 1440)}" w:type="dxa"/>'))

    doc.add_heading("Automated Metadata Scanner Implementation", level=1)
    p_desc = doc.add_paragraph("The complete production source code for metadata_scanner.py is embedded below:")

    # Create code block
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    cell = tbl.cell(0, 0)
    set_cell_width(cell, 6.5)
    set_cell_shading(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
    set_cell_borders(cell)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0

    r_hdr = p.add_run("# ==============================================================================\n# FILENAME: metadata_scanner.py (FSCT 8561 Lab 6 Automated Scanner)\n# ==============================================================================\n\n")
    r_hdr.font.name = "Consolas"
    r_hdr.font.size = Pt(7.0)
    r_hdr.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)
    r_hdr.bold = True

    lines = code_text.splitlines()
    for idx, line in enumerate(lines, 1):
        r_num = p.add_run(f"{idx:4d} | ")
        r_num.font.name = "Consolas"
        r_num.font.size = Pt(6.5)
        r_num.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8) # Muted line numbers

        r_code = p.add_run(line + "\n")
        r_code.font.name = "Consolas"
        r_code.font.size = Pt(6.5)
        sline = line.strip()
        if sline.startswith("#") or sline.startswith('"""') or sline.startswith("'''"):
            r_code.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        elif any(sline.startswith(kw) for kw in ("def ", "class ", "import ", "from ", "return ", "if ", "elif ", "else:", "for ", "while ", "try:", "except")):
            r_code.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            r_code.bold = True
        else:
            r_code.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    out = Path(__file__).parent / "test_scanner_code.docx"
    doc.save(str(out))
    print(f"Saved scanner code docx to: {out}")

if __name__ == "__main__":
    test_code_embed()
